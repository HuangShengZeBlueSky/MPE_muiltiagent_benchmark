import os
import re
import json
import numpy as np
import imageio
import math
from typing import Dict, Any, List
from utils_api import get_api_engine, get_unique_filename
from prompt.prompt_for_spread import (
    get_action_and_response_format,
    get_navigation_hints,
    get_physics_rules,
    get_task_and_reward,
)
from obs.parse_spread_obs import parse_spread_obs
try:
    from pettingzoo.mpe import simple_spread_v3
except ImportError:
    raise ImportError("请安装 pettingzoo: pip install pettingzoo[mpe]")

try:
    from openai import OpenAI
    import google.generativeai as genai
except ImportError:
    # 如果只是为了跑通代码，可以暂时忽略，但调用 API 会报错
    print("Warning: API libraries (openai, google-generativeai) not installed.")

ENV_MODULE = "MPE_Simple_v3"
LOCAL_RATIO = 0.5
DEFAULT_N = 3


def _format_current_obs(obs_struct: Dict[str, Any], num_agents: int) -> str:
    obs_semantics = (
        "OBSERVATION semantics:\n"
        f"- obs = [self_vel(2), self_pos(2), landmark_rel(2N), other_agent_rel(2({num_agents}-1)), comm(2({num_agents}-1))]\n"
        "- landmark_rel: (landmark_pos - your_pos) for each landmark.\n"
        "- other_agent_rel: (other_agent_pos - your_pos) for each teammate.\n"
        "- comm: other agents' communication (usually zeros).\n\n"
    )
    return (
        obs_semantics +
        "CURRENT OBS (structured):\n"
        f"{obs_struct}\n"
    )

def generate_semantic_feedback(agent_id: str, reward: float, obs_struct: Dict[str, Any]) -> str:
    """Translate raw numerical rewards and state into text feedback."""
    feedback = f"Step numeric reward: {reward:.3f}. "
    
    # Check collisions
    collisions = sum(1 for ag in obs_struct.get('other_agent_rel', []) if ag[2] < 0.3)
    if collisions > 0:
        feedback += f"CRITICAL: Collided with {collisions} teammate(s). "
        
    # Check landmark coverage
    lm_dists = [lm[2] for lm in obs_struct.get('landmark_rel', [])]
    if lm_dists:
        min_dist = min(lm_dists)
        if min_dist < 0.1:
            feedback += "Successfully covering a landmark. "
        else:
            feedback += f"Not covering any landmark (closest is {min_dist:.2f} away). "
            
    return feedback


def user_prompt(agent: str, step_idx: int, obs_struct: Dict[str, Any], num_agents: int, local_ratio: float, comm_history: Dict[str, str] = None, long_term_memory: str = None, short_term_memory: List[str] = None) -> str:
    header = (
        f"ENV: {ENV_MODULE}\n"
        f"AGENT: {agent}\n"
        f"STEP: {step_idx}"
    )

    if comm_history is not None:
        comm_str = "COMMUNICATION FIELD (from previous step):\n"
        for a_id, msg in comm_history.items():
            if a_id != agent:
                comm_str += f"- {a_id}: {msg}\n"
        if not comm_history:
            comm_str += "- (No messages yet)\n"
        comm_str += "\n"
    else:
        comm_str = "COMMUNICATION FIELD:\n- (No messages yet)\n\n"

    memory_str = "SHORT-TERM MEMORY (Recent actions and environment feedback):\n"
    if short_term_memory and len(short_term_memory) > 0:
        for mem in short_term_memory:
            memory_str += f"- {mem}\n"
    else:
        memory_str += "- (No memories yet)\n"
    memory_str += "\n"

    ltm_str = "LONG-TERM MEMORY (Abstract skills/protocols previously learned):\n"
    if long_term_memory is not None and long_term_memory.strip() != "":
        ltm_str += f"{long_term_memory}\n"
    else:
        ltm_str += "- (No specialized skills acquired yet)\n"

    parts = [
        header,
        get_task_and_reward(num_agents, local_ratio),
        get_physics_rules(),
        get_action_and_response_format(),
        get_navigation_hints(),  # ALWAYS Immutable
        ltm_str,  # Mutated by Optimizer over generations
        memory_str,  # Short term sliding window
        comm_str,
        _format_current_obs(obs_struct, num_agents),
    ]

    return "\n".join(parts)


# ==============================================================================
# 主流程
# ==============================================================================
def run_spread_game(
    provider: str | Dict[str, str],
    output_file: str = "spread_demo.mp4",
    N: int = DEFAULT_N,
    local_ratio: float = LOCAL_RATIO,
    long_term_memories: Dict[str, str] = None,
    disable_comm: bool = False,
    **kwargs
):
    """
    运行 Spread 游戏
    
    Args:
        provider: 模型提供商 ('qwen', 'deepseek', 'gpt', 'ollama', 'transformers', etc.) 
                  OR Dict mapping agent_id backends e.g. {"agent_0": "qwen", "agent_1": "deepseek"}
        output_file: 输出视频文件名
        N: 智能体数量
        local_ratio: 本地奖励比例
        **kwargs: 传递给 get_api_engine 的额外参数
    """
    MAX_STEPS = 30
    seed = kwargs.pop('seed', None)
    
    # Initialize LLM Engine(s)
    system_prompt = "You are a decision module for a game agent. Output only one-line JSON."
    
    print("Initializing MPE Simple...")
    env = simple_spread_v3.parallel_env(
        N=N,
        local_ratio=local_ratio,
        max_cycles=MAX_STEPS,
        continuous_actions=True,
        render_mode="rgb_array",
    )
    observations, infos = env.reset(seed=seed) if seed is not None else env.reset()
    
    # Instantiate engine dictionary after env reset so we know all env.agents
    agent_engines = {}
    if isinstance(provider, dict):
        for aid in env.agents:
            agent_prov = provider.get(aid, "qwen") # fallback
            agent_engines[aid] = get_api_engine(agent_prov, **kwargs)
    else:
        # Global provider
        shared_engine = get_api_engine(provider, **kwargs)
        for aid in env.agents:
            agent_engines[aid] = shared_engine
            
    frames = []
    game_log = []
    total_rewards = {aid: 0.0 for aid in env.agents}
    step_buffer = {}

    comm_hub = {}
    
    # Store the last K steps (e.g. 3) of short-term memory per agent
    st_memory = {aid: [] for aid in env.agents}
    MEMORY_LIMIT = 3

    for step in range(MAX_STEPS):
        print(f"=== STEP {step} ===")
        frame = env.render()
        if frame is not None:
            frames.append(frame)

        actions = {}
        step_buffer = {}
        new_comm_hub = {}
        for agent_id in env.agents:
            obs_raw = observations[agent_id]
            obs_struct = parse_spread_obs(obs_raw, num_agents=N)
            print(f"Agent {agent_id} Obs: {obs_struct}")

            ltm = long_term_memories.get(agent_id) if long_term_memories else None
            
            # Pass None if disable_comm is True, otherwise pass comm_hub
            active_comm = None if disable_comm else comm_hub
            
            full_prompt = user_prompt(agent_id, step, obs_struct, num_agents=N, local_ratio=local_ratio, comm_history=active_comm, long_term_memory=ltm, short_term_memory=st_memory[agent_id])

            action_vec, response_text = agent_engines[agent_id].generate_action(system_prompt, full_prompt)
            action_vec = np.clip(action_vec, 0.0, 1.0)
            actions[agent_id] = action_vec
            
            # Extract message
            message = ""
            try:
                clean_text = response_text.split("</think>")[-1] if "</think>" in response_text else response_text
                match = re.search(r'```json\s*(\{.*?\})\s*```', clean_text, re.DOTALL)
                if not match:
                    match = re.search(r'(\{.*?\})', clean_text, re.DOTALL)
                if match:
                    data = json.loads(match.group(1))
                    message = data.get("message", "")
            except Exception:
                pass
            new_comm_hub[agent_id] = message

            step_buffer[agent_id] = {"obs": obs_struct, "action": action_vec, "thought": response_text, "message": message}
            print(f"  Action: {np.round(action_vec, 2)}")
            print(f"  Message: {message}")
            try:
                print(f"  Response: {response_text[:]}...")
            except UnicodeEncodeError:
                print(f"  Response: [Unicode output omitted]")

        comm_hub = new_comm_hub

        if not actions:
            break

        observations, rewards, terminations, truncations, infos = env.step(actions)
        print(f"Rewards: {rewards}")
        
        for aid, r in rewards.items():
            total_rewards[aid] += r
            semantic_feedback = generate_semantic_feedback(aid, float(r), step_buffer[aid]["obs"])
            game_log.append({
                "step": step,
                "agent": aid,
                "obs": step_buffer[aid]["obs"],
                "action": step_buffer[aid]["action"].tolist(),
                "thought": step_buffer[aid]["thought"],
                "message": step_buffer[aid]["message"],
                "reward": float(r),
                "semantic_feedback": semantic_feedback
            })
            
            # Update short term memory
            # The action decided in the *previous* block resulted in this semantic_feedback
            action_snippet = np.round(step_buffer[aid]["action"], 2).tolist()
            st_memory[aid].append(f"Step {step}: Chose action force {action_snippet}. Feedback: {semantic_feedback}")
            # Keep only recent memory
            if len(st_memory[aid]) > MEMORY_LIMIT:
                st_memory[aid].pop(0)
        
        if all(terminations.values()) or all(truncations.values()):
            break

    env.close()
    
    # Add final summary
    mean_reward = sum(total_rewards.values()) / len(total_rewards) if total_rewards else 0.0
    game_log.append({
        "final_summary": True,
        "total_rewards": {k: float(v) for k, v in total_rewards.items()},
        "mean_reward": float(mean_reward)
    })
    print(f"\nFINAL REWARDS: {total_rewards}, MEAN: {mean_reward:.3f}")
    
    if frames:
        final_output = get_unique_filename(output_file)
        print(f"Saving video to {final_output}...")
        try:
            writer = imageio.get_writer(final_output, fps=2, codec='libx264', quality=8)
            for frame in frames:
                writer.append_data(frame)
            writer.close()
        except Exception:
            # Fallback: save as GIF if ffmpeg is not available
            gif_output = final_output.replace('.mp4', '.gif')
            imageio.mimsave(gif_output, frames, fps=2)
            print(f"  (ffmpeg unavailable, saved as GIF: {gif_output})")
    
    if game_log:
        log_file = get_unique_filename(output_file.replace(".mp4", ".json"))
        with open(log_file, "w", encoding="utf-8") as f:
            json.dump(game_log, f, indent=2, ensure_ascii=False)
        print(f"Saved log to {log_file}")

if __name__ == "__main__":
    # ========== 统一模型接口 ==========
    # 远程 API: 'deepseek', 'qwen', 'gpt', 'gemini'
    # 本地模型: 'transformers', 'ollama', 'vllm'

    # 方式 1: 使用默认配置
    PROVIDER = "qwen"
    run_spread_game(PROVIDER, f"demo_{PROVIDER}.mp4")
    
    # 方式 2: 自定义 API Key
    # PROVIDER = "deepseek"
    # run_spread_game(PROVIDER, f"demo_{PROVIDER}.mp4", api_key="your-key")
    
    # 方式 3: 使用本地 Ollama 模型
    # PROVIDER = "ollama"
    # run_spread_game(PROVIDER, f"demo_{PROVIDER}.mp4", model_name="qwen2.5:7b")
    
    # 方式 4: 使用 Transformers 本地模型
    # PROVIDER = "transformers"
    # run_spread_game(PROVIDER, f"demo_{PROVIDER}.mp4", 
    #                 model_path="Qwen/Qwen2.5-7B-Instruct", device="cuda")
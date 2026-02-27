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


def user_prompt(agent: str, step_idx: int, obs_struct: Dict[str, Any], num_agents: int, local_ratio: float) -> str:
    header = (
        f"ENV: {ENV_MODULE}\n"
        f"AGENT: {agent}\n"
        f"STEP: {step_idx}"
    )

    parts = [
        header,
        get_task_and_reward(num_agents, local_ratio),
        get_physics_rules(),
        get_action_and_response_format(),
        get_navigation_hints(),
        _format_current_obs(obs_struct, num_agents),
    ]

    return "\n".join(parts)


# ==============================================================================
# 主流程
# ==============================================================================
def run_spread_game(
    provider: str,
    output_file: str = "spread_demo.mp4",
    N: int = DEFAULT_N,
    local_ratio: float = LOCAL_RATIO,
    **kwargs
):
    """
    运行 Spread 游戏
    
    Args:
        provider: 模型提供商 ('qwen', 'deepseek', 'gpt', 'ollama', 'transformers', etc.)
        output_file: 输出视频文件名
        N: 智能体数量
        local_ratio: 本地奖励比例
        **kwargs: 传递给 get_api_engine 的额外参数
    """
    MAX_STEPS = 30
    seed = kwargs.pop('seed', None)
    llm_engine = get_api_engine(provider, **kwargs)
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
    frames = []
    game_log = []
    total_rewards = {aid: 0.0 for aid in env.agents}
    step_buffer = {}

    for step in range(MAX_STEPS):
        print(f"=== STEP {step} ===")
        frame = env.render()
        if frame is not None:
            frames.append(frame)

        actions = {}
        step_buffer = {}
        for agent_id in env.agents:
            obs_raw = observations[agent_id]
            obs_struct = parse_spread_obs(obs_raw, num_agents=N)
            print(f"Agent {agent_id} Obs: {obs_struct}")

            full_prompt = user_prompt(agent_id, step, obs_struct, num_agents=N, local_ratio=local_ratio)

            action_vec, response_text = llm_engine.generate_action(system_prompt, full_prompt)
            action_vec = np.clip(action_vec, 0.0, 1.0)
            actions[agent_id] = action_vec
            step_buffer[agent_id] = {"obs": obs_struct, "action": action_vec, "thought": response_text}
            print(f"  Action: {np.round(action_vec, 2)}")
            print(f"  Response: {response_text[:]}...")

        if not actions:
            break

        observations, rewards, terminations, truncations, infos = env.step(actions)
        print(f"Rewards: {rewards}")
        
        for aid, r in rewards.items():
            total_rewards[aid] += r
            game_log.append({
                "step": step,
                "agent": aid,
                "obs": step_buffer[aid]["obs"],
                "action": step_buffer[aid]["action"].tolist(),
                "thought": step_buffer[aid]["thought"],
                "reward": float(r)
            })
        
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
        imageio.mimsave(final_output, frames, fps=1)
    
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
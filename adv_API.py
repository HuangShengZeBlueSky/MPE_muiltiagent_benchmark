import numpy as np
import imageio
import json
from typing import Dict, Any

# 1. 导入通用工具
from utils_api import get_api_engine, get_unique_filename
from prompt.prompt_for_adv import (
    get_action_and_response_format,
    get_navigation_hints,
    get_physics_rules,
    get_task_and_reward,
)
from obs.parse_adv_obs import parse_adversary_obs

# 2. 导入环境
try:
    from pettingzoo.mpe import simple_adversary_v3
except ImportError:
    raise ImportError("请安装 pettingzoo: pip install pettingzoo[mpe]")

def get_header(env_name: str, agent_name: str, step: int, role: str) -> str:
    return (
        f"ENV: {env_name}\n"
        f"AGENT: {agent_name}\n"
        f"ROLE: {role.upper()}\n"
        f"STEP: {step}"
    )


def _format_current_obs(obs_struct: Dict[str, Any], num_good: int) -> str:
    """Format current observation data with role-specific highlights."""
    json_str = json.dumps(obs_struct)
    
    # Add obs semantics
    obs_semantics = (
        "OBSERVATION SEMANTICS:\n"
        f"- obs vectors are relative coordinates [dx, dy] and distances.\n"
        f"- landmarks: There are {num_good} landmarks. One is the Goal.\n"
    )
    if obs_struct['role'] == 'ADVERSARY':
        obs_semantics += "- good_agents: The Good Agents you need to watch/follow.\n\n"
    else:
        obs_semantics += (
            "- goal: The relative position of the REAL TARGET.\n"
            "- adversary: The enemy you must fool.\n"
            "- teammates: Your partner in crime.\n\n"
        )
    
    if obs_struct['role'] == 'GOOD_AGENT':
        goal_info = (
            f"- REAL TARGET (GOAL): {obs_struct['goal']['rel']} (Dist: {obs_struct['goal']['dist']})\n"
            f"  -> This is where the team needs to be.\n"
        )
        adv_info = (
            f"- ADVERSARY POS: {obs_struct['adversary']['rel']} (Dist: {obs_struct['adversary']['dist']})\n"
            f"  -> If Adversary dist to Goal is small, you are losing points!\n"
        )
        return (
            obs_semantics +
            "CURRENT OBS (Structured):\n"
            f"{json_str}\n"
            "--------------------------------------------------\n"
            "CRITICAL INFO:\n"
            f"{goal_info}"
            f"{adv_info}"
            "--------------------------------------------------\n"
        )
    else:
        return (
            obs_semantics +
            "CURRENT OBS (Structured):\n"
            f"{json_str}\n"
            "--------------------------------------------------\n"
            "CRITICAL INFO:\n"
            "- UNKNOWN GOAL: You must guess which landmark is the target.\n"
            "- HINT: Look at 'landmarks' and 'good_agents'. Are agents converging on Landmark 0 or 1?\n"
            "--------------------------------------------------\n"
        )


def user_prompt_adversary(agent: str, step: int, obs: Dict[str, Any], is_adversary: bool, num_good: int) -> str:
    """Assemble full prompt from modular components."""
    role_name = "ADVERSARY" if is_adversary else "GOOD_AGENT"
    
    parts = [
        get_header("MPE_Simple_Adversary_v3", agent, step, role_name),
        get_task_and_reward(is_adversary),
        get_physics_rules(),
        get_action_and_response_format(),
        get_navigation_hints(is_adversary),
        _format_current_obs(obs, num_good),
    ]
    return "\n\n".join(parts)


# ==============================================================================
# 2. 主流程
# ==============================================================================

def run_adversary_game(provider: str, output_name: str, **kwargs):
    """
    运行 Adversary 游戏
    
    Args:
        provider: 模型提供商 ('qwen', 'deepseek', 'gpt', 'ollama', 'transformers', etc.)
        output_name: 输出文件名前缀
        **kwargs: 传递给 get_api_engine 的额外参数（支持 seed 参数）
    """
    # 配置
    N_GOOD = 3         # 好人数量          
    MAX_STEPS = 30      # Adversary 环境通常步数较短
    
    # 初始化
    seed = kwargs.pop('seed', None)
    llm_engine = get_api_engine(provider, **kwargs)
    print(f"Initializing Adversary Env (N={N_GOOD})...")
    # 注意：render_mode="rgb_array" 用于生成视频
    env = simple_adversary_v3.parallel_env(N=N_GOOD, max_cycles=MAX_STEPS, continuous_actions=True, render_mode="rgb_array")
    
    observations, infos = env.reset(seed=seed) if seed is not None else env.reset()
    frames = []
    
    # 全局统计
    game_log = []
    total_reward_good = 0.0
    total_reward_adv = 0.0

    for step in range(MAX_STEPS):
        print(f"\n{'='*20} STEP {step} {'='*20}")
        
        # 1. 渲染画面
        frame = env.render()
        if frame is not None: frames.append(frame)
        
        actions = {}
        # 暂存本回合每个智能体的信息，等拿到 reward 再打印
        step_buffer = {} 

        # --- 2. 决策阶段 (Decision Phase) ---
        for agent_id in env.agents:
            obs_raw = observations[agent_id]
            is_adversary = "adversary" in agent_id
            
            # A. 解析观测 (Parsing)
            obs_struct = parse_adversary_obs(obs_raw, agent_id, N_GOOD)
            
            # B. 组装提示词 (Prompting)
            full_prompt = user_prompt_adversary(agent_id, step, obs_struct, is_adversary, N_GOOD)
            
            # C. 调用大模型 (Reasoning)
            system_role = "You are a Spy. Capture the target." if is_adversary else "You are a Secret Agent. Protect the target."
            
            # 为了防止网络波动，可以加个简单的重试或者异常捕获（在 get_api_engine 里已处理）
            action_vec, raw_thought = llm_engine.generate_action(system_role, full_prompt)
            
            # D. 动作后处理 (维度保护 + Clipping)
            expected_dim = env.action_space(agent_id).shape[0]
            actual_dim = int(action_vec.shape[0])
            if actual_dim != expected_dim:
                if actual_dim > expected_dim:
                    action_vec = action_vec[:expected_dim]
                else:
                    action_vec = np.pad(action_vec, (0, expected_dim - actual_dim), mode='constant', constant_values=0.0)
                print(
                    f"⚠️ Action dim adjusted for {agent_id}: expected {expected_dim}, got {actual_dim}. "
                    f"Using {expected_dim}-dim action."
                )

            action_vec = np.clip(action_vec, 0.0, 1.0)
            actions[agent_id] = action_vec
            
            # 存入 Buffer
            step_buffer[agent_id] = {
                "role": "BAD" if is_adversary else "GOOD",
                "obs_text": _format_current_obs(obs_struct, N_GOOD),
                "thought": raw_thought,
                "action": action_vec,
                # 存原始结构方便后续存 JSON
                "obs_struct": obs_struct 
            }

        if not actions: 
            print("No actions generated. Ending episode.")
            break

        # --- 3. 环境步进 (Physics Step) ---
        observations, rewards, terminations, truncations, infos = env.step(actions)
        
        # --- 4. 统一打印日志 (Readable Log & Analysis) ---
        for agent_id, info in step_buffer.items():
            reward = rewards.get(agent_id, 0.0)
            role_tag = f"[{info['role']}] {agent_id}"
            
            # 累加统计
            if info['role'] == "GOOD":
                # Good agents 共享奖励，为了不算重，这里只加一次，或者除以 N
                # 简单起见，我们在外面单算
                pass
            else:
                total_reward_adv += reward

            # 存入 JSON log
            game_log.append({
                "step": step,
                "agent": agent_id,
                "role": info['role'],
                "obs": info['obs_struct'],
                "action": info['action'].tolist(),
                "thought": info['thought'],
                "reward": reward
            })
            
            # 打印控制台
            print(f"\n🔷 {role_tag} | Reward: {reward:.3f}")
            
            # 4.1 打印模型看到的关键信息 (Obs Highlight)
            print(f"   👀 Obs Highlight:")
            for line in info['obs_text'].split('\n'):
                # 只打印包含关键信息的行，保持整洁
                if any(k in line for k in ["TARGET", "ADVERSARY", "Direction", "role"]):
                    print(f"      {line.strip()}")
            
            # 4.2 打印思考过程 (Thought)
            # 处理 DeepSeek 的 <think> 标签或 JSON 格式，取前 150 字符预览
            thought_preview = info['thought'][:150].replace('\n', ' ')
            print(f"   🧠 Thought: {thought_preview}...") 
            
            # 4.3 打印动作 (Action)
            act = info['action']
            act_str = f"[{act[0]:.1f}, L:{act[1]:.2f}, R:{act[2]:.2f}, D:{act[3]:.2f}, U:{act[4]:.2f}]"
            print(f"   🎬 Action: {act_str}")

        # 统计 Good Agent 的总分 (取其中一个即可，因为共享)
        # 假设 agent_0 是好人
        if 'agent_0' in rewards:
            total_reward_good += rewards['agent_0']

        if all(terminations.values()) or all(truncations.values()):
            print("\nGame Over (Terminated/Truncated).")
            break

    env.close()
    
    # Add final summary
    mean_reward = (total_reward_good + total_reward_adv) / 2.0
    game_log.append({
        "final_summary": True,
        "total_rewards": {"good": total_reward_good, "adversary": total_reward_adv},
        "mean_reward": float(mean_reward)
    })
    
    print(f"\n{'='*40}")
    print(f"📊 EPISODE SUMMARY")
    print(f"   Total Good Reward: {total_reward_good:.2f}")
    print(f"   Total Adv Reward:  {total_reward_adv:.2f}")
    print(f"   Mean Reward: {mean_reward:.2f}")
    print(f"{'='*40}\n")

    # --- 5. 保存结果 ---
    if frames:
        final_video = get_unique_filename(output_name + ".mp4")
        print(f"Saving video to {final_video} ...")
        # macro_block_size=1 用于解决某些播放器的尺寸兼容问题
        imageio.mimsave(final_video, frames, fps=4, macro_block_size=1)
    
    final_log = get_unique_filename(output_name + ".json")
    print(f"Saving logs to {final_log} ...")
    with open(final_log, "w", encoding="utf-8") as f:
        json.dump(game_log, f, indent=4, ensure_ascii=False)

# ==============================================================================
# 3. 运行入口
# ==============================================================================
if __name__ == "__main__":
    # ========== 统一模型接口 ==========
    # 远程 API: 'deepseek', 'qwen', 'gpt', 'gemini'
    # 本地模型: 'transformers', 'ollama', 'vllm'
    
    # 方式 1: 使用默认配置
    PROVIDER = "qwen"
    
    # 方式 2: 自定义 API Key (可选)
    # PROVIDER = "deepseek"
    # run_adversary_game(PROVIDER, "adv_demo", api_key="your-key")
    
    # 方式 3: 使用本地 Ollama 模型
    # PROVIDER = "ollama"
    # run_adversary_game(PROVIDER, "adv_demo", model_name="qwen2.5:7b")
    
    # 方式 4: 使用 Transformers 本地模型
    # PROVIDER = "transformers"
    # run_adversary_game(PROVIDER, "adv_demo", model_path="Qwen/Qwen2.5-7B-Instruct", device="cuda")

    N_EPISODES = 1
    print(f"Plan to run {N_EPISODES} episodes...")

    for i in range(N_EPISODES):
        print(f"\n\n" + "="*40)
        print(f"🎬 STARTING BATCH {i+1} / {N_EPISODES}")
        batch_name = f"adv_demo_run_{i+1}"
        try:
            run_adversary_game(PROVIDER, batch_name)
        except Exception as e:
            print(f"❌ Error: {e}")
            continue
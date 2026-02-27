import numpy as np
import json
from typing import Dict, Any

# 1. 导入通用工具
from utils_api import get_api_engine, get_unique_filename
from prompt.prompt_for_crypto import (
    get_action_and_response_format,
    get_navigation_hints,
    get_physics_rules,
    get_task_and_reward,
)
from obs.parse_crypto_obs import parse_crypto_obs

# 2. 导入环境
try:
    from pettingzoo.mpe import simple_crypto_v3
except ImportError:
    raise ImportError("请安装 pettingzoo: pip install pettingzoo[mpe]")

def get_header(env_name: str, agent_name: str, step: int) -> str:
    return (
        f"ENV: {env_name}\n"
        f"AGENT: {agent_name}\n"
        f"STEP: {step}"
    )


def _format_current_obs(obs_struct: Dict[str, Any]) -> str:
    role = obs_struct.get("role", "UNKNOWN")
    data_flow = [
        "CURRENT DATA FLOW:",
        f"- role: {role}",
        f"- raw: {obs_struct.get('raw')}",
    ]
    if role == "ALICE":
        data_flow.append(f"- message (M): {obs_struct.get('message')}")
        data_flow.append(f"- key (K): {obs_struct.get('key')}")
    elif role == "BOB":
        data_flow.append(f"- key (K): {obs_struct.get('key')}")
        data_flow.append(f"- ciphertext (C): {obs_struct.get('ciphertext')}")
    elif role == "EVE":
        data_flow.append(f"- ciphertext (C): {obs_struct.get('ciphertext')}")
    return "\n".join(data_flow)


def user_prompt_crypto(agent_id: str, step: int, obs_struct: Dict[str, Any]) -> str:
    role = obs_struct.get("role", "UNKNOWN")
    parts = [
        get_header("Simple_Crypto_v3", agent_id, step),
        get_task_and_reward(role),
        get_physics_rules(),
        get_action_and_response_format(),
        get_navigation_hints(role),
        _format_current_obs(obs_struct),
    ]
    return "\n\n".join(parts)


# ============================================================================== 
# 3. 主循环
# ==============================================================================
def run_crypto_game(provider: str, output_name: str, **kwargs):
    # MPE Crypto 每一帧的数据通常是独立的（或者说环境不会记忆上一帧的加密），
    # 真正的学习需要多轮迭代。但在 zero-shot 设定下，我们看模型单次的推理能力。
    MAX_STEPS = 10
    
    seed = kwargs.pop('seed', None)
    llm_engine = get_api_engine(provider, **kwargs)

    print("Initializing Crypto Env (Fair Mode)...")
    env = simple_crypto_v3.parallel_env(max_cycles=MAX_STEPS, continuous_actions=True, render_mode="rgb_array")
    
    observations, infos = env.reset(seed=seed) if seed is not None else env.reset()
    frames = []
    game_log = []
    
    for step in range(MAX_STEPS):
        print(f"\n{'='*40} STEP {step} {'='*40}")
        
        frame = env.render()
        if frame is not None:
            frames.append(frame)
        
        actions = {}
        step_buffer = {} # 暂存本回合信息

        # --- 1. Decision Phase ---
        for agent_id in env.agents:
            obs_raw = observations[agent_id]
            obs_struct = parse_crypto_obs(obs_raw, agent_id)
            
            # Prompt
            full_prompt = user_prompt_crypto(agent_id, step, obs_struct)
            
            # System Role
            if 'alice' in agent_id: sys_r = "You are Alice, a Cryptographer."
            elif 'bob' in agent_id: sys_r = "You are Bob, a Cryptographer."
            else: sys_r = "You are Eve, a Code Breaker."
            
            # API Call
            action_vec, raw_thought = llm_engine.generate_action(sys_r, full_prompt)
            
            # 维度修正 & Clip
            if len(action_vec) < 4:
                action_vec = np.concatenate([action_vec, np.zeros(4 - len(action_vec))])
            elif len(action_vec) > 4:
                action_vec = action_vec[:4]
            action_vec = np.clip(action_vec, 0.0, 1.0)
            
            actions[agent_id] = action_vec
            
            step_buffer[agent_id] = {
                "struct": obs_struct,
                "action": action_vec,
                "thought": raw_thought
            }

        # --- 2. Step Phase ---
        observations, rewards, terminations, truncations, infos = env.step(actions)
        
        # --- 3. Analysis Phase ---
        # 获取真值 (Ground Truth)
        true_msg = step_buffer['alice_0']['struct']['message']
        
        for aid, info in step_buffer.items():
            r = rewards.get(aid, 0.0)
            role = info['struct']['role']
            print(f"\n👤 {aid} ({role}) | Reward: {r:.3f}")
            
            # 打印逻辑链
            if role == 'ALICE':
                msg = np.array(info['struct']['message'])
                key = np.array(info['struct']['key'])
                cip = np.array(info['action'])
                print(f"   [Logic] Msg {np.round(msg,2)} + Key {np.round(key,2)} -> Cipher {np.round(cip,2)}")
                
            elif role == 'BOB':
                key = np.array(info['struct']['key'])
                cip = np.array(info['struct']['ciphertext']) # 这是上一回合的，或者本回合还没收到？
                # MPE 机制提醒：Bob 这一步看到的 Ciphertext 其实是 Alice *上一步* 发的。
                # 在 Step 0，Bob 看到的 Ciphertext 通常是 0。
                # 所以 Bob 的推理其实是滞后一步的。但为了评测 LLM 单步能力，我们看它是否尝试去算。
                guess = np.array(info['action'])
                print(f"   [Logic] Key {np.round(key,2)} + Cipher {np.round(cip,2)} -> Guess {np.round(guess,2)}")
                
                # 计算当前帧误差 (虽然环境可能是滞后结算，我们肉眼看当下的匹配度)
                # 注意：Bob 本回合的猜测应该对应 Alice 本回合的发送吗？
                # 不，MPE 是 Alice 发 -> Env 存 -> 下一步 Bob 收。
                # 所以 Step 0 Bob 猜不对是正常的。我们要看 Step 1。
                
            elif role == 'EVE':
                cip = np.array(info['struct']['ciphertext'])
                guess = np.array(info['action'])
                print(f"   [Logic] Cipher {np.round(cip,2)} -> Guess {np.round(guess,2)}")

            # 打印思维链摘要
            print(f"   🧠 Thought: {info['thought'][:200].replace(chr(10), ' ')}...")
            
            game_log.append({
                "step": step,
                "agent": aid,
                "reward": r,
                "obs": info['struct'],
                "action": info['action'].tolist(),
                "thought": info['thought']
            })

        if all(terminations.values()) or all(truncations.values()):
            print("Game Over.")
            break

    env.close()
    
    # Calculate final summary
    total_rewards = {}
    for entry in game_log:
        if "agent" in entry:
            aid = entry["agent"]
            total_rewards[aid] = total_rewards.get(aid, 0.0) + entry.get("reward", 0.0)
    
    mean_reward = sum(total_rewards.values()) / len(total_rewards) if total_rewards else 0.0
    game_log.append({
        "final_summary": True,
        "total_rewards": total_rewards,
        "mean_reward": float(mean_reward)
    })
    print(f"\n📊 FINAL: Total Rewards={total_rewards}, Mean={mean_reward:.3f}")
    
    # Save video
    if frames:
        vid_name = get_unique_filename(output_name + ".mp4")
        import imageio
        imageio.mimsave(vid_name, frames, fps=1, macro_block_size=1)
        print(f"Saved video to {vid_name}")
    
    final_log = get_unique_filename(output_name + ".json")
    with open(final_log, "w", encoding="utf-8") as f:
        json.dump(game_log, f, indent=4)
    print(f"Saved logs to {final_log}")

# ============================================================================== 
# 4. 入口
# ==============================================================================
if __name__ == "__main__":
    # ========== 统一模型接口 ==========
    # 远程 API: 'deepseek', 'qwen', 'gpt', 'gemini'
    # 本地模型: 'transformers', 'ollama', 'vllm'
    
    # 方式 1: 使用默认配置
    PROVIDER = "qwen"
    
    # 方式 2: 自定义 API Key
    # PROVIDER = "deepseek"
    # run_crypto_game(PROVIDER, "crypto_demo", api_key="your-key")
    
    # 方式 3: 使用本地 Ollama 模型
    # PROVIDER = "ollama"
    # run_crypto_game(PROVIDER, "crypto_demo", model_name="qwen2.5:7b")
    
    # 方式 4: 使用 Transformers 本地模型
    # PROVIDER = "transformers"
    # run_crypto_game(PROVIDER, "crypto_demo", model_path="Qwen/Qwen2.5-7B-Instruct", device="cuda")

    print("Starting Crypto Fair Evaluation...")
    run_crypto_game(PROVIDER, "crypto_fair_run")
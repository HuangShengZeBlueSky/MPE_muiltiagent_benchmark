import numpy as np
import json
from typing import Dict, Any

from utils_api import get_api_engine, get_unique_filename
from prompt.prompt_for_reference import (
    get_action_and_response_format,
    get_navigation_hints,
    get_physics_rules,
    get_task_and_reward,
)
from obs.parse_reference_obs import parse_reference_obs

try:
    from pettingzoo.mpe import simple_reference_v3
except ImportError:
    raise ImportError("请安装 pettingzoo: pip install pettingzoo[mpe]")


def _format_current_obs(obs_struct: Dict[str, Any], agent_id: str) -> str:
    lines = [
        "OBSERVATION SEMANTICS:",
        "- obs = [vel(2), landmarks(3*2), partner_goal_rgb(3), comm(10)]",
        "CURRENT OBS STRUCT:",
        f"- agent_id: {agent_id}",
        f"- vel: {obs_struct.get('vel')}",
        f"- landmarks: {obs_struct.get('landmarks')}",
        f"- partner_goal_rgb: {obs_struct.get('partner_goal_rgb')}",
        f"- partner_target_id: {obs_struct.get('partner_target_id')}",
        f"- heard_signal: {obs_struct.get('heard_signal')} (strength={obs_struct.get('signal_strength')})",
    ]
    warn = obs_struct.get("warning")
    if warn:
        lines.append(f"- warning: {warn}")
    return "\n".join(lines)


def user_prompt_reference(agent_id: str, step: int, obs_struct: Dict[str, Any]) -> str:
    parts = [
        get_task_and_reward(),
        get_physics_rules(),
        get_action_and_response_format(),
        get_navigation_hints(),
        _format_current_obs(obs_struct, agent_id),
    ]
    return "\n\n".join(parts)


def run_reference_game(provider: str, output_name: str, **kwargs):
    MAX_STEPS = 30
    seed = kwargs.pop('seed', None)
    llm_engine = get_api_engine(provider, **kwargs)

    print("Initializing Reference Env (Modular)...")
    env = simple_reference_v3.parallel_env(max_cycles=MAX_STEPS, continuous_actions=True, render_mode="rgb_array")

    observations, infos = env.reset(seed=seed) if seed is not None else env.reset()
    frames = []
    game_log = []
    total_rewards = {aid: 0.0 for aid in env.agents}

    for step in range(MAX_STEPS):
        print(f"\n{'='*30} STEP {step} {'='*30}")
        frame = env.render()
        if frame is not None:
            frames.append(frame)

        actions = {}
        step_buffer = {}

        for agent_id in env.agents:
            obs_struct = parse_reference_obs(observations[agent_id], agent_id)
            full_prompt = user_prompt_reference(agent_id, step, obs_struct)

            sys_r = "You are a precise communication agent. Follow the required action indices strictly."
            action_vec, raw_thought = llm_engine.generate_action(sys_r, full_prompt)

            if len(action_vec) < 15:
                action_vec = np.concatenate([action_vec, np.zeros(15 - len(action_vec))])
            action_vec = np.clip(action_vec[:15], 0.0, 1.0)

            actions[agent_id] = action_vec
            step_buffer[agent_id] = {"struct": obs_struct, "action": action_vec, "thought": raw_thought}

        observations, rewards, terminations, truncations, infos = env.step(actions)

        for aid, info in step_buffer.items():
            r = rewards.get(aid, 0.0)
            total_rewards[aid] = total_rewards.get(aid, 0.0) + r

            struct = info["struct"]
            act = info["action"]

            move_str = "HOLD"
            if len(act) >= 5:
                move_idx = int(np.argmax(act[0:5]))
                move_str = ["HOLD", "LEFT", "RIGHT", "DOWN", "UP"][move_idx]
                if max(act[0:5]) < 0.1:
                    move_str = "HOLD"

            say_str = "SILENT"
            say_idx = -1
            if len(act) >= 15 and max(act[5:15]) > 0.1:
                say_idx = int(np.argmax(act[5:15]))
                say_str = f"SAY_{say_idx}"

            required_say_idx = 5 + struct.get("partner_target_id", -1)
            say_value = act[required_say_idx] if 0 <= required_say_idx < len(act) else 0.0

            print(f"\nAGENT {aid} | Reward: {r:.4f}")
            print(f"   Speaker: target_id={struct.get('partner_target_id')} -> index {required_say_idx} value {say_value:.2f}")
            print(f"   Listener: heard={struct.get('heard_signal')} (strength={struct.get('signal_strength')}) -> move {move_str}")
            print(f"   Action: move={move_str}, say={say_str}")
            warn = struct.get("warning")
            if warn:
                print(f"   Warning: {warn}")
            
            game_log.append({
                "step": step,
                "agent": aid,
                "obs": struct,
                "action": act.tolist(),
                "thought": info["thought"],
                "reward": r
            })

        if all(terminations.values()) or all(truncations.values()):
            print("Game Over.")
            break

    env.close()

    # Add final summary
    mean_reward = sum(total_rewards.values()) / len(total_rewards) if total_rewards else 0.0
    game_log.append({
        "final_summary": True,
        "total_rewards": {k: float(v) for k, v in total_rewards.items()},
        "mean_reward": float(mean_reward)
    })
    print(f"\n📊 FINAL: Total Rewards={total_rewards}, Mean={mean_reward:.3f}")

    if frames:
        vid_name = get_unique_filename(output_name + ".mp4")
        import imageio
        imageio.mimsave(vid_name, frames, fps=4, macro_block_size=1)
        print(f"Saved video to {vid_name}")

    final_log = get_unique_filename(output_name + ".json")
    with open(final_log, "w", encoding="utf-8") as f:
        json.dump(game_log, f, indent=4)
    print(f"Saved detailed logs to {final_log}")


if __name__ == "__main__":
    # Unified model interface examples:
    # PROVIDER options: 'deepseek', 'qwen', 'gpt', 'gemini', 'transformers', 'ollama', 'vllm'
    PROVIDER = "qwen"

    # Example overrides:
    # run_reference_game("deepseek", "reference_demo", api_key="your-key")
    # run_reference_game("ollama", "reference_demo", model_name="qwen2.5:7b")
    # run_reference_game("transformers", "reference_demo", model_path="Qwen/Qwen2.5-7B-Instruct", device="cuda")

    print("Starting Reference Run (Modular)...")
    run_reference_game(PROVIDER, "reference_modular")

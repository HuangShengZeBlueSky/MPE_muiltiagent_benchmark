import numpy as np
import json
from typing import Dict, Any

from utils_api import get_api_engine, get_unique_filename
from prompt.prompt_for_speaker_listener import (
    get_action_and_response_format,
    get_navigation_hints,
    get_physics_rules,
    get_task_and_reward,
)
from obs.parse_speaker_listener_obs import parse_speaker_listener_obs

try:
    from pettingzoo.mpe import simple_speaker_listener_v4
except ImportError:
    raise ImportError("请安装 pettingzoo: pip install pettingzoo[mpe]")


def _format_current_obs(obs_struct: Dict[str, Any], agent_id: str) -> str:
    role = obs_struct["role"]
    lines = [
        "OBSERVATION SEMANTICS:",
    ]
    if role == "SPEAKER":
        lines.extend([
            "- obs = [goal_vector(3)] one-hot indicating target landmark",
            "CURRENT OBS STRUCT:",
            f"- agent_id: {agent_id}",
            f"- goal_vector: {obs_struct.get('goal_vector')}",
            f"- target_landmark_id: {obs_struct.get('target_landmark_id')}",
        ])
    else:
        lines.extend([
            "- obs = [vel(2), landmarks(3x2), comm_vector(3)]",
            "CURRENT OBS STRUCT:",
            f"- agent_id: {agent_id}",
            f"- vel: {obs_struct.get('vel')}",
            f"- landmarks: {obs_struct.get('landmarks')}",
            f"- comm_vector: {obs_struct.get('comm_vector')}",
            f"- heard_id: {obs_struct.get('heard_id')}",
        ])
    
    warn = obs_struct.get("warning")
    if warn:
        lines.append(f"- warning: {warn}")
    return "\n".join(lines)


def user_prompt_speaker_listener(agent_id: str, step: int, obs_struct: Dict[str, Any]) -> str:
    role = obs_struct["role"]
    parts = [
        get_task_and_reward(role),
        get_physics_rules(role),
        get_action_and_response_format(role),
        get_navigation_hints(role),
        _format_current_obs(obs_struct, agent_id),
    ]
    return "\n\n".join(parts)


def run_speaker_listener(provider: str, output_name: str, **kwargs):
    MAX_STEPS = 30
    seed = kwargs.pop('seed', None)
    llm_engine = get_api_engine(provider, **kwargs)

    print("Initializing Speaker-Listener (Modular)...")
    env = simple_speaker_listener_v4.parallel_env(max_cycles=MAX_STEPS, continuous_actions=True, render_mode="rgb_array")

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
            obs_struct = parse_speaker_listener_obs(observations[agent_id], agent_id)
            role = obs_struct["role"]
            full_prompt = user_prompt_speaker_listener(agent_id, step, obs_struct)

            sys_r = f"You are a precise {role} agent. Output strict JSON."
            action_vec, raw_thought = llm_engine.generate_action(sys_r, full_prompt)

            # Determine expected dimension
            expected_dim = 3 if role == "SPEAKER" else 5

            if len(action_vec) < expected_dim:
                action_vec = np.concatenate([action_vec, np.zeros(expected_dim - len(action_vec))])
            action_vec = np.clip(action_vec[:expected_dim], 0.0, 1.0)

            actions[agent_id] = action_vec
            step_buffer[agent_id] = {"struct": obs_struct, "action": action_vec, "thought": raw_thought}

        observations, rewards, terminations, truncations, infos = env.step(actions)

        for aid, info in step_buffer.items():
            r = rewards.get(aid, 0.0)
            total_rewards[aid] = total_rewards.get(aid, 0.0) + r

            struct = info["struct"]
            act = info["action"]
            role = struct["role"]

            print(f"\nAGENT {aid} ({role}) | Reward: {r:.4f}")

            if role == "SPEAKER":
                target_id = struct.get("target_landmark_id")
                say_idx = int(np.argmax(act)) if max(act) > 0.1 else -1
                print(f"   Target: {target_id} -> Broadcast: Say_{say_idx}")
                print(f"   Action: {np.round(act, 2)}")
            else:
                heard = struct.get("heard_id")
                move_idx = int(np.argmax(act)) if max(act) > 0.1 else 0
                move_str = ["HOLD", "LEFT", "RIGHT", "DOWN", "UP"][move_idx]
                print(f"   Heard: {heard} -> Move: {move_str}")
                print(f"   Action: {np.round(act, 2)}")

            warn = struct.get("warning")
            if warn:
                print(f"   Warning: {warn}")

            game_log.append({
                "step": step,
                "agent": aid,
                "role": role,
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
    # run_speaker_listener("deepseek", "sl_demo", api_key="your-key")
    # run_speaker_listener("ollama", "sl_demo", model_name="qwen2.5:7b")
    # run_speaker_listener("transformers", "sl_demo", model_path="Qwen/Qwen2.5-7B-Instruct", device="cuda")

    print("Starting Speaker-Listener Run (Modular)...")
    run_speaker_listener(PROVIDER, "speaker_listener_modular")

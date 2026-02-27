import json
import numpy as np
import imageio
from typing import Dict, Any

from utils_api import get_api_engine, get_unique_filename
from prompt.prompt_for_simple import (
    get_action_and_response_format,
    get_navigation_hints,
    get_physics_rules,
    get_task_and_reward,
)
from obs.parse_simple_obs import parse_simple_obs

try:
    from pettingzoo.mpe import simple_v3
except ImportError:
    raise ImportError("缺少环境库: pip install pettingzoo[mpe]")


class NumpyEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        if isinstance(obj, (np.floating, float)):
            return float(obj)
        if isinstance(obj, (np.integer, int)):
            return int(obj)
        return super().default(obj)


def _format_current_obs(obs_struct: Dict[str, Any]) -> str:
    lines = [
        "OBSERVATION SEMANTICS:",
        "- obs = [vel_x, vel_y, dx, dy] where dx,dy = landmark_pos - your_pos",
        "CURRENT OBS (structured):",
        f"- vel: {obs_struct.get('vel')}",
        f"- landmark_rel: {obs_struct.get('landmark_rel')} [dx, dy, distance]",
    ]
    return "\n".join(lines)


def user_prompt_simple(agent: str, step_idx: int, obs_struct: Dict[str, Any]) -> str:
    parts = [
        f"ENV: MPE_Simple_v3\nAGENT: {agent}\nSTEP: {step_idx}",
        get_task_and_reward(),
        get_physics_rules(),
        get_action_and_response_format(),
        get_navigation_hints(),
        _format_current_obs(obs_struct),
    ]
    return "\n\n".join(parts)


def run_simple_game(provider: str, output_name: str, **kwargs):
    MAX_STEPS = 30
    seed = kwargs.pop('seed', None)
    llm_engine = get_api_engine(provider, **kwargs)

    print("Initializing MPE Simple (Modular)...")
    env = simple_v3.parallel_env(max_cycles=MAX_STEPS, continuous_actions=True, render_mode="rgb_array")
    observations, infos = env.reset(seed=seed) if seed is not None else env.reset()
    frames = []
    game_log = []

    for step in range(MAX_STEPS):
        print(f"\n{'='*20} STEP {step} {'='*20}")
        frame = env.render()
        if frame is not None:
            frames.append(frame)

        actions = {}
        step_buffer = {}

        for agent_id in env.agents:
            if agent_id not in observations:
                continue

            obs_struct = parse_simple_obs(observations[agent_id])
            full_prompt = user_prompt_simple(agent_id, step, obs_struct)
            sys_r = "You are a decision module for a simple single-agent env. Output strict JSON only."

            action_vec, raw_thought = llm_engine.generate_action(sys_r, full_prompt)

            expected_dim = 5
            if action_vec is None:
                action_vec = np.zeros(expected_dim, dtype=np.float32)
            else:
                action_vec = np.array(action_vec, dtype=np.float32)
                if action_vec.size == 0:
                    action_vec = np.zeros(expected_dim, dtype=np.float32)
            if len(action_vec) < expected_dim:
                action_vec = np.concatenate([action_vec, np.zeros(expected_dim - len(action_vec))])
            action_vec = action_vec[:expected_dim]
            action_vec[:expected_dim] = np.clip(action_vec[:expected_dim], 0.0, 1.0)

            actions[agent_id] = action_vec
            step_buffer[agent_id] = {"obs": obs_struct, "action": action_vec, "thought": raw_thought}

            print(f"[{agent_id}] action: {np.round(action_vec, 2)} | thought: {str(raw_thought)[:120]}")

        if not actions:
            break

        observations, rewards, terminations, truncations, infos = env.step(actions)

        print("Rewards:")
        for aid, r in rewards.items():
            print(f"  {aid}: {r:.3f}")
            game_log.append({
                "step": step,
                "agent": aid,
                "obs": step_buffer.get(aid, {}).get("obs"),
                "action": step_buffer.get(aid, {}).get("action"),
                "thought": step_buffer.get(aid, {}).get("thought"),
                "reward": float(r)
            })

        if all(terminations.values()) or all(truncations.values()):
            print("Game over (terminated or truncated).")
            break

    env.close()

    # Add final summary
    total_rewards = {}
    for entry in game_log:
        if "agent" in entry:
            aid = entry["agent"]
            total_rewards[aid] = total_rewards.get(aid, 0.0) + entry.get("reward", 0.0)
    
    mean_reward = sum(total_rewards.values()) / len(total_rewards) if total_rewards else 0.0
    game_log.append({
        "final_summary": True,
        "total_rewards": {k: float(v) for k, v in total_rewards.items()},
        "mean_reward": float(mean_reward)
    })
    print(f"\n📊 FINAL: Total Rewards={total_rewards}, Mean={mean_reward:.3f}")

    if frames:
        vid_name = get_unique_filename(f"{output_name}.mp4")
        imageio.mimsave(vid_name, frames, fps=5, macro_block_size=1)
        print(f"Saved video to {vid_name}")

    if game_log:
        log_name = get_unique_filename(f"{output_name}.json")
        with open(log_name, "w", encoding="utf-8") as f:
            json.dump(game_log, f, indent=2, cls=NumpyEncoder)
        print(f"Saved log to {log_name}")


if __name__ == "__main__":
    # PROVIDER options: 'deepseek', 'qwen', 'gpt', 'gemini', 'transformers', 'ollama', 'vllm'
    PROVIDER = "qwen"
    # run_simple(PROVIDER, "simple_demo", api_key="your-key")
    run_simple_game(PROVIDER, "simple_modular")
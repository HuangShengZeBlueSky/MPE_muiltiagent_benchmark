import os
import json
import math
import numpy as np
from typing import Dict, Any, List
from collections import defaultdict

from utils_api import get_api_engine, get_unique_filename
from prompt.prompt_for_world_comm import (
    get_action_and_response_format,
    get_navigation_hints,
    get_physics_rules,
    get_task_and_reward,
)
from obs.parse_world_comm_obs import parse_world_comm_obs

try:
    from pettingzoo.mpe import simple_world_comm_v3
except ImportError:
    raise ImportError("缺少环境库: pip install pettingzoo[mpe]")


class NumpyEncoder(json.JSONEncoder):
    """JSON encoder for numpy types."""
    def default(self, obj):
        if isinstance(obj, (np.integer, np.floating)):
            return float(obj) if isinstance(obj, np.floating) else int(obj)
        elif isinstance(obj, np.ndarray):
            return obj.tolist()
        elif isinstance(obj, (bool, np.bool_)):
            return bool(obj)
        elif hasattr(obj, 'item'):
            return obj.item()
        return super().default(obj)


def _format_current_obs(obs_struct: Dict[str, Any], agent_name: str) -> str:
    role = obs_struct.get("role", "UNKNOWN")
    lines = [
        "OBSERVATION SEMANTICS:",
        "- obs = [vel(2), position(2), landmarks(10), teammates(6), enemies(4), comm(4)] role-dependent",
        "CURRENT OBS STRUCT:",
        f"- agent_name: {agent_name}",
        f"- role: {role}",
        f"- self.position: {obs_struct.get('self', {}).get('position')}",
        f"- self.velocity: {obs_struct.get('self', {}).get('velocity')}",
    ]
    
    if role == "LEADER":
        lines.extend([
            f"- enemies (prey): {obs_struct.get('enemies')}",
            f"- teammates (hunters): {len(obs_struct.get('teammates', []))} units",
        ])
    elif role == "HUNTER":
        comm = obs_struct.get("communication")
        lines.extend([
            f"- communication.active: {comm.get('active') if comm else False}",
            f"- enemies (prey): {obs_struct.get('enemies')}",
        ])
    else:  # PREY
        lines.extend([
            f"- enemies (threats): {len(obs_struct.get('enemies', []))} hunters",
            f"- teammates (partner): {obs_struct.get('teammates')}",
        ])
    
    return "\n".join(lines)


def user_prompt_world_comm(agent_name: str, step: int, obs_struct: Dict[str, Any]) -> str:
    """Assemble the full prompt for the agent."""
    role = obs_struct.get("role", "UNKNOWN")
    
    # For LEADER, compute prey absolute coordinates for communication
    comm_hint = ""
    if role == "LEADER":
        self_pos = np.array(obs_struct.get("self", {}).get("position", [0.0, 0.0]))
        prey_coords = []
        for enemy in obs_struct.get("enemies", []):
            abs_pos = np.round(self_pos + np.array(enemy.get("rel", [0.0, 0.0])), 3)
            prey_coords.extend(abs_pos.tolist())
        while len(prey_coords) < 4:
            prey_coords.append(0.0)
        
        comm_hint = (
            f"\nCOMMUNICATION PAYLOAD:\n"
            f"Broadcast these prey absolute coordinates in action[5:9]:\n"
            f"- Prey0_X={prey_coords[0]}, Prey0_Y={prey_coords[1]}\n"
            f"- Prey1_X={prey_coords[2]}, Prey1_Y={prey_coords[3]}"
        )
    
    parts = [
        get_task_and_reward(role),
        get_physics_rules(role),
        get_action_and_response_format(role),
        get_navigation_hints(role),
        _format_current_obs(obs_struct, agent_name),
        comm_hint,
    ]
    return "\n\n".join(filter(None, parts))


def run_world_comm(provider: str, output_name: str, **kwargs):
    MAX_STEPS = 50
    seed = kwargs.pop('seed', None)
    llm_engine = get_api_engine(provider, **kwargs)

    print("Initializing World Comm Environment (Modular)...")
    env = simple_world_comm_v3.parallel_env(
        num_good=2, num_adversaries=4, num_obstacles=1, num_food=2, num_forests=2,
        max_cycles=MAX_STEPS, continuous_actions=True, render_mode="rgb_array"
    )

    observations, infos = env.reset(seed=seed) if seed is not None else env.reset()
    frames = []
    total_rewards = defaultdict(float)
    game_log = []

    for step in range(MAX_STEPS):
        print(f"\n{'='*30} STEP {step} {'='*30}")
        frame = env.render()
        if frame is not None:
            frames.append(frame)

        actions = {}
        step_buffer = {}

        for agent_id in env.agents:
            if agent_id not in observations:
                continue

            # Parse observation
            obs_struct = parse_world_comm_obs(observations[agent_id], agent_id)
            role = obs_struct.get("role", "UNKNOWN")

            # Generate prompt and action
            full_prompt = user_prompt_world_comm(agent_id, step, obs_struct)
            sys_r = f"You are a tactical {role} agent. Output strict JSON only."

            action_vec, raw_thought = llm_engine.generate_action(sys_r, full_prompt)

            # Determine expected dimension based on role
            if role == "LEADER":
                expected_dim = 9
            else:
                expected_dim = 5

            # 修复 ValueError，并处理 None/空返回
            if action_vec is None:
                action_vec = np.zeros(expected_dim, dtype=np.float32)
            else:
                action_vec = np.array(action_vec, dtype=np.float32)
                if action_vec.size == 0:
                    action_vec = np.zeros(expected_dim, dtype=np.float32)
            if len(action_vec) < expected_dim:
                action_vec = np.concatenate([action_vec, np.zeros(expected_dim - len(action_vec))])
            action_vec = action_vec[:expected_dim]

            # For movement (indices 0-4), clip to [0, 1]
            if len(action_vec) >= 5:
                action_vec[:5] = np.clip(action_vec[:5], 0.0, 1.0)
            # For communication (indices 5+), allow any float

            actions[agent_id] = action_vec
            step_buffer[agent_id] = {"struct": obs_struct, "action": action_vec, "thought": raw_thought}

            # Print step info
            print(f"\n[{agent_id}] Role: {role}")
            print(f"   Thought: {raw_thought[:100]}")
            print(f"   Action: {np.round(action_vec, 2)}")

        if not actions:
            break

        observations, rewards, terminations, truncations, infos = env.step(actions)

        # Log rewards
        print(f"\n--- Rewards (Step {step}) ---")
        for aid, r in rewards.items():
            total_rewards[aid] += r
            print(f"{aid}: {r:.3f} (total: {total_rewards[aid]:.3f})")

            struct = step_buffer[aid]["struct"]
            act = step_buffer[aid]["action"]

            game_log.append({
                "step": step,
                "agent": aid,
                "role": struct.get("role"),
                "obs": struct,
                "action": act.tolist(),
                "thought": step_buffer[aid]["thought"],
                "reward": float(r),
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
    print(f"\nFINAL REWARDS: {dict(total_rewards)}, MEAN: {mean_reward:.3f}")

    if frames:
        import imageio
        vid_name = get_unique_filename(output_name + ".mp4")
        imageio.mimsave(vid_name, frames, fps=1, macro_block_size=1)
        print(f"Saved video to {vid_name}")

    final_log = get_unique_filename(output_name + ".json")
    with open(final_log, "w", encoding="utf-8") as f:
        json.dump(game_log, f, indent=4, cls=NumpyEncoder)
    print(f"Saved detailed logs to {final_log}")


if __name__ == "__main__":
    # Unified model interface examples:
    # PROVIDER options: 'deepseek', 'qwen', 'gpt', 'gemini', 'transformers', 'ollama', 'vllm'
    PROVIDER = "qwen"

    # Example overrides:
    # run_world_comm("deepseek", "world_comm_demo", api_key="your-key")
    # run_world_comm("ollama", "world_comm_demo", model_name="qwen2.5:7b")
    # run_world_comm("transformers", "world_comm_demo", model_path="Qwen/Qwen2.5-7B-Instruct", device="cuda")

    print("Starting World Comm Run (Modular)...")
    run_world_comm(PROVIDER, "world_comm_modular")

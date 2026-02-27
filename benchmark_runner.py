"""
Unified benchmark runner for all 9 MPE games.
Features:
- Runs any supported game for N episodes with adjustable parameters.
- Each episode saves video (*.mp4) and JSON log (per-step: obs, action, thought, reward).
- Computes per-episode total/mean rewards and aggregates mean/std across episodes.
"""

import json
import math
import sys
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional

# Load environment variables from .env file
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

# Ensure project root on sys.path
ROOT = Path(__file__).resolve().parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

# Import game runners
from spread_API import run_spread_game
from adv_API import run_adversary_game
from tag_API import run_tag_game
from push import run_push_game
from crypto import run_crypto_game
from reference import run_reference_game
from speaker_listener import run_speaker_listener
from world_comm import run_world_comm
from simple import run_simple_game

# Map environment name to its runner callable and a default step cap for display/logging only
GAME_RUNNERS: Dict[str, Callable[..., None]] = {
    "spread": run_spread_game,
    "adversary": run_adversary_game,
    "tag": run_tag_game,
    "push": run_push_game,
    "crypto": run_crypto_game,
    "reference": run_reference_game,
    "speaker_listener": run_speaker_listener,
    "world_comm": run_world_comm,
    "simple": run_simple_game,
}


def _ensure_dir(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)


def _find_latest_with_prefix(prefix: Path, suffix: str) -> Optional[Path]:
    """Find the latest file matching prefix*{suffix}."""
    candidates = sorted(prefix.parent.glob(prefix.name + "*" + suffix), key=lambda p: p.stat().st_mtime)
    return candidates[-1] if candidates else None


def _parse_episode_log(log_path: Path) -> Dict[str, Any]:
    with log_path.open("r", encoding="utf-8") as f:
        data = json.load(f)

    # Strategy: Prioritize final_summary (most accurate for multi-role scenarios)
    final_summary = None
    steps: List[Dict[str, Any]] = []
    
    # First pass: find final_summary and collect step entries
    for entry in data:
        if entry.get("final_summary"):
            final_summary = entry
            continue
        
        step = entry.get("step")
        if step is not None:
            steps.append(entry)
    
    # ✅ Primary: Use final_summary if available (accurate for role-based aggregation)
    if final_summary:
        return {
            "log_path": str(log_path),
            "total_rewards": final_summary.get("total_rewards", {}),
            "mean_reward": float(final_summary.get("mean_reward", 0.0)),
            "steps": len(steps),
        }
    
    # ✅ Fallback: Accumulate per-agent rewards (for backwards compatibility)
    rewards_per_agent: Dict[str, float] = {}
    for entry in steps:
        aid = entry.get("agent")
        r = float(entry.get("reward", 0.0))
        rewards_per_agent[aid] = rewards_per_agent.get(aid, 0.0) + r

    agent_rewards = list(rewards_per_agent.values())
    mean_reward = sum(agent_rewards) / len(agent_rewards) if agent_rewards else 0.0
    
    return {
        "log_path": str(log_path),
        "total_rewards": rewards_per_agent,
        "mean_reward": mean_reward,
        "steps": len(steps),
    }


def run_single_episode(env_name: str, provider: str, episode_idx: int, output_dir: Path, seed: Optional[int] = None, **game_kwargs) -> Dict[str, Any]:
    if env_name not in GAME_RUNNERS:
        raise ValueError(f"Unsupported env_name: {env_name}")

    runner = GAME_RUNNERS[env_name]
    episode_dir = output_dir / env_name
    _ensure_dir(episode_dir)

    # Pre-compute a unique base name to avoid get_unique_filename adding suffix
    base_name = episode_dir / f"{env_name}_ep{episode_idx}"
    
    # If seed not provided, use episode_idx (1-20)
    if seed is None:
        seed = episode_idx

    # Invoke game runner; runners save mp4/json using the provided base name
    if env_name == "spread":
        runner(provider, output_file=str(base_name) + ".mp4", seed=seed, **game_kwargs)
    elif env_name == "adversary":
        runner(provider, str(base_name), seed=seed, **game_kwargs)
    elif env_name == "tag":
        runner(provider, str(base_name), seed=seed, **game_kwargs)
    elif env_name == "push":
        runner(provider, str(base_name), seed=seed, **game_kwargs)
    elif env_name == "crypto":
        runner(provider, str(base_name), seed=seed, **game_kwargs)
    elif env_name == "reference":
        runner(provider, str(base_name), seed=seed, **game_kwargs)
    elif env_name == "speaker_listener":
        runner(provider, str(base_name), seed=seed, **game_kwargs)
    elif env_name == "world_comm":
        runner(provider, str(base_name), seed=seed, **game_kwargs)
    elif env_name == "simple":
        runner(provider, str(base_name), seed=seed, **game_kwargs)

    # Locate produced files
    log_path = _find_latest_with_prefix(base_name, ".json")
    video_path = _find_latest_with_prefix(base_name, ".mp4")

    episode_stats = {
        "episode": episode_idx,
        "env": env_name,
        "log": str(log_path) if log_path else None,
        "video": str(video_path) if video_path else None,
        "mean_reward": None,
        "total_rewards": {},
    }

    if log_path and log_path.exists():
        parsed = _parse_episode_log(log_path)
        episode_stats.update({
            "mean_reward": parsed["mean_reward"],
            "total_rewards": parsed["total_rewards"],
            "steps": parsed["steps"],
        })

    return episode_stats


def run_benchmark(
    env_name: str,
    provider: str,
    episodes: int = 3,
    output_dir: str = "results/benchmarks",
    seed_start: int = 1,
    **game_kwargs,
) -> Dict[str, Any]:
    """
    Run N episodes for a given environment and provider.
    Each episode uses a different seed for reproducibility.
    
    Args:
        env_name: Name of the environment (one of GAME_RUNNERS keys)
        provider: LLM provider ('qwen', 'deepseek', 'ollama', etc.)
        episodes: Number of episodes to run
        output_dir: Directory to save results
        seed_start: Starting seed value (default 1). Seeds used: seed_start, seed_start+1, ..., seed_start+episodes-1
        **game_kwargs: Additional arguments to pass to game runners
    
    Returns:
        Benchmark results with mean/std of rewards across episodes
    """
    out_dir = Path(output_dir)
    _ensure_dir(out_dir)

    all_episode_stats: List[Dict[str, Any]] = []
    episode_means: List[float] = []

    for ep in range(1, episodes + 1):
        seed = seed_start + ep - 1
        print(f"\n[Benchmark] {env_name} | Episode {ep}/{episodes} | Seed {seed}")
        stats = run_single_episode(env_name, provider, ep, out_dir, seed=seed, **game_kwargs)
        all_episode_stats.append(stats)
        if stats.get("mean_reward") is not None:
            episode_means.append(stats["mean_reward"])

    mean_reward = sum(episode_means) / len(episode_means) if episode_means else 0.0
    variance = (
        sum((x - mean_reward) ** 2 for x in episode_means) / len(episode_means)
        if episode_means else 0.0
    )
    std_reward = math.sqrt(variance)

    return {
        "env": env_name,
        "provider": provider,
        "episodes": episodes,
        "mean_reward": mean_reward,
        "std_reward": std_reward,
        "episode_stats": all_episode_stats,
    }


if __name__ == "__main__":
    # ========== 使用示例 ==========
    
    # 示例 1: 单个游戏，1个episode，快速测试
    # result = run_benchmark(env_name="simple", provider="qwen", episodes=1)
    
    # 示例 2: 10个episode的 Adversary 环境测试
    # 会生成：results/benchmarks/adversary/adversary_ep{1-10}.{mp4,json}
    # 最后计算平均奖励和方差统计
#     result = run_benchmark(
#     env_name="adversary",
#     provider="qwen",
#     episodes=10,
#     output_dir="results/benchmarks",
# )
    
    # 遍历所有9个环境
    environments = ["spread", "adversary", "tag", "push", "crypto", "reference", "speaker_listener", "world_comm", "simple"]
    for env_name in environments:
        result = run_benchmark(
            env_name=env_name,
            provider="zaiwen",
            episodes=5,
            output_dir="results/benchmarks",
        )
    
    # 示例 3: 自定义参数（如本地模型）
    # result = run_benchmark(
    #     env_name="tag",
    #     provider="ollama",
    #     episodes=5,
    #     output_dir="results/benchmarks",
    #     model_name="qwen2.5:7b",
    # )
    
    # 示例 4: 使用Transformers本地模型
    # result = run_benchmark(
    #     env_name="spread",
    #     provider="transformers",
    #     episodes=3,
    #     output_dir="results/benchmarks",
    #     model_path="Qwen/Qwen2.5-7B-Instruct",
    #     device="cuda",
    # )
    
    print("\n" + "="*60)
    print("📊 BENCHMARK SUMMARY")
    print("="*60)
    print(f"Environment: {result['env']}")
    print(f"Provider: {result['provider']}")
    print(f"Episodes: {result['episodes']}")
    print(f"Mean Reward (across episodes): {result['mean_reward']:.4f}")
    print(f"Std Dev: {result['std_reward']:.4f}")
    print("="*60)

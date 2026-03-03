import json
import math
import re
from collections import defaultdict
from pathlib import Path

import matplotlib.pyplot as plt

BASE_DIR = Path("results/batch_benchmarks")
TARGET_MODELS = ["Gemini-3.0-Flash", "kimi-k2.5", "Qwen-3-Max"]
TARGET_GAMES = ["spread", "adversary", "tag"]
REPORT_PATH = BASE_DIR / "batch_benchmark_report.md"
PLOTS_DIR = BASE_DIR / "plots"
TREND_PLOT_PATH = PLOTS_DIR / "reward_trend_by_game.png"
SUMMARY_PLOT_PATH = PLOTS_DIR / "reward_mean_std.png"


def _episode_sort_key(file_path: Path):
    match = re.search(r"_ep(\d+)(?:_(\d+))?\.json$", file_path.name)
    if not match:
        return (10**9, 0)
    ep = int(match.group(1))
    rerun = int(match.group(2) or 0)
    return (ep, rerun)


def _group_latest_episode_files(files):
    grouped = defaultdict(list)
    for file_path in files:
        match = re.search(r"_ep(\d+)(?:_\d+)?\.json$", file_path.name)
        if not match:
            continue
        ep = int(match.group(1))
        grouped[ep].append(file_path)

    latest = []
    for ep in sorted(grouped.keys()):
        candidates = grouped[ep]
        chosen = sorted(candidates, key=lambda p: (p.stat().st_mtime, _episode_sort_key(p)))[-1]
        latest.append(chosen)
    return latest


def _safe_mean(values):
    return sum(values) / len(values) if values else 0.0


def _safe_var(values):
    if not values:
        return 0.0
    mean_val = _safe_mean(values)
    return sum((x - mean_val) ** 2 for x in values) / len(values)


def parse_episode_json(file_path: Path):
    with file_path.open("r", encoding="utf-8") as file:
        data = json.load(file)

    final_summary = None
    step_rows = []
    for item in data:
        if item.get("final_summary"):
            final_summary = item
        elif "step" in item:
            step_rows.append(item)

    rewards = [float(item.get("reward", 0.0)) for item in step_rows]
    actions = [item.get("action") for item in step_rows if isinstance(item.get("action"), list)]
    action_dims = [len(action) for action in actions]

    max_step = max((int(item.get("step", 0)) for item in step_rows), default=-1)
    step_count = max_step + 1 if max_step >= 0 else 0

    per_agent_reward = defaultdict(float)
    for item in step_rows:
        agent = item.get("agent", "unknown")
        per_agent_reward[agent] += float(item.get("reward", 0.0))

    episode_mean_reward = None
    total_rewards = {}
    if final_summary:
        episode_mean_reward = float(final_summary.get("mean_reward", 0.0))
        total_rewards = final_summary.get("total_rewards", {}) or {}
    else:
        if per_agent_reward:
            episode_mean_reward = _safe_mean(list(per_agent_reward.values()))
            total_rewards = dict(per_agent_reward)
        else:
            episode_mean_reward = 0.0

    return {
        "file": str(file_path),
        "step_rows": len(step_rows),
        "step_count": step_count,
        "episode_mean_reward": episode_mean_reward,
        "reward_mean_per_row": _safe_mean(rewards),
        "reward_var_per_row": _safe_var(rewards),
        "reward_min_per_row": min(rewards) if rewards else 0.0,
        "reward_max_per_row": max(rewards) if rewards else 0.0,
        "action_dim_modes": sorted(set(action_dims)),
        "total_rewards": total_rewards,
        "agent_count": len(set(item.get("agent", "unknown") for item in step_rows)),
    }


def analyze_all():
    all_results = {}
    model_game_stats = {}

    for model in TARGET_MODELS:
        all_results[model] = {}
        model_dir = BASE_DIR / model
        for game in TARGET_GAMES:
            game_dir = model_dir / game
            if not game_dir.exists():
                all_results[model][game] = {"error": f"missing directory: {game_dir}"}
                continue

            files = sorted(game_dir.glob("*.json"), key=_episode_sort_key)
            files = _group_latest_episode_files(files)
            if not files:
                all_results[model][game] = {"error": "no json logs found"}
                continue

            episodes = [parse_episode_json(file_path) for file_path in files]

            ep_means = [ep["episode_mean_reward"] for ep in episodes]
            step_counts = [ep["step_count"] for ep in episodes]
            row_reward_means = [ep["reward_mean_per_row"] for ep in episodes]
            row_reward_vars = [ep["reward_var_per_row"] for ep in episodes]
            role_reward_buckets = defaultdict(list)

            action_dims = set()
            for ep in episodes:
                action_dims.update(ep["action_dim_modes"])
                for role_key, role_reward in ep["total_rewards"].items():
                    role_reward_buckets[role_key].append(float(role_reward))

            role_reward_summary = {
                role: {
                    "mean_total_reward": _safe_mean(vals),
                    "var_total_reward": _safe_var(vals),
                    "min_total_reward": min(vals),
                    "max_total_reward": max(vals),
                }
                for role, vals in sorted(role_reward_buckets.items())
            }

            game_stats = {
                "episodes": len(episodes),
                "episode_mean_reward_avg": _safe_mean(ep_means),
                "episode_mean_reward_var": _safe_var(ep_means),
                "episode_mean_reward_std": math.sqrt(_safe_var(ep_means)),
                "episode_mean_reward_min": min(ep_means),
                "episode_mean_reward_max": max(ep_means),
                "avg_step_count": _safe_mean(step_counts),
                "avg_reward_mean_per_row": _safe_mean(row_reward_means),
                "avg_reward_var_per_row": _safe_mean(row_reward_vars),
                "action_dims_seen": sorted(action_dims),
                "role_reward_summary": role_reward_summary,
                "episode_files": [ep["file"] for ep in episodes],
                "episode_mean_series": ep_means,
            }

            all_results[model][game] = game_stats
            model_game_stats[(model, game)] = game_stats

    return all_results, model_game_stats


def build_plots(model_game_stats):
    PLOTS_DIR.mkdir(parents=True, exist_ok=True)

    fig, axes = plt.subplots(1, len(TARGET_GAMES), figsize=(18, 5), sharey=False)
    if len(TARGET_GAMES) == 1:
        axes = [axes]

    for idx, game in enumerate(TARGET_GAMES):
        ax = axes[idx]
        for model in TARGET_MODELS:
            stats = model_game_stats.get((model, game))
            if not stats or "episode_mean_series" not in stats:
                continue
            series = stats["episode_mean_series"]
            x = list(range(1, len(series) + 1))
            ax.plot(x, series, marker="o", linewidth=1.5, label=model)

        ax.set_title(f"{game} episode mean reward")
        ax.set_xlabel("Episode")
        ax.set_ylabel("Mean reward")
        ax.grid(True, alpha=0.25)

    handles, labels = axes[0].get_legend_handles_labels()
    if handles:
        fig.legend(handles, labels, loc="upper center", ncol=3, bbox_to_anchor=(0.5, 1.08))
    fig.tight_layout()
    fig.savefig(TREND_PLOT_PATH, dpi=180, bbox_inches="tight")
    plt.close(fig)

    fig, axes = plt.subplots(1, len(TARGET_GAMES), figsize=(18, 5), sharey=False)
    if len(TARGET_GAMES) == 1:
        axes = [axes]

    for idx, game in enumerate(TARGET_GAMES):
        ax = axes[idx]
        means = []
        stds = []
        labels = []
        for model in TARGET_MODELS:
            stats = model_game_stats.get((model, game))
            if not stats:
                continue
            means.append(stats["episode_mean_reward_avg"])
            stds.append(stats["episode_mean_reward_std"])
            labels.append(model)

        x = list(range(len(labels)))
        if labels:
            ax.bar(x, means, yerr=stds, capsize=4)
            ax.set_xticks(x)
            ax.set_xticklabels(labels, rotation=20, ha="right")

        ax.set_title(f"{game} mean ± std")
        ax.set_ylabel("Mean reward")
        ax.grid(True, axis="y", alpha=0.25)

    fig.tight_layout()
    fig.savefig(SUMMARY_PLOT_PATH, dpi=180, bbox_inches="tight")
    plt.close(fig)


def build_report(all_results):
    lines = []
    lines.append("# Batch Benchmarks 日志分析报告")
    lines.append("")
    lines.append(f"分析目录: `{BASE_DIR}`")
    lines.append("")
    lines.append("## 1) 按游戏区分的 JSON 日志读取路径")
    lines.append("")

    for game in TARGET_GAMES:
        lines.append(f"### {game}")
        lines.append("")
        lines.append("| 模型 | 日志数量 | 示例日志路径 |")
        lines.append("|---|---:|---|")
        for model in TARGET_MODELS:
            stats = all_results.get(model, {}).get(game, {})
            if "error" in stats:
                lines.append(f"| {model} | 0 | {stats['error']} |")
                continue
            files = stats.get("episode_files", [])
            example = files[0] if files else "-"
            lines.append(f"| {model} | {len(files)} | `{example}` |")
        lines.append("")

    lines.append("## 2) JSON 日志可记录指标")
    lines.append("")
    lines.append("日志中可直接读取的核心字段：")
    lines.append("")
    lines.append("- 步级字段：`step`, `agent`, `role`, `obs`, `action`, `thought`, `reward`")
    lines.append("- 局级字段（结尾）：`final_summary`, `total_rewards`, `mean_reward`")
    lines.append("- 可衍生统计：每局步数、每步奖励均值/方差、动作维度一致性、各角色总回报统计")
    lines.append("")

    lines.append("## 3) 指标汇总（均值/方差/标准差等）")
    lines.append("")
    lines.append("| 模型 | 游戏 | 局数 | 局均值reward均值 | 局均值reward方差 | 局均值reward标准差 | min | max | 平均步数 | 动作维度 |")
    lines.append("|---|---|---:|---:|---:|---:|---:|---:|---:|---|")

    for model in TARGET_MODELS:
        for game in TARGET_GAMES:
            stats = all_results.get(model, {}).get(game, {})
            if "error" in stats:
                lines.append(f"| {model} | {game} | 0 | - | - | - | - | - | - | {stats['error']} |")
                continue
            lines.append(
                "| {model} | {game} | {episodes} | {avg:.4f} | {var:.4f} | {std:.4f} | {minv:.4f} | {maxv:.4f} | {steps:.2f} | {dims} |".format(
                    model=model,
                    game=game,
                    episodes=stats["episodes"],
                    avg=stats["episode_mean_reward_avg"],
                    var=stats["episode_mean_reward_var"],
                    std=stats["episode_mean_reward_std"],
                    minv=stats["episode_mean_reward_min"],
                    maxv=stats["episode_mean_reward_max"],
                    steps=stats["avg_step_count"],
                    dims=stats["action_dims_seen"],
                )
            )

    lines.append("")
    lines.append("## 4) 各游戏-各模型角色总回报统计")
    lines.append("")

    for game in TARGET_GAMES:
        lines.append(f"### {game}")
        lines.append("")
        lines.append("| 模型 | 角色 | 平均总回报 | 方差 | 最小值 | 最大值 |")
        lines.append("|---|---|---:|---:|---:|---:|")
        for model in TARGET_MODELS:
            stats = all_results.get(model, {}).get(game, {})
            if "error" in stats:
                lines.append(f"| {model} | - | - | - | - | - |")
                continue
            role_stats = stats.get("role_reward_summary", {})
            if not role_stats:
                lines.append(f"| {model} | - | - | - | - | - |")
                continue
            for role, role_values in role_stats.items():
                lines.append(
                    f"| {model} | {role} | {role_values['mean_total_reward']:.4f} | {role_values['var_total_reward']:.4f} | {role_values['min_total_reward']:.4f} | {role_values['max_total_reward']:.4f} |"
                )
        lines.append("")

    lines.append("## 5) 折线图与可视化")
    lines.append("")
    lines.append("- 局均值 reward 折线图（按游戏分面）: ![trend](plots/reward_trend_by_game.png)")
    lines.append("- 均值±标准差柱状图: ![summary](plots/reward_mean_std.png)")
    lines.append("")

    REPORT_PATH.write_text("\n".join(lines), encoding="utf-8")


def main():
    all_results, model_game_stats = analyze_all()
    build_plots(model_game_stats)
    build_report(all_results)
    print(f"Report generated: {REPORT_PATH}")
    print(f"Trend plot: {TREND_PLOT_PATH}")
    print(f"Summary plot: {SUMMARY_PLOT_PATH}")


if __name__ == "__main__":
    main()

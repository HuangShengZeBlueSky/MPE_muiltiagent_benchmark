import json
import re
from collections import defaultdict
from pathlib import Path

import matplotlib.pyplot as plt

BASE_DIR = Path("results/batch_benchmarks")
MODELS = ["Gemini-3.0-Flash", "kimi-k2.5", "Qwen-3-Max"]
GAMES = ["spread", "adversary", "tag"]
OUT_DIR = BASE_DIR / "plots"
REPORT_PATH = BASE_DIR / "batch_benchmark_detailed_report.md"


def _episode_key(path: Path):
    match = re.search(r"_ep(\d+)(?:_(\d+))?\.json$", path.name)
    if not match:
        return (10**9, 0)
    ep = int(match.group(1))
    rerun = int(match.group(2) or 0)
    return (ep, rerun)


def _latest_per_episode(paths):
    grouped = defaultdict(list)
    for path in paths:
        match = re.search(r"_ep(\d+)(?:_(\d+))?\.json$", path.name)
        if not match:
            continue
        ep = int(match.group(1))
        rerun = int(match.group(2) or 0)
        grouped[ep].append((rerun, path.stat().st_mtime, path))

    selected = []
    for ep in sorted(grouped):
        selected.append(sorted(grouped[ep], key=lambda x: (x[0], x[1]))[-1][2])
    return selected


def _load_episode(path: Path):
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def _step_role_rewards(entries, game):
    by_step = defaultdict(lambda: defaultdict(list))
    for row in entries:
        if not isinstance(row, dict) or "step" not in row:
            continue
        step = int(row.get("step", 0))
        reward = float(row.get("reward", 0.0))
        role = str(row.get("role", "unknown"))
        agent = str(row.get("agent", "unknown"))

        role_l = role.lower()
        agent_l = agent.lower()

        if game == "adversary":
            if "adversary" in role_l or "bad" in role_l or "adversary" in agent_l:
                camp = "adversary"
            elif "good" in role_l or (agent_l.startswith("agent_") and "adversary" not in agent_l):
                camp = "good"
            else:
                camp = "other"
        elif game == "tag":
            if "predator" in role_l or agent_l.startswith("adversary_"):
                camp = "predators"
            elif "prey" in role_l or agent_l.startswith("agent_"):
                camp = "prey"
            else:
                camp = "other"
        elif game == "spread":
            camp = "good"
        else:
            camp = "other"

        by_step[step][camp].append(reward)
        by_step[step]["team"].append(reward)

    result = {}
    for step, camp_map in by_step.items():
        result[step] = {camp: sum(vals) / len(vals) for camp, vals in camp_map.items() if vals}
    return result


def _final_summary(entries):
    finals = [r for r in entries if isinstance(r, dict) and r.get("final_summary")]
    return finals[-1] if finals else None


def analyze():
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    camp_summary = defaultdict(lambda: defaultdict(dict))
    step_curves = defaultdict(lambda: defaultdict(dict))
    gemini_tag_zero_episodes = []

    for model in MODELS:
        for game in GAMES:
            game_dir = BASE_DIR / model / game
            paths = _latest_per_episode(sorted(game_dir.glob("*.json"), key=_episode_key))
            if not paths:
                continue

            episode_step_maps = []
            camp_totals = defaultdict(list)

            for path in paths:
                entries = _load_episode(path)
                step_map = _step_role_rewards(entries, game)
                episode_step_maps.append(step_map)

                fin = _final_summary(entries)
                if fin:
                    for k, v in (fin.get("total_rewards") or {}).items():
                        camp_totals[str(k)].append(float(v))

                    if model == "Gemini-3.0-Flash" and game == "tag":
                        tr = fin.get("total_rewards") or {}
                        if float(tr.get("predators", 0.0)) == 0.0 and float(tr.get("prey", 0.0)) == 0.0:
                            gemini_tag_zero_episodes.append(path.name)

            max_step = max((max(m.keys()) if m else 0 for m in episode_step_maps), default=0)
            curve = {}
            for step in range(max_step + 1):
                buckets = defaultdict(list)
                for ep_map in episode_step_maps:
                    if step not in ep_map:
                        continue
                    for camp, val in ep_map[step].items():
                        buckets[camp].append(val)
                curve[step] = {camp: (sum(vals) / len(vals)) for camp, vals in buckets.items() if vals}

            step_curves[model][game] = curve

            for camp_name, vals in camp_totals.items():
                if vals:
                    mean_val = sum(vals) / len(vals)
                    var_val = sum((x - mean_val) ** 2 for x in vals) / len(vals)
                    camp_summary[model][game][camp_name] = {
                        "mean": mean_val,
                        "var": var_val,
                        "min": min(vals),
                        "max": max(vals),
                        "episodes": len(vals),
                    }

    return camp_summary, step_curves, gemini_tag_zero_episodes


def save_camp_tables_and_plot(camp_summary):
    camp_md_path = OUT_DIR / "camp_breakdown.md"
    plot_path = OUT_DIR / "camp_breakdown_adv_tag.png"

    lines = ["# ADV/TAG 双阵营统计", ""]
    lines.append("## adversary")
    lines.append("")
    lines.append("| 模型 | 阵营 | 均值 | 方差 | 最小 | 最大 | 局数 |")
    lines.append("|---|---|---:|---:|---:|---:|---:|")
    for model in MODELS:
        for camp in ["adversary", "good"]:
            stats = camp_summary.get(model, {}).get("adversary", {}).get(camp)
            if not stats:
                lines.append(f"| {model} | {camp} | - | - | - | - | - |")
            else:
                lines.append(
                    f"| {model} | {camp} | {stats['mean']:.4f} | {stats['var']:.4f} | {stats['min']:.4f} | {stats['max']:.4f} | {stats['episodes']} |"
                )

    lines.append("")
    lines.append("## tag")
    lines.append("")
    lines.append("| 模型 | 阵营 | 均值 | 方差 | 最小 | 最大 | 局数 |")
    lines.append("|---|---|---:|---:|---:|---:|---:|")
    for model in MODELS:
        for camp in ["predators", "prey"]:
            stats = camp_summary.get(model, {}).get("tag", {}).get(camp)
            if not stats:
                lines.append(f"| {model} | {camp} | - | - | - | - | - |")
            else:
                lines.append(
                    f"| {model} | {camp} | {stats['mean']:.4f} | {stats['var']:.4f} | {stats['min']:.4f} | {stats['max']:.4f} | {stats['episodes']} |"
                )

    camp_md_path.write_text("\n".join(lines), encoding="utf-8")

    fig, axes = plt.subplots(1, 2, figsize=(14, 5))

    x = list(range(len(MODELS)))
    width = 0.35

    adv_a = [camp_summary.get(m, {}).get("adversary", {}).get("adversary", {}).get("mean", 0.0) for m in MODELS]
    adv_g = [camp_summary.get(m, {}).get("adversary", {}).get("good", {}).get("mean", 0.0) for m in MODELS]
    axes[0].bar([i - width / 2 for i in x], adv_a, width=width, label="adversary")
    axes[0].bar([i + width / 2 for i in x], adv_g, width=width, label="good")
    axes[0].set_xticks(x)
    axes[0].set_xticklabels(MODELS, rotation=15, ha="right")
    axes[0].set_title("Adversary game camp mean total reward")
    axes[0].grid(True, axis="y", alpha=0.25)
    axes[0].legend()

    tag_p = [camp_summary.get(m, {}).get("tag", {}).get("predators", {}).get("mean", 0.0) for m in MODELS]
    tag_y = [camp_summary.get(m, {}).get("tag", {}).get("prey", {}).get("mean", 0.0) for m in MODELS]
    axes[1].bar([i - width / 2 for i in x], tag_p, width=width, label="predators")
    axes[1].bar([i + width / 2 for i in x], tag_y, width=width, label="prey")
    axes[1].set_xticks(x)
    axes[1].set_xticklabels(MODELS, rotation=15, ha="right")
    axes[1].set_title("Tag game camp mean total reward")
    axes[1].grid(True, axis="y", alpha=0.25)
    axes[1].legend()

    fig.tight_layout()
    fig.savefig(plot_path, dpi=180, bbox_inches="tight")
    plt.close(fig)

    return camp_md_path, plot_path


def save_step_tables_and_plots(step_curves):
    out_files = []
    for model in MODELS:
        model_md = OUT_DIR / f"step_curve_{model}.md"
        fig, axes = plt.subplots(1, 3, figsize=(18, 5), sharex=True)

        md_lines = [f"# {model} 每步长奖励变化（10局平均）", ""]

        for idx, game in enumerate(GAMES):
            curve = step_curves.get(model, {}).get(game, {})
            steps = sorted(curve.keys())
            if not steps:
                continue

            team_vals = [curve[s].get("team", 0.0) for s in steps]
            axes[idx].plot(steps, team_vals, label="team", linewidth=2)

            extra_keys = [k for k in curve[steps[0]].keys() if k != "team"]
            for k in extra_keys:
                vals = [curve[s].get(k, 0.0) for s in steps]
                axes[idx].plot(steps, vals, label=k, linestyle="--")

            axes[idx].set_title(f"{game} step-reward curve")
            axes[idx].set_xlabel("step")
            axes[idx].set_ylabel("avg reward")
            axes[idx].grid(True, alpha=0.25)
            axes[idx].legend(fontsize=8)

            md_lines.append(f"## {game}")
            md_lines.append("")
            md_lines.append("| step | team | adversary | good | predators | prey | other |")
            md_lines.append("|---:|---:|---:|---:|---:|---:|---:|")
            for s in steps:
                row = curve[s]
                md_lines.append(
                    "| {s} | {team:.6f} | {adv:.6f} | {good:.6f} | {pred:.6f} | {prey:.6f} | {other:.6f} |".format(
                        s=s,
                        team=row.get("team", 0.0),
                        adv=row.get("adversary", 0.0),
                        good=row.get("good", 0.0),
                        pred=row.get("predators", 0.0),
                        prey=row.get("prey", 0.0),
                        other=row.get("other", 0.0),
                    )
                )
            md_lines.append("")

        fig.tight_layout()
        fig_path = OUT_DIR / f"step_curve_{model}.png"
        fig.savefig(fig_path, dpi=180, bbox_inches="tight")
        plt.close(fig)

        md_lines.append(f"![{model} step curve]({fig_path.name})")
        model_md.write_text("\n".join(md_lines), encoding="utf-8")
        out_files.extend([model_md, fig_path])

    return out_files


def save_main_report(camp_md_path, camp_plot_path, step_outputs, zero_eps):
    lines = ["# Batch Benchmark 详细分析（清晰版）", ""]
    lines.append("## 1) ADV/TAG 双阵营分别是多少")
    lines.append("")
    lines.append(f"- 统计表: [{camp_md_path.name}](plots/{camp_md_path.name})")
    lines.append(f"- 对比图: ![camp](plots/{camp_plot_path.name})")
    lines.append("")

    lines.append("## 2) 同一游戏按步长的奖励变化（10局平均）")
    lines.append("")
    for p in step_outputs:
        if p.suffix == ".md":
            lines.append(f"- 表格: [{p.name}](plots/{p.name})")
        if p.suffix == ".png":
            lines.append(f"- 图: ![{p.name}](plots/{p.name})")
    lines.append("")

    lines.append("## 3) Gemini-3.0-Flash 的 tag 为何会出现 0")
    lines.append("")
    if zero_eps:
        lines.append("检测到以下局 `predators=0` 且 `prey=0`（该局无有效追逐回报，导致均值接近0）：")
        for ep in zero_eps:
            lines.append(f"- {ep}")
    else:
        lines.append("未检测到双边同时为 0 的局。")
    lines.append("")
    lines.append("说明：tag 的 `mean_reward` 是两边平均，很多局出现 `predators=+X` 与 `prey=-X`，两者相加后接近 0，因此看到总均值接近 0 是正常现象。")

    REPORT_PATH.write_text("\n".join(lines), encoding="utf-8")


def main():
    camp_summary, step_curves, zero_eps = analyze()
    camp_md, camp_plot = save_camp_tables_and_plot(camp_summary)
    step_outputs = save_step_tables_and_plots(step_curves)
    save_main_report(camp_md, camp_plot, step_outputs, zero_eps)

    print(f"Detailed report: {REPORT_PATH}")
    print(f"Camp table: {camp_md}")
    print(f"Camp plot: {camp_plot}")
    for path in step_outputs:
        print(path)


if __name__ == "__main__":
    main()

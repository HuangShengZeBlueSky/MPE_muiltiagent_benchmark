# Benchmark 批量评测

## 概述

`benchmark_runner.py` 提供了标准化的批量评测系统，支持：

- 多轮次运行 (N episodes)，每轮使用不同随机种子
- 自动计算均值和标准差
- 跨环境汇总统计
- 结构化的评测报告输出

## 核心 API

### `run_benchmark()` 函数

```python
from benchmark_runner import run_benchmark

result = run_benchmark(
    env_name="spread",           # 环境名 (9选1)
    provider="qwen",             # LLM 提供商
    episodes=5,                  # 运行轮数
    output_dir="results/benchmarks",  # 输出目录
    seed_start=1,                # 起始种子
    **game_kwargs                # 额外参数
)
```

**参数说明**:

| 参数 | 类型 | 默认值 | 说明 |
|:-----|:----:|:------:|:-----|
| `env_name` | str | 必填 | 环境名称 |
| `provider` | str | 必填 | LLM 提供商 |
| `episodes` | int | 3 | 运行轮数 |
| `output_dir` | str | `"results/benchmarks"` | 输出目录 |
| `seed_start` | int | 1 | 起始种子 (seed_start, seed_start+1, ...) |

**支持的环境名称**:

```python
GAME_RUNNERS = {
    "simple", "spread", "adversary", "push", "tag",
    "crypto", "reference", "speaker_listener", "world_comm"
}
```

### `run_single_episode()` 函数

运行单个 episode：

```python
from benchmark_runner import run_single_episode
from pathlib import Path

stats = run_single_episode(
    env_name="spread",
    provider="qwen",
    episode_idx=1,
    output_dir=Path("results/benchmarks"),
    seed=42
)
```

## 输出结构

### 文件输出

```
results/benchmarks/
├── spread/
│   ├── spread_ep1.mp4          # Episode 1 游戏录像
│   ├── spread_ep1.json         # Episode 1 详细日志
│   ├── spread_ep2.mp4
│   ├── spread_ep2.json
│   └── ...
├── tag/
│   ├── tag_ep1.mp4
│   ├── tag_ep1.json
│   └── ...
└── ...
```

### 返回值结构

```python
result = {
    "env": "spread",
    "provider": "qwen",
    "episodes": 5,
    "mean_reward": -12.345,    # 跨 episode 平均奖励
    "std_reward": 2.456,       # 跨 episode 奖励标准差
    "episode_stats": [
        {
            "episode": 1,
            "env": "spread",
            "log": "results/benchmarks/spread/spread_ep1.json",
            "video": "results/benchmarks/spread/spread_ep1.mp4",
            "mean_reward": -11.2,
            "total_rewards": {
                "agent_0": -10.5,
                "agent_1": -12.1,
                "agent_2": -11.0
            },
            "steps": 25
        },
        // ...
    ]
}
```

## 使用示例

### 单个环境快速测试

```python
result = run_benchmark(
    env_name="simple",
    provider="qwen",
    episodes=1
)
print(f"Mean Reward: {result['mean_reward']:.4f}")
```

### 全环境评测

```python
environments = [
    "simple", "spread", "adversary", "push", "tag",
    "crypto", "reference", "speaker_listener", "world_comm"
]

all_results = {}
for env_name in environments:
    result = run_benchmark(
        env_name=env_name,
        provider="qwen",
        episodes=5,
        output_dir="results/benchmarks",
    )
    all_results[env_name] = result
    print(f"{env_name}: {result['mean_reward']:.4f} ± {result['std_reward']:.4f}")
```

### 多模型对比

```python
providers = ["qwen", "deepseek", "openai"]

for provider in providers:
    result = run_benchmark(
        env_name="spread",
        provider=provider,
        episodes=10,
        output_dir=f"results/benchmarks/{provider}",
    )
    print(f"{provider}: {result['mean_reward']:.4f} ± {result['std_reward']:.4f}")
```

### 使用本地模型

```python
# Ollama
result = run_benchmark(
    env_name="tag",
    provider="ollama",
    episodes=5,
    model_name="qwen2.5:7b",
)

# Transformers
result = run_benchmark(
    env_name="spread",
    provider="transformers",
    episodes=3,
    model_path="Qwen/Qwen2.5-7B-Instruct",
    device="cuda",
)
```

## 日志解析

### JSON 日志格式

每个 episode 的 JSON 日志包含：

```json
[
  {
    "step": 0,
    "agent": "agent_0",
    "observation": { ... },
    "action": [0.0, 0.8, 0.0, 0.0, 0.5],
    "thought": "Target is left-up, applying thrust",
    "reward": -0.45
  },
  // ... 更多步骤
  {
    "final_summary": true,
    "total_rewards": { "agent_0": -12.3, "agent_1": -8.7 },
    "mean_reward": -10.5
  }
]
```

### 编程解析

```python
import json

with open("results/benchmarks/spread/spread_ep1.json") as f:
    data = json.load(f)

# 提取每步奖励
step_rewards = [entry["reward"] for entry in data if "step" in entry]

# 提取 LLM 思考过程
thoughts = [entry["thought"] for entry in data if "step" in entry]

# 提取最终统计
final = [entry for entry in data if entry.get("final_summary")]
```

## 统计分析

`run_benchmark()` 自动计算两个核心统计指标：

| 指标 | 公式 | 含义 |
|:-----|:-----|:-----|
| **Mean Reward** | `Σ(episode_mean) / N` | 跨 episode 平均奖励 |
| **Std Reward** | `√(Σ(x - mean)² / N)` | 奖励的标准差 |

其中 `episode_mean` 是每个 episode 中所有智能体奖励的平均值。

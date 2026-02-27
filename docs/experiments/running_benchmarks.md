# 运行10次 Adversary 环境测试 - 完整指南

## 快速开始

```bash
cd /workspaces/MPE_muiltiagent_benchmark

# 激活环境
source .venv-1/bin/activate

# 运行10个episode的adversary测试
python3 benchmark_runner.py
```

## 执行流程详解

### 第一步：初始化（耗时：几秒）
```
✓ 创建输出目录: results/benchmarks/adversary/
✓ 导入游戏runner: run_adversary_game
✓ 初始化LLM引擎: provider="qwen"
```

### 第二步：循环运行10个episode

对于每个episode（i = 1 到 10）：

#### 2.1 Episode 1 时间表

| 阶段 | 操作 | 输出 | 耗时 |
|------|------|------|------|
| **初始化** | 创建 adversary 环境 | env = simple_adversary_v3(...) | 1-2s |
| **决策循环** | 循环 MAX_STEPS(5) 步 | | |
| - Step 0 | 3个GOOD agents + 1个ADVERSARY = 4个LLM调用 | 4个action + 4个thought | 20-30s |
| - Step 1-4 | 每步4个LLM调用 | | 80-120s |
| **日志记录** | 保存step entries到JSON | `adversary_ep1.json` (包含20个step entries) | 0.5s |
| **视频保存** | 保存5帧到mp4 | `adversary_ep1.mp4` | 1s |
| **最终汇总** | 计算final_summary | `{"total_rewards": {"good": 8.5, "adversary": 2.1}, "mean_reward": 5.3}` | 0.1s |
| **小计** | Episode 1 | 2个文件保存 | **100-150s** |

#### 2.2 Episodes 2-10（同样过程重复）

```
Episode 2: run_adversary_game() -> adversary_ep2.{mp4,json}
Episode 3: run_adversary_game() -> adversary_ep3.{mp4,json}
...
Episode 10: run_adversary_game() -> adversary_ep10.{mp4,json}
```

**总耗时** = Episode初始化 + 10 × 单个episode时间 = **1000-1500 秒** (16-25分钟)

---

## 日志生成过程

### 单个Episode的日志生成

#### 输入：run_adversary_game() 的参数
```python
{
    "provider": "qwen",
    "output_name": "results/benchmarks/adversary/adversary_ep1",
    "N_GOOD": 3,
    "MAX_STEPS": 5
}
```

#### 输出：`adversary_ep1.json` 的结构

```json
[
  // ========== Step 0 ==========
  {
    "step": 0,
    "agent": "agent_0",
    "role": "GOOD",
    "obs": {
      "role": "GOOD_AGENT",
      "goal": {"rel": [0.52, -0.38], "dist": 0.65},
      "landmarks": [
        {"id": 0, "rel": [0.52, -0.38], "dist": 0.65, "is_target": true},
        {"id": 1, "rel": [-0.48, 0.62], "dist": 0.79, "is_target": false},
        {"id": 2, "rel": [0.15, -0.85], "dist": 0.86, "is_target": false}
      ],
      "adversary": {"rel": [0.28, -0.42], "dist": 0.50},
      "teammate": {"id": "agent_1", "rel": [-0.15, 0.08], "dist": 0.17}
    },
    "action": [0.0, 0.2, 0.8, 0.0, 0.0],    // [HOLD, LEFT, RIGHT, DOWN, UP]
    "thought": "The goal is at [0.52, -0.38]. I'll move RIGHT (a[2]=0.8) towards it. The adversary is at [0.28, -0.42] which is somewhat close, but I can try to reach the goal first.",
    "reward": 0.12
  },
  {
    "step": 0,
    "agent": "agent_1",
    "role": "GOOD",
    "obs": {...},
    "action": [0.0, 0.0, 0.1, 0.5, 0.0],
    "thought": "...",
    "reward": 0.08
  },
  {
    "step": 0,
    "agent": "agent_2",
    "role": "GOOD",
    "obs": {...},
    "action": [0.0, 0.3, 0.0, 0.0, 0.7],
    "thought": "...",
    "reward": 0.15
  },
  {
    "step": 0,
    "agent": "adversary_0",
    "role": "BAD",
    "obs": {
      "role": "ADVERSARY",
      "landmarks": [
        {"id": 0, "rel": [0.52, -0.38], "dist": 0.65},
        {"id": 1, "rel": [-0.48, 0.62], "dist": 0.79},
        {"id": 2, "rel": [0.15, -0.85], "dist": 0.86}
      ],
      "good_agents": [
        {"id": "agent_0", "rel": [0.28, -0.42], "dist": 0.50},
        {"id": "agent_1", "rel": [0.15, 0.28], "dist": 0.31},
        {"id": "agent_2", "rel": [-0.12, 0.35], "dist": 0.37}
      ]
    },
    "action": [0.0, 0.0, 0.5, 0.5, 0.0],
    "thought": "The good agents are spread out. Agent 0 is closest at [0.28, -0.42]. I should move towards the landmark at [0.52, -0.38] where agent_0 is heading.",
    "reward": -0.05
  },
  
  // ========== Step 1 ==========
  {
    "step": 1,
    "agent": "agent_0",
    "role": "GOOD",
    "obs": {...},
    "action": [...],
    "thought": "...",
    "reward": 0.14
  },
  // ... (同样格式，Steps 1-4)
  
  // ========== 最终汇总（Final Summary） ==========
  {
    "final_summary": true,
    "total_rewards": {
      "agent_0": 0.62,      // 5步的累计奖励
      "agent_1": 0.58,
      "agent_2": 0.64,
      "adversary_0": -0.18
    },
    "mean_reward": 0.415    // (0.62 + 0.58 + 0.64 - 0.18) / 4
  }
]
```

**日志统计**：
- 总条目数：4 agents × 5 steps + 1 final_summary = **21条**
- 文件大小：约 50-100 KB (取决于LLM思维过程长度)

---

## Benchmark Runner 的处理

### 第三步：解析日志

对每个 episode_i.json：

```python
def _parse_episode_log(episode_1_json):
    # 1. 找到 final_summary
    final_summary = {
        "total_rewards": {"agent_0": 0.62, "agent_1": 0.58, ...},
        "mean_reward": 0.415
    }
    
    # 2. ✅ 直接使用 final_summary 中的数据（修复后）
    return {
        "log_path": "results/benchmarks/adversary/adversary_ep1.json",
        "total_rewards": {"agent_0": 0.62, "agent_1": 0.58, ...},
        "mean_reward": 0.415,        # ✅ 准确！
        "steps": 5
    }
```

### 第四步：汇总统计

```python
all_episode_stats = [
    {"episode": 1, "mean_reward": 0.415, "total_rewards": {...}},
    {"episode": 2, "mean_reward": 0.398, "total_rewards": {...}},
    ...
    {"episode": 10, "mean_reward": 0.421, "total_rewards": {...}}
]

episode_means = [0.415, 0.398, ..., 0.421]

# 计算聚合统计
mean_reward = sum(episode_means) / 10 = 0.409
variance = sum((x - 0.409)^2 for x in episode_means) / 10 = 0.000125
std_reward = sqrt(0.000125) = 0.0112
```

### 第五步：输出结果

**控制台输出**：
```
============================================================
📊 BENCHMARK SUMMARY
============================================================
Environment: adversary
Provider: qwen
Episodes: 10
Mean Reward (across episodes): 0.4090
Std Dev: 0.0112
============================================================

📈 Episode Statistics:

  Episode 1:
    Mean Reward: 0.4150
    Total Rewards: {'agent_0': 0.62, 'agent_1': 0.58, 'agent_2': 0.64, 'adversary_0': -0.18}
    Steps: 5

  Episode 2:
    Mean Reward: 0.3980
    Total Rewards: {'agent_0': 0.59, 'agent_1': 0.55, 'agent_2': 0.61, 'adversary_0': -0.15}
    Steps: 5

  ...

  Episode 10:
    Mean Reward: 0.4210
    Total Rewards: {'agent_0': 0.65, 'agent_1': 0.60, 'agent_2': 0.66, 'adversary_0': -0.19}
    Steps: 5

✅ Results saved to benchmark_results.json
```

**文件输出**：`benchmark_results.json`
```json
{
  "env": "adversary",
  "provider": "qwen",
  "episodes": 10,
  "mean_reward": 0.409,
  "std_reward": 0.0112,
  "episode_stats": [
    {
      "episode": 1,
      "env": "adversary",
      "log": "results/benchmarks/adversary/adversary_ep1.json",
      "video": "results/benchmarks/adversary/adversary_ep1.mp4",
      "mean_reward": 0.415,
      "total_rewards": {"agent_0": 0.62, ...},
      "steps": 5
    },
    ...
  ]
}
```

---

## 输出文件结构

10个episode后，生成的文件：

```
results/benchmarks/
├── adversary/
│   ├── adversary_ep1.mp4          (5帧视频)
│   ├── adversary_ep1.json         (21条日志)
│   ├── adversary_ep2.mp4
│   ├── adversary_ep2.json
│   ├── ...
│   ├── adversary_ep10.mp4
│   └── adversary_ep10.json
│
└── benchmark_results.json         (汇总统计)

总计：
- 20个文件（10个mp4 + 10个json）
- 总大小：约 500-1000 MB（每个视频 50-100 MB）
- 日志总行数：约 210 条entry（10 episodes × 21 entries）
```

---

## 关键参数说明

### 日志中的关键字段含义

| 字段 | 含义 | Adversary示例 |
|------|------|-------------|
| `step` | 游戏步数 (0-4) | 0 |
| `agent` | 智能体ID | "agent_0" 或 "adversary_0" |
| `role` | 角色类型 | "GOOD" 或 "BAD" |
| `obs` | 解析后的观测 | {"goal": {...}, "landmarks": [...]} |
| `action` | 连续动作向量 | [0.0, 0.2, 0.8, 0.0, 0.0] |
| `thought` | LLM的思考过程 | "The goal is at..." |
| `reward` | 该步的奖励 | 0.12 |
| `final_summary` | 游戏结束标志 | true |
| `total_rewards` | 所有agents的累计奖励 | {"agent_0": 0.62, ...} |
| `mean_reward` | 游戏的平均奖励 | 0.415 |

---

## 常见问题 & 故障排除

### Q1: 测试需要多长时间？
**A**: 按照以下估算：
- 单个episode：2-3分钟（含4个LLM调用×5步）
- 10个episodes：20-30分钟
- 如果使用本地模型(Ollama/Transformers)：可能更快（GPU加速）

### Q2: 如何修改MAX_STEPS（步数）？
**A**: 当前所有环境的MAX_STEPS是硬编码的。要修改，在对应的游戏文件中修改：
```python
# adv_API.py
MAX_STEPS = 5  # → 改为你想要的步数
```

### Q3: 日志中的 `mean_reward` 是怎么算的？
**A**: 对于Adversary：
```
mean_reward = (agent_0.reward + agent_1.reward + agent_2.reward + adversary_0.reward) / 4
            = (0.62 + 0.58 + 0.64 - 0.18) / 4
            = 0.415
```
注意：好人奖励为正，坏人奖励为负（零和游戏）

### Q4: 如何使用本地模型（Ollama）运行？
**A**: 修改benchmark_runner.py的main：
```python
result = run_benchmark(
    env_name="adversary",
    provider="ollama",
    episodes=10,
    output_dir="results/benchmarks",
    model_name="qwen2.5:7b"
)
```

### Q5: 视频太大，如何减小文件大小？
**A**: 修改对应游戏文件的 `imageio.mimsave()` 参数：
```python
# 降低FPS或质量
imageio.mimsave(vid_name, frames, fps=2, macro_block_size=2)
```

---

## 数据分析建议

### 提取10个episode的统计趋势

```python
import json
import numpy as np

with open("benchmark_results.json") as f:
    data = json.load(f)

# 提取每个episode的mean_reward
means = [s["mean_reward"] for s in data["episode_stats"]]

# 计算趋势
print(f"Min: {min(means):.4f}")
print(f"Max: {max(means):.4f}")
print(f"Mean: {np.mean(means):.4f}")
print(f"Std: {np.std(means):.4f}")

# 检查是否有改进趋势
print(f"Episode 1-5 avg: {np.mean(means[:5]):.4f}")
print(f"Episode 6-10 avg: {np.mean(means[5:]):.4f}")
```

---


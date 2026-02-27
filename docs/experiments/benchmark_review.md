# Benchmark Runner - 日志处理分析与改进

## 当前问题分析

### 1. _parse_episode_log 函数的问题

**当前实现** (lines 56-73)：
```python
def _parse_episode_log(log_path: Path) -> Dict[str, Any]:
    with log_path.open("r", encoding="utf-8") as f:
        data = json.load(f)

    rewards_per_agent: Dict[str, float] = {}
    steps: List[Dict[str, Any]] = []
    for entry in data:
        step = entry.get("step")
        if step is None:
            continue              # ❌ 跳过了 final_summary
        steps.append(entry)
        aid = entry.get("agent")
        r = float(entry.get("reward", 0.0))
        rewards_per_agent[aid] = rewards_per_agent.get(aid, 0.0) + r

    total_rewards = rewards_per_agent
    agent_rewards = list(total_rewards.values())
    mean_reward = sum(agent_rewards) / len(agent_rewards) if agent_rewards else 0.0
```

**问题**：

对于 **Adversary (adv_API)** 环境，日志格式为：
```json
[
  {"step": 0, "agent": "agent_0", "role": "GOOD", "reward": 0.1},
  {"step": 0, "agent": "agent_1", "role": "GOOD", "reward": 0.08},
  {"step": 0, "agent": "agent_2", "role": "GOOD", "reward": 0.12},
  {"step": 0, "agent": "adversary_0", "role": "BAD", "reward": -0.05},
  ...
  {"final_summary": true, "total_rewards": {"good": 8.5, "adversary": 2.1}, "mean_reward": 5.3}
]
```

**处理过程**：

| 阶段 | 计算 | 结果 |
|------|------|------|
| 累加 step entries | agent_0 + agent_1 + agent_2 + adversary_0 | rewards_per_agent = {agent_0: 5.1, agent_1: 4.8, agent_2: 5.2, adversary_0: -1.5} |
| 平均 | (5.1 + 4.8 + 5.2 - 1.5) / 4 | mean_reward = **3.4** |
| **忽视** final_summary | 未读取 | 舍弃 {"good": 8.5, "adversary": 2.1, "mean_reward": 5.3} |

**结果不一致**！
- `_parse_episode_log` 计算: mean_reward = 3.4 (所有agent的简单平均)
- 日志中 `final_summary`: mean_reward = 5.3 (角色聚合的平均)

---

### 2. 10次 Adversary 环境测试会发生什么

命令：
```bash
python3 benchmark_runner.py
# run_benchmark(env_name="adversary", provider="qwen", episodes=10)
```

**输出目录结构**：
```
results/benchmarks/
└── adversary/
    ├── adversary_ep1.mp4
    ├── adversary_ep1.json          # Step logs + final_summary
    ├── adversary_ep2.mp4
    ├── adversary_ep2.json
    ├── ...
    ├── adversary_ep10.mp4
    └── adversary_ep10.json
```

**数据流**：

1. **Episode 1**：
   - `run_single_episode()` 调用 `run_adversary_game()` 
   - 保存 `adversary_ep1.json` (包含final_summary)
   - `_parse_episode_log()` 读取日志
   - ❌ 忽视final_summary，重新计算mean_reward

2. **Episodes 2-10**：同样过程

3. **聚合统计**：
   ```python
   all_episode_stats = [
       {"episode": 1, "mean_reward": 3.4},  # ❌ 不是5.3
       {"episode": 2, "mean_reward": 3.2},
       ...
       {"episode": 10, "mean_reward": 3.5},
   ]
   
   mean_reward = (3.4 + 3.2 + ... + 3.5) / 10 = 3.35  # 这个数字是错的！
   std_reward = sqrt(variance)
   ```

**最终输出**：
```json
{
  "env": "adversary",
  "provider": "qwen",
  "episodes": 10,
  "mean_reward": 3.35,        // ❌ 应该是 ~5.3 左右
  "std_reward": 0.25,
  "episode_stats": [
    {
      "episode": 1,
      "env": "adversary",
      "mean_reward": 3.4,      // ❌ 来自错误的计算
      "total_rewards": {
        "agent_0": 5.1,
        "agent_1": 4.8,
        "agent_2": 5.2,
        "adversary_0": -1.5    // ❌ 这里不应该直接平均
      },
      "steps": 25
    },
    ...
  ]
}
```

---

### 3. 不同游戏受影响情况

| 游戏 | 是否受影响 | 原因 |
|------|----------|------|
| **Spread** | ✅ **正确** | 所有agent同质，简单平均 = 最终平均 |
| **Tag** | ❌ **错误** | `final_summary` 用角色聚合（Prey 1 agent vs Predators 3）|
| **World Comm** | ❌ **错误** | 三种角色(LEADER/HUNTER/PREY)不同权重 |
| **Adversary** | ❌ **错误** | 好人 vs 坏人权重应该 1:1，不是 3:1 |
| **Crypto** | ✅ **正确** | 三个agent独立，简单平均可接受 |
| **Push** | ❌ **错误** | 好人 vs 坏人权重应该 1:1 |
| **Simple** | ✅ **正确** | 单agent |
| **Reference** | ✅ **正确** | 两个agent等权 |
| **Speaker-Listener** | ✅ **正确** | 两个agent等权 |

---

## 解决方案

### 改进策略

**优先使用 `final_summary` 中的数据**，而不是重新计算：

```python
def _parse_episode_log(log_path: Path) -> Dict[str, Any]:
    with log_path.open("r", encoding="utf-8") as f:
        data = json.load(f)
    
    # 首先尝试找到 final_summary
    final_summary = None
    steps: List[Dict[str, Any]] = []
    
    for entry in data:
        if entry.get("final_summary"):
            final_summary = entry
            continue
        
        step = entry.get("step")
        if step is not None:
            steps.append(entry)
    
    # ✅ 方案 1: 使用 final_summary（最准确）
    if final_summary:
        return {
            "log_path": str(log_path),
            "total_rewards": final_summary.get("total_rewards", {}),
            "mean_reward": final_summary.get("mean_reward", 0.0),
            "steps": len(steps),
        }
    
    # ✅ 方案 2: 回退到按agent累加（兼容旧日志）
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
```

---

### 预期改进效果

**运行10次 Adversary 测试后**：

#### 修改前 ❌
```json
{
  "mean_reward": 3.35,       // 错误：agent简单平均
  "std_reward": 0.25,
  "episode_stats": [
    {"mean_reward": 3.4},    // 应该是 5.3
    {"mean_reward": 3.2},
    ...
  ]
}
```

#### 修改后 ✅
```json
{
  "mean_reward": 5.32,       // 正确：使用 final_summary
  "std_reward": 0.18,        
  "episode_stats": [
    {
      "mean_reward": 5.3,
      "total_rewards": {
        "good": 8.5,
        "adversary": 2.1
      }
    },
    {
      "mean_reward": 5.2,
      "total_rewards": {
        "good": 8.3,
        "adversary": 2.2
      }
    },
    ...
  ]
}
```

---

## 建议

### 立即执行
1. **更新 `_parse_episode_log()` 函数**以优先使用 `final_summary`
2. **添加数据验证日志**：打印 final_summary 数据来确认一致性

### 长期改进
1. 统一日志API：制定明确的"优先级"规则
2. 在 `final_summary` 中添加元数据：`{"role_weights": {"good": 3, "adversary": 1}, ...}`
3. 创建日志验证工具检查一致性


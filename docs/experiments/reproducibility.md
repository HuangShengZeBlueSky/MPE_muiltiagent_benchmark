# 随机种子固定指南

## 概述

为了确保实验的可重现性，所有9个MPE游戏环境现已支持 **随机种子 (seed)** 参数。

## 快速使用

### 方式1：使用 benchmark_runner (推荐)

运行10个episode的Adversary测试，使用种子 1-10：

```python
from benchmark_runner import run_benchmark

result = run_benchmark(
    env_name="adversary",
    provider="qwen",
    episodes=10,
    output_dir="results/benchmarks",
    seed_start=1  # 使用种子 1, 2, 3, ..., 10
)
```

运行5个episode的Spread测试，使用种子 5-9：

```python
result = run_benchmark(
    env_name="spread",
    provider="qwen",
    episodes=5,
    seed_start=5  # 使用种子 5, 6, 7, 8, 9
)
```

### 方式2：直接运行单个游戏（带seed）

```python
from adv_API import run_adversary_game

# 使用固定种子 42
run_adversary_game("qwen", "my_game", seed=42)
```

### 方式3：命令行运行所有10个episodes

```bash
python3 benchmark_runner.py  # 默认使用种子 1-10
```

## 参数说明

### benchmark_runner.py 中的新参数

```python
run_benchmark(
    env_name: str,              # 游戏名称
    provider: str,              # LLM提供商
    episodes: int = 3,          # 运行的episode数
    output_dir: str = "results/benchmarks",
    seed_start: int = 1,        # ✅ 新增：起始种子 (默认 1)
    **game_kwargs
)
```

**seed_start 说明**：
- 如果 `episodes=10` 且 `seed_start=1`
- 则使用的种子为：1, 2, 3, 4, 5, 6, 7, 8, 9, 10
- 每个episode使用不同的种子 = 不同的初始状态

**seed_start 说明**：
- 如果 `episodes=10` 且 `seed_start=5`
- 则使用的种子为：5, 6, 7, 8, 9, 10, 11, 12, 13, 14

### 各游戏的seed支持

所有9个游戏都支持 `seed` 参数：

| 游戏 | 文件 | seed参数 | 用法 |
|------|------|---------|------|
| Spread | spread_API.py | ✅ | `run_spread_game(provider, output_file, seed=1)` |
| Adversary | adv_API.py | ✅ | `run_adversary_game(provider, output_name, seed=1)` |
| Tag | tag_API.py | ✅ | `run_tag_game(provider, output_name, seed=1)` |
| Push | push.py | ✅ | `run_push_game(provider, output_name, seed=1)` |
| Crypto | crypto.py | ✅ | `run_crypto_game(provider, output_name, seed=1)` |
| Reference | reference.py | ✅ | `run_reference_game(provider, output_name, seed=1)` |
| Speaker-Listener | speaker_listener.py | ✅ | `run_speaker_listener(provider, output_name, seed=1)` |
| World Comm | world_comm.py | ✅ | `run_world_comm(provider, output_name, seed=1)` |
| Simple | simple.py | ✅ | `run_simple_game(provider, output_name, seed=1)` |

## 实现原理

### Benchmark Runner 的处理流程

```python
# benchmark_runner.py 中的 run_benchmark 函数
for ep in range(1, episodes + 1):
    seed = seed_start + ep - 1      # 计算该episode的seed
    print(f"Episode {ep}/{episodes} | Seed {seed}")
    
    # 传递给run_single_episode
    stats = run_single_episode(
        env_name, provider, ep, 
        output_dir, 
        seed=seed,              # ✅ 传递seed
        **game_kwargs
    )

# 各游戏的环境初始化
env = simple_spread_v3.parallel_env(
    num_agents=N,
    max_cycles=MAX_STEPS,
    continuous_actions=True,
    render_mode="rgb_array",
    seed=seed                   # ✅ PettingZoo使用此seed
)
```

## 可重现性保证

### 固定seed的效果

**episode 1 (seed=1)**：
- 初始状态 S1 → 运行 → 日志1.json (固定)
- 再跑一遍 episode 1 (seed=1) → 完全相同的初始状态 S1

**episode 2 (seed=2)**：
- 初始状态 S2 → 运行 → 日志2.json (固定，但不同于episode1)
- 再跑一遍 episode 2 (seed=2) → 完全相同的初始状态 S2

### 示例：Adversary 10-episode 的可重现性

```bash
# 第一次运行
$ python3 benchmark_runner.py
[Benchmark] adversary | Episode 1/10 | Seed 1
[Benchmark] adversary | Episode 2/10 | Seed 2
...
[Benchmark] adversary | Episode 10/10 | Seed 10
生成文件：
  adversary_ep1.json (seed=1)
  adversary_ep2.json (seed=2)
  ...
  adversary_ep10.json (seed=10)

# 一周后，重新运行相同命令
$ python3 benchmark_runner.py
[Benchmark] adversary | Episode 1/10 | Seed 1
[Benchmark] adversary | Episode 2/10 | Seed 2
...
[Benchmark] adversary | Episode 10/10 | Seed 10

# 结果对比
adversary_ep1.json (新) == adversary_ep1.json (旧) ✅
adversary_ep2.json (新) == adversary_ep2.json (旧) ✅
...
mean_reward (新) ≈ mean_reward (旧) ✅
```

**注**：LLM的响应可能因模型版本/参数不同而略有变化，但环境初始状态完全相同。

## 常见用法

### 1. 对比不同LLM的性能

```python
# 使用相同的种子集合 (1-10) 测试不同的LLM

# Qwen 模型
qwen_result = run_benchmark(
    env_name="tag",
    provider="qwen",
    episodes=10,
    seed_start=1
)

# DeepSeek 模型
deepseek_result = run_benchmark(
    env_name="tag",
    provider="deepseek",
    episodes=10,
    seed_start=1
)

# 对比：相同的初始环境，不同的LLM表现
```

### 2. 参数搜索

```python
# 测试不同的模型参数

for temperature in [0.3, 0.5, 0.7]:
    result = run_benchmark(
        env_name="spread",
        provider="qwen",
        episodes=10,
        seed_start=1,
        temperature=temperature  # 传递给get_api_engine
    )
    print(f"Temp={temperature}: mean_reward={result['mean_reward']:.3f}")
```

### 3. 可重现的论文实验

```python
# 在论文中明确指定种子范围

# Figure 3 in Paper
result = run_benchmark(
    env_name="world_comm",
    provider="gpt",
    episodes=20,
    seed_start=1  # 种子 1-20
)

# 读者可以用完全相同的条件重现该结果
```

## 技术细节

### PettingZoo 的 seed 参数

```python
env = simple_spread_v3.parallel_env(
    num_agents=3,
    max_cycles=100,
    continuous_actions=True,
    seed=42  # ← 控制环境初始化随机数
)

observations, infos = env.reset()
# 此时的observations由seed决定
# seed=42时每次都完全相同
# seed=43时会得到不同的初始状态
```

### 支持的种子范围

- 任何非负整数：0, 1, 2, ..., 2^31-1
- 推荐：1-20 或 1-100（小范围便于论文报告）
- 避免：非常大的数值或负数可能导致行为不确定

## 故障排除

### Q1: 两次运行使用相同seed仍然得到不同的初始状态？
**A**: 可能是因为：
1. LLM的响应不同（这是正常的，LLM的随机性独立于环境）
2. 环境版本不同（升级PettingZoo可能改变seed行为）
3. 检查 seed 参数是否正确传递

### Q2: 能否只固定部分随机性？
**A**: 通过seed固定的是**环境初始化**，LLM的随机性单独控制：
```python
# 固定环境，固定LLM
result = run_benchmark(env_name="tag", provider="qwen", episodes=5, seed_start=1, temperature=0.0)

# 固定环境，随机LLM（默认）
result = run_benchmark(env_name="tag", provider="qwen", episodes=5, seed_start=1)
```

### Q3: 如何为历史数据补充seed信息？
**A**: 新的日志会包含seed，历史日志无法追溯。建议：
- 重新运行获得带seed的结果
- 或在报告中说明"历史数据未记录seed"

## 下一步

- [RUN_10_EPISODES_GUIDE.md](RUN_10_EPISODES_GUIDE.md) - 10个episode的详细指南
- [LOGGING_FORMAT_SUMMARY.md](LOGGING_FORMAT_SUMMARY.md) - 日志格式说明
- [BENCHMARK_REVIEW.md](BENCHMARK_REVIEW.md) - Benchmark分析

# Benchmark Evaluation

## Usage

```python
from benchmark_runner import run_benchmark

result = run_benchmark(
    env_name="spread",           # Any of 9 environments
    provider="qwen",             # LLM provider
    episodes=5,                  # Number of episodes
    output_dir="results/benchmarks",
)

print(f"Mean: {result['mean_reward']:.4f} ± {result['std_reward']:.4f}")
```

## Supported Environments

```python
"simple", "spread", "adversary", "push", "tag",
"crypto", "reference", "speaker_listener", "world_comm"
```

## Output Structure

```
results/benchmarks/
├── spread/
│   ├── spread_ep1.mp4    # Episode 1 video
│   ├── spread_ep1.json   # Episode 1 log
│   └── ...
└── ...
```

## Multi-Model Comparison

```python
for provider in ["qwen", "deepseek", "openai"]:
    result = run_benchmark("spread", provider, episodes=10)
    print(f"{provider}: {result['mean_reward']:.4f} ± {result['std_reward']:.4f}")
```

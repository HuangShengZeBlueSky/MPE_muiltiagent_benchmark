# Quick Start

## Prerequisites

- Python ≥ 3.8
- At least one LLM API key or local model

## 1. Install Dependencies

```bash
git clone https://github.com/your-repo/MPE_muiltiagent_benchmark.git
cd MPE_muiltiagent_benchmark
pip install -r requirements.txt
```

## 2. Configure API Key

```bash
# Option A: .env file (recommended)
echo 'DEEPSEEK_API_KEY=sk-your-key' > .env

# Option B: Environment variable
export DEEPSEEK_API_KEY="sk-your-key"

# Option C: Runtime parameter
engine = get_api_engine("deepseek", api_key="sk-your-key")
```

## 3. Run Your First Game

```bash
python simple.py      # Simplest environment
python spread_API.py  # Cooperative coverage
python tag_API.py     # Predator-prey chase
```

## 4. View Output

Each run generates:
- `xxx_demo.mp4` — Game replay video
- `xxx_demo.json` — Step-by-step log (obs, action, thought, reward)

::: tip JSON Log Sample
```json
{
  "step": 5,
  "agent": "agent_0",
  "observation": { "vel": [0.1, -0.2], "landmark_rel": [-0.3, 0.5] },
  "action": [0.0, 0.8, 0.0, 0.0, 0.5],
  "thought": "Target is left and above, applying thrust",
  "reward": -0.34
}
```
:::

## Next Steps

- 🎮 [Game Environments](/en/games/) — All 9 environments explained
- 🧠 [Prompt Engineering](/en/advanced/prompt-engineering) — Prompt system design
- 📊 [Benchmark](/en/advanced/benchmark) — Batch evaluation guide

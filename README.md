# MPE Multi-Agent Benchmark 🎮🤖

https://huangshengzebluesky.github.io/MPE_muiltiagent_benchmark/
<img width="3000" height="1670" alt="image" src="https://github.com/user-attachments/assets/0e78a541-ba6a-4ee1-bd46-913e72cf2b53" />

A multi-agent reinforcement learning benchmark suite based on PettingZoo MPE environments with integrated LLM API-driven agent decision-making.

[![Python](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![PettingZoo](https://img.shields.io/badge/PettingZoo-MPE-green.svg)](https://pettingzoo.farama.org/)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

🌐 **Available in**: [English](README_en.md) | [中文](README_zh.md) | [日本語](README_ja.md) | [Tiếng Việt](README_vi.md)

In here you can find some game videos and log.
https://cloud.tsinghua.edu.cn/d/8780829bc1bd45e480bf/
---

## 🌟 Key Features

- 🎯 **9 Classic Environments**: Cover cooperation, adversarial, and communication scenarios
- 🤖 **LLM Integration**: Support for OpenAI, DeepSeek, Qwen, Gemini
- 📊 **Standardized Parsing**: Convert raw observations to LLM-friendly JSON format
- 📝 **Comprehensive Documentation**: Complete guides from quick start to advanced development
- 🔧 **Modular Design**: Easy to extend and customize

## 📁 Project Structure

```
MPE_muiltiagent_benchmark/
├── 📄 Configuration Files
│   ├── requirements.txt          # Python dependencies
│   ├── requirements.lock         # Pinned versions for reproducibility
│   ├── pyproject.toml            # Project configuration
│   ├── .env.example              # API keys template
│   └── .gitignore                # Git ignore rules
│
├── 📚 Documentation (docs/)
│   ├── README.md                 # Documentation hub
│   ├── getting_started/          # Getting started guides
│   │   ├── quickstart.md         # ⭐ Quick start (5 min)
│   │   ├── environment_setup.md  # Detailed environment setup
│   │   ├── dependency_management.md # requirements.txt vs requirements.lock
│   │   └── overview.md           # Project overview
│   ├── configuration/            # Configuration guides
│   │   └── api_keys.md           # 🔑 API key management
│   ├── architecture/             # Architecture & design
│   │   ├── observation_space.md  # Observation parsing
│   │   ├── logging_system.md     # 📊 Logging system
│   │   └── models.md             # 🤖 Model usage
│   ├── experiments/              # Experiment guides
│   │   ├── reproducibility.md    # 🎲 Seed fixing
│   │   ├── running_benchmarks.md # Running benchmarks
│   │   └── benchmark_review.md   # 📈 Benchmark analysis
│   └── dev_notes/                # Developer notes
│       ├── work_summary.md       # Work summary
│       ├── workflow_standardization.md # Workflow standards
│       └── api_keys_refactor.md  # API key migration log
│
├── 🎮 Environment Implementations (9 complete games)
│   ├── spread_API.py             # Simple Spread
│   ├── adv_API.py                # Simple Adversary
│   ├── tag_API.py                # Simple Tag
│   ├── push.py                   # Simple Push
│   ├── crypto.py                 # Simple Crypto
│   ├── reference.py              # Simple Reference
│   ├── speaker_listener.py       # Simple Speaker Listener
│   ├── world_comm.py             # Simple World Comm
│   ├── simple.py                 # Simple (Basic)
│   └── utils_api.py              # Unified LLM API interface
│
├── 🧪 Testing & Tools
│   ├── benchmark_runner.py       # ✅ Batch testing framework
│   ├── setup_api_keys.py         # ✅ API key setup script
│   ├── verify_environment.py     # ✅ Environment verification
│   └── test_unified_api.py       # API tests
│
├── 🔍 Observation Parsing (obs/)
│   ├── parse_*_obs.py            # 9 environment parsers
│   └── utils.py                  # Common utility functions
│
├── 💬 Prompt Engineering (prompt/)
│   └── prompt_for_*.py           # Standardized Prompt modules
│
└── 📊 Results Output (results/)
    └── benchmarks/<env>/         # Test results per environment
        ├── *.mp4                 # Video recordings
        └── *.json                # Detailed logs
```

## 🚀 Quick Start

### System Requirements

- **Python**: 3.8+ (Recommended: 3.12.3, tested)
- **Operating System**: Linux / macOS / Windows
- **Dependency Manager**: pip / conda / uv

### 1. Install Dependencies

```bash
# Clone repository
git clone https://github.com/HuangShengZeBlueSky/MPE_muiltiagent_benchmark.git
cd MPE_muiltiagent_benchmark

# Option A: Using venv (Recommended)
python -m venv .venv
source .venv/bin/activate  # Linux/macOS
# .venv\Scripts\activate   # Windows
pip install -r requirements.txt

# Option B: Using conda
conda create -n mpe-bench python=3.12
conda activate mpe-bench
pip install -r requirements.txt

# Option C: Direct install (Not recommended)
pip install -r requirements.txt
```

**Verify Installation**:
```bash
# Run environment verification script
python verify_environment.py
# ✅ All checks pass means setup is successful
```

**📖 Detailed Guide**: See [docs/getting_started/environment_setup.md](docs/getting_started/environment_setup.md)

### 2. Configure API Keys 🔑

#### Method A: Interactive Configuration (Recommended)
```bash
python setup_api_keys.py
```

#### Method B: Manual Configuration
```bash
# Copy template and edit
cp .env.example .env
nano .env  # Add your API keys
```

#### Method C: Environment Variables
```bash
export QWEN_API_KEY="sk-your-key"
export DEEPSEEK_API_KEY="sk-your-key"
export OPENAI_API_KEY="sk-your-key"
```

**Get API Keys**:
- Qwen (Recommended): https://dashscope.console.aliyun.com
- DeepSeek: https://platform.deepseek.com
- OpenAI: https://platform.openai.com/api-keys
- Gemini: https://aistudio.google.com/apikey

**📖 Detailed Configuration**: See [docs/configuration/api_keys.md](docs/configuration/api_keys.md)

### 3. Run Tests

#### Single Environment Test
```bash
# Run a single game (uses Qwen API by default)
python adv_API.py
python spread_API.py
python tag_API.py
```

#### Batch Benchmark Testing (Recommended)
```bash
# Run 10 episodes of Adversary with seeds 1-10
python benchmark_runner.py

# Custom environment and number of episodes
python -c "from benchmark_runner import run_benchmark; run_benchmark(env_name='spread', provider='qwen', episodes=20, seed_start=1)"
```

**Output**: Automatically saves videos (`*.mp4`) and logs (`*.json`) to `results/benchmarks/<env>/`

**📖 Detailed Guide**: [docs/getting_started/quickstart.md](docs/getting_started/quickstart.md)

## 🧭 Repository Workflow

- **Environment Setup**: Create virtual environment and install dependencies
- **Model Selection**: Configure model via `utils_api.get_api_engine(provider)`
    - Available: `deepseek`, `qwen`, `gpt`, `gemini`, `transformers`, `ollama`, `vllm`
    - Pass corresponding parameters: `api_key`, `model_name`, `model_path`, etc.
- **Observation Parsing**: Use `obs/parse_*.py` for structured parsing
- **Prompt Building**: Call four standardized functions from `prompt/prompt_for_*.py`
- **Run Environment**: Execute main script (e.g., `reference.py`, `world_comm.py`)
- **Output**: Automatically saves videos (mp4) and detailed logs (json)

### Running Common Environments

```bash
# Run with specific provider (modify PROVIDER at top of file)
python reference.py
python speaker_listener.py
python world_comm.py

# Run world communication and parse real observations
PYTHONPATH=. python obs/test_parse_world_comm_obs_real.py
```

### Model Configuration Example

```python
from utils_api import get_api_engine

# Remote APIs (auto-reads env vars for keys)
llm = get_api_engine("qwen")           # Alibaba Qwen
llm = get_api_engine("deepseek")       # DeepSeek
llm = get_api_engine("gpt")            # OpenAI GPT
llm = get_api_engine("gemini")         # Google Gemini

# Local models (no API keys needed)
llm = get_api_engine("transformers", model_path="Qwen/Qwen2.5-7B-Instruct")
llm = get_api_engine("ollama", model_name="qwen2.5:7b")
llm = get_api_engine("vllm", model_path="meta-llama/Llama-3-8B")

# Call
action, thought = llm.generate_action(system_prompt, user_prompt)
```

### Output and Logs

- **Videos**: `world_comm_modular_*.mp4` etc. (frame-by-frame for playback)
- **Logs**: `*.json` (contains observations, actions, rewards, and LLM responses)

### Important Notes

- PettingZoo `mpe` will migrate to `mpe2` in future; current code is backwards compatible
- For Google Gemini, note `google.generativeai` deprecation; consider migrating to `google.genai`

## 📖 Web Documentation

- Chinese: docs/index_zh.html (open locally)
- English: docs/index_en.html (open in browser)

## 🎯 Supported Environments

| Environment | Type | Agents | Parsing | Prompt | Logging | Seed | Description |
|-------------|------|--------|---------|--------|---------|------|-------------|
| **Simple Spread** | Cooperation | N | ✅ | ✅ | ✅ | ✅ | Cover all landmarks |
| **Simple Adversary** | Adversarial | N+1 | ✅ | ✅ | ✅ | ✅ | Deception & reasoning |
| **Simple Tag** | Pursuit-Evasion | N+1 | ✅ | ✅ | ✅ | ✅ | Hunter captures prey |
| **Simple Push** | Physics | 2 | ✅ | ✅ | ✅ | ✅ | Push object to target |
| **Simple Crypto** | Cryptography | 3 | ✅ | ✅ | ✅ | ✅ | Alice/Bob/Eve game |
| **Simple Reference** | Reference | 2 | ✅ | ✅ | ✅ | ✅ | Color reference |
| **Simple Speaker Listener** | Communication | 2 | ✅ | ✅ | ✅ | ✅ | Encode-decode |
| **Simple World Comm** | Complex | N | ✅ | ✅ | ✅ | ✅ | Multi-landmark scenario |
| **Simple (Basic)** | Basic | 1 | ✅ | ✅ | ✅ | ✅ | Basic cooperation |

✅ = Completed and tested

## 💡 Core Features

### 1. Unified Benchmark Testing Framework ⭐

Batch test multiple environments with fixed seeds for reproducible experiments:

```python
from benchmark_runner import run_benchmark

# Run 10 episodes with seeds 1-10
result = run_benchmark(
    env_name="adversary",      # Choose from 9 environments
    provider="qwen",           # qwen/deepseek/gpt/gemini/ollama/transformers
    episodes=10,               # Number of runs
    seed_start=1,              # Starting seed (ensures reproducibility)
    output_dir="results/benchmarks"
)

# Output statistics
print(f"Mean Reward: {result['mean_reward']:.4f}")
print(f"Std Dev: {result['std_reward']:.4f}")

# Automatically generates:
# - results/benchmarks/adversary/adversary_ep1.mp4
# - results/benchmarks/adversary/adversary_ep1.json
# - ... (10 episodes total)
```

**Features**:
- ✅ Support all 9 environments
- ✅ Fixed seeds (1-20) ensure reproducibility
- ✅ Auto-calculate mean reward and standard deviation
- ✅ Complete logs (obs + action + thought + reward)
- ✅ Auto-save videos and JSON

### 2. Observation Parsers

Convert raw numerical vectors to semantic JSON format:

```python
from obs.parse_adv_obs import parse_adversary_obs

# Input: numpy array [10 dimensions]
obs_raw = np.array([-0.66, -1.32, ...])

# Output: structured JSON
obs_struct = parse_adversary_obs(obs_raw, 'agent_0', num_good=2)

# {
#   "role": "GOOD_AGENT",
#   "goal": {
#     "relative_position": [-0.66, -1.32],
#     "distance": 1.48,
#     "direction": "DOWN",
#     "description": "⭐ True goal is DOWN from you, distance 1.48"
#   },
#   "tactical_hint": "SCORER - You're closer to goal, charge forward!"
# }
```

### 3. LLM API Integration

Unified API interface supporting multiple LLMs:

```python
from utils_api import get_api_engine

# Remote APIs (auto-read keys from environment)
llm = get_api_engine("qwen")           # Alibaba Qwen
llm = get_api_engine("deepseek")       # DeepSeek
llm = get_api_engine("gpt")            # OpenAI GPT
llm = get_api_engine("gemini")         # Google Gemini

# Local models (no API keys needed)
llm = get_api_engine("transformers", model_path="Qwen/Qwen2.5-7B-Instruct")
llm = get_api_engine("ollama", model_name="qwen2.5:7b")
llm = get_api_engine("vllm", model_path="meta-llama/Llama-3-8B")

# Call
action, thought = llm.generate_action(system_prompt, user_prompt)
```

**Supported Providers**:
- ☁️ **Remote APIs**: OpenAI, DeepSeek, Qwen, Gemini
- 🖥️ **Local Models**: Transformers, Ollama, vLLM
- 🔐 **Key Management**: Via `.env` files or environment variables

### 4. Standardized Prompt Engineering Framework

Each environment has modular Prompt components (in `prompt/` directory):

```python
from prompt.prompt_for_adversary import (
    get_task_and_reward,
    get_action_and_response_format,
    get_physics_rules,
    get_navigation_hints
)

def build_full_prompt(agent, step, obs):
    return "\n\n".join([
        f"ENV: Adversary | AGENT: {agent} | STEP: {step}",
        get_task_and_reward(),
        get_physics_rules(),
        get_action_and_response_format(),
        get_navigation_hints(),
        format_obs(obs)  # from obs/parse_adv_obs.py
    ])
```

**Standardized Structure** (all environments follow):
1. `get_task_and_reward()` - Task objectives and reward mechanisms
2. `get_action_and_response_format()` - Action space and output format
3. `get_physics_rules()` - Physics rules and environment settings
4. `get_navigation_hints()` - Navigation hints and strategy suggestions

See: [docs/dev_notes/workflow_standardization.md](docs/dev_notes/workflow_standardization.md)

## 📊 Output Artifacts

### Single Run Output
Running a single environment (e.g., `python adv_API.py`) generates:
- **Video** (`adversary_demo.mp4`): Visual playback
- **Log** (`adversary_demo.json`): Complete trajectory

### Batch Benchmark Output
Running `benchmark_runner.py` generates:
```
results/benchmarks/adversary/
├── adversary_ep1.mp4
├── adversary_ep1.json
├── adversary_ep2.mp4
├── adversary_ep2.json
...
└── adversary_ep10.json
```

### JSON Log Format
Each record contains:
```json
{
  "step": 0,
  "agent": "agent_0",
  "obs": {...},              // Structured observation
  "action": [0.8, 0.2, ...], // Action vector
  "thought": "LLM response", // Thinking process
  "reward": 0.15             // Reward value
}
```

Appended summary:
```json
{
  "final_summary": true,
  "total_rewards": {"agent_0": 12.5, "agent_1": 8.3},
  "mean_reward": 10.4,
  "steps": 50
}
```

See: [docs/architecture/logging_system.md](docs/architecture/logging_system.md)

## 🔬 Research Applications

This project can be used for research on:

### Supported Experiments
- ✅ **Reproducible Experiments**: Fixed seeds 1-20 ensure consistent initial states
- ✅ **Model Comparison**: Unified interface to test different LLMs (Qwen/DeepSeek/GPT/Gemini)
- ✅ **Prompt Engineering**: Modular Prompts enable ablation studies
- ✅ **Performance Evaluation**: Auto-calculate mean rewards and standard deviation
- ✅ **Behavior Analysis**: Complete logs record decision-making process per step

### Research Directions
- 🔬 Feasibility of LLMs as multi-agent policies
- 🔬 Impact of prompt engineering on cooperative behavior
- 🔬 Zero-shot vs Few-shot multi-agent learning
- 🔬 Emergent natural language communication protocols
- 🔬 Performance-cost tradeoffs across model sizes

### Example Research Workflow
```python
# 1. Test different models with same seeds
for provider in ["qwen", "deepseek", "gpt"]:
    result = run_benchmark(
        env_name="adversary",
        provider=provider,
        episodes=20,
        seed_start=1  # Same initial state
    )
    print(f"{provider}: {result['mean_reward']:.3f}")

# 2. Hyperparameter search (temperature, prompt variants, etc.)
# 3. Analyze decision patterns in JSON logs
```

## 📚 Documentation Guide

**Complete Documentation Index**: [docs/README.md](docs/README.md) 📖

### 🚀 Getting Started
- [Quick Start](docs/getting_started/quickstart.md) - Get running in 5 minutes
- [Environment Setup](docs/getting_started/environment_setup.md) - Detailed setup guide
- [Dependency Management](docs/getting_started/dependency_management.md) - requirements.txt vs requirements.lock
- [Project Overview](docs/getting_started/overview.md) - Project architecture

### ⚙️ Configuration
- [API Key Configuration](docs/configuration/api_keys.md) - Secure API key management

### 🏗️ Architecture
- [Observation Space](docs/architecture/observation_space.md) - Parsing development
- [Logging System](docs/architecture/logging_system.md) - Log format specification
- [Model Usage Guide](docs/architecture/models.md) - Supported LLMs

### 🧪 Experiments
- [Reproducible Experiments](docs/experiments/reproducibility.md) - Seed fixing guide
- [Running Benchmarks](docs/experiments/running_benchmarks.md) - Batch testing workflow
- [Benchmark Evaluation](docs/experiments/benchmark_review.md) - Multi-role log analysis

### 🛠️ Developer Notes
- [Work Summary](docs/dev_notes/work_summary.md) - v1.0 development history
- [Workflow Standardization](docs/dev_notes/workflow_standardization.md) - Design principles
- [API Key Refactor](docs/dev_notes/api_keys_refactor.md) - Migration log

## 🛠️ Development Status

### Completed ✅ (Version 1.0)
- [x] **9 Complete Environments** (spread, adversary, tag, push, crypto, reference, speaker_listener, world_comm, simple)
- [x] **Unified LLM API Interface** (Remote: qwen/deepseek/gpt/gemini; Local: transformers/ollama/vllm)
- [x] **Observation Parsers** (9 environments with standardized JSON output)
- [x] **Prompt Standardization** (4 modular functions × 9 environments)
- [x] **Logging System** (obs + action + thought + reward + final_summary)
- [x] **Benchmark Framework** (Batch testing + statistical analysis)
- [x] **Seed Mechanism** (1-20 reproducible experiments)
- [x] **API Key Management** (.env files + interactive setup script)
- [x] **Documentation** (15+ Markdown documents)
- [x] **Video Recording** (Auto-generate mp4 per episode)

### Test Coverage ✅
- [x] All 9 environments run independently
- [x] Benchmark framework tests all environments
- [x] Seed fixing verified
- [x] Log format unified and complete
- [x] API key security management

### Planned 📅 (Version 1.1+)
- [ ] Performance benchmark database
- [ ] Interactive visualization Dashboard
- [ ] Few-shot example library
- [ ] Multi-process parallel testing
- [ ] More local model support

## 🤝 Contributing

Contributions welcome! Steps:

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

**Contribution Areas**:
- Implement parsers for new environments
- Improve Prompt engineering templates
- Add new evaluation metrics
- Enhance documentation and examples

## 📄 License

This project is licensed under MIT License - see [LICENSE](LICENSE) file

## 🙏 Acknowledgments

- [PettingZoo](https://pettingzoo.farama.org/) - Multi-agent environment library
- [OpenAI](https://openai.com/) - LLM APIs
- All contributors

## 📧 Contact

- **Author**: HuangShengZeBlueSky
- **Repository**: https://github.com/HuangShengZeBlueSky/MPE_muiltiagent_benchmark
- **Issues**: [GitHub Issues](https://github.com/HuangShengZeBlueSky/MPE_muiltiagent_benchmark/issues)

## ⭐ Star History

If this project helps you, please give it a Star ⭐!

---

**Last Updated**: 2026-01-26  
**Version**: 1.0.0 - All core features complete  
**Status**: ✅ Production Ready

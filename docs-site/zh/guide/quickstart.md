# 快速开始

## 环境要求

- Python ≥ 3.8
- Node.js ≥ 16（仅文档站需要）
- 至少一个 LLM API Key 或本地模型

## 1. 安装依赖

```bash
# 克隆仓库
git clone https://github.com/your-repo/MPE_muiltiagent_benchmark.git
cd MPE_muiltiagent_benchmark

# 安装 Python 依赖
pip install -r requirements.txt
```

核心依赖列表：

| 包名 | 用途 |
|:-----|:-----|
| `pettingzoo[mpe]` | MPE 多智能体环境 |
| `openai` | OpenAI / DeepSeek / Qwen API 调用 |
| `google-generativeai` | Google Gemini API |
| `numpy` | 数组运算 |
| `imageio[ffmpeg]` | 视频录制 |
| `python-dotenv` | .env 文件加载 |

可选依赖（本地模型）：

| 包名 | 用途 |
|:-----|:-----|
| `transformers` + `torch` | HuggingFace 本地推理 |
| `ollama` | Ollama 本地推理 |
| `vllm` | vLLM 加速推理 |

## 2. 配置 API Key

### 方式 A: .env 文件（推荐）

在项目根目录创建 `.env` 文件：

```env
# 至少配置一个即可
DEEPSEEK_API_KEY=sk-your-key-here
QWEN_API_KEY=sk-your-key-here
OPENAI_API_KEY=sk-your-key-here
GOOGLE_API_KEY=your-key-here
```

### 方式 B: 环境变量

```bash
# Linux / macOS
export DEEPSEEK_API_KEY="sk-your-key-here"

# Windows PowerShell
$env:DEEPSEEK_API_KEY = "sk-your-key-here"

# Windows CMD
set DEEPSEEK_API_KEY=sk-your-key-here
```

### 方式 C: 运行时传参

```python
from utils_api import get_api_engine
engine = get_api_engine(
    "deepseek",
    api_key="sk-your-key-here",
    base_url="https://api.deepseek.com"
)
```

## 3. 运行你的第一个游戏

### Simple — 最简单的入门环境

```bash
python simple.py
```

这将会：
1. 创建一个 `simple_v3` 环境（1 个智能体 + 1 个地标）
2. 使用默认 LLM（通常为 Qwen）进行 25 步推理
3. 在当前目录生成：
   - `simple_demo.mp4` — 游戏录像
   - `simple_demo.json` — 每步的详细日志

### 更多游戏

```bash
# 协作覆盖 — 3 个智能体需要覆盖 3 个地标
python spread_API.py

# 追逐捕获 — 3 个捕食者 vs 1 个猎物
python tag_API.py

# 欺骗推理 — Good Agents 欺骗 Adversary
python adv_API.py

# 加密通信 — Alice 加密, Bob 解密, Eve 窃听
python crypto.py

# 单向通信 — Speaker 传目标, Listener 导航
python speaker_listener.py

# 大规模协调 — Leader 广播猎物坐标
python world_comm.py
```

## 4. 查看输出

### MP4 视频

使用任意视频播放器打开生成的 `.mp4` 文件即可观看游戏录像。

### JSON 日志

日志文件包含每一步的完整记录：

```json
[
  {
    "step": 0,
    "agent": "agent_0",
    "observation": {
      "vel": [0.0, 0.0],
      "landmark_rel": [-0.42, 0.67]
    },
    "action": [0.0, 0.7, 0.0, 0.0, 0.6],
    "thought": "Landmark is to the left and above. Applying left and up thrust.",
    "reward": -0.65
  },
  {
    "step": 1,
    "agent": "agent_0",
    "observation": {
      "vel": [-0.35, 0.30],
      "landmark_rel": [-0.25, 0.40]
    },
    "action": [0.0, 0.5, 0.0, 0.0, 0.4],
    "thought": "Getting closer. Reducing thrust to avoid overshoot.",
    "reward": -0.22
  }
]
```

::: tip 日志字段说明
- `step`: 当前步数
- `agent`: 智能体 ID
- `observation`: 解析后的结构化观测
- `action`: LLM 输出的 5 维动作向量
- `thought`: LLM 的思维链（notes 字段）
- `reward`: 当前步的奖励值
:::

## 5. 使用本地模型（可选）

### Ollama

```bash
# 1. 安装 Ollama: https://ollama.ai
# 2. 下载模型
ollama pull qwen2.5:7b

# 3. 修改游戏脚本中的 provider 参数（或直接使用 benchmark_runner）
python -c "
from benchmark_runner import run_benchmark
result = run_benchmark('simple', 'ollama', episodes=1)
print(f'Mean Reward: {result[\"mean_reward\"]:.4f}')
"
```

### Transformers

```python
from benchmark_runner import run_benchmark
result = run_benchmark(
    env_name="simple",
    provider="transformers",
    episodes=1,
    model_path="Qwen/Qwen2.5-7B-Instruct",
    device="cuda"  # 或 "cpu"
)
```

## 下一步

- 🎮 查看 [游戏环境总览](/zh/games/) 了解全部 9 个环境
- 🧠 查看 [提示词工程](/zh/advanced/prompt-engineering) 了解提示词设计
- 📊 查看 [Benchmark 评测](/zh/advanced/benchmark) 了解批量评测

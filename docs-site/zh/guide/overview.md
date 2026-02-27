# 项目概述

## 什么是 MPE Multi-Agent Benchmark？

MPE Multi-Agent Benchmark 是一个基于 **PettingZoo MPE (Multi-agent Particle Environment)** 的大语言模型多智能体基准测试套件。它将 LLM 直接作为智能体的「决策大脑」，在 9 个经典的多智能体博弈场景中进行 **零样本 (zero-shot)** 推理决策。

## 核心思想

传统强化学习 (RL) 中，智能体的策略由神经网络学习得到：

```
观测 (numpy) → 神经网络策略 → 动作 (numpy)
```

在本项目中，我们将这一过程替换为：

```
观测 (numpy) → 结构化解析 → 自然语言提示词 → LLM 推理 → JSON 动作
```

这使得我们可以直接评估 LLM 的：
- **空间推理能力**：理解相对坐标、距离、方向
- **博弈决策能力**：在对抗和合作场景中做出合理决策
- **通信协调能力**：通过自然语言理解通信协议
- **策略规划能力**：制定长期策略并执行

## 为什么选择 MPE？

MPE 是多智能体研究中最经典的基准环境之一，具有以下优势：

| 特性 | 说明 |
|:-----|:-----|
| **经典性** | MADDPG 等里程碑论文使用的原始环境 |
| **多样性** | 9 个场景覆盖协作、对抗、通信、欺骗等范式 |
| **简洁性** | 2D 连续空间，4-5 维动作，便于 LLM 理解 |
| **可视化** | 内置渲染，自动生成 MP4 录像 |
| **标准化** | PettingZoo 封装，API 统一 |

## 支持的 LLM 后端

本项目通过 `utils_api.py` 中的 `APIInferencer` 类提供统一的推理接口，支持以下后端：

### 远程 API

| 提供商 | Provider 名 | 环境变量 |
|:-------|:----------:|:---------|
| OpenAI (GPT-4o 等) | `openai` | `OPENAI_API_KEY` |
| DeepSeek | `deepseek` | `DEEPSEEK_API_KEY` |
| 通义千问 (Qwen) | `qwen` | `QWEN_API_KEY` |
| Google Gemini | `gemini` | `GOOGLE_API_KEY` |

### 本地模型

| 框架 | Provider 名 | 配置参数 |
|:-----|:----------:|:---------|
| Ollama | `ollama` | `model_name` (如 `qwen2.5:7b`) |
| Transformers | `transformers` | `model_path`, `device` |
| vLLM | `vllm` | `model_path` |

## 项目特色

### 📝 模块化提示词系统

每个游戏的提示词被精心拆分为 4 个标准模块，存放在 `prompt/` 目录下：

1. **`get_task_and_reward()`** — 游戏规则与奖励函数
2. **`get_physics_rules()`** — 物理引擎参数
3. **`get_action_and_response_format()`** — 动作空间与 JSON 输出格式
4. **`get_navigation_hints()`** — 导航策略与 few-shot 示例

这种模块化设计使得：
- 新增游戏时只需实现这 4 个函数
- 可以独立地优化每个模块的提示词
- 复用跨游戏的通用组件（如物理规则、动作格式）

### 📊 完整的实验记录

每次运行都会自动保存：

- **MP4 视频**：完整的游戏录像，帧率可调
- **JSON 日志**：每一步的完整记录

```json
{
  "step": 5,
  "agent": "agent_0",
  "observation": { "vel": [0.1, -0.2], "landmark_rel": [-0.3, 0.5] },
  "action": [0.0, 0.8, 0.0, 0.0, 0.5],
  "thought": "Target is to the left and above, applying left and up thrust",
  "reward": -0.34
}
```

### 🔄 批量评测系统

`benchmark_runner.py` 提供了标准化的评测流程：
- 支持多轮次运行（N episodes），每轮使用不同种子
- 自动计算均值和标准差
- 生成结构化的评测报告

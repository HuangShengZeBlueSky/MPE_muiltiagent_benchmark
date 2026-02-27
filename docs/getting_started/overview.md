# MPE Multi-Agent Benchmark 项目概览

## 📋 项目简介

本项目是一个**多智能体强化学习基准测试套件**，基于 PettingZoo 的 MPE (Multi-agent Particle Environment) 环境，集成了 LLM (大语言模型) API 来驱动智能体决策。项目涵盖了多种经典的多智能体协作与对抗场景。

## 🎯 核心目标

1. **标准化测试框架**：为不同的 MPE 环境提供统一的 API 接口
2. **LLM 智能体集成**：支持通过自然语言 prompt 驱动智能体行为
3. **多场景覆盖**：包含协作、对抗、通信等多种多智能体交互模式
4. **可重复性**：提供完整的观测解析、prompt 工程和评估流程

## 🏗️ 项目架构

### 1. 核心模块

#### 1.1 通用工具层 (`utils_api.py`)
- **APIInferencer 类**：统一的 LLM API 调用接口
  - 支持 OpenAI (GPT)、DeepSeek、Qwen、Google Gemini 等
  - 标准化的输入输出处理
  - 错误处理和重试机制
- **辅助函数**：
  - `get_unique_filename()`: 防止文件覆盖
  - `get_api_engine()`: API 引擎工厂函数

#### 1.2 环境特定实现文件
每个文件对应一个 MPE 环境，包含完整的 pipeline：

| 文件名 | 环境 | 核心任务 |
|--------|------|---------|
| `spread_API.py` | Simple Spread | 协作覆盖地标 (N agents → N landmarks) |
| `adv_API.py` | Simple Adversary | 对抗推理 (好智能体保护目标 vs 敌对智能体渗透) |
| `tag_API.py` | Simple Tag | 追逐逃跑 (捕食者围捕 vs 猎物躲避) |
| `push.py` | Simple Push | 物理推理 (推动物体到目标) |
| `crypto.py` | Simple Crypto | 密码学游戏 (Alice/Bob 加密通信 vs Eve 窃听) |
| `reference.py` | Simple Reference | 引用游戏 (通过颜色描述协作导航) |
| `speaker_listener.py` | Simple Speaker Listener | 通信协作 (speaker 编码目标 → listener 执行) |
| `world_comm.py` | Simple World Comm | 复杂世界通信 (多角色分工协作) |

### 2. 观测解析模块 (`obs/` 目录)

包含验证和测试脚本，用于：
- 分析环境观测空间的维度和语义
- 验证观测向量的正确性
- 为 prompt 工程提供精确的语义映射

## 🔧 技术栈

### 核心依赖
- **numpy** (≥1.24.0): 数值计算和数据处理
- **pettingzoo[mpe]** (≥1.24.0): 多智能体环境
- **imageio** (≥2.31.0): 视频渲染和导出
- **openai** (≥1.0.0): OpenAI API 客户端
- **google-generativeai** (≥0.3.0): Google Gemini API

### 开发工具
- **Python** ≥3.8
- **uv**: 现代化的 Python 包管理器 (推荐使用 `pyproject.toml`)
- **pytest**: 单元测试框架
- **black**: 代码格式化工具

## 📊 支持的环境列表

### 1. Simple Spread (协作)
- **智能体数量**: N (可配置，通常 3)
- **任务**: 所有智能体分别占据 N 个地标，避免碰撞
- **关键机制**: 全局奖励 (团队协作) + 局部惩罚 (碰撞)

### 2. Simple Adversary (对抗推理)
- **智能体**: 1 敌对 + N 友好智能体
- **任务**: 
  - 友方：保护隐藏的目标地标，使用欺骗策略
  - 敌方：观察友方行为，推理真实目标
- **核心能力**: 意图推理、欺骗策略

### 3. Simple Tag (追逐逃跑)
- **智能体**: 多个捕食者 + 1 猎物
- **任务**:
  - 捕食者：围捕猎物 (速度劣势，需协作)
  - 猎物：利用障碍物躲避
- **核心能力**: 路径规划、围捕策略

### 4. Simple Push (物理推理)
- **智能体**: 1 对抗智能体 + 1 友好智能体
- **任务**: 友好智能体需推动地标到目标位置
- **核心能力**: 物理操作、目标导向控制

### 5. Simple Crypto (密码学)
- **智能体**: Alice (发送方) + Bob (接收方) + Eve (窃听者)
- **任务**:
  - Alice: 加密消息
  - Bob: 使用共享密钥解密
  - Eve: 尝试破解密文
- **核心能力**: 编码策略、密钥管理

### 6. Simple Reference (引用理解)
- **智能体**: 2 个协作智能体
- **任务**: 通过颜色描述协作导航到正确地标
- **核心能力**: 语义理解、引用消解

### 7. Simple Speaker Listener (通信)
- **智能体**: Speaker (说话者) + Listener (听众)
- **任务**:
  - Speaker: 观察目标地标，发送编码信息
  - Listener: 根据信息导航到目标
- **核心能力**: 信息编码、通信协议

### 8. Simple World Comm (复杂世界)
- **智能体**: 多个带有不同角色的智能体
- **任务**: 在复杂环境中通过通信协作 (食物、森林、障碍物)
- **核心能力**: 角色理解、多目标规划

## 🚀 使用指南

### 安装依赖

#### 方法 1: 使用 uv (推荐)
```bash
# 安装 uv (如果尚未安装)
curl -LsSf https://astral.sh/uv/install.sh | sh

# 创建虚拟环境并安装依赖
uv venv
source .venv/bin/activate  # Linux/Mac
# .venv\Scripts\activate   # Windows

uv pip install -e .
```

#### 方法 2: 使用 pip
```bash
pip install -r requirements.txt
```

### 配置 API 密钥

需要设置环境变量：
```bash
# OpenAI / DeepSeek
export OPENAI_API_KEY="your-api-key"
export OPENAI_BASE_URL="https://api.deepseek.com"  # 可选

# Google Gemini
export GEMINI_API_KEY="your-api-key"
```

### 运行示例

```python
# 以 Simple Spread 为例
python spread_API.py

# 其他环境类似
python adv_API.py
python tag_API.py
# ...
```

## 📝 代码设计模式

### 每个环境文件的标准结构：

```python
# 1. 导入依赖
import numpy as np
import imageio
from utils_api import get_api_engine, get_unique_filename
from pettingzoo.mpe import environment_name

# 2. 观测解析器
def parse_obs(obs: np.ndarray, agent_id: str) -> Dict[str, Any]:
    """将原始观测向量转换为结构化语义信息"""
    pass

# 3. Prompt 工程模块
def get_task_goal() -> str:
    """任务目标描述"""
    pass

def get_reward_info() -> str:
    """奖励函数说明"""
    pass

def get_action_space() -> str:
    """动作空间定义"""
    pass

def build_full_prompt(...) -> str:
    """组装完整的 LLM prompt"""
    pass

# 4. 动作解析器
def parse_action(response: str) -> np.ndarray:
    """从 LLM 文本输出中提取动作向量"""
    pass

# 5. 主评估循环
def run_episode(...):
    """运行完整 episode，返回性能指标"""
    pass

# 6. 视频导出 (可选)
def export_video(...):
    """将 episode 导出为 MP4"""
    pass
```

## 🎯 核心设计理念

### 1. 模块化 Prompt 工程
- 将 prompt 拆分为多个独立组件：
  - 任务描述 (Task)
  - 观测语义 (Observation Semantics)
  - 奖励函数 (Reward)
  - 动作空间 (Action Space)
  - 历史信息 (History)
- 便于调试和消融实验

### 2. 观测语义化
- 将低维数值向量 (如 18 维) 映射为高层语义：
  - 位置 → "距离地标 A: 0.5m, 方向: 东北"
  - 速度 → "当前速度: 0.2 m/s"
  - 颜色 → "RGB(1.0, 0.0, 0.0) → 红色地标"

### 3. 统一 API 接口
- `APIInferencer` 类屏蔽不同 LLM 提供商的差异
- 支持快速切换模型进行对比实验

### 4. 可重复性保证
- 所有观测解析逻辑都经过验证 (`obs/` 中的测试脚本)
- 记录每步的输入输出 (JSON log)
- 固定随机种子

## 📦 输出产物

运行环境后会生成：
1. **JSON 日志** (`*_log.json`): 完整的 episode 轨迹
   - 每步的观测、动作、奖励
   - LLM 的原始响应
   - 解析后的动作
2. **视频文件** (`*.mp4`): 可视化的 episode 回放
3. **性能指标**: 总奖励、成功率等

## 🔬 研究方向

本项目可用于研究：
1. **LLM 作为多智能体策略的可行性**
2. **Prompt 工程对协作行为的影响**
3. **不同 LLM 在推理/协作任务上的对比**
4. **零样本 vs Few-shot 多智能体学习**
5. **自然语言通信协议的涌现**

## 📚 参考资源

- [PettingZoo 文档](https://pettingzoo.farama.org/)
- [MPE 环境说明](https://pettingzoo.farama.org/environments/mpe/)
- [OpenAI API 文档](https://platform.openai.com/docs/)
- [Google Gemini API 文档](https://ai.google.dev/docs)

## 🛠️ 开发计划

### 已完成 ✅
- [x] 8 个 MPE 环境的完整实现
- [x] 统一的 API 调用接口
- [x] 观测语义化解析器
- [x] 模块化 Prompt 工程框架
- [x] 视频导出功能
- [x] JSON 日志记录

### 进行中 🚧
- [ ] 批量评估脚本 (多个 episode 平均性能)
- [ ] Few-shot 示例库
- [ ] 更多 LLM 后端支持 (Claude, LLaMA)

### 计划中 📅
- [ ] 自动化超参数调优
- [ ] 多智能体通信协议分析工具
- [ ] 交互式可视化 Dashboard
- [ ] 基准测试结果数据库

## 🤝 贡献指南

欢迎提交 Issue 和 Pull Request！

贡献方向：
1. 添加新的 MPE 环境支持
2. 改进 Prompt 工程模板
3. 优化观测解析器
4. 添加新的评估指标
5. 修复 Bug

## 📄 许可证

MIT License

---

**作者**: HuangShengZeBlueSky  
**仓库**: [MPE_muiltiagent_benchmark](https://github.com/HuangShengZeBlueSky/MPE_muiltiagent_benchmark)  
**最后更新**: 2026-01-24

# 提示词工程

## 模块化设计

本项目的提示词系统遵循**标准化模块设计**，每个游戏的提示词由 4 个独立函数组成，存放在 `prompt/prompt_for_xxx.py` 中。

```
prompt/
├── prompt_for_simple.py           # 4 个标准函数
├── prompt_for_spread.py
├── prompt_for_adv.py
├── prompt_for_push.py
├── prompt_for_tag.py
├── prompt_for_crypto.py
├── prompt_for_reference.py
├── prompt_for_speaker_listener.py
└── prompt_for_world_comm.py
```

## 四大标准模块

### 模块 A: 任务与奖励 — `get_task_and_reward()`

**作用**: 告诉 LLM "你在玩什么游戏，怎么得分"

**典型内容**:
- 角色定义（如 Predator / Prey）
- 游戏目标
- 奖励公式（量化指标）
- 胜利/失败条件

**示例** (Simple):

```python
def get_task_and_reward() -> str:
    return (
        "TASK / GOAL:\n"
        "- Single agent must move to the single landmark.\n\n"
        "REWARD (from source):\n"
        "- reward = -||agent_pos - landmark_pos||^2 = -(dx^2 + dy^2).\n"
        "- Maximize reward by driving dx, dy toward 0.\n"
    )
```

**角色参数化示例** (Tag):

```python
def get_task_and_reward(is_predator: bool) -> str:
    if is_predator:
        return (
            "TASK: HUNTING (You are a PREDATOR / WOLF)\n"
            "- Goal: Catch the Prey (Green).\n"
            "REWARD: +10.0 for hitting the prey; -0.1 per step distance."
        )
    return (
        "TASK: SURVIVAL (You are the PREY / SHEEP)\n"
        "- Goal: Run away from Predators (Red).\n"
        "REWARD: -10.0 if caught; +0.1 per safe step."
    )
```

### 模块 B: 物理规则 — `get_physics_rules()`

**作用**: 描述物理引擎参数，帮助 LLM 理解动力学

**核心参数**:

| 参数 | 值 | 含义 |
|:-----|:--:|:-----|
| `dt` | 0.1 | 时间步长 |
| `damping` | 0.25 | 阻尼系数 (每步速度衰减 25%) |
| `mass` | 1.0 | 默认质量 |
| `sensitivity` | 5.0 | 动作到力的映射 |

**更新顺序**:
```
(1) 位置更新: p ← p + v × dt    (使用旧速度)
(2) 阻尼应用: v ← v × (1 - damping)
(3) 推力应用: v ← v + (F / mass) × dt
```

### 模块 C: 动作格式 — `get_action_and_response_format()`

**作用**: 定义 LLM 的输出格式，包含 few-shot 示例

**标准输出**:

```json
{"action": [a0, a1, a2, a3, a4], "notes": "Short Strategy"}
```

**Few-shot 示例**:

| 场景 | 推荐动作 |
|:-----|:---------|
| 目标在左上 (`dx<0, dy>0`) | `[0, 0.8, 0, 0, 0.8]` |
| 目标在右下 (`dx>0, dy<0`) | `[0, 0, 0.9, 0.9, 0]` |
| 接近目标 (`dist<0.2`) | `[0, 0, 0, 0, 0]` (刹车) |
| 接近边界 (`|x|>0.9`) | 向中心方向推 |

### 模块 D: 导航策略 — `get_navigation_hints()`

**作用**: 提供角色特定的策略指导

**通用内容**:
- 相对坐标语义解释
- 动作互斥规则
- 边界处理 few-shot
- 制动 few-shot

**角色特定内容**:
- Predator: 追击策略、预判拦截
- Prey: 逃跑策略、边界警告
- Good Agent: 欺骗策略
- Adversary: 推理策略

## 完整提示词组装流程

以 `spread_API.py` 为例，每一步的提示词组装：

```python
def user_prompt(agent_id, step, obs_struct):
    # 1. 基础信息
    prompt = f"Step {step}, You are {agent_id}.\n"
    prompt += f"Observation:\n{json.dumps(obs_struct, indent=2)}\n\n"
    
    # 2. 拼接 4 大模块
    prompt += get_task_and_reward(num_agents=3, local_ratio=0.5) + "\n"
    prompt += get_physics_rules() + "\n"
    prompt += get_action_and_response_format() + "\n"
    prompt += get_navigation_hints() + "\n"
    
    return prompt
```

## System Prompt

System Prompt 通常很简短，定义 LLM 的角色：

```python
system_prompt = (
    "You are an expert game-playing AI agent in a 2D physics environment. "
    "Analyze your observation carefully and output a precise action "
    "in the specified JSON format."
)
```

## 提示词设计最佳实践

### 1. 明确的坐标语义

```
OBS RELATIVE COORD: obs gives (other - you).
Example: other at (0,1), you at (1,0) => relative = [-1, 1]
```

始终在提示词中解释"相对坐标"的含义，避免 LLM 混淆方向。

### 2. 互斥动作规则

```
NEVER output opposing actions like [0, 0.6, 0.2, ...]
(Left & Right both active). This wastes force.
One side MUST be 0.0.
```

### 3. 边界警告

```
BOUNDARY WARNING: Stay within [-1.0, 1.0].
If |x| or |y| > 0.9, thrust back toward center.
```

### 4. 量化奖励公式

提供精确的数学公式而非模糊描述：

```
# ✅ 好的
reward = -||agent - landmark||^2 = -(dx^2 + dy^2)

# ❌ 不好的
reward: you get more points when closer to the landmark
```

## 自定义提示词

如需为新游戏创建提示词，只需在 `prompt/` 目录创建新文件并实现这 4 个函数：

```python
# prompt/prompt_for_my_game.py

__all__ = [
    "get_task_and_reward",
    "get_action_and_response_format",
    "get_physics_rules",
    "get_navigation_hints",
]

def get_task_and_reward(**kwargs) -> str:
    return "..."

def get_physics_rules(**kwargs) -> str:
    return "..."

def get_action_and_response_format(**kwargs) -> str:
    return "..."

def get_navigation_hints(**kwargs) -> str:
    return "..."
```

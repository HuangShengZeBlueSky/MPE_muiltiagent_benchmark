# Speaker-Listener — 单向通信

::: info 环境信息
- **PettingZoo 名称**: `simple_speaker_listener_v4`
- **智能体**: 1 Speaker + 1 Listener
- **地标数量**: 3
- **类型**: 单向通信 + 语义对齐
:::

## 游戏目标

经典的**信号对齐**环境：

### Speaker (说者)
- **看到**: 目标地标的 one-hot 向量（如 `[0, 1, 0]` 表示地标 1）
- **不能移动**: 只输出 3 维通信信号
- **任务**: 将目标信息编码为信号，让 Listener 理解

### Listener (听者)  
- **看到**: 3 个地标的相对位置 + Speaker 发来的 3 维信号
- **不能通信**: 只输出运动动作
- **任务**: 根据信号推断目标，导航到正确地标

## 观测空间

### Speaker 观测

| 字段 | 维度 | 含义 |
|:-----|:----:|:-----|
| `goal_vector` | 3 | 目标地标 one-hot 编码 |
| `target_landmark_id` | 1 | 目标地标 ID (0/1/2) |

### Listener 观测

| 字段 | 维度 | 含义 |
|:-----|:----:|:-----|
| `vel` | 2 | 自身速度 |
| `landmarks[]` | 3 组 | 3 个地标相对位置 + 距离 + 方向 |
| `comm_vector` | 3 | Speaker 传来的通信信号 |
| `heard_id` | 1 | 推断的目标 ID (按最大分量) |

### 观测示例

::: tip Speaker 观测
```json
{
  "goal_vector": [0, 0, 1],
  "target_landmark_id": 2
}
```
→ 目标是地标 2，Speaker 需要输出信号让 Listener 去地标 2
:::

::: tip Listener 观测
```json
{
  "vel": [0.0, 0.0],
  "landmark_0": {"rel": [-0.3, 0.5], "dist": 0.58, "dir": "LEFT/UP"},
  "landmark_1": {"rel": [0.4, -0.2], "dist": 0.45, "dir": "RIGHT/DOWN"},
  "landmark_2": {"rel": [-0.1, -0.7], "dist": 0.71, "dir": "DOWN"},
  "comm_vector": [0.2, 0.1, 0.9],
  "heard_id": 2
}
```
→ 信号第 3 维最大，推断目标为地标 2
:::

## 动作空间

| 角色 | 动作维度 | 含义 |
|:----:|:--------:|:-----|
| Speaker | 3 | 通信信号 `[s0, s1, s2]`，各维 ∈ [0, 1] |
| Listener | 5 | 运动力 `[no_op, left, right, down, up]` |

## 奖励函数

两个智能体共享奖励，基于 Listener 到目标地标的距离：

```
reward = -dist(listener, target_landmark)
```

## 提示词策略

### Speaker 策略
```
将 one-hot 目标直接或经过简单变换输出为通信信号。
最简单方案: 直接输出 goal_vector 作为 action。

例如: 目标是地标 1 → action = [0, 1, 0]
```

### Listener 策略
```
1. 分析 comm_vector：找到最大分量对应的地标 ID
2. 导航到对应地标
3. 利用 heard_id 作为辅助线索
```

## 运行方式

```bash
python speaker_listener.py
```

# Spread — 协作覆盖

::: info 环境信息
- **PettingZoo 名称**: `simple_spread_v3`
- **智能体数量**: N (默认 3)
- **地标数量**: N (默认 3)
- **类型**: 纯协作 (Cooperative)
:::

## 游戏目标

N 个智能体需要**协作覆盖** N 个地标：
- 每个地标至少有一个智能体靠近
- 同时**避免碰撞**（碰撞有惩罚）
- 需要隐式协调（无专用通信通道）

这是评测 LLM **多智能体协调能力**的核心环境。

## 观测空间

每个智能体的观测经 `parse_spread_obs()` 解析后：

| 字段 | 维度 | 含义 |
|:-----|:----:|:-----|
| `self_vel` | 2 | 自身速度 `[vx, vy]` |
| `self_pos` | 2 | 自身绝对位置 `[x, y]` |
| `landmark_rel_0..N-1` | 2×N | 各地标相对位置 `(landmark - self)` |
| `other_agent_rel_0..N-2` | 2×(N-1) | 其他智能体相对位置 |
| `comm_0..N-2` | 2×(N-1) | 其他智能体通信信号（通常为 0） |

### 观测解析代码

```python
# obs/parse_spread_obs.py
def parse_spread_obs(obs, num_agents=3):
    idx = 0
    result = {}
    result["self_vel"] = obs[idx:idx+2].tolist(); idx += 2
    result["self_pos"] = obs[idx:idx+2].tolist(); idx += 2
    
    for i in range(num_agents):
        result[f"landmark_rel_{i}"] = obs[idx:idx+2].tolist(); idx += 2
    
    for i in range(num_agents - 1):
        result[f"other_agent_rel_{i}"] = obs[idx:idx+2].tolist(); idx += 2
    
    for i in range(num_agents - 1):
        result[f"comm_{i}"] = obs[idx:idx+2].tolist(); idx += 2
    
    return result
```

## 奖励函数

Spread 使用**混合奖励**机制：

### 全局奖励 (Global Reward)

```
global = -Σ_landmark min_agent ‖agent - landmark‖
```

对每个地标，找到**离它最近的智能体**的距离，然后求和取负。全局奖励由所有智能体共享。

### 局部奖励 (Local Reward)

```
local = -1.0  (每次碰撞)
```

碰撞判定：`dist(agent_i, agent_j) < size_i + size_j`，其中 `size = 0.15`。

### 总奖励

```
total = global × (1 - local_ratio) + local × local_ratio
```

`local_ratio` 默认为 `0.5`，平衡全局覆盖和局部避碰。

::: warning 碰撞惩罚
碰撞区域：`dist < 0.30`（两个 size=0.15 的智能体）  
危险区域：`dist < 0.35`（接近碰撞，需立即规避）
:::

## 提示词中的策略指导

### 坐标估算技巧

提示词中教导 LLM 估算其他智能体到地标的距离：

```
other_to_landmark = landmark_rel - other_agent_rel
```

这让智能体可以推断"哪个队友更适合去哪个地标"。

### 互斥动作规则

```
- 不要同时输出对立力 (如 left=0.6, right=0.2)
- 一个轴上只有一个方向 > 0，另一个必须为 0.0
```

### 到达稳定规则

```
- 接近目标 (dist < 0.2) 时，检查自身速度
- 如果速度过快，设为 0.0 或极小值 (0.05) 滑行减速
- 不要在靠近目标时全力推进 (1.0)！
```

## 动作空间

标准 5 维连续动作 `[no_op, left, right, down, up]`，各维取值 [0, 1]。

## LLM 提示词完整结构

```python
def user_prompt(agent_id, step, obs_struct):
    prompt = f"Step {step}, You are {agent_id}.\n"
    prompt += f"Observation: {json.dumps(obs_struct)}\n"
    prompt += get_task_and_reward(num_agents=3, local_ratio=0.5)
    prompt += get_physics_rules()
    prompt += get_action_and_response_format()
    prompt += get_navigation_hints()
    return prompt
```

## 运行方式

```bash
python spread_API.py
```

<!-- 📊 实验结果占位 -->

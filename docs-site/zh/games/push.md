# Push — 对抗推挤

::: info 环境信息
- **PettingZoo 名称**: `simple_push_v3`
- **智能体**: 1 Adversary (Blocker) + 1 Good Agent (Runner)
- **地标数量**: 2 (1 真实 + 1 假目标)
- **类型**: 物理对抗 + 信息不对称
:::

## 游戏目标

### Good Agent (Runner)
- **知道**哪个地标是真实目标
- **目标**: 冲到真实目标地标
- **挑战**: 避免被 Adversary 物理推挤偏离路线

### Adversary (Blocker)  
- **不知道**哪个地标是真实目标
- **目标**: 阻止 Good Agent 到达目标
- **策略**: 从 Good Agent 的运动方向推断目标，然后卡位阻挡
- **优势**: 质量比 Good Agent 大，碰撞时能推开对方

## 观测空间

### Good Agent 观测

| 字段 | 含义 |
|:-----|:-----|
| `vel`, `speed` | 自身速度和速率 |
| `goal_rel`, `goal_dist` | 真实目标相对位置及距离 |
| `fake_rel`, `fake_dist` | 假地标相对位置及距离 |
| `opponent_rel`, `opponent_dist` | 对手相对位置及距离 |

### Adversary 观测

| 字段 | 含义 |
|:-----|:-----|
| `vel`, `speed` | 自身速度和速率 |
| `landmark_0`, `landmark_1` | 两个地标的相对位置（不知真假） |
| `opponent_rel`, `opponent_dist` | Good Agent 的相对位置 |

## 奖励函数

| 角色 | 奖励 |
|:----:|:-----|
| Good Agent | 越接近真实目标，奖励越高；碰撞和延迟有惩罚 |
| Adversary | Good Agent 越远离目标，奖励越高 |

## 物理特性

::: warning 质量不对称
- **Adversary 质量更大**：碰撞时可以推开轻量的 Good Agent
- **Good Agent 质量更小**：碰撞时会被推开，需要绕行或快速冲刺
:::

## 策略

### Good Agent 策略
```
- 全速奔向真实目标，忽略假地标
- 如果 Adversary 挡路，侧步绕行后重新冲向目标
- 接近目标时减速，避免过冲
```

### Adversary 策略
```
- 观察 Good Agent 的运动方向，推断哪个是真目标
- 提前卡位：站在 Good Agent 和疑似目标之间
- 利用质量优势推开 Good Agent
- 如果判断失误，立即切换阻挡另一个地标
```

## 运行方式

```bash
python push.py
```

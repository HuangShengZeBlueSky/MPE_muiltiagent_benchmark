# Adversary — 欺骗与推理

::: info 环境信息
- **PettingZoo 名称**: `simple_adversary_v3`
- **智能体**: 1 Adversary (红色) + N Good Agents (绿色, 默认 2)
- **地标数量**: N+1 (默认 3)
- **类型**: 对抗 + 信息不对称
:::

<video controls width="100%" style="max-width: 640px; border-radius: 8px;">
  <source src="/MPE_muiltiagent_benchmark/videos/adversary_ep1.mp4" type="video/mp4">
  Your browser does not support the video tag.
</video>

## 游戏目标

这是一个经典的**信息不对称**博弈环境，测试 LLM 的**欺骗与推理**能力。

### Good Agents (绿色) — 守护者

- **知道**哪个地标是目标 (通过观测中的 `goal` 字段)
- **目标**: 占领目标地标，同时**迷惑** Adversary
- **策略**: 分兵——一人冲目标 (Scorer)，另一人做诱饵 (Decoy) 假装去错误的地标

### Adversary (红色) — 渗透者

- **不知道**哪个地标是目标
- **目标**: 通过**观察** Good Agents 的行为推理出目标地标
- **策略**: 跟踪最有目的性的 Good Agent，推断其目的地

## 观测空间

### Good Agent 观测

经 `parse_adversary_obs()` 解析后：

| 字段 | 含义 | 维度 |
|:-----|:-----|:----:|
| `vel` | 自身速度 | 2 |
| `goal` | 目标地标相对位置 + 距离 | 3 |
| `landmarks[]` | 所有地标的相对位置 + 距离 + 方向文字 | N+1 组 |
| `adversary` | 对手相对位置 + 距离 + 方向文字 | 1 组 |
| `teammate` | 队友相对位置 | 1 组 |

::: tip Good Agent 独有信息
Good Agent 的观测中有 `goal` 字段，直接告知目标地标的相对位置。这是 Adversary 所不具备的关键信息。
:::

### Adversary 观测

| 字段 | 含义 | 维度 |
|:-----|:-----|:----:|
| `vel` | 自身速度 | 2 |
| `landmarks[]` | 所有地标的相对位置 + 距离 + 方向文字 | N+1 组 |
| `good_agents[]` | 所有 Good Agent 的相对位置 + 距离 | N 组 |

::: warning Adversary 的信息劣势
Adversary 看到所有地标但**不知道哪个是目标**。必须通过分析 Good Agents 的移动模式来推断。
:::

## 奖励函数

**零和博弈** (Zero-Sum):

| 角色 | 奖励方向 |
|:----:|:---------|
| Good Agents | 希望 Adversary **远离**真实目标地标 |
| Adversary | 希望自己**靠近**真实目标地标 |

## 提示词策略

### Good Agent 策略 — 欺骗与分工

```
STRATEGY (DECEPTION & SPLIT):
1. 分析局势:
   - 我比 Adversary 更靠近目标？→ 我是 SCORER
   - Adversary 比我更靠近目标？→ 我是 DECOY

2. SCORER: 全速冲向目标地标！
3. DECOY: 不要去目标，选一个错误的地标，假装那是目标！
4. 永远不要和队友站在同一位置，分割地图！
```

### Adversary 策略 — 推理与追踪

```
STRATEGY (INFERENCE):
1. 分析 Good Agents：谁移动更快？谁在朝地标移动？
2. 选择目标：挑一个 Good Agent 正在保护或冲向的地标
3. 移动：去那个地标（最小化距离）
4. 如果发现跟错了诱饵，立即切换目标！
```

## 运行方式

```bash
python adv_API.py
```

<!-- 📊 实验结果占位 -->

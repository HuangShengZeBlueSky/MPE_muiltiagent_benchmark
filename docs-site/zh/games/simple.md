# Simple — 基础导航

::: info 环境信息
- **PettingZoo 名称**: `simple_v3`
- **模块**: `pettingzoo.mpe.simple_v3`
- **智能体数量**: 1
- **地标数量**: 1
- **类型**: 单智能体导航
:::

<!-- 🎬 视频占位符: 将 simple 的演示视频放在 public/videos/ 目录下 -->
<!-- <video controls width="100%"><source src="/videos/simple_demo.mp4" type="video/mp4"></video> -->

## 游戏目标

这是最简单的 MPE 环境，用作基线。**单个智能体**需要移动到**唯一的地标**位置。

没有对手、没有队友、没有通信——纯粹测试 LLM 的空间推理和运动控制能力。

## 观测空间

智能体的原始观测为 4 维 numpy 数组，经 `parse_simple_obs()` 解析后结构如下：

| 字段 | 维度 | 含义 | 坐标语义 |
|:-----|:----:|:-----|:---------|
| `vel` | 2 | 自身速度 `[vx, vy]` | 绝对速度 |
| `landmark_rel` | 2 | 地标相对位置 `[dx, dy]` | `landmark_pos - agent_pos` |

### 观测解析代码

```python
# obs/parse_simple_obs.py
def parse_simple_obs(obs):
    return {
        "vel": [round(obs[0], 4), round(obs[1], 4)],      # 自身速度
        "landmark_rel": [round(obs[2], 4), round(obs[3], 4)],  # 地标相对位置
    }
```

### 相对坐标理解

::: tip 坐标语义
`landmark_rel = [dx, dy]` 表示 **地标相对于自身的位置**。
- `dx < 0` → 地标在左方 → 应按 `a[1]` (Left)
- `dx > 0` → 地标在右方 → 应按 `a[2]` (Right)  
- `dy < 0` → 地标在下方 → 应按 `a[3]` (Down)
- `dy > 0` → 地标在上方 → 应按 `a[4]` (Up)

**示例**: 地标在 `(0, 1)`，自身在 `(1, 0)` → `landmark_rel = [-1, 1]` → 应向左上方移动
:::

## 奖励函数

```
reward = -‖agent_pos - landmark_pos‖² = -(dx² + dy²)
```

| 条件 | 奖励 |
|:-----|:----:|
| 完全到达地标 (`dx=0, dy=0`) | **0** (最大值) |
| 距离 0.5 | **-0.25** |
| 距离 1.0 | **-1.0** |
| 距离 2.0 | **-4.0** |

**优化目标**: 最大化奖励 = 最小化与地标的距离。

## 动作空间

| 索引 | 含义 | 取值 | 物理映射 |
|:----:|:-----|:----:|:---------|
| `a[0]` | 无操作 | [0, 1] | 忽略 |
| `a[1]` | 左推力 | [0, 1] | 负 X 力 |
| `a[2]` | 右推力 | [0, 1] | 正 X 力 |
| `a[3]` | 下推力 | [0, 1] | 负 Y 力 |
| `a[4]` | 上推力 | [0, 1] | 正 Y 力 |

**净力公式**:
- `F_x = (a[2] - a[1]) × 5.0`
- `F_y = (a[4] - a[3]) × 5.0`

## 提示词结构

### 任务与奖励

```
TASK / GOAL:
- Single agent must move to the single landmark.

REWARD (from source):
- reward = -||agent_pos - landmark_pos||^2 = -(dx^2 + dy^2).
- Maximize reward by driving dx, dy toward 0.
```

### 物理规则

```
PHYSICS (from mpe2==0.0.1):
- Time step dt = 0.1.
- Damping = 0.25 => v <- 0.75 * v each step.
- Mass = 1.0.
- Update order: position uses old v; then damping; then thrust.
- sensitivity = 5.0.
```

### 导航策略 (Few-shot)

提示词中嵌入了 few-shot 导航示例：

| 场景 | 推荐动作 |
|:-----|:---------|
| 地标在左上 (`dx<0, dy>0`) | `a1=0.8, a4=0.8, 其他=0` |
| 地标在右下 (`dx>0, dy<0`) | `a2=0.9, a3=0.9, 其他=0` |
| 接近目标 (`|dx|,|dy|<0.2`) | 全部设为 `0.0` |
| 接近边界 (`|x|>0.9`) | 向中心推 `a1=0.8` |

## LLM 输出格式

```json
{"action": [0.0, 0.8, 0.0, 0.0, 0.6], "notes": "Target is left and up, applying left+up thrust"}
```

## 运行方式

```bash
python simple.py
```

输出文件：
- `simple_demo.mp4` — 游戏录像
- `simple_demo.json` — 日志

<!-- 📊 实验结果占位 -->
<!-- 
## 实验结果

| Model | Mean Reward | Std Dev | Episodes |
|:------|:----------:|:-------:|:--------:|
| Qwen-3-Max | - | ± | 5 |
| DeepSeek-Chat | - | ± | 5 |
| GPT-4o | - | ± | 5 |
-->

# Simple — Navigation

::: info Environment
- **PettingZoo**: `simple_v3` | **Agents**: 1 | **Landmarks**: 1
:::

## Objective
Single agent navigates to a single landmark. Tests basic spatial reasoning.

## Observation Space

| Field | Dim | Description |
|:------|:---:|:------------|
| `vel` | 2 | Agent velocity `[vx, vy]` |
| `landmark_rel` | 2 | Relative to landmark `[dx, dy]` = landmark - agent |

## Reward Function
```
reward = -‖agent_pos - landmark_pos‖² = -(dx² + dy²)
```

## Action Space
5D: `[no_op, left, right, down, up]` ∈ [0,1]⁵

## Run
```bash
python simple.py
```

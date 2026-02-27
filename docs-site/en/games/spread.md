# Spread — Cooperative Coverage

::: info Environment
- **PettingZoo**: `simple_spread_v3` | **Agents**: N (default 3) | **Landmarks**: N
:::

## Objective
N agents cooperatively cover N landmarks while avoiding collisions.

## Observation Space
| Field | Description |
|:------|:------------|
| `self_vel` | Agent velocity |
| `self_pos` | Absolute position |
| `landmark_rel_i` | Relative position to landmark i |
| `other_agent_rel_i` | Relative position to other agents |

## Reward Function
```
global = -Σ_landmark min_agent dist(agent, landmark)
local  = -1.0 per collision (dist < 0.30)
total  = global × (1 - local_ratio) + local × local_ratio
```

## Run
```bash
python spread_API.py
```

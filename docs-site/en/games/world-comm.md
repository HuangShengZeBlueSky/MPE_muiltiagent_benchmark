# World Comm — Large-Scale Coordination

::: info Environment
- **PettingZoo**: `simple_world_comm_v3` | **Agents**: 4 Adversary (1 Leader + 3 Hunter) + 2 Prey
:::

## Objective
Most complex environment with food, forests, obstacles.

| Role | Action Dim | Goal |
|:----:|:----------:|:-----|
| **Leader** | 9 (5 move + 4 comm) | Broadcast prey coordinates |
| **Hunter** | 5 | Chase prey using leader signals |
| **Prey** | 5 | Evade hunters, reach food |

## Run
```bash
python world_comm.py
```

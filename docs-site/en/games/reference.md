# Reference — Bidirectional Communication

::: info Environment
- **PettingZoo**: `simple_reference_v3` | **Agents**: 2 (dual speaker/listener) | **Action Dim**: 15
:::

## Objective
Each agent sees the OTHER agent's target color and broadcasts a signal to help them navigate.

**Action**: 15D = 5 (movement) + 10 (communication signal)

## Run
```bash
python reference.py
```

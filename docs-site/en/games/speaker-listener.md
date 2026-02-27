# Speaker-Listener — Unidirectional Communication

::: info Environment
- **PettingZoo**: `simple_speaker_listener_v4` | **Agents**: 1 Speaker + 1 Listener
:::

## Objective
- **Speaker**: Sees target (one-hot) → emits 3D signal (no movement)
- **Listener**: Sees landmarks + receives signal → navigates to target

## Action Space
| Role | Dim | Content |
|:----:|:---:|:--------|
| Speaker | 3 | Communication signal |
| Listener | 5 | Movement forces |

## Run
```bash
python speaker_listener.py
```

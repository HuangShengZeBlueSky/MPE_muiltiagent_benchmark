# Tag — Predator-Prey Chase

::: info Environment
- **PettingZoo**: `simple_tag_v3` | **Agents**: 3 Predators + 1 Prey | **Obstacles**: 2
:::

## Objective
- **Predators**: Cooperatively hunt prey (collision = catch)
- **Prey**: Evade using obstacles (higher acceleration than predators)

## Reward Function
| Role | Condition | Reward |
|:----:|:----------|:------:|
| Predator | Catch prey | **+10.0** |
| Predator | Distance cost | **-0.1** × dist |
| Prey | Caught | **-10.0** |
| Prey | Out of bounds | **-1.0** / step |
| Prey | Survived | **+0.1** / step |

## Run
```bash
python tag_API.py
```

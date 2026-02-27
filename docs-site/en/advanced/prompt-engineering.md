# Prompt Engineering

## Modular Design

Each game's prompt is decomposed into 4 standardized modules in `prompt/prompt_for_xxx.py`:

| Module | Function | Content |
|:-------|:---------|:--------|
| **Task & Reward** | `get_task_and_reward()` | Game rules, role objectives, reward formulas |
| **Physics** | `get_physics_rules()` | dt, damping, mass, collision detection |
| **Action Format** | `get_action_and_response_format()` | Action dimensions, JSON format, few-shot |
| **Navigation** | `get_navigation_hints()` | Coordinate semantics, boundary handling, strategy |

## Output Format (All Games)

```json
{"action": [a0, a1, a2, a3, a4], "notes": "Short Strategy"}
```

## Best Practices

1. **Explicit coordinate semantics**: Always explain relative coordinates
2. **Mutual exclusion**: Never activate opposing directions
3. **Boundary warnings**: Thrust toward center when near edges
4. **Quantified rewards**: Use mathematical formulas, not vague descriptions

## Adding New Games

Create `prompt/prompt_for_my_game.py` with these 4 functions:

```python
def get_task_and_reward(**kwargs) -> str: ...
def get_physics_rules(**kwargs) -> str: ...
def get_action_and_response_format(**kwargs) -> str: ...
def get_navigation_hints(**kwargs) -> str: ...
```

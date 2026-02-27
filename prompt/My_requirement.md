
### B. 游戏规则、任务目标与奖励提示词

- 作用：明确告知大模型当前环境的目标、胜负条件、奖励函数等。
- 形式：TASK/GOAL、REWARD、环境特殊规则等。
- 每个环境的目标和奖励机制差异较大（如合作、对抗、生存等）。

### C. 动作空间与输出格式提示词

- 作用：规范大模型输出的动作格式、动作空间维度、数值范围，以及输出 JSON 格式要求。
- 形式：ACTION SPACE、RESPONSE FORMAT、动作向量含义、取值范围、输出 JSON 示例。
- 各环境动作空间维度和含义不同（如有无通信、动作数量等）。

### D. 物理规则提示词

- 作用：描述环境的物理引擎细节，便于模型推理运动规律。
- 形式：PHYSICS、PHYSICS RULES、物理参数（如 dt、damping、mass、受力公式等）。
- 物理规则大体类似，但有细微差别（如速度衰减、碰撞判定等）。

### E. 导航/决策/策略提示词

- 作用：为模型提供决策建议、导航逻辑。
- 形式：NAVIGATION RULES、COORDINATION HINT等。
- 具体内容根据环境差异化（如 spread 强调避障与分工，tag 强调追捕与逃脱）。

最终五个提示词梳理为:
__all__ = [
    "get_task_and_reward",
    "get_action_and_response_format",
    "get_physics_rules",
    "get_navigation_hints",
]
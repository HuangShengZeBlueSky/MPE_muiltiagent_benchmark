"""
Prompt components for the Simple Push environment.
Modularized into 4 categories per WORKFLOW_STANDARDIZATION.md.
"""

__all__ = [
    "get_task_and_reward",
    "get_action_and_response_format",
    "get_physics_rules",
    "get_navigation_hints",
]


def get_task_and_reward(role: str) -> str:
    if role == "ADVERSARY":
        task = (
            "ROLE: ADVERSARY (Blocker)\n"
            "- OBJECTIVE: Prevent the Good Agent from reaching the True Target.\n"
            "- FOG: You see two landmarks but don't know which is real. Infer from the Good Agent's motion.\n"
            "- PHYSICS: You are heavy; collisions can shove the opponent."
        )
        reward = "REWARD: Higher when Good Agent stays far from the True Target."
    else:
        task = (
            "ROLE: GOOD AGENT (Runner)\n"
            "- OBJECTIVE: Reach the TRUE TARGET landmark.\n"
            "- DISTRACTION: Another landmark is fake; ignore it.\n"
            "- PHYSICS: You are light; avoid collisions."
        )
        reward = "REWARD: Higher when you are close to the True Target; penalties for delays/collisions."
    return f"{task}\n\n{reward}"


def get_action_and_response_format() -> str:
    return (
        "ACTION SPACE (Continuous forces, length 5):\n"
        "- Vector a=[a0..a4] in [0,1]; a0 no-op, a1 left force, a2 right force, a3 down force, a4 up force.\n"
        "- Net force: fx=(a2-a1)*sensitivity, fy=(a4-a3)*sensitivity; higher = faster acceleration.\n"
        "Few-shot action tips:\n"
        "- Target left/up (dx<0, dy>0): a1=0.8, a4=0.8, others 0.\n"
        "- Target right/down (dx>0, dy<0): a2=0.9, a3=0.9, others 0.\n"
        "- Close to target or about to collide: set all to 0.0 to brake.\n\n"
        "RESPONSE FORMAT (strict JSON, one line):\n"
        '{"action": [a0,a1,a2,a3,a4], "notes": "Short Strategy"}\n'
        "Output ONLY the JSON line."
    )


def get_physics_rules() -> str:
    return (
        "PHYSICS RULES:\n"
        "- 2D continuous dynamics with inertia; velocity decays slowly.\n"
        "- Actions map to forces on X/Y axes; keep within [0,1].\n"
        "- Collisions matter: Adversary is heavier than Good Agent."
    )


def get_navigation_hints(role: str) -> str:
    if role == "ADVERSARY":
        return (
            "NAVIGATION HINTS (Adversary):\n"
            "- OBS RELATIVE COORD: obs uses (other - you). Example: other (0,1), you (1,0) => [-1, 1].\n"
            "- Watch the Good Agent's heading; block the landmark they pursue.\n"
            "- Use your mass to shove; position yourself between Good Agent and suspected target.\n"
            "- Avoid indecision: commit to blocking the most likely target."
            "- BOUNDARY FEW-SHOT: If |x| or |y| > 0.9, thrust back toward center (e.g., x>0.9 -> a1=0.8, others 0).\n"
        )
    return (
        "NAVIGATION HINTS (Good Agent):\n"
        "- OBS RELATIVE COORD: obs uses (other - you). Example: other (0,1), you (1,0) => [-1, 1].\n"
        "- Run toward the TRUE TARGET; ignore the fake landmark.\n"
        "- If Adversary blocks, sidestep and re-approach; keep thrusting toward goal.\n"
        "- Don't overshoot: reduce thrust when close to the target.\n"
        "- **BOUNDARY WARNING**: Stay within map bounds [-1.0, 1.0] to avoid penalties."
        "- Few-shot brake: when |dx|,|dy|<0.2, set all actions to 0.0 for stability.\n"
    )

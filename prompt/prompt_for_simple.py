"""
Prompt components for MPE Simple environment.
Only exports the four required sections per workflow.
"""

__all__ = [
    "get_task_and_reward",
    "get_action_and_response_format",
    "get_physics_rules",
    "get_navigation_hints",
]


def get_task_and_reward() -> str:
    return (
        "TASK / GOAL:\n"
        "- Single agent must move to the single landmark.\n\n"
        "REWARD (from source):\n"
        "- reward = -||agent_pos - landmark_pos||^2 = -(dx^2 + dy^2).\n"
        "- Maximize reward by driving dx, dy toward 0.\n"
    )


def get_action_and_response_format() -> str:
    return (
        "ACTION SPACE (continuous forces):\n"
        "- Action a=[a0..a4] in [0,1]; a0 no-op, a1 left force, a2 right force, a3 down force, a4 up force.\n"
        "- Net force: fx=(a2-a1)*sensitivity, fy=(a4-a3)*sensitivity; force drives acceleration.\n"
        "Few-shot action tips:\n"
        "- Target left/up (dx<0, dy>0): a1=0.8, a4=0.8, others 0.\n"
        "- Target right/down (dx>0, dy<0): a2=0.9, a3=0.9, others 0.\n"
        "- Close to target (|dx|,|dy|<0.2): set all to 0.0 to stop.\n\n"
        "RESPONSE FORMAT (STRICT JSON, ONE LINE):\n"
        '{"action": [a0,a1,a2,a3,a4], "notes": "Short Strategy"}\n'
        "- a0..a4 are floats in [0,1]. Output ONLY this JSON line.\n"
    )


def get_physics_rules() -> str:
    return (
        "PHYSICS (from mpe2==0.0.1):\n"
        "- Time step dt = 0.1.\n"
        "- Damping = 0.25 => v <- 0.75 * v each step.\n"
        "- Mass = 1.0.\n"
        "- Update order: position uses old v; then damping; then thrust.\n"
        "- Continuous action thrust mapping: u_x = sensitivity*(right-left), u_y = sensitivity*(up-down).\n"
        "- sensitivity = 5.0 (no accel override in this env).\n"
    )


def get_navigation_hints() -> str:
    return (
        "NAVIGATION HINTS:\n"
        "- OBS RELATIVE COORD: obs gives landmark_rel = landmark - you. Example: landmark (0,1), you (1,0) => [-1, 1].\n"
        "- Reduce distance to landmark each step; prefer decisive thrust along dx, dy signs.\n"
        "- If |dx| > |dy|, emphasize horizontal thrust; else emphasize vertical.\n"
        "- BOUNDARY FEW-SHOT: If |x| or |y| > 0.9, thrust back toward center (e.g., x>0.9 -> a1=0.8, others 0).\n"
        "- Brake few-shot: when near target (|dx|,|dy|<0.2) set all actions to 0.0 to avoid overshoot.\n"
    )

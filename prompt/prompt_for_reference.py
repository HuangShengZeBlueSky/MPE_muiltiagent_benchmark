"""
Prompt components for the Simple Reference environment.
Modularized into 4 categories per WORKFLOW_STANDARDIZATION.md.
"""

__all__ = [
    "get_task_and_reward",
    "get_action_and_response_format",
    "get_physics_rules",
    "get_navigation_hints",
]


def get_task_and_reward() -> str:
    return (
        "ROLE: Dual-role agent (Speaker + Listener)\n"
        "- SPEAK: You observe the partner's goal color; announce it every step.\n"
        "- LISTEN: You hear your own goal via a received signal; move there.\n"
        "- DO BOTH: Speak and move simultaneously in every step.\n\n"
        "REWARD: Higher when you consistently say the correct goal and reach your target quickly;\n"
        "penalties for silence, wrong calls, or slow movement."
    )


def get_action_and_response_format() -> str:
    return (
        "ACTION SPACE (length 15, continuous [0,1]):\n"
        "- [0]: No-Op\n"
        "- [1]: LEFT force, [2]: RIGHT force, [3]: DOWN force, [4]: UP force (a1..a4 apply thrust).\n"
        "- [5]: Say 0, [6]: Say 1, [7]: Say 2 (speech indices)\n"
        "- [8-14]: Reserved (keep at 0).\n"
        "Multiple indices can be active (e.g., move + say).\n"
        "Few-shot action tips:\n"
        "- Target left/up: a1=0.8, a4=0.8, others 0 (speech index separately set).\n"
        "- Target right/down: a2=0.9, a3=0.9, others 0.\n"
        "- Near goal or to brake: set a1..a4=0.0 while keeping speech active.\n\n"
        "RESPONSE FORMAT (one-line JSON):\n"
        '{"action": [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0], "notes": "Short Strategy"}\n'
        "Output only the JSON line."
    )


def get_physics_rules() -> str:
    return (
        "PHYSICS RULES:\n"
        "- 2D continuous dynamics with light inertia; movement responds to forces.\n"
        "- Collisions are mild but can slow you down; avoid unnecessary contact.\n"
        "- Speech actions do not affect movement; you can speak and move together."
    )


def get_navigation_hints() -> str:
    return (
        "NAVIGATION HINTS:\n"
        "- OBS RELATIVE COORD: movement obs uses (landmark - you). Example: landmark (0,1), you (1,0) => [-1, 1].\n"
        "- SPEAK: Keep the correct 'Say' index at 1.0 every step (index = 5 + partner_target_id).\n"
        "- LISTEN: If you hear a signal (0/1/2), move toward the matching landmark; if silence, hold or drift minimally.\n"
        "- MOTION: Choose the dominant axis toward the target and push steadily; reduce thrust when close.\n"
        "- BOUNDARY FEW-SHOT: If |x| or |y| > 0.9, thrust back toward center (e.g., x>0.9 -> set a1=0.8, others 0).\n"
        "- Brake few-shot: when |dx|,|dy|<0.2 set movement actions to 0.0; keep speech correct.\n"
    )

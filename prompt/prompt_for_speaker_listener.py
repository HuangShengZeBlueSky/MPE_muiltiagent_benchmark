"""
Prompt components for Simple Speaker-Listener environment.
Modularized into 4 categories per WORKFLOW_STANDARDIZATION.md.
Supports both SPEAKER and LISTENER roles.
"""

__all__ = [
    "get_task_and_reward",
    "get_action_and_response_format",
    "get_physics_rules",
    "get_navigation_hints",
]


def get_task_and_reward(role: str) -> str:
    if role == "SPEAKER":
        task = (
            "ROLE: SPEAKER (Static Guide)\n"
            "- OBJECTIVE: Observe the goal landmark and broadcast its index via communication.\n"
            "- BROADCAST: Output a one-hot vector [3] where the 1.0 position matches the target landmark ID.\n"
            "- STATIONARY: You do not move; only transmit."
        )
        reward = "REWARD: Higher when you correctly broadcast the target landmark index consistently."
    else:
        task = (
            "ROLE: LISTENER (Blind Navigator)\n"
            "- OBJECTIVE: Receive the speaker's signal and navigate to the correct landmark.\n"
            "- DEAF: You cannot see landmarks directly; rely on the speaker's communication signal.\n"
            "- MOTION: Move in the direction indicated by the signal."
        )
        reward = "REWARD: Higher when you move toward the spoken landmark and reach it."
    return f"{task}\n\n{reward}"


def get_action_and_response_format(role: str) -> str:
    if role == "SPEAKER":
        return (
            "ACTION SPACE (Speaker, length 3, one-hot):\n"
            "[0]: Say Landmark 0\n"
            "[1]: Say Landmark 1\n"
            "[2]: Say Landmark 2\n"
            "Activate exactly one index (set to 1.0; others to 0.0).\n\n"
            "RESPONSE FORMAT (strict JSON, one line):\n"
            '{"action": [0.0, 0.0, 1.0], "notes": "broadcast landmark 2"}\n'
            "Output only the JSON line."
        )
    else:
        return (
            "ACTION SPACE (Listener, length 5, movement):\n"
            "- Vector a=[a0..a4] in [0,1]; a0 no-op, a1 left force, a2 right force, a3 down force, a4 up force.\n"
            "- Net force: fx=(a2-a1)*sensitivity, fy=(a4-a3)*sensitivity; force accelerates you.\n"
            "Few-shot action tips:\n"
            "- Target left/up: a1=0.8, a4=0.8, others 0.\n"
            "- Target right/down: a2=0.9, a3=0.9, others 0.\n"
            "- Close to goal or to brake: set all to 0.0.\n\n"
            "RESPONSE FORMAT (strict JSON, one line):\n"
            '{"action": [0.0, 0.5, 0.0, 0.0, 0.0], "notes": "Short Strategy"}\n'
            "Output only the JSON line."
        )


def get_physics_rules(role: str) -> str:
    if role == "SPEAKER":
        return (
            "PHYSICS RULES (Speaker):\n"
            "- You are static (no movement dynamics).\n"
            "- Communication broadcast is instant and received at distance.\n"
            "- Signal decays over time steps; maintain consistent output."
        )
    else:
        return (
            "PHYSICS RULES (Listener):\n"
            "- 2D continuous dynamics with light inertia; movement responds to forces.\n"
            "- Collisions with objects slow you down slightly.\n"
            "- Velocity accumulates; adjust thrust to control speed."
        )


def get_navigation_hints(role: str) -> str:
    if role == "SPEAKER":
        return (
            "NAVIGATION HINTS (Speaker):\n"
            "- Verify the goal vector and identify which landmark is the target.\n"
            "- Broadcast the correct index every step without hesitation.\n"
            "- Do not change your broadcast mid-episode unless goal changes."
        )
    else:
        return (
            "NAVIGATION HINTS (Listener):\n"
            "- OBS RELATIVE COORD: obs uses (landmark - you). Example: landmark (0,1), you (1,0) => [-1, 1].\n"
            "- Listen carefully to the signal index received from the speaker.\n"
            "- Compute the landmark position based on the signal index.\n"
            "- Move steadily toward that landmark; reduce thrust when close to avoid overshooting."
            "- BOUNDARY FEW-SHOT: If |x| or |y| > 0.9, thrust back toward center (e.g., x>0.9 -> a1=0.8, others 0).\n"
            "- Brake few-shot: when |dx|,|dy|<0.2 set all movement actions to 0.0.\n"
        )

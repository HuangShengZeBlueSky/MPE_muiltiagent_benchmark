"""
Prompt templates for the MPE Simple Tag environment.

Categories (see prompt/My_requirement.md):
- A. Observation semantics
- B. Task/goal and reward
- C. Action space and output format
- D. Physics rules
- E. Navigation/strategy hints
"""

from typing import Dict, Any

# -----------------------------------------------------------------------------
# B. Game rules, task, and reward
# -----------------------------------------------------------------------------
def get_task_and_reward(is_predator: bool) -> str:
    if is_predator:
        return (
            "TASK: HUNTING (You are a PREDATOR / WOLF)\n"
            "- Goal: Catch the Prey (Green).\n"
            "- Strategy: Prey is faster; cooperate to corner it.\n"
            "- Success: Physical collision with the prey.\n"
            "REWARD (Greedy):\n"
            "- +10.0 for hitting the prey (collision).\n"
            "- -0.1 per step for distance to prey (closer is better)."
        )
    return (
        "TASK: SURVIVAL (You are the PREY / SHEEP)\n"
        "- Goal: Run away from Predators (Red).\n"
        "- Strategy: Use obstacles to juke them.\n"
        "- Constraint: Stay within map (x,y in [-1.0, 1.0]).\n"
        "REWARD (Survival):\n"
        "- -10.0 if caught by a predator.\n"
        "- -1.0 per step when out of bounds.\n"
        "- +0.1 per safe step survived."
    )


# -----------------------------------------------------------------------------
# C. Action space and output format
# -----------------------------------------------------------------------------
def get_action_and_response_format() -> str:
    return (
        "ACTION SPACE & PHYSICS MAPPING (Continuous):\n"
        "1. Vector a=[a0..a4] in [0,1]; a0 no-op, a1 left force, a2 right force, a3 down force, a4 up force.\n"
        "2. Net Force: Force_X = (a2 - a1) * Sensitivity; Force_Y = (a4 - a3) * Sensitivity.\n"
        "3. Intensity: 1.0 = max thrust, 0.0 = no thrust.\n"
        "4. Few-shot action tips:\n"
        "   - Target left/up: a1=0.8, a4=0.8, others 0.\n"
        "   - Target right/down: a2=0.9, a3=0.9, others 0.\n"
        "   - Close or in collision danger: set all to 0.0 to brake.\n"
        "RESPONSE FORMAT (strict, ONE LINE ONLY):\n"
        '{"action": [a0,a1,a2,a3,a4], "notes": "Short Strategy"}\n'
        "- Output ONLY this JSON line."
    )


# -----------------------------------------------------------------------------
# D. Physics rules
# -----------------------------------------------------------------------------
def get_physics_rules() -> str:
    return (
        "PHYSICS RULES:\n"
        "- Time step dt = 0.1; Damping = 0.25 (velocity decays).\n"
        "- Dynamics: p += v*dt; v = v*(1-damping) + force*dt.\n"
        "- Prey has higher acceleration than predators."
    )


# -----------------------------------------------------------------------------
# E. Navigation / strategy hints
# -----------------------------------------------------------------------------
def get_navigation_hints(is_predator: bool) -> str:
    base = (
        "NAVIGATION PHYSICS:\n"
        "- Relative position: [dx, dy] = Target - You (obs uses other - you). Example: target (0,1), you (1,0) => [-1, 1].\n"
        "- Move left/right via a[1]/a[2]; down/up via a[3]/a[4].\n"
        "- Avoid opposing thrust (do not press left & right together).\n"
        "- Boundary few-shot: if |x| or |y| > 0.9, thrust back toward center (e.g., x>0.9 -> a1=0.8, others 0).\n"
        "- Brake few-shot: when |dx|,|dy|<0.2 set actions to 0.0 to stabilize.\n"
    )
    if is_predator:
        return base + (
            "STRATEGY (PREDATOR):\n"
            "- Identify prey (last other-agent entry).\n"
            "- Chase: minimize dx, dy; lead the target if it is moving.\n"
            "- Coordinate with teammates to corner the prey."
        )
    return base + (
        "STRATEGY (PREY):\n"
        "- Identify closest predator (all other-agent entries).\n"
        "- Run opposite to the closest predator.\n"
        "- **CRITICAL BOUNDARY WARNING**: You MUST stay within [-1.0, 1.0] on both axes.\n"
        "  Going out of bounds incurs -1.0 penalty per step. If |x| or |y| > 0.85, turn back immediately!"
    )


__all__ = [
    "get_task_and_reward",
    "get_action_and_response_format",
    "get_physics_rules",
    "get_navigation_hints",
]

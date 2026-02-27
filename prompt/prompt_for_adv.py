"""
Prompt components for Simple Adversary environment.
Modularized according to WORKFLOW_STANDARDIZATION.md.
"""

__all__ = [
    'get_task_and_reward',
    'get_action_and_response_format',
    'get_physics_rules',
    'get_navigation_hints',
]


def get_task_and_reward(is_adversary: bool) -> str:
    """B. Task objective and reward structure."""
    if is_adversary:
        task = (
            "TASK: INFILTRATION (Role: ADVERSARY)\n"
            "- Situation: You don't know which landmark is the Target.\n"
            "- Goal: Guess the Target and be close to it.\n"
            "- Strategy: Observe the Green Agents. They know the target. Follow the one who moves with purpose!\n"
            "- Scoring: You gain points by being close to the real Target."
        )
    else:
        task = (
            "TASK: PROTECTION (Role: GOOD AGENT)\n"
            "- Situation: You know the Target Landmark. The Red Adversary does not.\n"
            "- Goal: Occupy the Target Landmark AND keep the Adversary away from it.\n"
            "- Strategy: DECEPTION IS KEY. Split up! One agent goes to the Goal, the other acts as a DECOY to lure the Adversary to a wrong landmark.\n"
            "- Scoring: You lose points if the Adversary is close to the real Target."
        )
    
    reward = "REWARD: Zero-Sum Game. Good Agents want to minimize Adv-Goal dist. Adv wants to maximize it."
    return f"{task}\n\n{reward}"


def get_action_and_response_format() -> str:
    """C. Action space definition and response format."""
    return (
        "ACTION SPACE (Continuous forces):\n"
        "- Vector a=[a0..a4] in [0,1]; a0 no-op, a1 left force, a2 right force, a3 down force, a4 up force.\n"
        "- Net force: fx=(a2-a1)*sensitivity, fy=(a4-a3)*sensitivity; force accelerates you.\n"
        "- Intensity: 1.0 = max thrust, 0.0 = stop.\n"
        "Few-shot action tips:\n"
        "- Target left/up (dx<0, dy>0): a1=0.8, a4=0.8, others 0.\n"
        "- Target right/down (dx>0, dy<0): a2=0.9, a3=0.9, others 0.\n"
        "- Near goal or collision risk: set all to 0.0 to brake.\n\n"
        "RESPONSE FORMAT (strict, ONE LINE ONLY):\n"
        '{"action": [a0,a1,a2,a3,a4], "notes": "Short Strategy"}\n'
        "- Output ONLY this JSON line."
    )


def get_physics_rules() -> str:
    """D. Physics engine rules (simplified for adversary env)."""
    return (
        "PHYSICS RULES:\n"
        "- Continuous action space with damping.\n"
        "- Agents accelerate towards action directions.\n"
        "- All agents have similar physical capabilities."
    )


def get_navigation_hints(is_adversary: bool) -> str:
    """E. Navigation strategies and role-specific tactics."""
    base_physics = (
        "NAVIGATION COMPASS (CRITICAL):\n"
        "- OBS RELATIVE COORD: obs gives (other - you). Example: other (0,1), you (1,0) => [-1, 1].\n"
        "1. LOOK at the `Direction` hint in Observation.\n"
        "   - If it says 'UP', you MUST press `a[4]` (Up).\n"
        "   - If it says 'DOWN', you MUST press `a[3]` (Down).\n"
        "   - If it says 'LEFT', you MUST press `a[1]` (Left).\n"
        "   - If it says 'RIGHT', you MUST press `a[2]` (Right).\n"
        "2. DO NOT OVERTHINK COORDINATES. Trust the text direction.\n"
        "3. SELF-CORRECTION:\n"
        "   - If you want to go to a target at [dx, dy] = [0.5, 2.0]:\n"
        "   - dx is Positive -> RIGHT (a[2])\n"
        "   - dy is Positive -> UP (a[4])\n"
        "   - DO NOT press Down. DO NOT press Left.\n"
        "4. BOUNDARY FEW-SHOT: If |x| or |y| > 0.9, thrust back to center (e.g., x>0.9 -> a1=0.8, others 0).\n"
    )

    if is_adversary:
        return base_physics + (
            "\nSTRATEGY (INFERENCE):\n"
            "1. ANALYZE AGENTS: Look at 'good_agents'. Who is moving faster? Who is heading to a landmark?\n"
            "2. SELECT TARGET: Pick a landmark that a Good Agent is protecting or rushing towards.\n"
            "3. MOVE: Go to that landmark (Minimize dist to landmark).\n"
            "4. CHANGE: If you realize you are following a decoy, switch target immediately!"
        )
    else:
        return base_physics + (
            "\nSTRATEGY (DECEPTION & SPLIT):\n"
            "1. **BOUNDARY WARNING**: Stay within map bounds [-1.0, 1.0] to avoid penalties.\n"
            "2. ANALYZE SITUATION:\n"
            "   - Am I closer to the Goal than the Adversary? -> I am the SCORER.\n"
            "   - Is the Adversary closer to the Goal than me? -> I must be the DECOY.\n"
            "2. ROLE: SCORER:\n"
            "   - Rush to the 'goal' immediately! Maximize speed.\n"
            "3. ROLE: DECOY (Crucial):\n"
            "   - Do NOT go to the goal. Pick a WRONG landmark.\n"
            "   - Pretend it is the goal! Move towards it to trick the Adversary.\n"
            "4. TEAMWORK: Never stand on the same spot as your teammate. Split the map!"
        )

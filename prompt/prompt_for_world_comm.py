"""
Prompt components for Simple World Comm environment.
Modularized into 4 categories per WORKFLOW_STANDARDIZATION.md.
Supports LEADER, HUNTER, and PREY roles.
"""

__all__ = [
    "get_task_and_reward",
    "get_action_and_response_format",
    "get_physics_rules",
    "get_navigation_hints",
]


def get_task_and_reward(role: str) -> str:
    if role == "LEADER":
        task = (
            "ROLE: LEADER (Adversary Coordinator)\n"
            "- OBJECTIVE: See all prey positions and broadcast coordinates to hunters.\n"
            "- PERCEPTION: You observe all agents and food/obstacles.\n"
            "- COMMUNICATION: You transmit prey absolute coordinates to help hunters.\n"
            "- MOVEMENT: You can move and hunt as well."
        )
        reward = "REWARD: Higher when prey are caught; bonus for leading successful hunts."
    elif role == "HUNTER":
        task = (
            "ROLE: HUNTER (Adversary Pursuit)\n"
            "- OBJECTIVE: Chase and catch prey using movement and leader signals.\n"
            "- PERCEPTION: You see nearby agents but rely on leader for full coordination.\n"
            "- COMMUNICATION: You receive prey coordinates from the leader.\n"
            "- HUNTING: Move aggressively toward prey."
        )
        reward = "REWARD: Higher when you catch prey; bonus for teamwork with other hunters."
    else:  # PREY
        task = (
            "ROLE: PREY (Survivor)\n"
            "- OBJECTIVE: Avoid hunters and reach food sources.\n"
            "- PERCEPTION: You see threats (hunters) and food locations.\n"
            "- SURVIVAL: Run away from hunters; do not stop.\n"
            "- FEEDING: Move toward food when safe."
        )
        reward = "REWARD: Higher when you stay alive and consume food; penalties for being caught."
    
    return f"{task}\n\n{reward}"


def get_action_and_response_format(role: str) -> str:
    if role == "LEADER":
        return (
            "ACTION SPACE (Leader, length 9):\n"
            "[0]: No-Op\n"
            "[1]: LEFT force, [2]: RIGHT force, [3]: DOWN force, [4]: UP force (a1..a4 apply thrust)\n"
            "[5]: Prey0_X, [6]: Prey0_Y, [7]: Prey1_X, [8]: Prey1_Y (communication coords)\n"
            "Movement indices: 0.0-1.0. Communication indices: any float (can be negative/>1).\n\n"
            "RESPONSE FORMAT (strict JSON, one line):\n"
            '{"action": [0.0, 0.5, 0.0, 0.0, 0.0, 0.2, 0.3, -0.1, 0.4], "notes": "Short Strategy"}\n'
            "Output only the JSON line."
        )
    elif role == "HUNTER":
        return (
            "ACTION SPACE (Hunter, length 5):\n"
            "- Vector a=[a0..a4] in [0,1]; a0 no-op, a1 left force, a2 right force, a3 down force, a4 up force.\n"
            "- Net force: fx=(a2-a1)*sensitivity, fy=(a4-a3)*sensitivity; force accelerates you.\n"
            "- Only one of (left,right) and one of (down,up) should be >0 to avoid cancellation.\n"
            "Few-shot action tips:\n"
            "- Prey left/up: a1=0.9, a4=0.9, others 0.\n"
            "- Prey right/down: a2=0.9, a3=0.9, others 0.\n"
            "- Close or overshoot risk: set all to 0.0 to brake.\n\n"
            "RESPONSE FORMAT (strict JSON, one line):\n"
            '{"action": [0.0, 0.0, 1.0, 0.0, 0.8], "notes": "Short Strategy"}\n'
            "Output only the JSON line."
        )
    else:  # PREY
        return (
            "ACTION SPACE (Prey, length 5):\n"
            "- Vector a=[a0..a4] in [0,1]; a0 no-op, a1 left force, a2 right force, a3 down force, a4 up force.\n"
            "- Net force: fx=(a2-a1)*sensitivity, fy=(a4-a3)*sensitivity.\n"
            "- Keep within bounds [-1.0, 1.0].\n"
            "Few-shot action tips:\n"
            "- Threat on right: set a1=0.9 to flee left; keep a2=0.\n"
            "- Threat above: set a3=0.9 to flee down; keep a4=0.\n"
            "- Near boundary (x>0.9): a1=0.8 to return, others 0.\n\n"
            "RESPONSE FORMAT (strict JSON, one line):\n"
            '{"action": [0.0, 1.0, 0.0, 0.5, 0.0], "notes": "Short Strategy"}\n'
            "Output only the JSON line."
        )


def get_physics_rules(role: str) -> str:
    base_rules = (
        "PHYSICS CONSTRAINTS:\n"
        "1. EXCLUSIVE AXIS: Cannot move left and right simultaneously (one must be 0.0).\n"
        "2. EXCLUSIVE AXIS: Cannot move up and down simultaneously (one must be 0.0).\n"
        "3. MOVEMENT: Values > 0.5 indicate decisive movement. Avoid weak inputs like 0.05.\n"
        "4. INERTIA: Velocity decays slowly; acceleration is cumulative.\n"
    )
    
    if role == "PREY":
        return base_rules + (
            "5. **CRITICAL BOUNDARY WARNING**: You MUST stay within [-1.0, 1.0] on both axes.\n"
            "   Out-of-bounds movement incurs HEAVY PENALTIES. Monitor your position constantly!\n"
            "6. EVASION: Keep moving; stopping exposes you to predators."
        )
    else:
        return base_rules + (
            "5. COLLISION: Mild collisions can occur; avoid wasting energy on blocked paths.\n"
        )


def get_navigation_hints(role: str) -> str:
    if role == "LEADER":
        return (
            "NAVIGATION HINTS (Leader):\n"
            "- OBS RELATIVE COORD: movement obs uses (other - you). Example: other (0,1), you (1,0) => [-1, 1].\n"
            "- Maintain position to observe all prey.\n"
            "- Broadcast prey coordinates consistently.\n"
            "- Move strategically to cut off escape routes or assist hunters.\n"
            "- Keep prey in visual range for updates."
            "- Boundary few-shot: if |x| or |y|>0.9, thrust back toward center (e.g., x>0.9 -> a1=0.8, others 0).\n"
        )
    elif role == "HUNTER":
        return (
            "NAVIGATION HINTS (Hunter):\n"
            "- OBS RELATIVE COORD: prey_rel = prey - you. Example: prey (0,1), you (1,0) => [-1, 1].\n"
            "- Follow leader's broadcast coordinates when prey are distant.\n"
            "- Chase visibly detected prey aggressively with max speed (1.0).\n"
            "- Coordinate with other hunters to corner prey.\n"
            "- Reduce speed near prey to avoid overshooting."
            "- Boundary few-shot: if |x| or |y|>0.9, thrust back toward center (x>0.9 -> a1=0.8, others 0).\n"
        )
    else:  # PREY
        return (
            "NAVIGATION HINTS (Prey):\n"
            "- OBS RELATIVE COORD: hunter_rel = hunter - you; example hunter (0,1), you (1,0) => [-1, 1].\n"
            "- Detect threats early; run away from visible hunters immediately.\n"
            "- Move toward food sources but prioritize survival over food.\n"
            "- Use obstacles and forests as cover.\n"
            "- Avoid corners; keep open escape routes.\n"
            "- Never stop moving."
            "- Boundary few-shot: if |x| or |y|>0.9, thrust back toward center (x>0.9 -> a1=0.8, others 0).\n"
            "- Brake few-shot: if you must stop to turn, set all actions to 0.0 for one step.\n"
        )

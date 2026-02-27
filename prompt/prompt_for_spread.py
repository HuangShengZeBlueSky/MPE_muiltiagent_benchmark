"""
Prompt templates for the MPE Simple Spread environment.

This file extracts and groups all prompt-related text from spread_API.py
following the categories defined in prompt/My_requirement.md:
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
def get_task_and_reward(num_agents: int, local_ratio: float) -> str:
    return (
        "TASK / GOAL:\n"
        f"- Cooperative: N agents and N landmarks (N={int(num_agents)}).\n"
        "- Team should cover all landmarks while avoiding collisions.\n"
        "REWARD (from source):\n"
        "- Global reward (shared):\n"
        "  global = - sum_over_landmarks( min_over_agents( EuclideanDistance(agent, landmark) ) )\n"
        "- Local reward (per-agent):\n"
        "  local = -1 for each collision with another agent.\n"
        "  collision if distance(agent_i, agent_j) < size_i + size_j (here agent.size=0.15).\n"
        f"- Total reward returned by env (mixing rule): reward = global*(1-local_ratio) + local*local_ratio, local_ratio={float(local_ratio)}\n"
    )


# -----------------------------------------------------------------------------
# C. Action space and output format
# -----------------------------------------------------------------------------
def get_action_and_response_format() -> str:
    return (
        "ACTION SPACE & PHYSICS MAPPING (Continuous):\n"
        "1. Structure: Action vector a=[a0..a4] in [0.0, 1.0].\n"
        "2. Index Semantics (forces):\n"
        "   - a0: No-Op (ignored)\n"
        "   - a1: Left  thrust (negative X force)\n"
        "   - a2: Right thrust (positive X force)\n"
        "   - a3: Down  thrust (negative Y force)\n"
        "   - a4: Up    thrust (positive Y force)\n"
        "3. Net Force (physics):\n"
        "   - Force_X = (a2 - a1) * sensitivity\n"
        "   - Force_Y = (a4 - a3) * sensitivity\n"
        "   - Force drives acceleration; higher means faster.\n"
        "4. Few-shot action tips:\n"
        "   - Target on left/up  (dx<0, dy>0): a1=0.8, a4=0.8, a2=a3=0.0\n"
        "   - Target on right/down(dx>0, dy<0): a2=0.9, a3=0.9, a1=a4=0.0\n"
        "   - Approaching target (|dx|,|dy|<0.2): set all to 0.0 to brake.\n"
        "RESPONSE FORMAT (strict, ONE LINE ONLY):\n"
        '{"action": [a0,a1,a2,a3,a4], "notes": "Short Strategy"}\n'
        "- a0..a4 must be floats in [0,1]; output ONLY this JSON line."
    )


# -----------------------------------------------------------------------------
# D. Physics rules
# -----------------------------------------------------------------------------
def get_physics_rules() -> str:
    return (
        "PHYSICS (from mpe2==0.0.1 source code):\n"
        "- Time step dt = 0.1\n"
        "- Damping = 0.25, so velocity decays each step: v <- 0.75 * v\n"
        "- Mass = 1.0\n"
        "- Update order per step:\n"
        "  (1) position uses OLD velocity: p <- p + v * dt\n"
        "  (2) apply damping: v <- v * (1 - damping)\n"
        "  (3) apply thrust: v <- v + (u / mass) * dt\n"
        "- Continuous action a in [0,1]^5 with order [no_action,left,right,down,up]\n"
        "  Thrust mapping:\n"
        "    u_x = sensitivity * (right - left)\n"
        "    u_y = sensitivity * (up - down)\n"
        "  sensitivity = 5.0 (unless agent.accel is set; this env does not set it)\n"
        "- Scale hint: if (right-left)=1 then Δv_x per step is 5.0*dt = 0.5\n"
        "  and position step from velocity uses dt=0.1.\n"
        "- **BOUNDARY WARNING**: Stay within map bounds [-1.0, 1.0] on both axes. Going out may cause issues.\n"
    )


# -----------------------------------------------------------------------------
# E. Navigation / strategy hints
# -----------------------------------------------------------------------------
def get_navigation_hints() -> str:
    return (
        "COORDINATION hint (deducible from obs):\n"
        "- If you want to estimate how close another agent is to a landmark:\n"
        "  other_to_landmark = landmark_rel - other_agent_rel\n\n"
        "NAVIGATION RULES (CRITICAL):\n"
        "0. OBS RELATIVE COORDS: obs gives relative = (other - self). Example: other (0,1), you (1,0) => [-1, 1].\n"
        "1. Understand Relative Position [dx, dy] = Landmark - You\n"
        "2. X-Axis Logic (Net Force = Right - Left):\n"
        "   - If dx is NEGATIVE (Target is LEFT)  -> Set 'left' > 0, AND KEEP 'right' = 0.0.\n"
        "   - If dx is POSITIVE (Target is RIGHT) -> Set 'right' > 0, AND KEEP 'left' = 0.0.\n"
        "3. Y-Axis Logic (Net Force = Up - Down):\n"
        "   - If dy is NEGATIVE (Target is BELOW) -> Set 'down' > 0, AND KEEP 'up' = 0.0.\n"
        "   - If dy is POSITIVE (Target is ABOVE) -> Set 'up' > 0, AND KEEP 'down' = 0.0.\n"
        "4. MUTUAL EXCLUSION (Avoid Waste):\n"
        "   - NEVER output opposing actions like [0, 0.6, 0.2, ...] (Left & Right both active).\n"
        "   - This cancels out force. One side MUST be 0.0.\n"
        "5. ARRIVAL STABILITY (Speed Control):\n"
        "   - When approaching target (dist < 0.2), check 'self_vel'.\n"
        "   - Goal: Velocity must be small (vx~0, vy~0) at target.\n"
        "   - Action: If close but fast, set action to 0.0 (coast) or tiny (0.05) to break inertia. DO NOT use full thrust (1.0)!\n"
        "6. COLLISION GUARD (High Penalty):\n"
        "   - Collision occurs if dist(agent_i, agent_j) < 0.3.\n"
        "   - Check 'other_agent_rel'. If neighbor dist < 0.35 (Danger Zone), IMMEDIATE PRIORITY is to move AWAY from neighbor.\n"
        "7. BOUNDARY FEW-SHOT: If |x| or |y| > 0.9, thrust back toward center (e.g., x>0.9 => set a1=0.8, others 0).\n"
    )


__all__ = [
    "get_task_and_reward",
    "get_action_and_response_format",
    "get_physics_rules",
    "get_navigation_hints",
]

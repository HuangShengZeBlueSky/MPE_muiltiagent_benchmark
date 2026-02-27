"""
Observation parser for Simple Push environment.
Splits roles (adversary vs good) and computes distances.
"""

import math
import numpy as np
from typing import Dict, Any, List


def _round_vec(vec: List[float]) -> List[float]:
    return [round(x, 2) for x in vec]


def _dist(vec: List[float]) -> float:
    return round(math.sqrt(vec[0] ** 2 + vec[1] ** 2), 2)


def parse_push_obs(obs: np.ndarray, agent_id: str) -> Dict[str, Any]:
    data = obs.tolist() if isinstance(obs, np.ndarray) else obs
    struct: Dict[str, Any] = {}

    struct['role'] = 'ADVERSARY' if 'adversary' in agent_id else 'GOOD_AGENT'
    struct['raw_vector'] = _round_vec(data)
    struct['vel'] = _round_vec(data[0:2])
    struct['speed'] = _dist(struct['vel'])

    if struct['role'] == 'ADVERSARY':
        # Adversary obs (8 dims): Vel(2), LM_A(2), LM_B(2), Good(2)
        lm_a = _round_vec(data[2:4])
        lm_b = _round_vec(data[4:6])
        struct['landmarks'] = [
            {'id': 'LM_A', 'rel': lm_a, 'dist': _dist(lm_a)},
            {'id': 'LM_B', 'rel': lm_b, 'dist': _dist(lm_b)}
        ]
        struct['opponent_rel'] = _round_vec(data[6:8])
        struct['opponent_dist'] = _dist(struct['opponent_rel'])
    else:
        # Good agent obs (19 dims): Vel(2), Goal(2), Colors..., LMs, Adversary(2)
        struct['goal_rel'] = _round_vec(data[2:4])
        struct['goal_dist'] = _dist(struct['goal_rel'])

        lm_a = _round_vec(data[7:9])
        lm_b = _round_vec(data[9:11])
        dist_a_to_goal = math.sqrt((lm_a[0] - struct['goal_rel'][0]) ** 2 + (lm_a[1] - struct['goal_rel'][1]) ** 2)
        if dist_a_to_goal < 0.1:
            struct['fake_rel'] = lm_b
        else:
            struct['fake_rel'] = lm_a
        struct['fake_dist'] = _dist(struct['fake_rel'])

        struct['opponent_rel'] = _round_vec(data[-2:])
        struct['opponent_dist'] = _dist(struct['opponent_rel'])

    return struct


if __name__ == "__main__":
    print("=" * 60)
    print("Simple Push Observation Parser - Self Test")
    print("=" * 60)

    # Case 1: Adversary obs (len=8)
    obs_adv = np.array([0.1, 0.0, 0.5, 0.2, -0.3, 0.4, 0.7, -0.6])
    print("\n[Case 1] Adversary (len=8)")
    print("Raw:", obs_adv.tolist())
    print("Parsed:", parse_push_obs(obs_adv, "adversary_0"))

    # Case 2: Good agent obs (len=19)
    obs_good = np.array([
        0.0, 0.1,      # vel
        0.2, -0.1,     # goal
        0.1, 0.1, 0.1, # self color (ignored)
        0.0,           # pad
        0.3, 0.2,      # LM_A
        -0.5, 0.6,     # LM_B
        0.0, 0.0, 0.0, 0.0, 0.0, # colors (ignored)
        -0.4, 0.9      # adversary rel
    ])
    print("\n[Case 2] Good Agent (len=19)")
    print("Raw:", obs_good.tolist())
    print("Parsed:", parse_push_obs(obs_good, "agent_0"))

    # Case 3: Short / malformed obs
    obs_short = np.array([0.1, 0.2, 0.3])
    print("\n[Case 3] Short obs (len=3)")
    print("Raw:", obs_short.tolist())
    print("Parsed:", parse_push_obs(obs_short, "agent_x"))

    print("\nSelf test complete.")

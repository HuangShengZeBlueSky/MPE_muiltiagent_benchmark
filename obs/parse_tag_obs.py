"""
Parser for MPE Simple Tag observations.
Extracts structured fields and includes a small self-test.
"""

import math
import numpy as np
from typing import Dict, Any


def parse_tag_obs(obs: np.ndarray, agent_id: str, num_obstacles: int, num_good: int, num_adversaries: int) -> Dict[str, Any]:
    """Parse raw observation into structured components.

    Observation layout (per agent):
      [self_vel(2), self_pos(2), obstacles_rel(2*num_obstacles), other_agents_rel(2*(total_agents-1))]
    where total_agents = num_good + num_adversaries.
    """
    data = obs.tolist() if isinstance(obs, np.ndarray) else obs
    total_agents = num_good + num_adversaries
    expected_len = 4 + 2 * num_obstacles + 2 * (total_agents - 1)

    if len(data) < expected_len:
        return {"error": "dim_mismatch", "raw_len": len(data), "expected_min": expected_len}

    ptr = 0
    struct: Dict[str, Any] = {}

    struct["self_vel"] = [round(data[ptr], 2), round(data[ptr + 1], 2)]; ptr += 2
    struct["self_pos"] = [round(data[ptr], 2), round(data[ptr + 1], 2)]; ptr += 2

    struct["obstacles_rel"] = []
    for _ in range(num_obstacles):
        dx, dy = data[ptr], data[ptr + 1]
        dist = math.sqrt(dx * dx + dy * dy)
        struct["obstacles_rel"].append([round(dx, 2), round(dy, 2), round(dist, 2)])
        ptr += 2

    num_others = total_agents - 1
    others = []
    for _ in range(num_others):
        if ptr + 1 >= len(data):
            break
        dx, dy = data[ptr], data[ptr + 1]
        dist = math.sqrt(dx * dx + dy * dy)
        others.append([round(dx, 2), round(dy, 2), round(dist, 2)])
        ptr += 2

    is_predator = "adversary" in agent_id
    struct["enemies"] = []
    struct["teammates"] = []

    if is_predator:
        prey_count = num_good
        if len(others) >= prey_count:
            struct["enemies"] = others[-prey_count:]
            struct["teammates"] = others[:-prey_count]
        else:
            struct["enemies"] = others
    else:
        struct["enemies"] = others

    return struct


if __name__ == "__main__":
    print("=" * 60)
    print("Simple Tag observation parser demo")
    print("=" * 60)

    num_obstacles = 2
    num_good = 1
    num_adversaries = 3
    total_agents = num_good + num_adversaries

    # Case 1: Predator
    raw_pred = np.array([
        0.1, -0.1,   # self_vel
        0.2, -0.2,   # self_pos
        0.5, -0.4,   # obstacle 0
        -0.3, 0.6,   # obstacle 1
        0.1, 0.2,    # teammate 1
        -0.4, 0.5,   # teammate 2
        0.7, -0.8    # prey (last entry)
    ])
    parsed_pred = parse_tag_obs(raw_pred, "adversary_0", num_obstacles, num_good, num_adversaries)
    print("\n[Predator] raw len:", len(raw_pred))
    print("Parsed:", parsed_pred)

    # Case 2: Prey
    raw_prey = np.array([
        -0.05, 0.0,  # self_vel
        -0.3, 0.4,   # self_pos
        -0.2, 0.3,   # obstacle 0
        0.6, -0.5,   # obstacle 1
        0.5, 0.1,    # predator 1
        -0.6, -0.2,  # predator 2
        0.2, -0.7    # predator 3
    ])
    parsed_prey = parse_tag_obs(raw_prey, "agent_0", num_obstacles, num_good, num_adversaries)
    print("\n[Prey] raw len:", len(raw_prey))
    print("Parsed:", parsed_prey)

    # Case 3: Dimension mismatch
    bad_raw = np.array([0.0, 0.0, 0.0])
    parsed_bad = parse_tag_obs(bad_raw, "agent_0", num_obstacles, num_good, num_adversaries)
    print("\n[Dim Mismatch]", parsed_bad)

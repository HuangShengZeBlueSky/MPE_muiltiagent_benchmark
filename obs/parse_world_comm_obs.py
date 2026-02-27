"""
Observation parser for Simple World Comm environment.
Handles LEADER (adversary), HUNTER (adversary), and PREY roles.
Includes self-tests when run directly.
"""

import math
import numpy as np
from typing import Dict, Any, List


def _round_vec(vec: List[float]) -> List[float]:
    return [round(x, 3) for x in vec]


def _dist(v: List[float]) -> float:
    return round(math.sqrt(v[0] ** 2 + v[1] ** 2), 3)


def parse_world_comm_obs(obs: np.ndarray, agent_name: str) -> Dict[str, Any]:
    """
    Environment: simple_world_comm_v3
    Parses observation based on agent role (LEADER, HUNTER, or PREY).
    """
    data = obs.tolist() if isinstance(obs, np.ndarray) else list(obs)
    
    def vec(idx):
        if idx + 1 < len(data):
            return _round_vec([data[idx], data[idx + 1]])
        return _round_vec([0.0, 0.0])
    
    res = {
        "agent_name": agent_name,
        "raw_len": len(data),
        "raw": _round_vec(data[:min(len(data), 34)]),
        "self": {
            "velocity": vec(0),
            "position": vec(2),
            "in_bounds": abs(data[2]) <= 1.0 and abs(data[3]) <= 1.0 if len(data) > 3 else False,
        },
        "role": "",
        "landmarks": {
            "obstacle": vec(4),
            "food_1": vec(6),
            "food_2": vec(8),
            "forest_1": vec(10),
            "forest_2": vec(12),
        },
        "teammates": [],
        "enemies": [],
        "communication": None,
    }

    is_adversary = "adversary" in agent_name

    if is_adversary:
        res["role"] = "LEADER" if "lead" in agent_name else "HUNTER"
        
        # Teammates (other adversaries)
        for i in range(3):
            idx = 14 + i * 2
            pos = vec(idx)
            status = "HIDDEN" if (_dist(pos) < 0.01) else "VISIBLE"
            res["teammates"].append({
                "id": f"teammate_{i}",
                "rel": pos,
                "dist": _dist(pos),
                "status": status,
            })
        
        # Enemies (prey)
        for i in range(2):
            idx = 20 + i * 2
            pos = vec(idx)
            d = _dist(pos)
            status = "HIDDEN" if (d < 0.01) else "VISIBLE"
            res["enemies"].append({
                "id": f"prey_{i}",
                "rel": pos,
                "dist": d,
                "status": status,
            })
        
        # Communication (HUNTER only)
        if res["role"] == "HUNTER" and len(data) > 33:
            comm_raw = data[30:34]
            res["communication"] = {
                "signal": _round_vec(comm_raw),
                "active": max(np.abs(comm_raw)) > 0.01 if comm_raw else False,
            }
    else:
        res["role"] = "PREY"
        
        # Enemies (adversaries) - 4 hunters/leaders
        for i in range(4):
            idx = 14 + i * 2
            pos = vec(idx)
            res["enemies"].append({
                "id": f"threat_{i}",
                "rel": pos,
                "dist": _dist(pos),
            })
        
        # Teammate (partner prey)
        pos = vec(22)
        res["teammates"].append({
            "id": "partner",
            "rel": pos,
            "dist": _dist(pos),
        })

    return res


if __name__ == "__main__":
    print("=" * 60)
    print("Simple World Comm Observation Parser - Self Test")
    print("=" * 60)

    # Case 1: LEADER obs
    obs_leader = np.array([
        0.1, 0.0,              # vel
        0.2, -0.1,             # position
        0.5, 0.2, -0.3, 0.4,   # obstacle, food_1
        0.1, -0.5, 0.0, 0.1, -0.2, 0.3,  # food_2, forest_1, forest_2
        0.3, 0.1, -0.2, 0.4, 0.0, -0.3,  # 3 teammates (6 vals)
        0.6, 0.2, -0.4, 0.5,   # 2 prey (4 vals)
        0.0, 0.0, 0.0, 0.0     # padding
    ])
    print("\n[Case 1] LEADER obs (len=34)")
    print("Raw len:", len(obs_leader))
    parsed = parse_world_comm_obs(obs_leader, "adversary_lead_0")
    print("Parsed role:", parsed["role"])
    print("Enemies (prey):", parsed["enemies"])
    print("Teammates:", parsed["teammates"][:1])

    # Case 2: HUNTER obs with communication
    obs_hunter = np.array([
        -0.1, 0.05,            # vel
        -0.2, 0.3,             # position
        0.4, -0.1, 0.2, 0.5,   # obstacles/food
        -0.3, 0.1, 0.0, -0.4, 0.1, 0.2,  # more landmarks
        0.1, 0.3, -0.1, 0.2, 0.0, -0.2,  # teammates
        0.5, 0.4, -0.3, 0.1,   # enemies (prey)
        0.8, 0.2, 0.1, 0.05    # comm signal (heard at indices 5-8)
    ])
    print("\n[Case 2] HUNTER obs (len=34)")
    print("Raw len:", len(obs_hunter))
    parsed = parse_world_comm_obs(obs_hunter, "adversary_hunt_1")
    print("Parsed role:", parsed["role"])
    print("Communication:", parsed.get("communication"))
    print("Enemies:", parsed["enemies"][:1])

    # Case 3: PREY obs
    obs_prey = np.array([
        0.0, 0.1,              # vel
        -0.5, 0.6,             # position (in bounds)
        0.8, -0.3, 0.2, 0.5,   # landmarks
        -0.2, 0.1, 0.3, -0.4, 0.1, 0.0,  # forests
        -0.1, 0.2, 0.4, -0.2, -0.3, 0.5,  # 4 threats (predators)
        0.1, -0.1,             # partner (1 prey)
        0.0, 0.0, 0.0, 0.0, 0.0, 0.0  # padding
    ])
    print("\n[Case 3] PREY obs (len=34)")
    print("Raw len:", len(obs_prey))
    parsed = parse_world_comm_obs(obs_prey, "agent_prey_0")
    print("Parsed role:", parsed["role"])
    print("Threats:", parsed["enemies"][:2])
    print("Partner:", parsed["teammates"])

    # Case 4: Short obs (error handling)
    obs_short = np.array([0.1, 0.2, 0.3, 0.4, 0.5])
    print("\n[Case 4] Short obs (len=5)")
    print("Raw len:", len(obs_short))
    parsed = parse_world_comm_obs(obs_short, "agent_test")
    print("Parsed:", parsed["role"], "| raw_len:", parsed["raw_len"])

    print("\nSelf test complete.")

"""
Observation parser for MPE simple_v3 (single agent, single landmark).
Includes self-test when run directly.
"""

import math
import numpy as np
from typing import Dict, Any, List

__all__ = ["parse_simple_obs"]


def _round_vec(vec: List[float]) -> List[float]:
    return [round(x, 3) for x in vec]


def parse_simple_obs(obs: np.ndarray) -> Dict[str, Any]:
    """
    Expect obs shape: [vel_x, vel_y, rel_x, rel_y].
    Returns structured dict with velocity, relative position, and distance.
    """
    data = obs.tolist() if isinstance(obs, np.ndarray) else list(obs)
    if len(data) != 4:
        return {"error": f"Expected 4 dims, got {len(data)}", "raw": _round_vec(data)}

    vx, vy, dx, dy = data
    dist = math.sqrt(dx ** 2 + dy ** 2)
    return {
        "vel": _round_vec([vx, vy]),
        "landmark_rel": _round_vec([dx, dy, dist]),
    }


if __name__ == "__main__":
    print("=" * 60)
    print("simple_v3 observation parser self-test")
    print("=" * 60)

    # Case 1: normal obs
    obs1 = np.array([0.1, -0.2, 0.5, -0.4])
    parsed1 = parse_simple_obs(obs1)
    print("\n[Case 1] len=4")
    print("raw:", obs1.tolist())
    print("parsed:", parsed1)

    # Case 2: wrong length
    obs2 = np.array([0.1, 0.2, 0.3])
    parsed2 = parse_simple_obs(obs2)
    print("\n[Case 2] len=3 (error)")
    print("raw:", obs2.tolist())
    print("parsed:", parsed2)

    # Case 3: zero vector
    obs3 = np.array([0.0, 0.0, 0.0, 0.0])
    parsed3 = parse_simple_obs(obs3)
    print("\n[Case 3] zeros")
    print("raw:", obs3.tolist())
    print("parsed:", parsed3)

    print("\nSelf-test complete.")

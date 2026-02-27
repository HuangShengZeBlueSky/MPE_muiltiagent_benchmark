"""
Observation parser for the Simple Reference environment.
Pads short observations and computes structured fields for speaker/listener tasks.
Includes self-tests when run directly.
"""

import math
import numpy as np
from typing import Dict, Any, List

EXPECTED_LEN = 21


def _round_vec(vec: List[float]) -> List[float]:
    return [round(x, 2) for x in vec]


def _dist(vec: List[float]) -> float:
    return round(math.sqrt(vec[0] ** 2 + vec[1] ** 2), 2)


def parse_reference_obs(obs: np.ndarray, agent_id: str) -> Dict[str, Any]:
    data_list = obs.tolist() if isinstance(obs, np.ndarray) else list(obs)
    orig_len = len(data_list)
    padded = data_list + [0.0] * max(0, EXPECTED_LEN - orig_len)

    struct: Dict[str, Any] = {
        "agent_id": agent_id,
        "raw": _round_vec(data_list),
        "raw_len": orig_len,
    }
    if orig_len < EXPECTED_LEN:
        struct["warning"] = f"obs length {orig_len} < expected {EXPECTED_LEN}; padded with zeros."

    struct["vel"] = _round_vec(padded[0:2])

    landmarks = []
    colors = ["Red", "Green", "Blue"]
    for i in range(3):
        start = 2 + i * 2
        rel = padded[start : start + 2]
        landmarks.append({
            "id": i,
            "color_name": colors[i],
            "rel": _round_vec(rel),
            "dist": _dist(rel),
        })
    struct["landmarks"] = landmarks

    goal_rgb = padded[8:11]
    struct["partner_goal_rgb"] = _round_vec(goal_rgb)
    struct["partner_target_id"] = int(np.argmax(goal_rgb)) if len(goal_rgb) > 0 else -1

    comm_vec = padded[11:21]
    struct["heard_signal"] = -1
    struct["signal_strength"] = 0.0
    if len(comm_vec) > 0 and max(comm_vec) > 0.1:
        struct["heard_signal"] = int(np.argmax(comm_vec))
        struct["signal_strength"] = round(float(max(comm_vec)), 2)

    return struct


if __name__ == "__main__":
    print("=" * 60)
    print("Simple Reference Observation Parser - Self Test")
    print("=" * 60)

    # Case 1: Normal obs (len=21) with clear signal 2
    obs_full = np.array([
        0.1, -0.2,        # vel
        0.3, 0.1, 0.5, 0.2, 0.0, 0.0,  # three landmarks (x,y each)
        0.0, 0.5, 0.1,    # partner goal RGB
        0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.9, 0.1  # comm vector
    ])
    print("\n[Case 1] Normal obs (len=21)")
    print("Raw len:", len(obs_full))
    print("Parsed:", parse_reference_obs(obs_full, "agent_0"))

    # Case 2: Normal obs with silence (all comm near zero)
    obs_silence = np.array([
        -0.1, 0.0,        # vel
        -0.2, 0.4, 0.6, -0.1, 0.2, -0.3,
        0.3, 0.2, 0.1,
        0.05, 0.02, 0.01, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0
    ])
    print("\n[Case 2] Silence in comm channel")
    print("Raw len:", len(obs_silence))
    print("Parsed:", parse_reference_obs(obs_silence, "agent_1"))

    # Case 3: Short / malformed obs (len<21)
    obs_short = np.array([0.2, -0.1, 0.3, 0.4, 0.5])
    print("\n[Case 3] Short obs (len=5)")
    print("Raw len:", len(obs_short))
    print("Parsed:", parse_reference_obs(obs_short, "agent_x"))

    print("\nSelf test complete.")

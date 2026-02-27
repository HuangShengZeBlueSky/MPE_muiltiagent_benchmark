"""
Observation parser for Simple Speaker-Listener environment.
Handles both SPEAKER (one-hot goal) and LISTENER (vel + landmarks + comm) roles.
Includes self-tests when run directly.
"""

import math
import numpy as np
from typing import Dict, Any, List


def _round_vec(vec: List[float]) -> List[float]:
    return [round(x, 2) for x in vec]


def parse_speaker_listener_obs(obs: np.ndarray, agent_id: str) -> Dict[str, Any]:
    """
    Environment: simple_speaker_listener_v4
    - Speaker obs: [3] one-hot goal vector
    - Listener obs: [11] = vel(2) + landmarks(6) + comm(3)
    """
    data = obs.tolist() if isinstance(obs, np.ndarray) else list(obs)
    struct: Dict[str, Any] = {
        "agent_id": agent_id,
        "raw": _round_vec(data),
        "raw_len": len(data),
    }

    if "speaker" in agent_id:
        struct["role"] = "SPEAKER"
        if len(data) >= 3:
            goal_vec = data[0:3]
            struct["goal_vector"] = _round_vec(goal_vec)
            struct["target_landmark_id"] = int(np.argmax(goal_vec))
        else:
            struct["warning"] = f"obs length {len(data)} < 3 for SPEAKER; truncated"
            struct["goal_vector"] = _round_vec(data + [0.0] * (3 - len(data)))
            struct["target_landmark_id"] = 0

    else:  # listener
        struct["role"] = "LISTENER"
        padded = data + [0.0] * max(0, 11 - len(data))
        if len(data) < 11:
            struct["warning"] = f"obs length {len(data)} < 11 for LISTENER; padded with zeros."

        struct["vel"] = _round_vec(padded[0:2])

        landmarks = []
        for i in range(3):
            start = 2 + i * 2
            pos = padded[start : start + 2]
            landmarks.append({
                "id": i,
                "rel": _round_vec(pos),
            })
        struct["landmarks"] = landmarks

        comm_vec = padded[8:11]
        struct["comm_vector"] = _round_vec(comm_vec)

        heard_id = -1
        if len(comm_vec) > 0 and max(comm_vec) > 0.1:
            heard_id = int(np.argmax(comm_vec))
        struct["heard_id"] = heard_id

    return struct


if __name__ == "__main__":
    print("=" * 60)
    print("Simple Speaker-Listener Observation Parser - Self Test")
    print("=" * 60)

    # Case 1: Speaker obs (len=3)
    obs_speaker = np.array([0.0, 0.5, 1.0])
    print("\n[Case 1] Speaker obs (len=3)")
    print("Raw:", obs_speaker.tolist())
    print("Parsed:", parse_speaker_listener_obs(obs_speaker, "speaker_0"))

    # Case 2: Listener obs (len=11) with signal
    obs_listener = np.array([
        0.1, -0.2,        # vel
        0.5, 0.3, -0.4, 0.2, 0.1, -0.5,  # 3 landmarks
        0.0, 0.8, 0.1     # comm signal (heard landmark 1)
    ])
    print("\n[Case 2] Listener obs (len=11) with signal")
    print("Raw:", obs_listener.tolist())
    print("Parsed:", parse_speaker_listener_obs(obs_listener, "listener_0"))

    # Case 3: Listener obs with silence
    obs_silent = np.array([
        -0.1, 0.05,
        0.2, 0.1, -0.3, 0.4, 0.0, -0.2,
        0.05, 0.02, 0.01  # all below threshold
    ])
    print("\n[Case 3] Listener obs (len=11) with silence")
    print("Raw:", obs_silent.tolist())
    print("Parsed:", parse_speaker_listener_obs(obs_silent, "listener_0"))

    # Case 4: Short speaker obs (error handling)
    obs_short_speaker = np.array([1.0, 0.0])
    print("\n[Case 4] Short speaker obs (len=2)")
    print("Raw:", obs_short_speaker.tolist())
    print("Parsed:", parse_speaker_listener_obs(obs_short_speaker, "speaker_0"))

    # Case 5: Short listener obs (error handling)
    obs_short_listener = np.array([0.1, 0.2, 0.3, 0.4])
    print("\n[Case 5] Short listener obs (len=4)")
    print("Raw:", obs_short_listener.tolist())
    print("Parsed:", parse_speaker_listener_obs(obs_short_listener, "listener_0"))

    print("\nSelf test complete.")

"""
Observation parser for Simple Crypto environment.
Extracts structured fields for Alice, Bob, and Eve roles.
"""

import numpy as np
from typing import Dict, Any


def parse_crypto_obs(obs: np.ndarray, agent_id: str) -> Dict[str, Any]:
    """Parse raw observation into structured dict per role."""
    data = obs.tolist() if isinstance(obs, np.ndarray) else obs
    rounded = [round(x, 2) for x in data]
    struct: Dict[str, Any] = {"raw": rounded}

    if "alice" in agent_id:
        struct["role"] = "ALICE"
        struct["message"] = rounded[0:4]
        struct["key"] = rounded[4:8]
    elif "bob" in agent_id:
        struct["role"] = "BOB"
        struct["key"] = rounded[0:4]
        struct["ciphertext"] = rounded[4:8]
    elif "eve" in agent_id:
        struct["role"] = "EVE"
        struct["ciphertext"] = rounded[0:4]
    else:
        struct["role"] = "UNKNOWN"

    return struct


if __name__ == "__main__":
    print("=" * 60)
    print("Simple Crypto Observation Parser - Self Test")
    print("=" * 60)

    # Case 1: Alice
    obs_alice = np.array([0.1, 0.2, 0.3, 0.4, 0.9, 0.8, 0.7, 0.6])
    print("\n[Case 1] Alice obs (len=8)")
    print("Raw:", obs_alice.tolist())
    print("Parsed:", parse_crypto_obs(obs_alice, "alice_0"))

    # Case 2: Bob
    obs_bob = np.array([0.9, 0.8, 0.7, 0.6, 0.4, 0.3, 0.2, 0.1])
    print("\n[Case 2] Bob obs (len=8)")
    print("Raw:", obs_bob.tolist())
    print("Parsed:", parse_crypto_obs(obs_bob, "bob_0"))

    # Case 3: Eve (shorter obs)
    obs_eve = np.array([0.5, 0.6, 0.7, 0.8])
    print("\n[Case 3] Eve obs (len=4)")
    print("Raw:", obs_eve.tolist())
    print("Parsed:", parse_crypto_obs(obs_eve, "eve_0"))

    # Case 4: Dimension mismatch / unknown agent
    obs_short = np.array([0.1, 0.2])
    print("\n[Case 4] Unknown agent (len=2)")
    print("Raw:", obs_short.tolist())
    print("Parsed:", parse_crypto_obs(obs_short, "agent_x"))

    print("\nSelf test complete.")

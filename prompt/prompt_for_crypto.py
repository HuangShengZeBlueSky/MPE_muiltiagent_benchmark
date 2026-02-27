"""
Prompt components for the Simple Crypto environment.
Modularized according to WORKFLOW_STANDARDIZATION.md (4 categories).
"""

__all__ = [
    "get_task_and_reward",
    "get_action_and_response_format",
    "get_physics_rules",
    "get_navigation_hints",
]


def get_task_and_reward(role: str) -> str:
    """B. Task and reward for each role."""
    if role == "ALICE":
        task = (
            "TASK: ENCRYPTED COMMUNICATION (Role: ALICE)\n"
            "- OBJECTIVE: Send the 'Secret Message' to Bob. Output a 'Ciphertext'.\n"
            "- SECURITY: Eve is eavesdropping. Hide the message from Eve.\n"
            "- TOOL: You share a 'Private Key' with Bob.\n"
            "- STRATEGY: Combine Message and Key so that Bob can invert it, Eve cannot.\n"
        )
        reward = "REWARD: You succeed when Bob can recover the message and Eve cannot guess it."
    elif role == "BOB":
        task = (
            "TASK: DECRYPTION (Role: BOB)\n"
            "- OBJECTIVE: Recover the 'Secret Message' sent by Alice.\n"
            "- DATA: You received a 'Ciphertext' and you have a 'Private Key'.\n"
            "- LOGIC: Alice mixed Message and Key; invert the operation to recover Message.\n"
        )
        reward = "REWARD: Accurate recovery of the message; penalized if you guess wrong."
    else:  # EVE
        task = (
            "TASK: CODE BREAKING (Role: EVE)\n"
            "- OBJECTIVE: Intercept the 'Ciphertext' and guess the 'Secret Message'.\n"
            "- CHALLENGE: You do NOT have the Private Key.\n"
            "- STRATEGY: Analyze ciphertext patterns; make the best guess.\n"
        )
        reward = "REWARD: Higher if your guess matches the true message."
    return f"{task}\n\n{reward}"


def get_action_and_response_format() -> str:
    """C. Action space and strict response format."""
    return (
        "ACTION SPACE (Continuous, length 4):\n"
        "- Output a vector of 4 floats in [0.0, 1.0].\n"
        "- Alice -> Output Ciphertext.\n"
        "- Bob/Eve -> Output Message Guess.\n\n"
        "RESPONSE FORMAT (strict JSON, one line):\n"
        '{"action": [v1, v2, v3, v4], "notes": "Short Strategy"}\n'
        "- Output ONLY the JSON line."
    )


def get_physics_rules() -> str:
    """D. Environment / data flow rules (lightweight)."""
    return (
        "DATA FLOW RULES:\n"
        "- Each step is a new message/key/cipher context.\n"
        "- Observations already provide needed vectors; no hidden dynamics.\n"
        "- Keep outputs within [0,1]; the env will clip or score based on distance."
    )


def get_navigation_hints(role: str) -> str:
    """E. Strategy guidance per role."""
    if role == "ALICE":
        return (
            "STRATEGY HINTS (ALICE):\n"
            "- Mix Message and Key in a reversible way (for Bob) but obscure to Eve.\n"
            "- Simple approach: add or XOR-like mix and mod to [0,1].\n"
            "- Avoid outputting the raw message."
        )
    if role == "BOB":
        return (
            "STRATEGY HINTS (BOB):\n"
            "- Use the shared Key to invert Alice's mixing (e.g., subtract or un-mix).\n"
            "- Check that results stay in [0,1]. If unsure, pick the closest feasible message."
        )
    return (
        "STRATEGY HINTS (EVE):\n"
        "- You lack the Key; infer patterns from ciphertext magnitude and symmetry.\n"
        "- Guess the most plausible message given the numbers you see."
    )

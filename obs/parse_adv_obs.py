"""
Observation parser for Simple Adversary environment.
Extracts structured information from raw observation vectors.
"""

import math
import numpy as np
from typing import Dict, Any


def parse_adversary_obs(obs: np.ndarray, agent_id: str, num_good: int) -> Dict[str, Any]:
    """
    Parse raw observation for simple_adversary_v3 environment.
    
    Args:
        obs: Raw observation vector from environment
        agent_id: Agent identifier (contains 'adversary' for adversary agents)
        num_good: Number of good agents/landmarks (N parameter)
    
    Returns:
        Structured observation dictionary with role-specific fields
    
    Observation structure verified for N=2:
    - Adversary (8 dims): [Landmark_0(2), Landmark_1(2), Good_0(2), Good_1(2)]
    - Good Agent (10 dims): [Goal(2), Landmark_0(2), Landmark_1(2), Adversary(2), Teammate(2)]
    """
    data = obs.tolist() if isinstance(obs, np.ndarray) else obs
    struct = {}
    
    def get_vec(start_idx):
        """Helper: Extract [dx, dy] and compute distance."""
        if start_idx + 1 >= len(data):
            return [0.0, 0.0], 0.0
        dx, dy = data[start_idx], data[start_idx + 1]
        dist = math.sqrt(dx**2 + dy**2)
        return [round(dx, 2), round(dy, 2)], round(dist, 2)

    is_adversary = "adversary" in agent_id
    
    if is_adversary:
        # === Adversary perspective ===
        struct['role'] = 'ADVERSARY'
        
        # 1. Landmarks (first 2N positions)
        struct['landmarks'] = []
        ptr = 0
        for i in range(num_good):
            vec, dist = get_vec(ptr)
            struct['landmarks'].append({'id': i, 'rel': vec, 'dist': dist})
            ptr += 2
            
        # 2. Good agents (next 2N positions)
        struct['good_agents'] = []
        for i in range(num_good):
            vec, dist = get_vec(ptr)
            struct['good_agents'].append({'id': f"agent_{i}", 'rel': vec, 'dist': dist})
            ptr += 2
            
    else:
        # === Good agent perspective ===
        struct['role'] = 'GOOD_AGENT'
        
        # 1. Goal (first 2 positions)
        vec, dist = get_vec(0)
        struct['goal'] = {'rel': vec, 'dist': dist}
        
        # 2. Landmarks (next 2N positions) - mark which is the target
        struct['landmarks'] = []
        ptr = 2
        for i in range(num_good):
            vec, d = get_vec(ptr)
            # Check if this landmark is the goal (coordinates nearly match)
            is_target = (abs(vec[0] - struct['goal']['rel'][0]) < 0.01 and 
                        abs(vec[1] - struct['goal']['rel'][1]) < 0.01)
            struct['landmarks'].append({
                'id': i, 
                'rel': vec, 
                'dist': d, 
                'is_target': is_target
            })
            ptr += 2
            
        # 3. Adversary (next 2 positions)
        vec, dist = get_vec(ptr)
        struct['adversary'] = {'rel': vec, 'dist': dist}
        ptr += 2
        
        # 4. Teammates (remaining 2*(N-1) positions)
        struct['teammates'] = []
        for i in range(num_good - 1):
            vec, dist = get_vec(ptr)
            struct['teammates'].append({'rel': vec, 'dist': dist})
            ptr += 2

    return struct


if __name__ == "__main__":
    print("="*60)
    print("Simple Adversary Observation Parser - Self Test")
    print("="*60)
    
    # Test configuration
    NUM_GOOD = 2
    
    # Case 1: Adversary observation (N=2 -> 8 dims)
    print("\n[Case 1] Adversary Agent (8 dims)")
    obs_adv = np.array([
        0.5, 0.3,    # Landmark 0
        -0.2, 0.8,   # Landmark 1
        0.1, -0.4,   # Good Agent 0
        -0.6, 0.2    # Good Agent 1
    ])
    print(f"Raw obs length: {len(obs_adv)}")
    print(f"Raw obs: {obs_adv.tolist()}")
    
    parsed_adv = parse_adversary_obs(obs_adv, "adversary_0", NUM_GOOD)
    print(f"\nParsed structure:")
    print(f"  Role: {parsed_adv['role']}")
    print(f"  Landmarks: {parsed_adv['landmarks']}")
    print(f"  Good Agents: {parsed_adv['good_agents']}")
    
    # Case 2: Good agent observation (N=2 -> 10 dims)
    print("\n" + "-"*60)
    print("[Case 2] Good Agent (10 dims)")
    obs_good = np.array([
        0.5, 0.3,    # Goal
        0.5, 0.3,    # Landmark 0 (is goal)
        -0.2, 0.8,   # Landmark 1
        -0.3, -0.5,  # Adversary
        0.4, 0.1     # Teammate
    ])
    print(f"Raw obs length: {len(obs_good)}")
    print(f"Raw obs: {obs_good.tolist()}")
    
    parsed_good = parse_adversary_obs(obs_good, "agent_0", NUM_GOOD)
    print(f"\nParsed structure:")
    print(f"  Role: {parsed_good['role']}")
    print(f"  Goal: {parsed_good['goal']}")
    print(f"  Landmarks: {parsed_good['landmarks']}")
    print(f"  Adversary: {parsed_good['adversary']}")
    print(f"  Teammates: {parsed_good['teammates']}")
    
    # Verify goal identification
    target_landmark = [lm for lm in parsed_good['landmarks'] if lm['is_target']]
    print(f"\n  Target landmark identified: {target_landmark}")
    
    # Case 3: Dimension mismatch handling
    print("\n" + "-"*60)
    print("[Case 3] Dimension Mismatch (robustness test)")
    obs_short = np.array([0.1, 0.2, 0.3])  # Too short
    print(f"Raw obs length: {len(obs_short)} (expected 8 for adversary)")
    
    try:
        parsed_short = parse_adversary_obs(obs_short, "adversary_0", NUM_GOOD)
        print(f"Parsed (with padding): {parsed_short}")
        print("✓ Parser handled short input gracefully")
    except Exception as e:
        print(f"✗ Error: {e}")
    
    print("\n" + "="*60)
    print("✓ Self-test completed")
    print("="*60)

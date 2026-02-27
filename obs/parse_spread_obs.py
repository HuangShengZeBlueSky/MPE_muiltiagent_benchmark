"""
MPE Simple Spread 环境的观测解析器

该模块提供 parse_spread_obs 函数，将原始观测向量解析为结构化的字典，
包含自身状态、地标相对位置、其他智能体相对位置等信息，并预计算距离。
"""

import math
import numpy as np
from typing import Dict, Any


def parse_spread_obs(obs: np.ndarray, num_agents: int) -> Dict[str, Any]:
    """
    针对 MPE 'simple_spread_v3' 环境的通用解析器。
    
    Args:
        obs: 原始观测向量 (numpy array)
        num_agents: 环境中智能体的总数 (N)，用于计算切片位置。
                    注意：MPE 默认 N=3，但也可能自定义。
    
    Returns:
        Dict: 结构化的观测数据，包含距离预计算。
              包含字段: self_vel, self_pos, landmark_rel, other_agent_rel
    
    Observation Structure:
        - obs = [self_vel(2), self_pos(2), landmark_rel(2N), other_agent_rel(2(N-1)), comm(2(N-1))]
        - Total length: 4 + 2N + 2(N-1) + 2(N-1) = 6N
        - For N=3: length = 18
    """
    data = obs.tolist() if isinstance(obs, np.ndarray) else obs
    
    # --- 1. 维度校验 ---
    # 公式: 4 + 2*N + 2*(N-1) + 2*(N-1)
    # 简化: 4 + 2N + 4N - 4 = 6N
    # 比如 N=3，长度应该是 18。
    expected_len = 4 + 2 * num_agents + 2 * (num_agents - 1) * 2
    
    # 容错：有些版本的 simple_spread comm 通道维度可能不同，或者被关闭
    # 这里我们主要确保前半部分物理信息正确
    if len(data) < expected_len - 2*(num_agents-1):  # 至少要有物理信息
        return {"error": "dim_mismatch", "raw_len": len(data), "expected_min": expected_len}

    ptr = 0
    struct = {}

    # --- 2. 自身状态 ---
    # [vx, vy]
    struct['self_vel'] = [round(data[ptr], 2), round(data[ptr+1], 2)]
    ptr += 2
    # [px, py]
    struct['self_pos'] = [round(data[ptr], 2), round(data[ptr+1], 2)]
    ptr += 2

    # --- 3. Landmarks (N 个) ---
    # 目标：不仅给坐标，还要给距离，方便模型做 "min_over_agents" 的判断
    struct['landmark_rel'] = []
    for k in range(num_agents):  # 默认 landmark 数量 = agent 数量
        dx = data[ptr]
        dy = data[ptr+1]
        dist = math.sqrt(dx**2 + dy**2)
        # 格式: [dx, dy, dist]
        struct['landmark_rel'].append([round(dx, 2), round(dy, 2), round(dist, 2)])
        ptr += 2

    # --- 4. Teammates (N-1 个) ---
    # 目标：给距离，方便避障 (collision avoidance)
    struct['other_agent_rel'] = []
    for j in range(num_agents - 1):
        dx = data[ptr]
        dy = data[ptr+1]
        dist = math.sqrt(dx**2 + dy**2)
        
        # 避障预警：Agent 半径 0.15，碰撞阈值 0.3。
        # 如果距离 < 0.35，我们在数据里加一个 flag 提示模型注意
        warning = "COLLISION_RISK" if dist < 0.35 else "safe"
        
        # 格式: [dx, dy, dist] (暂不把 warning 放进 list，以免破坏 float 结构，
        # 如果模型足够聪明，看 dist 也就懂了，这里保持纯数字更稳)
        struct['other_agent_rel'].append([round(dx, 2), round(dy, 2), round(dist, 2)])
        ptr += 2

    # --- 5. Comm (N-1 个) ---
    # 通常是 zeros，直接跳过或者记录一下
    # struct['comm'] = data[ptr:] 
    
    return struct


if __name__ == "__main__":
    """测试解析器功能"""
    print("=" * 60)
    print("MPE Simple Spread 观测解析器测试")
    print("=" * 60)
    
    # 测试用例 1: N=3 的标准情况
    # 观测向量长度应该是 18
    # [self_vel(2), self_pos(2), landmark_rel(6), other_agent_rel(4), comm(4)]
    print("\n测试用例 1: N=3, 标准观测向量")
    print("-" * 60)
    
    test_obs_1 = np.array([
        # self_vel (2)
        0.1, -0.05,
        # self_pos (2)
        0.2, 0.3,
        # landmark_rel (2*3=6): 3个地标的相对位置
        0.5, 0.4,   # landmark 0: [dx, dy]
        -0.3, 0.2,  # landmark 1: [dx, dy]
        0.1, -0.6,  # landmark 2: [dx, dy]
        # other_agent_rel (2*2=4): 2个其他智能体的相对位置
        0.15, 0.25,  # agent 1: [dx, dy] - 距离较近
        -0.8, 0.6,   # agent 2: [dx, dy]
        # comm (2*2=4): 2个其他智能体的通信
        0.0, 0.0,
        0.0, 0.0
    ])
    
    parsed_1 = parse_spread_obs(test_obs_1, num_agents=3)
    print(parsed_1)
    
    print(f"原始观测长度: {len(test_obs_1)}")
    print(f"\n解析结果:")
    print(f"  自身速度 (self_vel):     {parsed_1['self_vel']}")
    print(f"  自身位置 (self_pos):     {parsed_1['self_pos']}")
    print(f"\n  地标相对位置 (landmark_rel):")
    for i, lm in enumerate(parsed_1['landmark_rel']):
        print(f"    Landmark {i}: dx={lm[0]:6.2f}, dy={lm[1]:6.2f}, dist={lm[2]:6.2f}")
    print(f"\n  其他智能体相对位置 (other_agent_rel):")
    for i, ag in enumerate(parsed_1['other_agent_rel']):
        status = "⚠️ 碰撞风险" if ag[2] < 0.35 else "✓ 安全"
        print(f"    Agent {i+1}: dx={ag[0]:6.2f}, dy={ag[1]:6.2f}, dist={ag[2]:6.2f}  {status}")
    

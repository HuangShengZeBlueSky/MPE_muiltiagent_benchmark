"""
MPE 观测解析辅助工具函数
提供通用的辅助函数，用于所有环境的观测解析
"""

import math
from typing import Tuple, List, Dict, Any

# ==============================================================================
# 1. 几何计算函数
# ==============================================================================

def get_distance(dx: float, dy: float) -> float:
    """
    计算欧几里得距离
    
    参数:
        dx: X轴相对坐标
        dy: Y轴相对坐标
    
    返回:
        欧几里得距离
    """
    return math.sqrt(dx**2 + dy**2)


def get_direction(dx: float, dy: float, threshold: float = 0.1) -> str:
    """
    根据相对坐标返回主要方向
    
    参数:
        dx: X轴相对坐标 (负=左，正=右)
        dy: Y轴相对坐标 (负=下，正=上)
        threshold: 判断是否接近中心的阈值
    
    返回:
        方向字符串: UP, DOWN, LEFT, RIGHT, UP-LEFT, UP-RIGHT, DOWN-LEFT, DOWN-RIGHT, CENTER
    """
    if abs(dx) < threshold and abs(dy) < threshold:
        return "CENTER"
    
    # 确定水平方向
    h_dir = "RIGHT" if dx > threshold else "LEFT" if dx < -threshold else ""
    
    # 确定垂直方向
    v_dir = "UP" if dy > threshold else "DOWN" if dy < -threshold else ""
    
    # 组合方向
    if h_dir and v_dir:
        return f"{v_dir}-{h_dir}"
    return v_dir or h_dir or "CENTER"


def get_vector_info(dx: float, dy: float, decimals: int = 2) -> Dict[str, Any]:
    """
    获取向量的完整信息（位置、距离、方向）
    
    参数:
        dx: X轴相对坐标
        dy: Y轴相对坐标
        decimals: 保留小数位数
    
    返回:
        包含 relative_position, distance, direction 的字典
    """
    return {
        'relative_position': [round(dx, decimals), round(dy, decimals)],
        'distance': round(get_distance(dx, dy), decimals),
        'direction': get_direction(dx, dy)
    }


# ==============================================================================
# 2. 向量处理函数
# ==============================================================================

def round_vector(vec: List[float], decimals: int = 2) -> List[float]:
    """
    向量取整
    
    参数:
        vec: 输入向量
        decimals: 保留小数位数
    
    返回:
        取整后的向量
    """
    return [round(x, decimals) for x in vec]


def normalize_vector(vec: List[float]) -> List[float]:
    """
    向量归一化（单位化）
    
    参数:
        vec: 输入向量
    
    返回:
        归一化后的向量
    """
    mag = math.sqrt(sum(x**2 for x in vec))
    if mag < 1e-6:
        return vec
    return [x / mag for x in vec]


def get_velocity_info(vx: float, vy: float, decimals: int = 2) -> Dict[str, Any]:
    """
    获取速度信息
    
    参数:
        vx: X轴速度分量
        vy: Y轴速度分量
        decimals: 保留小数位数
    
    返回:
        包含 x, y, speed, direction 的字典
    """
    speed = get_distance(vx, vy)
    return {
        'x': round(vx, decimals),
        'y': round(vy, decimals),
        'speed': round(speed, decimals),
        'direction': get_direction(vx, vy) if speed > 0.01 else "STATIONARY"
    }


# ==============================================================================
# 3. 编码解析函数
# ==============================================================================

def parse_one_hot(vec: List[float]) -> int:
    """
    解析 One-Hot 向量，返回最大值的索引
    
    参数:
        vec: One-Hot 向量（或近似 One-Hot）
    
    返回:
        最大值的索引
    
    示例:
        [0, 0, 1] -> 2
        [0.1, 0.8, 0.1] -> 1
    """
    return int(max(range(len(vec)), key=lambda i: vec[i]))


def rgb_to_color_name(rgb: List[float], threshold: float = 0.5) -> str:
    """
    将 RGB 向量转换为颜色名称
    
    参数:
        rgb: RGB 向量 [r, g, b]，范围通常是 [0, 1]
        threshold: 判断颜色的阈值
    
    返回:
        颜色名称字符串
    
    常见颜色映射:
        [1, 0, 0] -> RED
        [0, 1, 0] -> GREEN
        [0, 0, 1] -> BLUE
        [1, 1, 0] -> YELLOW
        [0, 1, 1] -> CYAN
        [1, 0, 1] -> MAGENTA
        [0, 0, 0] -> BLACK
        [1, 1, 1] -> WHITE
    """
    r, g, b = rgb
    
    # 纯色检测
    if r > threshold and g < threshold and b < threshold:
        return "RED"
    elif g > threshold and r < threshold and b < threshold:
        return "GREEN"
    elif b > threshold and r < threshold and g < threshold:
        return "BLUE"
    
    # 混合色检测
    elif r > threshold and g > threshold and b < threshold:
        return "YELLOW"
    elif g > threshold and b > threshold and r < threshold:
        return "CYAN"
    elif r > threshold and b > threshold and g < threshold:
        return "MAGENTA"
    
    # 灰度检测
    elif r < 0.1 and g < 0.1 and b < 0.1:
        return "BLACK"
    elif r > 0.9 and g > 0.9 and b > 0.9:
        return "WHITE"
    elif abs(r - g) < 0.2 and abs(g - b) < 0.2:
        return "GRAY"
    
    return "UNKNOWN"


# ==============================================================================
# 4. 观测读取辅助函数
# ==============================================================================

def read_vector_2d(data: List[float], ptr: int, decimals: int = 2) -> Tuple[Dict[str, Any], int]:
    """
    从数据中读取一个2D向量并返回完整信息
    
    参数:
        data: 完整的观测数据
        ptr: 当前读取位置
        decimals: 保留小数位数
    
    返回:
        (向量信息字典, 新的指针位置)
    """
    if ptr + 1 >= len(data):
        return {'relative_position': [0.0, 0.0], 'distance': 0.0, 'direction': 'NONE'}, ptr
    
    dx, dy = data[ptr], data[ptr + 1]
    info = get_vector_info(dx, dy, decimals)
    return info, ptr + 2


def read_velocity(data: List[float], ptr: int, decimals: int = 2) -> Tuple[Dict[str, Any], int]:
    """
    从数据中读取速度向量
    
    参数:
        data: 完整的观测数据
        ptr: 当前读取位置
        decimals: 保留小数位数
    
    返回:
        (速度信息字典, 新的指针位置)
    """
    if ptr + 1 >= len(data):
        return {'x': 0.0, 'y': 0.0, 'speed': 0.0, 'direction': 'NONE'}, ptr
    
    vx, vy = data[ptr], data[ptr + 1]
    info = get_velocity_info(vx, vy, decimals)
    return info, ptr + 2


def read_color(data: List[float], ptr: int, decimals: int = 2) -> Tuple[Dict[str, Any], int]:
    """
    从数据中读取颜色向量（通常是3维RGB）
    
    参数:
        data: 完整的观测数据
        ptr: 当前读取位置
        decimals: 保留小数位数
    
    返回:
        (颜色信息字典, 新的指针位置)
    """
    if ptr + 2 >= len(data):
        return {'rgb': [0.0, 0.0, 0.0], 'name': 'UNKNOWN'}, ptr
    
    rgb = [data[ptr], data[ptr + 1], data[ptr + 2]]
    return {
        'rgb': round_vector(rgb, decimals),
        'name': rgb_to_color_name(rgb)
    }, ptr + 3


# ==============================================================================
# 5. 威胁评估函数
# ==============================================================================

def assess_threat_level(distance: float, 
                       low_threshold: float = 1.0,
                       high_threshold: float = 0.5) -> str:
    """
    根据距离评估威胁等级
    
    参数:
        distance: 与威胁目标的距离
        low_threshold: 低威胁阈值
        high_threshold: 高威胁阈值
    
    返回:
        威胁等级: HIGH, MEDIUM, LOW
    """
    if distance < high_threshold:
        return "HIGH"
    elif distance < low_threshold:
        return "MEDIUM"
    else:
        return "LOW"


# ==============================================================================
# 6. 描述生成函数
# ==============================================================================

def generate_position_description(entity_name: str, 
                                 relative_pos: List[float],
                                 distance: float,
                                 direction: str) -> str:
    """
    生成位置描述文本
    
    参数:
        entity_name: 实体名称 (如 "地标 0", "敌方", "队友")
        relative_pos: 相对位置 [x, y]
        distance: 距离
        direction: 方向
    
    返回:
        描述文本
    """
    return f"{entity_name} 在你的{direction}方向，距离 {distance:.2f}"


def generate_tactical_description(role: str,
                                  my_distance: float,
                                  target_distance: float,
                                  entity_type: str = "目标") -> str:
    """
    生成战术角色描述
    
    参数:
        role: 智能体角色
        my_distance: 我到目标的距离
        target_distance: 对手到目标的距离
        entity_type: 实体类型描述
    
    返回:
        战术建议文本
    """
    if my_distance < target_distance:
        return f"你更接近{entity_type}，应该直接冲向{entity_type}！"
    else:
        return f"对手更接近{entity_type}，考虑采用诱饵策略或拦截！"


# ==============================================================================
# 7. JSON 格式化辅助
# ==============================================================================

def create_base_observation_dict(agent_id: str, 
                                role: str,
                                description: str) -> Dict[str, Any]:
    """
    创建基础观测字典模板
    
    参数:
        agent_id: 智能体ID
        role: 角色名称
        description: 角色描述
    
    返回:
        基础观测字典
    """
    return {
        'agent_id': agent_id,
        'role': role,
        'description': description
    }


def add_landmark_info(obs_dict: Dict[str, Any],
                     landmarks: List[Dict[str, Any]]) -> None:
    """
    向观测字典添加地标信息
    
    参数:
        obs_dict: 观测字典
        landmarks: 地标信息列表
    """
    obs_dict['landmarks'] = landmarks


def add_agent_info(obs_dict: Dict[str, Any],
                  agents: List[Dict[str, Any]],
                  key: str = 'other_agents') -> None:
    """
    向观测字典添加其他智能体信息
    
    参数:
        obs_dict: 观测字典
        agents: 智能体信息列表
        key: 字典键名
    """
    obs_dict[key] = agents


# ==============================================================================
# 8. 调试辅助函数
# ==============================================================================

def print_raw_observation(obs: List[float], 
                         agent_id: str,
                         segments: List[Tuple[str, int]]) -> None:
    """
    打印原始观测向量的分段信息（用于调试）
    
    参数:
        obs: 原始观测向量
        agent_id: 智能体ID
        segments: 分段信息列表 [(名称, 维度), ...]
    
    示例:
        segments = [("速度", 2), ("位置", 2), ("地标", 4)]
    """
    print(f"\n🔍 调试: {agent_id} 的原始观测")
    print(f"   总维度: {len(obs)}")
    
    ptr = 0
    for name, dim in segments:
        if ptr + dim <= len(obs):
            segment_data = obs[ptr:ptr+dim]
            print(f"   {name} [{ptr}:{ptr+dim}]: {round_vector(segment_data, 2)}")
            ptr += dim
        else:
            print(f"   {name}: [超出范围]")
            break
    
    if ptr < len(obs):
        print(f"   未解析 [{ptr}:{len(obs)}]: {round_vector(obs[ptr:], 2)}")


# ==============================================================================
# 9. 常用常量
# ==============================================================================

# 方向映射（用于动作建议）
DIRECTION_TO_ACTION = {
    'UP': 'increase a[4]',
    'DOWN': 'increase a[3]',
    'LEFT': 'increase a[1]',
    'RIGHT': 'increase a[2]',
    'UP-LEFT': 'increase a[4] and a[1]',
    'UP-RIGHT': 'increase a[4] and a[2]',
    'DOWN-LEFT': 'increase a[3] and a[1]',
    'DOWN-RIGHT': 'increase a[3] and a[2]',
    'CENTER': 'no movement needed'
}

# 威胁等级颜色（用于可视化）
THREAT_COLORS = {
    'HIGH': '🔴',
    'MEDIUM': '🟡',
    'LOW': '🟢',
    'NONE': '⚪'
}

# 角色图标
ROLE_ICONS = {
    'ADVERSARY': '🔴',
    'GOOD_AGENT': '🟢',
    'PREDATOR': '🐺',
    'PREY': '🐑',
    'SPEAKER': '📢',
    'LISTENER': '👂',
    'ALICE': '🔐',
    'BOB': '🔓',
    'EVE': '👁️',
    'LEADER': '👑',
    'FOLLOWER': '🤝'
}


if __name__ == "__main__":
    # 测试函数
    print("=" * 70)
    print("MPE 观测解析辅助工具测试")
    print("=" * 70)
    
    # 测试几何计算
    print("\n1. 几何计算测试:")
    dx, dy = 0.5, 0.3
    print(f"   向量 ({dx}, {dy}):")
    print(f"   - 距离: {get_distance(dx, dy):.2f}")
    print(f"   - 方向: {get_direction(dx, dy)}")
    info = get_vector_info(dx, dy)
    print(f"   - 完整信息: {info}")
    
    # 测试速度信息
    print("\n2. 速度信息测试:")
    vx, vy = -0.2, 0.15
    vel_info = get_velocity_info(vx, vy)
    print(f"   速度向量 ({vx}, {vy}): {vel_info}")
    
    # 测试 One-Hot 解析
    print("\n3. One-Hot 解析测试:")
    one_hot = [0, 0, 1]
    print(f"   {one_hot} -> 索引 {parse_one_hot(one_hot)}")
    
    # 测试颜色解析
    print("\n4. 颜色解析测试:")
    colors = [
        [1.0, 0.0, 0.0],
        [0.0, 1.0, 0.0],
        [0.0, 0.0, 1.0],
        [1.0, 1.0, 0.0]
    ]
    for rgb in colors:
        print(f"   RGB {rgb} -> {rgb_to_color_name(rgb)}")
    
    # 测试威胁评估
    print("\n5. 威胁评估测试:")
    distances = [0.3, 0.7, 1.5]
    for dist in distances:
        level = assess_threat_level(dist)
        print(f"   距离 {dist} -> 威胁等级: {level} {THREAT_COLORS[level]}")
    
    print("\n✅ 所有测试完成！")

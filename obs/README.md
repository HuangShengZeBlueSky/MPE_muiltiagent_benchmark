# MPE 观测解析工具 (obs/)

本目录包含所有 MPE 环境的观测空间验证和解析工具。

## 📁 文件结构

```
obs/
├── utils.py                    # 通用辅助函数库 ⭐
├── parse_adv_obs.py           # Simple Adversary 解析器 ✅ (示例)
├── parse_spread_obs.py        # Simple Spread 解析器 (待实现)
├── parse_tag_obs.py           # Simple Tag 解析器 (待实现)
├── parse_push_obs.py          # Simple Push 解析器 (待实现)
├── parse_crypto_obs.py        # Simple Crypto 解析器 (待实现)
├── parse_reference_obs.py     # Simple Reference 解析器 (待实现)
├── parse_speaker_obs.py       # Simple Speaker Listener 解析器 (待实现)
├── parse_world_comm_obs.py    # Simple World Comm 解析器 (待实现)
├── parse_simple_obs.py        # Simple (Basic) 解析器 (待实现)
├── verify_all_envs.py         # 批量验证脚本 (待实现)
└── README.md                  # 本文件
```

## 🎯 核心功能

### 1. 观测解析器 (`parse_*_obs.py`)

每个解析器文件包含三个核心函数：

- **`parse_<env>_obs()`**: 将原始观测向量转换为结构化 JSON
- **`verify_obs_structure()`**: 验证观测空间的维度和正确性
- **`print_observation_semantics()`**: 打印观测语义说明

### 2. 辅助工具库 (`utils.py`)

提供通用的辅助函数：
- 几何计算：距离、方向
- 向量处理：归一化、取整
- 编码解析：One-Hot、RGB 转颜色名
- 威胁评估、描述生成等

## 🚀 快速开始

### 示例 1: 运行 Simple Adversary 解析器

```bash
# 激活虚拟环境
source /workspaces/MPE_muiltiagent_benchmark/.venv-1/bin/activate

# 运行解析器（包含完整的验证和语义说明）
python obs/parse_adv_obs.py
```

**输出内容**:
1. 观测语义说明（每个维度的含义）
2. 观测空间验证（维度检查）
3. 解析后的 JSON 格式
4. 关键信息摘要

### 示例 2: 在主代码中使用解析器

```python
# 在 adv_API.py 中
from obs.parse_adv_obs import parse_adversary_obs

# 在主循环中
for agent_id in env.agents:
    obs_raw = observations[agent_id]
    
    # 解析观测
    obs_struct = parse_adversary_obs(obs_raw, agent_id, num_good=2)
    
    # obs_struct 是一个字典，包含所有语义信息
    print(json.dumps(obs_struct, indent=2, ensure_ascii=False))
    
    # 用于构建 LLM prompt
    prompt = build_prompt(agent_id, obs_struct)
```

### 示例 3: 使用辅助工具

```python
from obs.utils import get_vector_info, rgb_to_color_name, assess_threat_level

# 计算位置信息
dx, dy = 0.5, 0.3
info = get_vector_info(dx, dy)
# {'relative_position': [0.5, 0.3], 'distance': 0.58, 'direction': 'UP-RIGHT'}

# 解析颜色
rgb = [1.0, 0.0, 0.0]
color = rgb_to_color_name(rgb)  # 'RED'

# 评估威胁
distance = 0.4
threat = assess_threat_level(distance)  # 'HIGH'
```

## 📋 JSON 输出格式说明

所有解析器输出的 JSON 遵循统一结构：

```json
{
  "agent_id": "agent_0",
  "role": "GOOD_AGENT",
  "description": "友好智能体 - 知道目标地标，需要保护它",
  
  "goal": {
    "relative_position": [-0.66, -1.32],
    "distance": 1.48,
    "direction": "DOWN",
    "description": "⭐ 真正的目标在你的DOWN方向，距离 1.48",
    "is_target": true
  },
  
  "landmarks": [
    {
      "id": 0,
      "relative_position": [-0.96, -1.38],
      "distance": 1.68,
      "direction": "DOWN",
      "is_target": false,
      "description": "地标 0 (诱饵) 在DOWN，距离 1.68"
    }
  ],
  
  "adversary": {
    "relative_position": [-0.94, -0.04],
    "distance": 0.94,
    "direction": "LEFT",
    "description": "🔴 敌方在你的LEFT方向，距离 0.94",
    "threat_level": "MEDIUM"
  },
  
  "tactical_hint": "SCORER - 你更接近目标，应该直接冲向目标！"
}
```

### 关键字段说明

| 字段 | 类型 | 说明 |
|------|------|------|
| `agent_id` | string | 智能体ID |
| `role` | string | 角色名称 (ADVERSARY, GOOD_AGENT, etc.) |
| `description` | string | 角色描述 |
| `relative_position` | [float, float] | 相对坐标 [x, y] |
| `distance` | float | 欧几里得距离 |
| `direction` | string | 主要方向 (UP/DOWN/LEFT/RIGHT) |
| `description` | string | 人类可读的描述 |
| `tactical_hint` | string | 战术建议 |

## 🔧 创建新的解析器

### 步骤 1: 探测观测空间

创建 `obs_<env>.py` 探测脚本：

```python
from pettingzoo.mpe import <environment_v3>
import numpy as np

env = <environment_v3>.parallel_env(...)
obs, _ = env.reset()

for agent_id, data in obs.items():
    print(f"Agent: {agent_id}, Shape: {data.shape}")
    print(f"Data: {np.round(data, 2)}")
```

### 步骤 2: 分析观测结构

运行探测脚本，记录：
- 每个智能体的观测维度
- 每个维度的语义含义
- 不同角色的观测差异

### 步骤 3: 实现解析器

使用模板创建 `parse_<env>_obs.py`：

```python
import numpy as np
import json
import math
from typing import Dict, Any
from pettingzoo.mpe import <environment_v3>
from obs.utils import get_vector_info, create_base_observation_dict

def parse_<env>_obs(obs: np.ndarray, agent_id: str, **kwargs) -> Dict[str, Any]:
    """解析观测向量"""
    data = obs.tolist() if isinstance(obs, np.ndarray) else obs
    
    # 创建基础结构
    struct = create_base_observation_dict(
        agent_id=agent_id,
        role=determine_role(agent_id),
        description="角色描述"
    )
    
    # 解析各个部分
    ptr = 0
    
    # 示例: 解析速度
    vel_info, ptr = read_velocity(data, ptr)
    struct['velocity'] = vel_info
    
    # 示例: 解析地标
    struct['landmarks'] = []
    for i in range(num_landmarks):
        pos_info, ptr = read_vector_2d(data, ptr)
        struct['landmarks'].append({
            'id': i,
            **pos_info,
            'description': f"地标 {i} ..."
        })
    
    # 添加战术提示
    struct['tactical_hint'] = generate_tactical_hint(struct)
    
    return struct

def verify_obs_structure(**params):
    """验证观测空间"""
    # 实现验证逻辑
    pass

def print_observation_semantics(**params):
    """打印观测语义"""
    # 实现语义说明
    pass

if __name__ == "__main__":
    print_observation_semantics()
    verify_obs_structure()
```

### 步骤 4: 测试验证

```bash
python obs/parse_<env>_obs.py
```

检查：
- [ ] 维度匹配
- [ ] JSON 格式正确
- [ ] 方向计算准确
- [ ] 描述清晰易懂

## 📊 9 个环境的状态

| 环境 | 文件 | 状态 | 关键特性 |
|------|------|------|---------|
| Simple Adversary | `parse_adv_obs.py` | ✅ 完成 | 敌我角色，目标推理 |
| Simple Spread | `parse_spread_obs.py` | ⏳ 待实现 | 协作覆盖，无角色差异 |
| Simple Tag | `parse_tag_obs.py` | ⏳ 待实现 | 追逃博弈，障碍物 |
| Simple Push | `parse_push_obs.py` | ⏳ 待实现 | 物理推理，目标导航 |
| Simple Crypto | `parse_crypto_obs.py` | ⏳ 待实现 | 三方博弈，编码解码 |
| Simple Reference | `parse_reference_obs.py` | ⏳ 待实现 | 颜色引用，协作导航 |
| Simple Speaker Listener | `parse_speaker_obs.py` | ⏳ 待实现 | 通信协作，One-Hot |
| Simple World Comm | `parse_world_comm_obs.py` | ⏳ 待实现 | 复杂环境，多种地标 |
| Simple (Basic) | `parse_simple_obs.py` | ⏳ 待实现 | 基础协作 |

## 🎓 最佳实践

### 1. 使用辅助函数

优先使用 `obs/utils.py` 中的函数，避免重复代码：

```python
from obs.utils import get_vector_info, assess_threat_level

# 好的做法 ✅
info = get_vector_info(dx, dy)

# 不推荐 ❌
info = {
    'relative_position': [dx, dy],
    'distance': math.sqrt(dx**2 + dy**2),
    'direction': '...'  # 手动判断
}
```

### 2. 添加详细描述

每个解析的字段都应该有 `description` 字段：

```python
{
    "id": 0,
    "relative_position": [0.5, 0.3],
    "distance": 0.58,
    "direction": "UP-RIGHT",
    "description": "地标 0 在你的右上方，距离 0.58"  # ✅ 好
}
```

### 3. 提供战术建议

在 JSON 中添加 `tactical_hint` 字段，帮助 LLM 理解当前局势：

```python
struct['tactical_hint'] = (
    "敌人距离目标更近，你应该采用诱饵策略，"
    "前往假地标吸引敌人注意力！"
)
```

### 4. 保持格式一致

所有解析器应该遵循相同的 JSON 结构标准，便于统一处理。

## 🐛 调试技巧

### 1. 使用 `print_raw_observation()`

```python
from obs.utils import print_raw_observation

segments = [
    ("速度", 2),
    ("位置", 2),
    ("地标", 4),
    ("其他智能体", 4)
]

print_raw_observation(obs, agent_id, segments)
```

### 2. 对比原始数据和解析结果

```python
print("原始:", np.round(obs_raw, 2))
print("解析:", json.dumps(obs_struct, indent=2))
```

### 3. 多次 reset 验证

```python
for i in range(3):
    obs, _ = env.reset()
    parsed = parse_obs(obs['agent_0'], 'agent_0')
    print(f"Reset {i}: {parsed['landmarks'][0]['distance']}")
```

## 📚 相关文档

- [OBS_PARSING_GUIDE.md](../OBS_PARSING_GUIDE.md) - 详细的开发指南
- [PROJECT_OVERVIEW.md](../PROJECT_OVERVIEW.md) - 项目整体概览
- [PettingZoo MPE 文档](https://pettingzoo.farama.org/environments/mpe/)

## 🤝 贡献

欢迎贡献新的解析器！步骤：
1. Fork 仓库
2. 创建 `parse_<env>_obs.py`
3. 遵循现有格式和最佳实践
4. 提交 Pull Request

---

**维护者**: HuangShengZeBlueSky  
**最后更新**: 2026-01-24

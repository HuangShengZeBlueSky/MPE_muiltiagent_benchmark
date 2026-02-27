# MPE 多智能体基准测试 - 日志格式汇总文档

## 概述

本文档详细记录了9个MPE环境的：
1. **观测解析（OBS）格式** - 原始观测向量被解析成的结构化格式
2. **日志记录（LOG）格式** - 游戏运行过程中保存到JSON文件的结构
3. **奖励记录位置** - 奖励值在日志中的具体位置

---

## 1. 观测解析格式（OBS Parsing Format）

### 1.1 Spread (spread_API.py)

**环境**：3个智能体协作覆盖地标

**OBS解析文件**：`obs/parse_spread_obs.py`

**原始观测**：`[self_vel(2), self_pos(2), landmark_rel(2N), other_agent_rel(2(N-1)), comm(2(N-1))]`

**解析后格式**：
```python
{
    "self_vel": [vx, vy],                    # 自身速度
    "self_pos": [px, py],                    # 自身位置（冗余）
    "landmark_rel": [                        # N个地标
        [dx, dy, dist],                      # 相对位置和距离
        ...
    ],
    "other_agent_rel": [                     # N-1个队友
        [dx, dy, dist],                      # 相对位置和距离
        ...
    ]
}
```

---

### 1.2 Tag (tag_API.py)

**环境**：1个猎物 vs 3个捕食者的追逐游戏

**OBS解析文件**：`obs/parse_tag_obs.py`

**原始观测**：`[self_vel(2), self_pos(2), obstacles_rel(2*num_obstacles), other_agents_rel(2*(total_agents-1))]`

**解析后格式**：
```python
# 猎物（Prey）角色
{
    "self_vel": [vx, vy],
    "self_pos": [px, py],
    "obstacles_rel": [
        [dx, dy, dist],
        ...
    ],
    "enemies": [                             # 3个捕食者
        [dx, dy, dist],
        ...
    ]
}

# 捕食者（Predator）角色
{
    "self_vel": [vx, vy],
    "self_pos": [px, py],
    "obstacles_rel": [
        [dx, dy, dist],
        ...
    ],
    "enemies": [                             # 1个猎物
        [dx, dy, dist]
    ],
    "teammates": [                           # 2个队友捕食者
        [dx, dy, dist],
        ...
    ]
}
```

---

### 1.3 World Comm (world_comm.py)

**环境**：多角色通信（LEADER、HUNTER、PREY）

**OBS解析文件**：`obs/parse_world_comm_obs.py`

**原始观测**：根据角色不同长度不同

**解析后格式**：
```python
# PREY角色
{
    "role": "PREY",
    "self": {
        "velocity": [vx, vy],
        "position": [px, py],
        "in_bounds": true/false
    },
    "landmarks": {
        "obstacle": [dx, dy],
        "food_1": [dx, dy],
        "food_2": [dx, dy],
        "forest_1": [dx, dy],
        "forest_2": [dx, dy]
    },
    "enemies": [                             # 4个敌人
        {
            "id": "threat_0",
            "rel": [dx, dy],
            "dist": d,
            "status": "VISIBLE/HIDDEN"
        },
        ...
    ]
}

# LEADER/HUNTER角色
{
    "role": "LEADER/HUNTER",
    "self": {...},
    "landmarks": {...},
    "teammates": [                           # 其他3个捕食者
        {
            "id": "teammate_0",
            "rel": [dx, dy],
            "dist": d,
            "status": "VISIBLE/HIDDEN"
        },
        ...
    ],
    "enemies": [                             # 2个猎物
        {
            "id": "prey_0",
            "rel": [dx, dy],
            "dist": d,
            "status": "VISIBLE/HIDDEN"
        },
        ...
    ],
    "communication": {                       # HUNTER专有
        "signal": [s1, s2, s3, s4],
        "active": true/false
    }
}
```

---

### 1.4 Adversary (adv_API.py)

**环境**：对抗游戏（3个好人 vs 1个坏人）

**OBS解析文件**：`obs/parse_adv_obs.py`

**原始观测**：根据角色不同

**解析后格式**：
```python
# GOOD_AGENT角色
{
    "role": "GOOD_AGENT",
    "goal": {
        "rel": [dx, dy],
        "dist": d
    },
    "landmarks": [
        {
            "id": 0,
            "rel": [dx, dy],
            "dist": d,
            "is_target": true/false
        },
        ...
    ],
    "adversary": {
        "rel": [dx, dy],
        "dist": d
    },
    "teammate": {
        "id": "agent_x",
        "rel": [dx, dy],
        "dist": d
    }
}

# ADVERSARY角色
{
    "role": "ADVERSARY",
    "landmarks": [
        {
            "id": 0,
            "rel": [dx, dy],
            "dist": d
        },
        ...
    ],
    "good_agents": [
        {
            "id": "agent_0",
            "rel": [dx, dy],
            "dist": d
        },
        ...
    ]
}
```

---

### 1.5 Crypto (crypto.py)

**环境**：密码学通信（Alice、Bob、Eve）

**OBS解析文件**：`obs/parse_crypto_obs.py`

**原始观测**：`[raw_values(4-8)]` 根据角色不同

**解析后格式**：
```python
# ALICE角色
{
    "role": "ALICE",
    "raw": [rounded_values],
    "message": [m1, m2, m3, m4],            # 待发送消息
    "key": [k1, k2, k3, k4]                 # 密钥
}

# BOB角色
{
    "role": "BOB",
    "raw": [rounded_values],
    "key": [k1, k2, k3, k4],                # 密钥
    "ciphertext": [c1, c2, c3, c4]         # 收到的密文
}

# EVE角色
{
    "role": "EVE",
    "raw": [rounded_values],
    "ciphertext": [c1, c2, c3, c4]         # 窃听的密文
}
```

---

### 1.6 Push (push.py)

**环境**：推动对抗游戏

**OBS解析文件**：`obs/parse_push_obs.py`

**原始观测**：根据角色不同（8维或19维）

**解析后格式**：
```python
# ADVERSARY角色
{
    "role": "ADVERSARY",
    "vel": [vx, vy],
    "speed": d,
    "landmarks": [
        {
            "id": "LM_A",
            "rel": [dx, dy],
            "dist": d
        },
        {
            "id": "LM_B",
            "rel": [dx, dy],
            "dist": d
        }
    ],
    "opponent_rel": [dx, dy],
    "opponent_dist": d
}

# GOOD_AGENT角色
{
    "role": "GOOD_AGENT",
    "vel": [vx, vy],
    "speed": d,
    "goal_rel": [dx, dy],
    "goal_dist": d,
    "fake_rel": [dx, dy],                   # 干扰地标
    "fake_dist": d,
    "opponent_rel": [dx, dy],
    "opponent_dist": d
}
```

---

### 1.7 Simple (simple.py)

**环境**：单智能体导航

**OBS解析文件**：`obs/parse_simple_obs.py`

**原始观测**：`[vel_x, vel_y, rel_x, rel_y]`

**解析后格式**：
```python
{
    "vel": [vx, vy],                        # 速度
    "landmark_rel": [dx, dy, dist]         # 相对位置和距离
}
```

---

### 1.8 Reference (reference.py)

**环境**：参考通信任务

**OBS解析文件**：`obs/parse_reference_obs.py`

**原始观测**：`[vel(2), landmarks(6), partner_goal_rgb(3), comm(10)]` (共21维)

**解析后格式**：
```python
{
    "vel": [vx, vy],
    "landmarks": [
        {
            "id": 0,
            "color_name": "Red/Green/Blue",
            "rel": [dx, dy],
            "dist": d
        },
        ...
    ],
    "partner_goal_rgb": [r, g, b],          # 伙伴的目标RGB值
    "partner_target_id": 0,                 # 推断的目标地标ID
    "heard_signal": -1,                     # 接收到的信号ID，-1表示未收到
    "signal_strength": 0.0                  # 信号强度
}
```

---

### 1.9 Speaker-Listener (speaker_listener.py)

**环境**：说话者-听话者通信

**OBS解析文件**：`obs/parse_speaker_listener_obs.py`

**原始观测**：根据角色不同（3维或11维）

**解析后格式**：
```python
# SPEAKER角色
{
    "role": "SPEAKER",
    "goal_vector": [g1, g2, g3],            # 独热编码目标地标
    "target_landmark_id": 0,                # 目标地标ID
    "raw": [raw_values],
    "raw_len": 3
}

# LISTENER角色
{
    "role": "LISTENER",
    "vel": [vx, vy],
    "landmarks": [
        {
            "id": 0,
            "rel": [dx, dy]
        },
        ...
    ],
    "comm_vector": [c1, c2, c3],            # 通信向量
    "heard_id": -1,                         # 推断的信号ID
    "raw": [raw_values],
    "raw_len": 11
}
```

---

## 2. 日志记录格式（LOG Format）

### 统一日志结构

每局游戏保存为JSON文件，包含：
- **每一步的记录**：多个 Step Entry
- **最终汇总**：一个 Final Summary Entry

#### Step Entry（每一步）
```json
{
    "step": 0,                              // 当前步数
    "agent": "agent_0",                     // 智能体ID
    "obs": {...},                           // 解析后的观测
    "action": [0.1, 0.2, ...],              // 动作（连续向量）
    "thought": "reasoning...",              // LLM的推理过程
    "reward": 1.5                           // **此步的奖励**
}
```

#### Final Summary Entry（游戏结束）
```json
{
    "final_summary": true,
    "total_rewards": {                      // 所有智能体的累计奖励
        "agent_0": 10.5,
        "agent_1": 12.3,
        ...
    },
    "mean_reward": 8.3                      // 平均奖励
}
```

---

### 游戏特定的日志说明

#### 2.1 Spread (spread_API.py)
**日志格式**：标准格式

**奖励记录**：
- 位置：每个Step Entry中的 `"reward"` 字段
- 含义：该步智能体获得的奖励
- Final Summary中的 `total_rewards`：按智能体ID汇总
- 计算方式：`mean_reward = sum(total_rewards.values()) / len(total_rewards)`

**示例**：
```json
{
    "step": 0,
    "agent": "agent_0",
    "obs": {...},
    "action": [0.1, 0.2, 0.3, 0.4, 0.5],
    "thought": "Move towards landmark 1",
    "reward": 0.05
}
```

---

#### 2.2 Tag (tag_API.py)
**日志格式**：标准格式

**奖励记录**：
- 位置：每个Step Entry中的 `"reward"` 字段
- **不同角色的奖励**：
  - Prey（猎物）：逃脱奖励
  - Predator（捕食者）：抓捕奖励
- Final Summary中：
  ```json
  {
      "total_rewards": {
          "prey": -5.0,           // 猎物总奖励（负值表示被追）
          "predators": 3.5        // 捕食者总奖励（平均值）
      },
      "mean_reward": -0.75
  }
  ```

**示例**：
```json
{
    "step": 0,
    "agent": "prey_0",
    "role": "prey",
    "obs": {...},
    "action": [0.0, 0.0, 1.0, 0.0, 0.0],
    "thought": "Escape left",
    "reward": -0.1
}
```

---

#### 2.3 World Comm (world_comm.py)
**日志格式**：标准格式

**奖励记录**：
- 位置：每个Step Entry中的 `"reward"` 字段
- **三种角色**：LEADER、HUNTER、PREY
- 各角色有不同的奖励机制
- Final Summary：汇总所有角色

**示例**：
```json
{
    "step": 0,
    "agent": "agent_adversary_lead",
    "role": "LEADER",
    "obs": {...},
    "action": [0.5, 0.2, 0.3, 0.1],
    "thought": "Move towards prey",
    "reward": 0.2
}
```

---

#### 2.4 Adversary (adv_API.py)
**日志格式**：标准格式

**奖励记录**：
- 位置：每个Step Entry中的 `"reward"` 字段
- **两种角色**：
  - GOOD_AGENT（3个）：保护目标奖励
  - ADVERSARY（1个）：破坏奖励
- Final Summary：
  ```json
  {
      "total_rewards": {
          "good": 8.5,        // 好人总奖励
          "adversary": 2.1    // 坏人总奖励
      },
      "mean_reward": 5.3
  }
  ```

---

#### 2.5 Crypto (crypto.py)
**日志格式**：标准格式

**奖励记录**：
- 位置：每个Step Entry中的 `"reward"` 字段
- **三种角色**：ALICE、BOB、EVE
- 各自独立的奖励
- Final Summary：
  ```json
  {
      "total_rewards": {
          "alice_0": 1.0,
          "bob_0": 0.8,
          "eve_0": -0.5
      },
      "mean_reward": 0.43
  }
  ```

---

#### 2.6 Push (push.py)
**日志格式**：标准格式

**奖励记录**：
- 位置：每个Step Entry中的 `"reward"` 字段
- **两种角色**：
  - GOOD_AGENT（1个）
  - ADVERSARY（1个）
- Final Summary：
  ```json
  {
      "total_rewards": {
          "good": 5.2,
          "adversary": 3.1
      },
      "mean_reward": 4.15
  }
  ```

---

#### 2.7 Simple (simple.py)
**日志格式**：标准格式

**奖励记录**：
- 位置：每个Step Entry中的 `"reward"` 字段
- 单智能体环境
- Final Summary：
  ```json
  {
      "total_rewards": {
          "agent_0": 28.5
      },
      "mean_reward": 28.5
  }
  ```

---

#### 2.8 Reference (reference.py)
**日志格式**：标准格式

**奖励记录**：
- 位置：每个Step Entry中的 `"reward"` 字段
- 两个智能体（Speaker和Listener）
- Final Summary：
  ```json
  {
      "total_rewards": {
          "speaker_0": 2.5,
          "listener_0": 3.2
      },
      "mean_reward": 2.85
  }
  ```

---

#### 2.9 Speaker-Listener (speaker_listener.py)
**日志格式**：标准格式

**奖励记录**：
- 位置：每个Step Entry中的 `"reward"` 字段
- **两种角色**：SPEAKER、LISTENER
- Final Summary：
  ```json
  {
      "total_rewards": {
          "speaker_0": 1.8,
          "listener_0": 2.1
      },
      "mean_reward": 1.95
  }
  ```

---

## 3. 快速参考表

| 游戏 | OBS维数 | 主要角色 | 智能体数 | 日志奖励位置 | Final Summary |
|------|--------|--------|--------|-----------|--------------|
| Spread | 6N | 单一 | N(=3) | `"reward"` | 按ID汇总 |
| Tag | 4+2N+4(N-1) | Prey/Predator | 4 | `"reward"` | 角色汇总 |
| World Comm | 可变 | LEADER/HUNTER/PREY | 6 | `"reward"` | 全部ID汇总 |
| Adversary | 可变 | GOOD/ADVERSARY | 4 | `"reward"` | 角色汇总 |
| Crypto | 4-8 | ALICE/BOB/EVE | 3 | `"reward"` | 全部ID汇总 |
| Push | 8/19 | GOOD/ADVERSARY | 2 | `"reward"` | 角色汇总 |
| Simple | 4 | 单一 | 1 | `"reward"` | 全部ID汇总 |
| Reference | 21 | SPEAKER/LISTENER | 2 | `"reward"` | 全部ID汇总 |
| Speaker-Listener | 3/11 | SPEAKER/LISTENER | 2 | `"reward"` | 全部ID汇总 |

---

## 4. 日志文件示例

### 完整的JSON日志示例

```json
[
  {
    "step": 0,
    "agent": "agent_0",
    "obs": {
      "self_vel": [0.1, -0.05],
      "self_pos": [0.2, -0.1],
      "landmark_rel": [
        [0.5, 0.3, 0.58],
        [-0.2, 0.4, 0.45],
        [0.1, -0.6, 0.61]
      ],
      "other_agent_rel": [
        [0.3, 0.2, 0.36],
        [-0.1, 0.5, 0.51]
      ]
    },
    "action": [0.0, 0.5, 0.2, 0.3, 0.0],
    "thought": "Move towards the closest landmark at position [0.5, 0.3]",
    "reward": 0.08
  },
  {
    "step": 1,
    "agent": "agent_0",
    "obs": {...},
    "action": [0.0, 0.4, 0.3, 0.2, 0.1],
    "thought": "Continue moving while avoiding teammates",
    "reward": 0.12
  },
  {
    "final_summary": true,
    "total_rewards": {
      "agent_0": 2.45,
      "agent_1": 2.38,
      "agent_2": 2.52
    },
    "mean_reward": 2.45
  }
]
```

---

## 5. 注意事项

1. **奖励的含义**：
   - 不同游戏的奖励尺度不同
   - Spread：通常为小数值（0.01-0.1）
   - Tag：可能为负值（逃脱失败）
   - 需要了解环境的具体奖励机制

2. **多角色奖励**：
   - Tag、Adversary、Push、World Comm等有多种角色
   - 不同角色的奖励可能存在对立性（零和）
   - Mean Reward通常是对称聚合

3. **OBS结构一致性**：
   - 所有环境都包含相对位置 `[dx, dy, dist]`
   - 距离预计算方便LLM判断
   - 结构化格式增强了可解释性

4. **视频和日志保存**：
   - 视频：`{output_name}.mp4` 格式，FPS根据环境调整
   - 日志：`{output_name}.json` 格式，UTF-8编码
   - 两者都有自动编号以避免覆盖


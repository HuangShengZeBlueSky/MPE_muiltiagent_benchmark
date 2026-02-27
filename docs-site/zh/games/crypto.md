# Crypto — 加密通信

::: info 环境信息
- **PettingZoo 名称**: `simple_crypto_v3`
- **智能体**: Alice (加密者) + Bob (解密者) + Eve (窃听者)
- **类型**: 通信安全 + 三方博弈
- **动作维度**: 4 (而非 5)
:::

## 游戏目标

这是一个独特的**信息安全博弈**环境，模拟加密通信场景。

### Alice — 加密者
- **看到**: 秘密消息 M (4维向量) + 私钥 K (4维向量)
- **任务**: 将 M 与 K 混合得到密文 C，使 Bob 能还原、Eve 不能猜出

### Bob — 解密者
- **看到**: 私钥 K + 密文 C (Alice 上一步的输出)
- **任务**: 用 K 逆向操作还原 M

### Eve — 窃听者
- **看到**: 仅密文 C (没有私钥)
- **任务**: 从 C 中猜测 M

## 观测空间

| 角色 | 观测内容 | 维度 |
|:----:|:---------|:----:|
| Alice | `message` (M): 4维 + `key` (K): 4维 | 8 |
| Bob | `key` (K): 4维 + `ciphertext` (C): 4维 | 8 |
| Eve | `ciphertext` (C): 4维 | 4 |

### 观测解析代码

```python
# obs/parse_crypto_obs.py
def parse_crypto_obs(obs, role):
    if role == "ALICE":
        return {
            "message": obs[0:4].tolist(),  # 秘密消息 M
            "key": obs[4:8].tolist(),      # 私钥 K
        }
    elif role == "BOB":
        return {
            "key": obs[0:4].tolist(),          # 私钥 K
            "ciphertext": obs[4:8].tolist(),   # 密文 C (Alice 输出)
        }
    else:  # EVE
        return {
            "ciphertext": obs[0:4].tolist(),   # 密文 C
        }
```

::: warning 时序延迟
Bob 看到的密文 C 是 Alice **上一步**发出的，存在一帧延迟。
:::

## 奖励函数

| 角色 | 奖励逻辑 |
|:----:|:---------|
| Alice & Bob | Bob 正确还原 M → 高奖励，Eve 猜对 M → 低奖励 |
| Eve | 猜测越接近 M → 越高奖励 |

## 动作空间

::: warning 注意
Crypto 的动作维度是 **4** (不是 5)！没有运动动作，纯粹是信号输出。
:::

| 角色 | 输出含义 | 维度 |
|:----:|:---------|:----:|
| Alice | 密文 C (加密后的信号) | 4 |
| Bob | 消息猜测 M̂ | 4 |
| Eve | 消息猜测 M̂ | 4 |

## 提示词策略

### Alice 策略
```
- 将 M 和 K 以可逆的方式混合（如加法/异或取模）
- 避免直接输出原始消息
- 简单方法: C = (M + K) mod 1.0
```

### Bob 策略
```
- 用共享密钥 K 逆转 Alice 的操作
- 例如: M = (C - K) mod 1.0
- 确保结果在 [0, 1] 范围内
```

### Eve 策略
```
- 没有密钥，只能分析密文模式
- 猜测最可能的消息
```

## 运行方式

```bash
python crypto.py
```

# Crypto — Encrypted Communication

::: info Environment
- **PettingZoo**: `simple_crypto_v3` | **Agents**: Alice + Bob + Eve | **Action Dim**: 4
:::

## Objective
- **Alice**: Encrypts message M with key K → ciphertext C
- **Bob**: Decrypts C using shared key K → recovers M
- **Eve**: Intercepts C (no key) → guesses M

## Action: 4D vector ∈ [0,1]⁴

## Run
```bash
python crypto.py
```

---

# Reference — Bidirectional Communication

::: info Environment
- **PettingZoo**: `simple_reference_v3` | **Agents**: 2 (dual role) | **Action Dim**: 15
:::

## Objective
Each agent sees the OTHER agent's target color and broadcasts a signal to help them navigate.

**Action**: 15D = 5 (movement) + 10 (communication)

## Run
```bash
python reference.py
```

---

# Speaker-Listener — Unidirectional Communication

::: info Environment
- **PettingZoo**: `simple_speaker_listener_v4` | **Agents**: 1 Speaker + 1 Listener
:::

## Objective
- **Speaker**: Sees target (one-hot) → emits 3D signal
- **Listener**: Sees landmarks + receives signal → navigates to target

## Run
```bash
python speaker_listener.py
```

---

# World Comm — Large-Scale Coordination

::: info Environment
- **PettingZoo**: `simple_world_comm_v3` | **Agents**: 4 Adversary (1 Leader + 3 Hunter) + 2 Prey
:::

## Objective
| Role | Action Dim | Goal |
|:----:|:----------:|:-----|
| **Leader** | 9 (5 move + 4 comm) | Broadcast prey coordinates |
| **Hunter** | 5 | Chase prey using leader signals |
| **Prey** | 5 | Evade hunters, reach food |

## Run
```bash
python world_comm.py
```

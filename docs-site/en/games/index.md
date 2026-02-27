# Game Environments Overview

This project includes 9 classic multi-agent game scenarios.

## Environment Summary

| # | Game | Type | Agents | Challenge | Comm | Action Dim |
|:-:|:-----|:-----|:------:|:----------|:----:|:----------:|
| 1 | [Simple](/en/games/simple) | Navigation | 1 | Navigate to landmark | ✗ | 5 |
| 2 | [Spread](/en/games/spread) | Cooperative | N (3) | Cover landmarks + avoid collisions | ✗ | 5 |
| 3 | [Adversary](/en/games/adversary) | Adversarial | 1+N | Deception & inference | ✗ | 5 |
| 4 | [Push](/en/games/push) | Adversarial | 1+1 | Physical blocking | ✗ | 5 |
| 5 | [Tag](/en/games/tag) | Chase | 3+1 | Cooperative hunting vs evasion | ✗ | 5 |
| 6 | [Crypto](/en/games/crypto) | Communication | 3 | Encryption vs eavesdropping | ✓ | 4 |
| 7 | [Reference](/en/games/reference) | Communication | 2 | Bidirectional signaling | ✓ | 15 |
| 8 | [Speaker-Listener](/en/games/speaker-listener) | Communication | 1+1 | Unidirectional navigation | ✓ | 3/5 |
| 9 | [World Comm](/en/games/world-comm) | Large-scale | 4+2 | Leader broadcast + team hunting | ✓ | 9/5 |

## Common Physics

| Parameter | Value | Description |
|:----------|:-----:|:------------|
| Time step `dt` | 0.1 | Per-step simulation time |
| Damping | 0.25 | Velocity decay: `v ← 0.75 × v` |
| Mass | 1.0 | Default agent mass |
| Sensitivity | 5.0 | Action-to-force multiplier |
| Map bounds | [-1, 1]² | X, Y range |

## Common Action Space

5D continuous: `[no_op, left, right, down, up]` ∈ [0,1]⁵

Net force: `F_x = (right - left) × sensitivity`, `F_y = (up - down) × sensitivity`

::: warning Important
- Never activate opposing directions simultaneously
- Reduce thrust when approaching target
- Thrust toward center when near boundaries (|x| or |y| > 0.9)
:::

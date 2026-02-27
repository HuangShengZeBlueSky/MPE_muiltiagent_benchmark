# Adversary — Deception & Inference

::: info Environment
- **PettingZoo**: `simple_adversary_v3` | **Agents**: 1 Adversary + N Good (default 2)
:::

<video controls width="100%" style="max-width: 640px; border-radius: 8px;">
  <source src="/MPE_muiltiagent_benchmark/videos/adversary_ep1.mp4" type="video/mp4">
  Your browser does not support the video tag.
</video>

## Objective
- **Good Agents**: Know the target; deceive Adversary by splitting (Scorer + Decoy)
- **Adversary**: Doesn't know target; must infer from Good Agents' behavior

**Zero-sum**: Good wants Adversary far from target; Adversary wants to be close.

## Key Observations
- **Good Agent**: Has `goal` field (target landmark position) — unique advantage
- **Adversary**: Sees all landmarks but no goal indicator

## Run
```bash
python adv_API.py
```

# Leadboard 评测报告

> 基于 `results/batch_benchmarks` 自动分析结果（模型：Gemini-3.0-Flash、kimi-k2.5、Qwen-3-Max、GLM-5）。

## 总览指标（按游戏）

| 模型 | 游戏 | 局数 | 局均值reward均值 | 方差 | 标准差 |
|---|---|---:|---:|---:|---:|
| Gemini-3.0-Flash | spread | 10 | -10.7402 | 13.9505 | 3.7350 |
| Gemini-3.0-Flash | adversary | 10 | -4.7327 | 10.3400 | 3.2156 |
| Gemini-3.0-Flash | tag | 10 | -0.2543 | 0.3035 | 0.5509 |
| kimi-k2.5 | spread | 10 | -31.6489 | 144.8989 | 12.0374 |
| kimi-k2.5 | adversary | 10 | -4.2067 | 3.0735 | 1.7531 |
| kimi-k2.5 | tag | 10 | -18.0182 | 313.0068 | 17.6920 |
| Qwen-3-Max | spread | 10 | -31.5752 | 57.3940 | 7.5759 |
| Qwen-3-Max | adversary | 10 | -4.1179 | 3.2433 | 1.8009 |
| Qwen-3-Max | tag | 10 | -20.9668 | 1181.0470 | 34.3664 |
| GLM-5 | spread | 10 | -37.7828 | 1145.1536 | 33.8401 |
| GLM-5 | adversary | 3 | -5.2547 | 9.5095 | 3.0837 |
| GLM-5 | tag | 10 | -1.5713 | 0.9724 | 0.9861 |

## ADV / TAG 双阵营结果

| 模型 | 游戏 | 阵营 | 平均总回报 | 方差 |
|---|---|---|---:|---:|
| Gemini-3.0-Flash | adversary | adversary | -23.2055 | 161.4644 |
| Gemini-3.0-Flash | adversary | good | 13.7400 | 121.7719 |
| kimi-k2.5 | adversary | adversary | -20.8570 | 129.2991 |
| kimi-k2.5 | adversary | good | 12.4436 | 111.4178 |
| Qwen-3-Max | adversary | adversary | -23.5216 | 374.3965 |
| Qwen-3-Max | adversary | good | 15.2857 | 288.5656 |
| Gemini-3.0-Flash | tag | predators | 34.0000 | 304.0000 |
| Gemini-3.0-Flash | tag | prey | -34.5085 | 311.5919 |
| kimi-k2.5 | tag | predators | 18.0000 | 436.0000 |
| kimi-k2.5 | tag | prey | -54.0364 | 1459.0762 |
| Qwen-3-Max | tag | predators | 11.0000 | 149.0000 |
| Qwen-3-Max | tag | prey | -52.9335 | 4413.0228 |
| GLM-5 | adversary | adversary | -28.1869 | 2.8213 |
| GLM-5 | adversary | good | 17.6776 | 42.1650 |
| GLM-5 | tag | predators | 11.0000 | 109.0000 |
| GLM-5 | tag | prey | -14.1426 | 99.9089 |

![ADV_TAG_Camp](/leadboard/camp_breakdown_adv_tag.png)

## 每步长奖励变化（10局平均）

### Gemini-3.0-Flash
![Gemini-Step](/leadboard/step_curve_Gemini-3.0-Flash.png)

### kimi-k2.5
![Kimi-Step](/leadboard/step_curve_kimi-k2.5.png)

### Qwen-3-Max
![Qwen-Step](/leadboard/step_curve_Qwen-3-Max.png)

### GLM-5
![GLM-Step](/leadboard/step_curve_GLM-5.png)

## 全局趋势图

![Reward-Trend](/leadboard/reward_trend_by_game.png)

![Reward-Mean-Std](/leadboard/reward_mean_std.png)

## 数据说明

- `tag` 的 `mean_reward` 可能接近 0，是因为常见 `predators=+X` 与 `prey=-X` 对消。
- 在当前日志中，Gemini 的 `tag_ep1_1.json` 出现了 `predators=0, prey=0` 的回合。
- 页面资源图来自 `results/batch_benchmarks/plots`，已复制到 `docs-site/public/leadboard/`。
- GLM-5 当前 `adversary` 仅有 `3` 局有效结果，跨模型比较时需考虑样本量差异。

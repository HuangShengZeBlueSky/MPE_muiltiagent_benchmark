---
layout: home
hero:
  name: MPE Multi-Agent Benchmark
  text: LLM 驱动的多智能体粒子环境基准测试
  tagline: 将大语言模型作为智能体「大脑」，在 9 个经典多智能体场景中进行零样本推理
  actions:
    - theme: brand
      text: 快速开始 →
      link: /zh/guide/quickstart
    - theme: alt
      text: 游戏环境
      link: /zh/games/
    - theme: alt
      text: GitHub
      link: https://github.com/your-repo/MPE_muiltiagent_benchmark

features:
  - icon: 🎯
    title: 9 个游戏环境
    details: 覆盖协作、对抗、通信、欺骗等多智能体博弈范式，全面评估 LLM 的多智能体推理能力
  - icon: 🤖
    title: 多 LLM 后端
    details: 支持 DeepSeek / Qwen / GPT / Gemini / Ollama / Transformers / vLLM 等主流模型
  - icon: 📊
    title: 结构化输出
    details: 每轮保存 JSON 日志（观测、思维链、动作、奖励）和 MP4 视频，完整记录决策过程
  - icon: 🧩
    title: 模块化提示词
    details: 每个游戏提示词解耦为任务目标、物理规则、动作格式、导航策略四大模块
  - icon: 🔄
    title: 批量评测
    details: benchmark_runner.py 支持多轮次 × 多种子 × 跨环境汇总统计
  - icon: 🌐
    title: 零样本推理
    details: 无需训练，LLM 直接根据文本描述生成连续动作，对标传统 RL 策略
---

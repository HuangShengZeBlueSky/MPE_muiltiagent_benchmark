---
layout: home
hero:
  name: MPE Multi-Agent Benchmark
  text: LLM-Driven Multi-Agent Particle Environment Benchmark
  tagline: Using LLMs as agent "brains" for zero-shot reasoning across 9 classic multi-agent game scenarios
  actions:
    - theme: brand
      text: Quick Start →
      link: /en/guide/quickstart
    - theme: alt
      text: Game Environments
      link: /en/games/
    - theme: alt
      text: GitHub
      link: https://github.com/your-repo/MPE_muiltiagent_benchmark

features:
  - icon: 🎯
    title: 9 Game Environments
    details: Covering cooperation, competition, communication, and deception paradigms for comprehensive LLM evaluation
  - icon: 🤖
    title: Multi-LLM Backend
    details: Support for DeepSeek / Qwen / GPT / Gemini / Ollama / Transformers / vLLM
  - icon: 📊
    title: Structured Output
    details: JSON logs (observation, chain-of-thought, action, reward) + MP4 video per episode
  - icon: 🧩
    title: Modular Prompts
    details: Each game's prompt decomposed into task, physics, action format, and navigation modules
  - icon: 🔄
    title: Batch Evaluation
    details: benchmark_runner.py supports N episodes × multiple seeds × cross-environment aggregation
  - icon: 🌐
    title: Zero-Shot Reasoning
    details: No training needed — LLMs directly generate continuous actions from text descriptions
---

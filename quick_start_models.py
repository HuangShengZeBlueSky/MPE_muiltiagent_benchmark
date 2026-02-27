#!/usr/bin/env python3
"""
快速开始：切换不同模型运行 Spread 游戏
"""

from spread_API import run_spread_game

# ============================================================
# 方式 1: 远程 API (推荐用于快速测试)
# ============================================================

# Qwen (阿里通义千问) - 默认配置已包含 API Key
run_spread_game("qwen", "demo_qwen.mp4")

# DeepSeek - 需要提供你的 API Key
# run_spread_game("deepseek", "demo_deepseek.mp4", api_key="sk-your-key")

# GPT (OpenAI) - 需要提供你的 API Key
# run_spread_game("gpt", "demo_gpt.mp4", api_key="sk-your-key", model_name="gpt-4o")

# Gemini (Google) - 需要提供你的 API Key
# run_spread_game("gemini", "demo_gemini.mp4", api_key="your-key")


# ============================================================
# 方式 2: 本地模型 - Ollama (推荐用于本地开发)
# ============================================================
# 前提: 先安装并启动 Ollama
# 1. 安装: https://ollama.com
# 2. 拉取模型: ollama pull qwen2.5:7b
# 3. 运行:

# run_spread_game("ollama", "demo_ollama.mp4", model_name="qwen2.5:7b")

# 或使用其他 Ollama 模型
# run_spread_game("ollama", "demo_llama.mp4", model_name="llama3.1:8b")


# ============================================================
# 方式 3: 本地模型 - Transformers (完全离线)
# ============================================================
# 前提: pip install transformers torch accelerate

# 方式 3.1: 使用 Hugging Face Hub 自动下载
# run_spread_game(
#     "transformers",
#     "demo_transformers.mp4",
#     model_path="Qwen/Qwen2.5-7B-Instruct",  # 或其他 HF 模型
#     device="cuda"  # 或 "cpu", "auto"
# )

# 方式 3.2: 使用本地已下载的模型
# run_spread_game(
#     "transformers",
#     "demo_transformers.mp4",
#     model_path="/path/to/local/model",
#     device="cuda"
# )

# 方式 3.3: 使用 CPU (内存较小的模型)
# run_spread_game(
#     "transformers",
#     "demo_transformers.mp4",
#     model_path="Qwen/Qwen2.5-1.5B-Instruct",
#     device="cpu"
# )


# ============================================================
# 方式 4: 本地模型 - vLLM (高性能批量推理)
# ============================================================
# 前提: pip install vllm (需要 CUDA GPU)

# run_spread_game(
#     "vllm",
#     "demo_vllm.mp4",
#     model_path="meta-llama/Llama-3-8B",
#     tensor_parallel_size=2  # 使用 2 张 GPU
# )


# ============================================================
# 自定义参数
# ============================================================
# 可以调整游戏参数
# run_spread_game(
#     "qwen",
#     "demo_custom.mp4",
#     N=4,  # 4 个智能体
#     local_ratio=0.3,  # 调整奖励权重
#     temperature=0.8,  # 调整模型创造性
#     max_tokens=2048  # 调整最大生成长度
# )


print("""
✅ 统一接口已就绪！

📝 快速切换模型的方法:

1. 远程 API (最简单):
   run_spread_game("qwen", "output.mp4")

2. 本地 Ollama (本地开发):
   run_spread_game("ollama", "output.mp4", model_name="qwen2.5:7b")

3. 本地 Transformers (完全离线):
   run_spread_game("transformers", "output.mp4", 
                   model_path="Qwen/Qwen2.5-7B-Instruct")

4. 高性能 vLLM (大规模推理):
   run_spread_game("vllm", "output.mp4", 
                   model_path="meta-llama/Llama-3-8B")

📖 更多详情请查看: MODEL_USAGE_GUIDE.md
""")

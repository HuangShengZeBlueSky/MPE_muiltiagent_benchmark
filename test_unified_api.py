#!/usr/bin/env python3
"""
模型接口统一测试示例
展示如何使用 get_api_engine 统一接口调用不同模型
"""

from utils_api import get_api_engine
import numpy as np

def test_model(provider: str, **kwargs):
    """测试指定模型的接口"""
    print("=" * 60)
    print(f"测试模型: {provider}")
    print("=" * 60)
    
    try:
        # 初始化引擎
        
        engine = get_api_engine(provider, **kwargs)
        print(f"✓ 模型加载成功")
        print(f"  Provider: {engine.provider}")
        print(f"  Model: {engine.model_name}")
        
        
        # 简单推理测试
        system_prompt = "You are a decision module for a game agent. Output only one-line JSON."
        user_prompt = '{"action": [0.0, 0.0, 0.5, 0.0, 0.0], "notes": "test"}\nGenerate a similar JSON with different action values.'
        
        print("\n发送推理请求...")
        action_vec, response = engine.generate_action(
            system_prompt,
            user_prompt,
            temperature=0.7,
            max_tokens=200,
            max_retries=2
        )
        
        print(f"✓ 推理成功")
        print(f"  Action: {action_vec}")
        print(f"  Response: {response[:100]}...")
        
        return True
        
    except Exception as e:
        print(f"✗ 测试失败: {e}")
        return False


if __name__ == "__main__":
    print("\n🚀 开始统一接口测试\n")
    
    # ========== 测试远程 API ==========
    print("\n【远程 API 测试】\n")
    
    # 1. Qwen
    test_model("zaiwen")  # 使用 .env 中的 API Key
    
    # 2. DeepSeek (需要替换 API Key)
    # test_model("deepseek", api_key="your-key")
    
    # 3. GPT (需要 API Key)
    # test_model("gpt", api_key="your-key", model_name="gpt-4o-mini")
    
    # ========== 测试本地模型 ==========
    print("\n\n【本地模型测试】\n")
    
    # 4. Ollama (需要先启动 Ollama 服务)
    # test_model("ollama", model_name="qwen2.5:7b")
    
    # 5. Transformers (需要先下载模型)
    # test_model("transformers", model_path="Qwen/Qwen2.5-1.5B-Instruct", device="cpu")
    
    # 6. vLLM (需要 GPU)
    # test_model("vllm", model_path="Qwen/Qwen2.5-7B-Instruct")
    
    print("\n" + "=" * 60)
    print("测试完成！")
    print("=" * 60)
    
    print("\n📖 使用说明:")
    print("1. 远程 API: 直接使用，只需提供 API Key")
    print("2. Ollama: 需要先运行 `ollama serve` 启动服务")
    print("3. Transformers: 需要先下载模型到本地")
    print("4. vLLM: 需要 GPU 支持")
    
    print("\n💡 切换模型示例:")
    print('  engine = get_api_engine("qwen")  # 远程 API')
    print('  engine = get_api_engine("ollama", model_name="llama3.1:8b")  # 本地')
    print('  engine = get_api_engine("transformers", model_path="/path/to/model")  # 自定义路径')

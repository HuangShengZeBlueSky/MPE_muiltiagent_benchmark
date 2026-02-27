#!/usr/bin/env python3
"""
交互式 API 密钥配置脚本
用于快速设置 .env 文件中的 API 密钥
"""

import os
from pathlib import Path

# 自动加载 .env 文件
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass


def validate_key(key_name: str, value: str) -> bool:
    """验证密钥格式"""
    if not value:
        return True  # 空值允许（跳过该密钥）
    
    if key_name == "QWEN_API_KEY" and not value.startswith("sk-"):
        print(f"  ⚠️  警告: Qwen 密钥通常以 'sk-' 开头")
    
    if key_name == "OPENAI_API_KEY" and not value.startswith("sk-"):
        print(f"  ⚠️  警告: OpenAI 密钥通常以 'sk-' 开头")
    
    return True


def setup_env():
    """交互式设置 .env 文件"""
    env_file = Path('.env')
    
    # 检查文件是否存在
    if env_file.exists():
        print(f"⚠️  {env_file} 文件已存在")
        response = input("是否覆盖? (y/n, 默认 n): ").strip().lower()
        if response != 'y':
            print("✅ 保留现有 .env 文件，取消配置")
            return
    
    print("\n" + "="*60)
    print("🔑 API 密钥配置向导")
    print("="*60)
    print("\n请输入你的 API 密钥（直接回车跳过某个密钥）\n")
    
    config = {}
    
    # Qwen
    print("📌 Qwen API (阿里云通义千问)")
    print("   获取地址: https://dashscope.console.aliyun.com")
    qwen_key = input("   QWEN_API_KEY: ").strip()
    if qwen_key:
        if validate_key("QWEN_API_KEY", qwen_key):
            config["QWEN_API_KEY"] = qwen_key
    
    # DeepSeek
    print("\n📌 DeepSeek API")
    print("   获取地址: https://platform.deepseek.com")
    deepseek_key = input("   DEEPSEEK_API_KEY: ").strip()
    if deepseek_key:
        if validate_key("DEEPSEEK_API_KEY", deepseek_key):
            config["DEEPSEEK_API_KEY"] = deepseek_key
    
    # OpenAI
    print("\n📌 OpenAI API (GPT-4, GPT-4o 等)")
    print("   获取地址: https://platform.openai.com/api-keys")
    openai_key = input("   OPENAI_API_KEY: ").strip()
    if openai_key:
        if validate_key("OPENAI_API_KEY", openai_key):
            config["OPENAI_API_KEY"] = openai_key
    
    # Google Gemini
    print("\n📌 Google Gemini API")
    print("   获取地址: https://aistudio.google.com/apikey")
    google_key = input("   GOOGLE_API_KEY: ").strip()
    if google_key:
        config["GOOGLE_API_KEY"] = google_key
    
    # 本地模型配置（可选）
    print("\n📌 本地模型配置（可选）")
    print("   如果使用本地模型，可配置以下内容\n")
    
    transformers_path = input("   Transformers 模型路径 (可选): ").strip()
    if transformers_path:
        config["TRANSFORMERS_MODEL_PATH"] = transformers_path
    
    ollama_model = input("   Ollama 模型名称 (可选, 默认: qwen2.5:7b): ").strip()
    if ollama_model:
        config["OLLAMA_MODEL_NAME"] = ollama_model
    
    if not config:
        print("\n⚠️  未输入任何密钥，取消配置")
        return
    
    # 写入 .env 文件
    print("\n" + "="*60)
    print("💾 保存配置...")
    
    with open('.env', 'w') as f:
        f.write("# API Keys Configuration\n")
        f.write("# 自动生成，请勿提交到 Git\n\n")
        for key, value in config.items():
            f.write(f'{key}={value}\n')
    
    print(f"✅ .env 文件已创建！")
    print(f"   位置: {env_file.absolute()}\n")
    
    # 安全提示
    print("⚠️  安全提示：")
    print("   - .env 文件已添加到 .gitignore，不会被提交")
    print("   - 请勿将 .env 分享给他人")
    print("   - 定期更新和轮换 API 密钥")
    print("\n✨ 配置完成！现在可以运行：")
    print("   python benchmark_runner.py")
    print("="*60)


def show_status():
    """显示当前的环境变量状态"""
    print("\n" + "="*60)
    print("🔍 环境变量检查")
    print("="*60 + "\n")
    
    keys_to_check = [
        ("QWEN_API_KEY", "Qwen"),
        ("DEEPSEEK_API_KEY", "DeepSeek"),
        ("OPENAI_API_KEY", "OpenAI"),
        ("GOOGLE_API_KEY", "Google Gemini"),
        ("TRANSFORMERS_MODEL_PATH", "Transformers"),
        ("OLLAMA_MODEL_NAME", "Ollama"),
    ]
    
    for env_key, provider in keys_to_check:
        value = os.getenv(env_key, "❌ 未设置")
        status = "✅" if value != "❌ 未设置" else "❌"
        
        # 隐藏密钥值
        if "KEY" in env_key and value != "❌ 未设置":
            display_value = f"{value[:10]}..." if len(value) > 10 else "***"
        else:
            display_value = value
        
        print(f"{status} {provider:20} {env_key:25} = {display_value}")
    
    # 检查 .env 文件
    print("\n")
    if Path('.env').exists():
        print("✅ .env 文件已存在")
    else:
        print("❌ .env 文件不存在")
    print("="*60)


if __name__ == '__main__':
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == '--status':
        show_status()
    else:
        setup_env()

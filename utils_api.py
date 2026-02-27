import os
import re
import json
import time
import numpy as np
from typing import Tuple, Optional, Dict, Any

# 自动加载 .env 文件中的环境变量
try:
    from dotenv import load_dotenv
    load_dotenv(verbose=False)
except ImportError:
    pass  # python-dotenv 未安装，使用系统环境变量

# ==============================================================================
# 1. 依赖检查与导入
# ==============================================================================
try:
    from openai import OpenAI
    import google.generativeai as genai
except ImportError:
    print("Warning: API libraries (openai, google-generativeai) not installed.")

# 本地模型依赖（可选）
try:
    import torch
    from transformers import AutoTokenizer, AutoModelForCausalLM
    TRANSFORMERS_AVAILABLE = True
except ImportError:
    TRANSFORMERS_AVAILABLE = False

try:
    import ollama
    OLLAMA_AVAILABLE = True
except ImportError:
    OLLAMA_AVAILABLE = False

# ==============================================================================
# 2. 通用工具函数
# ==============================================================================
def get_unique_filename(filepath):
    """
    如果文件存在，则在文件名后添加数字后缀，防止覆盖。
    例如: demo.mp4 -> demo_1.mp4
    """
    if not os.path.exists(filepath):
        return filepath

    base, ext = os.path.splitext(filepath)
    counter = 1
    while True:
        new_filepath = f"{base}_{counter}{ext}"
        if not os.path.exists(new_filepath):
            return new_filepath
        counter += 1

# ==============================================================================
# 3. 统一推理引擎 (支持远程API和本地模型)
# ==============================================================================
class APIInferencer:
    """
    统一的模型推理接口，支持：
    - 远程API: OpenAI协议 (DeepSeek, Qwen, GPT), Gemini
    - 本地模型: transformers, ollama, vllm
    """
    def __init__(
        self,
        provider: str,
        model_name: str,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        model_path: Optional[str] = None,
        device: str = "auto",
        **kwargs
    ):
        self.provider = provider.lower()
        self.model_name = model_name
        self.api_key = api_key
        self.device = device
        self.client = None
        self.tokenizer = None
        self.model = None
        
        print(f"Loading Model: {provider} -> {model_name}...")
        print(f"DEBUG: api_key = {api_key[:20] + '...' if api_key else 'None'}")
        
        # 远程 API 服务
        if self.provider in ["openai", "deepseek", "qwen", "gpt", "chatgpt"]:
            self._init_openai_api(base_url)
        
        elif self.provider == "gemini":
            self._init_gemini_api()
        
        # 本地模型
        elif self.provider == "transformers":
            self._init_transformers(model_path or model_name, **kwargs)
        
        elif self.provider == "ollama":
            self._init_ollama()
        
        elif self.provider == "vllm":
            self._init_vllm(model_path or model_name, **kwargs)
        
        else:
            raise ValueError(f"Unsupported provider: {provider}")
        
        print("Model initialized successfully.")
    
    def _init_openai_api(self, base_url: Optional[str]):
        """初始化 OpenAI 协议的 API"""
        self.client = OpenAI(api_key=self.api_key, base_url=base_url)
    
    def _init_gemini_api(self):
        """初始化 Gemini API"""
        genai.configure(api_key=self.api_key)
        self.client = genai.GenerativeModel(self.model_name)
    
    def _init_transformers(self, model_path: str, **kwargs):
        """初始化 Hugging Face transformers 本地模型"""
        if not TRANSFORMERS_AVAILABLE:
            raise ImportError("transformers not installed. Run: pip install transformers torch")
        
        device_map = "auto" if self.device == "auto" else self.device
        self.tokenizer = AutoTokenizer.from_pretrained(model_path)
        self.model = AutoModelForCausalLM.from_pretrained(
            model_path,
            device_map=device_map,
            torch_dtype=torch.float16 if torch.cuda.is_available() else torch.float32,
            **kwargs
        )
        print(f"  Device: {device_map}, Dtype: {self.model.dtype}")
    
    def _init_ollama(self):
        """初始化 Ollama 本地服务"""
        if not OLLAMA_AVAILABLE:
            raise ImportError("ollama not installed. Run: pip install ollama")
        self.client = ollama
    
    def _init_vllm(self, model_path: str, **kwargs):
        """初始化 vLLM 引擎（高性能推理）"""
        try:
            from vllm import LLM, SamplingParams
            self.client = LLM(model=model_path, **kwargs)
            self.sampling_params = SamplingParams(temperature=0.5, max_tokens=4096)
        except ImportError:
            raise ImportError("vllm not installed. Run: pip install vllm")

    def generate_action(
        self,
        system_prompt: str,
        user_prompt_str: str,
        temperature: float = 0.5,
        max_tokens: int = 4096,
        max_retries: int = 10
    ) -> Tuple[np.ndarray, str]:
        """
        统一的推理接口，返回 (action_vec, response_text)
        
        Args:
            system_prompt: 系统提示词
            user_prompt_str: 用户提示词
            temperature: 采样温度
            max_tokens: 最大生成token数
            max_retries: 最大重试次数
        
        Returns:
            (action_vec, response_text): 动作向量和完整回复
        """
        for attempt in range(max_retries):
            try:
                # 根据不同 provider 调用对应方法
                if self.provider in ["openai", "deepseek", "qwen", "gpt", "chatgpt"]:
                    response_text = self._call_openai_api(system_prompt, user_prompt_str, temperature, max_tokens)
                
                elif self.provider == "gemini":
                    response_text = self._call_gemini_api(system_prompt, user_prompt_str)
                
                elif self.provider == "transformers":
                    response_text = self._call_transformers(system_prompt, user_prompt_str, temperature, max_tokens)
                
                elif self.provider == "ollama":
                    response_text = self._call_ollama(system_prompt, user_prompt_str, temperature)
                
                elif self.provider == "vllm":
                    response_text = self._call_vllm(system_prompt, user_prompt_str, temperature, max_tokens)
                
                else:
                    raise ValueError(f"Unknown provider: {self.provider}")
                
                # 解析 JSON 并返回
                action_vec = self._parse_json(response_text)
                return action_vec, response_text

            except Exception as e:
                print(f"[Inference Error - Attempt {attempt+1}/{max_retries}] {e}")
                if attempt < max_retries - 1:
                    time.sleep(1)
                else:
                    return np.array([0,0,0,0,0], dtype=np.float32), f"Failed: {str(e)}"
    
    def _call_openai_api(self, system_prompt: str, user_prompt: str, temperature: float, max_tokens: int) -> str:
        """调用 OpenAI 协议 API"""
        completion = self.client.chat.completions.create(
            model=self.model_name,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=temperature,
            max_tokens=max_tokens
        )
        
        if not completion.choices or completion.choices[0].message is None:
            raise ValueError(f"Empty API response")
        
        return completion.choices[0].message.content
    
    def _call_gemini_api(self, system_prompt: str, user_prompt: str) -> str:
        """调用 Gemini API"""
        full_prompt = f"{system_prompt}\n\n{user_prompt}"
        response = self.client.generate_content(full_prompt)
        return response.text
    
    def _call_transformers(self, system_prompt: str, user_prompt: str, temperature: float, max_tokens: int) -> str:
        """调用 transformers 本地模型"""
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]
        
        # 使用 chat template
        if hasattr(self.tokenizer, "apply_chat_template"):
            prompt = self.tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
        else:
            # 降级方案
            prompt = f"{system_prompt}\n\nUser: {user_prompt}\n\nAssistant:"
        
        inputs = self.tokenizer(prompt, return_tensors="pt").to(self.model.device)
        
        outputs = self.model.generate(
            **inputs,
            max_new_tokens=max_tokens,
            temperature=temperature,
            do_sample=temperature > 0,
            pad_token_id=self.tokenizer.eos_token_id
        )
        
        response = self.tokenizer.decode(outputs[0][inputs.input_ids.shape[1]:], skip_special_tokens=True)
        return response
    
    def _call_ollama(self, system_prompt: str, user_prompt: str, temperature: float) -> str:
        """调用 Ollama 本地服务"""
        response = self.client.chat(
            model=self.model_name,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            options={"temperature": temperature}
        )
        return response['message']['content']
    
    def _call_vllm(self, system_prompt: str, user_prompt: str, temperature: float, max_tokens: int) -> str:
        """调用 vLLM 引擎"""
        prompt = f"{system_prompt}\n\nUser: {user_prompt}\n\nAssistant:"
        outputs = self.client.generate([prompt], self.sampling_params)
        return outputs[0].outputs[0].text

    def _parse_json(self, text: str) -> np.ndarray:
        """
        强壮的 JSON 解析器，能处理 <think> 标签和 Markdown 格式。
        """
        try:
            # 1. 移除 DeepSeek 思考过程
            clean_text = text.split("</think>")[-1] if "</think>" in text else text
            
            # 2. 提取 Markdown JSON
            match = re.search(r'```json\s*(\{.*?\})\s*```', clean_text, re.DOTALL)
            if not match:
                match = re.search(r'(\{.*?\})', clean_text, re.DOTALL)
            
            if match:
                data = json.loads(match.group(1))
                # 兼容 "action" 字段不存在的情况
                return np.array(data.get("action", [0]*5), dtype=np.float32)
            
            # 3. 兜底正则
            match = re.search(r'"action"\s*:\s*\[(.*?)\]', clean_text, re.DOTALL)
            if match:
                nums = re.findall(r"[-+]?\d*\.\d+|\d+", match.group(1))
                if len(nums) >= 5:
                    return np.array([float(x) for x in nums[:5]], dtype=np.float32)
            
            return np.array([0,0,0,0,0], dtype=np.float32)
        except Exception:
            return np.array([0,0,0,0,0], dtype=np.float32)

# ==============================================================================
# 4. 配置工厂（统一接口）
# ==============================================================================
def get_api_engine(provider: str, **kwargs) -> APIInferencer:
    """
    统一的模型加载接口，支持远程API和本地模型
    
    Args:
        provider: 模型提供商，支持:
            - 远程API: 'deepseek', 'qwen', 'gpt', 'chatgpt', 'gemini'
            - 本地模型: 'transformers', 'ollama', 'vllm'
        **kwargs: 额外配置参数（可覆盖默认配置）
    
    Examples:
        # 远程 API
        engine = get_api_engine("qwen")
        engine = get_api_engine("deepseek", api_key="your-key")
        
        # 本地模型
        engine = get_api_engine("transformers", model_path="/path/to/model")
        engine = get_api_engine("ollama", model_name="qwen2.5:7b")
        engine = get_api_engine("vllm", model_path="meta-llama/Llama-3-8B")
    """
    provider = provider.lower()
    
    # ========== 远程 API 配置 ==========
    if provider == "deepseek":
        config = {
            "provider": "deepseek",
            "api_key": kwargs.get("api_key", "sk-xxxxxxxx"),
            "base_url": "https://api.deepseek.com",
            "model_name": "deepseek-chat"
        }
    
    elif provider == "qwen":
        config = {
            "provider": "qwen",
            "api_key": kwargs.get("api_key", os.getenv("QWEN_API_KEY")),
            #"base_url": "https://realmrouter.cn/v1",
            #"base_url": "https://back.zaiwenai.com/api/v1/ai/chat/completions",
            "base_url": "https://autobak.zaiwen.top/api/v1/chat/completions",    
            #"model_name": "qwen3-max"
            "model_name": os.getenv("MODEL_NAME", "Qwen-3-Max")
        }
    
    elif provider == "zaiwen":
        # 专门为 Zaiwen 迁移的配置块
        config = {
            # 这里的 provider 设为 openai，以便复用 APIInferencer 中处理 OpenAI 协议的逻辑
            "provider": "openai", 
            # 优先使用传入参数 -> 其次环境变量 -> 最后默认值(由于你提供了 Key，这里作为 fallback)
            "api_key": kwargs.get("api_key", os.getenv("ZAIWEN_API_KEY")),
            # 注意 URL 路径修剪
            "base_url": "https://back.zaiwenai.com/api/v1/ai/",
            "model_name": kwargs.get("model_name", "Qwen-3-Max")    
        }
        print(f"DEBUG: Zaiwen config: {config}")
    
    elif provider in ["gpt", "chatgpt", "openai"]:
        config = {
            "provider": "openai",
            "api_key": kwargs.get("api_key", os.getenv("OPENAI_API_KEY")),
            "base_url": "https://api.openai.com/v1",
            "model_name": os.getenv("MODEL_NAME", "gpt-4o")
        }
    
    elif provider == "gemini":
        config = {
            "provider": "gemini",
            "api_key": kwargs.get("api_key", os.getenv("GOOGLE_API_KEY")),
            "model_name": kwargs.get("model_name", "gemini-1.5-pro")
        }
    
    # ========== 本地模型配置 ==========
    elif provider == "transformers":
        config = {
            "provider": "transformers",
            "model_path": kwargs.get("model_path", kwargs.get("model_name", "Qwen/Qwen2.5-7B-Instruct")),
            "device": kwargs.get("device", "auto"),
            "model_name": kwargs.get("model_name", "local-transformers")
        }
    
    elif provider == "ollama":
        config = {
            "provider": "ollama",
            "model_name": kwargs.get("model_name", "qwen2.5:7b")
        }
    
    elif provider == "vllm":
        config = {
            "provider": "vllm",
            "model_path": kwargs.get("model_path", kwargs.get("model_name", "Qwen/Qwen2.5-7B-Instruct")),
            "model_name": kwargs.get("model_name", "local-vllm"),
            "tensor_parallel_size": kwargs.get("tensor_parallel_size", 1)
        }
    
    else:
        raise ValueError(
            f"Unknown provider: {provider}\n"
            f"Supported: deepseek, qwen, gpt, gemini, transformers, ollama, vllm"
        )
    
    # 合并用户自定义配置
    config.update({k: v for k, v in kwargs.items() if k not in config})
    
    return APIInferencer(**config)
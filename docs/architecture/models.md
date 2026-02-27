# 模型接口使用指南

## 统一接口设计

`utils_api.py` 提供了 `get_api_engine()` 统一接口，支持：
- **远程 API**: DeepSeek, Qwen, GPT, Gemini
- **本地模型**: transformers, ollama, vllm

所有模型返回相同格式：`(action_vec, response_text)`

---

## 使用方法

### 1. 远程 API

#### Qwen (阿里通义千问)
```python
from utils_api import get_api_engine

# 使用默认配置
engine = get_api_engine("qwen")

# 自定义 API Key
engine = get_api_engine("qwen", api_key="your-api-key")
```

#### DeepSeek
```python
engine = get_api_engine("deepseek", api_key="sk-your-key")
```

#### GPT (OpenAI)
```python
engine = get_api_engine("gpt", api_key="sk-your-key", model_name="gpt-4o")
```

#### Gemini (Google)
```python
engine = get_api_engine("gemini", api_key="your-key", model_name="gemini-1.5-pro")
```

---

### 2. 本地模型

#### Transformers (Hugging Face)
```python
# 使用模型路径
engine = get_api_engine(
    "transformers",
    model_path="/path/to/local/model"  # 或 HF Hub: "Qwen/Qwen2.5-7B-Instruct"
)

# 指定设备
engine = get_api_engine(
    "transformers",
    model_path="Qwen/Qwen2.5-7B-Instruct",
    device="cuda:0"  # 或 "auto", "cpu"
)
```

**依赖安装**:
```bash
pip install transformers torch accelerate
```

#### Ollama (本地推理服务)
```python
# 使用 Ollama 本地服务（需先启动 Ollama）
engine = get_api_engine("ollama", model_name="qwen2.5:7b")

# 其他模型
engine = get_api_engine("ollama", model_name="llama3.1:8b")
```

**依赖安装**:
```bash
# 1. 安装 Ollama: https://ollama.com
# 2. 拉取模型
ollama pull qwen2.5:7b

# 3. 安装 Python 客户端
pip install ollama
```

#### vLLM (高性能推理)
```python
# 高性能批量推理
engine = get_api_engine(
    "vllm",
    model_path="meta-llama/Llama-3-8B",
    tensor_parallel_size=2  # 使用 2 张 GPU
)
```

**依赖安装**:
```bash
pip install vllm
```

---

## 完整示例

### spread_API.py 中切换模型

```python
if __name__ == "__main__":
    # ========== 远程 API ==========
    # PROVIDER = "qwen"
    # PROVIDER = "deepseek"
    # PROVIDER = "gpt"
    
    # ========== 本地模型 ==========
    # PROVIDER = "transformers"
    # kwargs = {"model_path": "Qwen/Qwen2.5-7B-Instruct", "device": "cuda"}
    
    PROVIDER = "ollama"
    kwargs = {"model_name": "qwen2.5:7b"}
    
    # 运行游戏
    run_spread_game(PROVIDER, f"demo_{PROVIDER}.mp4", **kwargs)
```

### 直接调用推理接口

```python
from utils_api import get_api_engine

# 初始化引擎
engine = get_api_engine("qwen")

# 推理
system_prompt = "You are a helpful assistant."
user_prompt = "Calculate 1+1"

action_vec, response_text = engine.generate_action(
    system_prompt,
    user_prompt,
    temperature=0.7,
    max_tokens=2048
)

print(f"Action: {action_vec}")
print(f"Response: {response_text}")
```

---

## 配置文件（可选）

可以创建 `model_config.json` 集中管理配置：

```json
{
    "qwen": {
        "api_key": "sk-your-key",
        "base_url": "https://api.qwen.com"
    },
    "transformers": {
        "model_path": "/data/models/Qwen2.5-7B",
        "device": "cuda:0"
    },
    "ollama": {
        "model_name": "qwen2.5:7b"
    }
}
```

然后在代码中加载：
```python
import json

with open("model_config.json") as f:
    config = json.load(f)

engine = get_api_engine("qwen", **config["qwen"])
```

---

## 性能对比

| 模型类型 | 延迟 | 成本 | 部署难度 | 适用场景 |
|---------|------|------|---------|---------|
| 远程 API | 低 | 按调用计费 | 简单 | 快速验证、小规模实验 |
| transformers | 中 | 免费 | 中等 | 中小规模研究 |
| ollama | 低 | 免费 | 简单 | 本地开发、快速迭代 |
| vllm | 极低 | 免费 | 复杂 | 大规模批量推理 |

---

## 常见问题

### Q: 如何查看当前使用的模型？
```python
print(f"Provider: {engine.provider}")
print(f"Model: {engine.model_name}")
```

### Q: 本地模型内存不足怎么办？
```python
# 使用 8bit 量化
engine = get_api_engine(
    "transformers",
    model_path="Qwen/Qwen2.5-7B-Instruct",
    load_in_8bit=True
)
```

### Q: 如何添加新的 API 提供商？
在 `utils_api.py` 的 `get_api_engine` 中添加配置：
```python
elif provider == "your_provider":
    config = {
        "provider": "your_provider",
        "api_key": kwargs.get("api_key"),
        "base_url": "https://api.your-provider.com",
        "model_name": "your-model"
    }
```

---

## 最佳实践

1. **开发阶段**: 使用 `ollama` 快速迭代
2. **实验阶段**: 使用远程 API 验证效果
3. **生产阶段**: 使用 `vllm` 高性能推理
4. **离线环境**: 使用 `transformers` 加载本地模型

---

## 故障排查

### API 调用失败
```python
# 增加重试次数
action_vec, response = engine.generate_action(
    system_prompt,
    user_prompt,
    max_retries=5
)
```

### 本地模型加载失败
```bash
# 检查依赖
pip install transformers torch --upgrade

# 检查磁盘空间
df -h

# 检查 GPU
nvidia-smi
```

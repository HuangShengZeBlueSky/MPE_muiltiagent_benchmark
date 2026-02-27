# API 密钥配置指南

本文档整合了 API 密钥的配置、安全管理和最佳实践。

---

## 📋 目录

1. [快速配置](#快速配置)
2. [配置方式](#配置方式)
3. [支持的提供商](#支持的提供商)
4. [安全最佳实践](#安全最佳实践)
5. [故障排查](#故障排查)

---

## 🚀 快速配置

### 方式一：使用交互式脚本（推荐）

```bash
python setup_api_keys.py
```

这会引导你输入 API 密钥并自动生成 `.env` 文件。

### 方式二：手动配置

```bash
# 1. 复制配置模板
cp .env.example .env

# 2. 编辑 .env 文件并填入你的密钥
nano .env
```

### 方式三：环境变量

```bash
# Linux/Mac
export QWEN_API_KEY="sk-your-key"
export DEEPSEEK_API_KEY="sk-your-key"
export OPENAI_API_KEY="sk-your-key"

# Windows PowerShell
$env:QWEN_API_KEY = "sk-your-key"
```

---

## 📝 配置方式详解

### 使用 `.env` 文件（推荐本地开发）

1. **复制模板文件**
   ```bash
   cp .env.example .env
   ```

2. **编辑 `.env` 文件，添加你的实际密钥**
   ```
   QWEN_API_KEY=sk-your-actual-key
   DEEPSEEK_API_KEY=sk-your-actual-key
   OPENAI_API_KEY=sk-your-actual-key
   GOOGLE_API_KEY=your-actual-key
   ```

3. **自动加载**（已在代码中配置）
   ```python
   from dotenv import load_dotenv
   load_dotenv()
   # 之后 os.getenv() 就能读取 .env 中的变量
   ```

### 使用系统环境变量

**Linux/Mac:**
```bash
export QWEN_API_KEY="sk-your-key"
export DEEPSEEK_API_KEY="sk-your-key"
export OPENAI_API_KEY="sk-your-key"
export GOOGLE_API_KEY="your-key"
```

**Windows (PowerShell):**
```powershell
$env:QWEN_API_KEY = "sk-your-key"
$env:DEEPSEEK_API_KEY = "sk-your-key"
$env:OPENAI_API_KEY = "sk-your-key"
$env:GOOGLE_API_KEY = "your-key"
```

**Windows (CMD):**
```cmd
set QWEN_API_KEY=sk-your-key
set DEEPSEEK_API_KEY=sk-your-key
set OPENAI_API_KEY=sk-your-key
set GOOGLE_API_KEY=your-key
```

### 运行时指定（单次运行）

```bash
QWEN_API_KEY=sk-your-key python benchmark_runner.py
```

或在 Python 代码中：
```python
from benchmark_runner import run_benchmark
import os

os.environ['QWEN_API_KEY'] = 'sk-your-key'

result = run_benchmark(
    env_name="adversary",
    provider="qwen",
    episodes=10
)
```

---

## 🔑 支持的 API 提供商

| 提供商 | 环境变量 | 获取地址 | 说明 |
|------|--------|--------|------|
| **Qwen** | `QWEN_API_KEY` | https://dashscope.console.aliyun.com | 阿里云通义千问 |
| **DeepSeek** | `DEEPSEEK_API_KEY` | https://platform.deepseek.com | 深度求索 |
| **OpenAI** | `OPENAI_API_KEY` | https://platform.openai.com/api-keys | GPT-4, GPT-4o 等 |
| **Gemini** | `GOOGLE_API_KEY` | https://aistudio.google.com/apikey | Google Gemini |

### 本地模型（无需 API 密钥）

如果使用本地模型，**无需配置 API 密钥**：

```python
from benchmark_runner import run_benchmark

# 使用 Transformers 本地模型
result = run_benchmark(
    env_name="adversary",
    provider="transformers",
    episodes=5,
    model_path="Qwen/Qwen2.5-7B-Instruct",
    device="cuda"  # 或 "cpu"
)

# 使用 Ollama 本地服务
result = run_benchmark(
    env_name="tag",
    provider="ollama",
    episodes=3,
    model_name="qwen2.5:7b"
)
```

---

## 🔐 安全最佳实践

### ✅ 应该做

- **使用 `.env` 文件**管理本地密钥
- **在 `.gitignore` 中列出** `.env`，防止提交
- **使用环境变量**传递生产环境密钥
- **定期轮换/更新** API 密钥
- **对不同的服务使用不同的密钥**
- **限制密钥权限**（如果平台支持）

### ❌ 不要做

- ❌ 在代码中硬编码 API 密钥
- ❌ 将包含密钥的文件提交到 Git
- ❌ 在日志中打印完整的 API 密钥
- ❌ 在 GitHub Issues 或讨论中公开密钥
- ❌ 在多个项目间共享同一个 API 密钥

### 🛡️ 安全检查清单

在推送代码前，确保：

```bash
# ✅ 检查 .env 是否被保护
git check-ignore .env
# 预期输出: .env

# ✅ 检查代码中没有硬编码密钥
grep -r "sk-" *.py | grep -v os.getenv
# 预期: 无输出或仅 utils_api.py 中有 os.getenv() 调用

# ✅ 检查 .gitignore 包含 .env
grep "^.env" .gitignore
# 预期输出: .env

# ✅ 验证配置脚本可用
python setup_api_keys.py --status
# 预期: 显示环境变量检查结果
```

### 🔒 密钥泄露应对

如果密钥已经泄露：

1. **立即撤销**：从 API 平台重新生成新密钥（撤销旧密钥）
2. **更新本地**：更新 `.env` 文件
3. **检查使用**：查看 API 平台的使用记录，确认是否有异常调用
4. **Git 历史**：如果密钥在 Git 历史中，考虑使用 `git filter-repo` 清理
5. **通知团队**：如果是团队项目，通知所有成员更新密钥

---

## 🔧 故障排查

### Q1: 运行时提示 API 密钥为 None

**原因**：环境变量未设置或 `.env` 文件未被加载

**解决方案**：
1. 确认 `.env` 文件存在且路径正确
2. 确认 Python 安装了 `python-dotenv`：`pip install python-dotenv`
3. 在代码最开始加入：
   ```python
   from dotenv import load_dotenv
   load_dotenv(verbose=True)  # verbose=True 会打印加载的变量
   ```
4. 验证环境变量是否设置：
   ```bash
   echo $QWEN_API_KEY   # Linux/Mac
   echo %QWEN_API_KEY%  # Windows CMD
   ```

### Q2: 提示 "401 Unauthorized" 或认证失败

**原因**：API 密钥无效或已过期

**解决方案**：
1. 检查密钥是否正确复制（无多余空格）
2. 确认密钥未过期或被撤销
3. 从官方平台重新获取密钥
4. 验证环境变量名称是否正确（区分大小写）

### Q3: 可以不用 .env，直接用系统环境变量吗？

**答案**：可以，但 `.env` 文件更方便。两者都支持，代码会优先读取环境变量。

### Q4: 如何为历史数据补充 seed 信息？

**答案**：新的日志会包含 seed，历史日志无法追溯。建议：
- 重新运行获得带 seed 的结果
- 或在报告中说明"历史数据未记录 seed"

### Q5: 多个项目如何管理密钥？

**建议**：
1. 每个项目独立的 `.env` 文件
2. 或使用密钥管理工具（如 1Password, Bitwarden）
3. 生产环境使用 CI/CD 平台的 Secrets 管理

---

## 📚 相关文档

- [快速开始](../getting_started/quickstart.md) - 5分钟快速上手
- [模型使用指南](../architecture/models.md) - 如何使用不同的 LLM
- [实验复现指南](../experiments/reproducibility.md) - 种子固定和可重现实验

---

## 🆘 获取帮助

如果遇到问题：
1. 查看 [GitHub Issues](https://github.com/HuangShengZeBlueSky/MPE_muiltiagent_benchmark/issues)
2. 运行 `python setup_api_keys.py --status` 检查配置
3. 查看 `utils_api.py` 中的实现细节

---

**最后更新**: 2026-01-26  
**版本**: 1.0.0

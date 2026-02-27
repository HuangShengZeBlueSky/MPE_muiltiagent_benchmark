# 环境配置详细指南

本文档提供完整的环境配置步骤，确保在任何系统上都能成功复现项目环境。

---

## 📋 系统要求

| 组件 | 要求 | 说明 |
|------|------|------|
| **Python** | 3.8+ | 推荐 3.12.3（已测试） |
| **操作系统** | Linux / macOS / Windows | 跨平台支持 |
| **内存** | 2GB+ | 视频生成需要额外内存 |
| **磁盘空间** | 1GB+ | 包括依赖和结果文件 |
| **网络** | 需要 | 下载依赖和调用 API |

---

## 🚀 快速安装（推荐）

### Linux / macOS

```bash
# 1. 克隆仓库
git clone https://github.com/HuangShengZeBlueSky/MPE_muiltiagent_benchmark.git
cd MPE_muiltiagent_benchmark

# 2. 创建虚拟环境
python3 -m venv .venv
source .venv/bin/activate

# 3. 安装依赖
pip install --upgrade pip
pip install -r requirements.txt

# 4. 验证安装
python -c "import pettingzoo; import openai; print('✅ 安装成功')"
```

### Windows (PowerShell)

```powershell
# 1. 克隆仓库
git clone https://github.com/HuangShengZeBlueSky/MPE_muiltiagent_benchmark.git
cd MPE_muiltiagent_benchmark

# 2. 创建虚拟环境
python -m venv .venv
.venv\Scripts\Activate.ps1

# 3. 安装依赖
pip install --upgrade pip
pip install -r requirements.txt

# 4. 验证安装
python -c "import pettingzoo; import openai; print('✅ 安装成功')"
```

---

## 📦 依赖说明

### 核心依赖 (必需)

| 包名 | 版本 | 用途 |
|------|------|------|
| `numpy` | >=1.24.0, <3.0.0 | 数值计算 |
| `imageio` | >=2.31.0 | 视频保存 |
| `imageio-ffmpeg` | >=0.4.9 | 视频编码 |
| `pettingzoo[mpe]` | >=1.24.0 | 多智能体环境 |
| `gymnasium` | >=1.2.0 | 环境接口（PettingZoo 依赖） |
| `openai` | >=1.0.0 | OpenAI API |
| `google-generativeai` | >=0.3.0 | Gemini API |
| `python-dotenv` | >=1.0.0 | 环境变量管理 |
| `Pillow` | >=10.0.0 | 图像处理 |

### 可选依赖 (本地模型)

如需使用本地模型，取消注释 `requirements.txt` 中的相应行：

```bash
# 取消注释后安装
pip install torch>=2.0.0
pip install transformers>=4.30.0
pip install ollama>=0.1.0
pip install vllm>=0.2.0
```

---

## 🔧 多种安装方式

### 方式 1: venv（推荐）

**优点**: Python 内置，简单可靠

```bash
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
# .venv\Scripts\activate   # Windows CMD
pip install -r requirements.txt
```

### 方式 2: conda

**优点**: 更好的包管理，适合复杂依赖

```bash
# 创建环境
conda create -n mpe-bench python=3.12 -y
conda activate mpe-bench

# 安装依赖
pip install -r requirements.txt

# 或使用 conda 安装部分包
conda install numpy pillow -y
pip install -r requirements.txt
```

### 方式 3: uv（新工具）

**优点**: 极快的安装速度

```bash
# 安装 uv (如果未安装)
curl -LsSf https://astral.sh/uv/install.sh | sh

# 使用 uv 创建环境
uv venv
source .venv/bin/activate

# 安装依赖
uv pip install -r requirements.txt
```

---

## ✅ 安装验证

### 1. 检查 Python 版本

```bash
python --version
# 期望: Python 3.8.x 或更高
```

### 2. 验证核心包

```bash
python -c "
import pettingzoo
import numpy as np
import imageio
import openai
from dotenv import load_dotenv
print('✅ 所有核心依赖已安装')
print(f'PettingZoo 版本: {pettingzoo.__version__}')
print(f'NumPy 版本: {np.__version__}')
"
```

### 3. 运行快速测试

```bash
# 测试环境创建（无需 API 密钥）
python -c "
from pettingzoo.mpe import simple_spread_v3
env = simple_spread_v3.parallel_env(N=3)
env.reset()
print('✅ PettingZoo MPE 环境可用')
"
```

### 4. 检查已安装包

```bash
pip list | grep -E "(pettingzoo|numpy|openai|imageio)"
```

---

## 🐛 常见问题

### Q1: `pettingzoo[mpe]` 安装失败

**原因**: 需要安装额外的依赖

**解决方案**:
```bash
# 分步安装
pip install gymnasium
pip install pettingzoo
pip install -r requirements.txt
```

### Q2: `imageio-ffmpeg` 找不到 ffmpeg

**原因**: ffmpeg 未正确安装

**解决方案**:
```bash
# 使用 imageio-ffmpeg 自带的 ffmpeg
python -c "import imageio_ffmpeg; print(imageio_ffmpeg.get_ffmpeg_exe())"

# 或手动安装 ffmpeg
# Ubuntu/Debian:
sudo apt-get install ffmpeg

# macOS:
brew install ffmpeg

# Windows:
# 从 https://ffmpeg.org/download.html 下载
```

### Q3: numpy 版本冲突

**原因**: numpy 2.x 与某些包不兼容

**解决方案**:
```bash
# 降级到 1.x
pip install "numpy>=1.24.0,<2.0.0"
```

### Q4: Windows 上 `activate` 无法运行

**原因**: PowerShell 执行策略限制

**解决方案**:
```powershell
# 临时允许脚本执行
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope Process

# 然后激活环境
.venv\Scripts\Activate.ps1
```

---

## 📊 依赖树

核心依赖关系：

```
MPE Multi-Agent Benchmark
├── pettingzoo[mpe] (多智能体环境)
│   ├── gymnasium (环境接口)
│   ├── pygame (渲染)
│   └── numpy (数值计算)
├── imageio (视频保存)
│   └── imageio-ffmpeg (编码器)
├── openai (GPT API)
├── google-generativeai (Gemini API)
├── python-dotenv (环境变量)
└── Pillow (图像处理)
```

---

## 🔒 生产环境部署

### 使用固定版本（推荐用于复现）

```bash
# 生成固定版本文件
pip freeze > requirements.lock

# 从固定版本安装
pip install -r requirements.lock
```

### Docker 部署（可选）

创建 `Dockerfile`:

```dockerfile
FROM python:3.12-slim

WORKDIR /app

# 安装系统依赖
RUN apt-get update && apt-get install -y \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

# 复制依赖文件
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 复制项目文件
COPY . .

CMD ["python", "benchmark_runner.py"]
```

构建和运行:
```bash
docker build -t mpe-benchmark .
docker run -v $(pwd)/results:/app/results mpe-benchmark
```

---

## 📚 相关文档

- [快速开始](quickstart.md) - 5分钟上手指南
- [API 密钥配置](../configuration/api_keys.md) - 配置 LLM API
- [项目概览](overview.md) - 了解项目结构

---

## 🆘 获取帮助

如果遇到安装问题：

1. **查看错误日志**: 复制完整错误信息
2. **检查版本**: 确认 Python 和 pip 版本
3. **尝试清理**: `pip cache purge && pip install -r requirements.txt`
4. **提交 Issue**: [GitHub Issues](https://github.com/HuangShengZeBlueSky/MPE_muiltiagent_benchmark/issues)

---

**最后更新**: 2026-01-26  
**测试环境**: Python 3.12.3, Ubuntu 24.04, macOS 14, Windows 11

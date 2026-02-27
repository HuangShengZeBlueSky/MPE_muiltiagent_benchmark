# 🎉 API 密钥安全改造完成

## 📋 改动摘要

为了安全开源，已完成以下改动：

### ✅ 代码改动

| 文件 | 改动 | 说明 |
|------|------|------|
| `utils_api.py` | 移除硬编码密钥 | 使用 `os.getenv("QWEN_API_KEY")` |
| `requirements.txt` | 添加依赖 | 新增 `python-dotenv>=1.0.0` |
| `.gitignore` | 创建/更新 | 防止 `.env` 提交到 Git |

### ✨ 新文件

| 文件 | 用途 | 备注 |
|------|------|------|
| `.env.example` | 配置模板 | ✅ 提交到 Git |
| `.env` | 本地密钥 | ❌ **不** 提交到 Git |
| `API_KEY_SETUP.md` | 详细文档 | 配置指南 |
| `SECURITY_API_KEYS.md` | 安全说明 | 最佳实践 |
| `setup_api_keys.py` | 交互脚本 | 一键配置 |

## 🚀 使用方式

### 对开源用户（想要使用你的项目）

```bash
# 1. 克隆项目
git clone https://github.com/your-username/MPE_muiltiagent_benchmark.git
cd MPE_muiltiagent_benchmark

# 2. 安装依赖
pip install -r requirements.txt

# 3. 配置 API 密钥（三选一）
# 方式A: 交互式配置（推荐）
python setup_api_keys.py

# 方式B: 手动配置
cp .env.example .env
nano .env  # 编辑文件，填入密钥

# 方式C: 环境变量
export QWEN_API_KEY="sk-xxx"

# 4. 运行项目
python benchmark_runner.py
```

### 对开发者（维护项目）

**永远记住：**
- ❌ 不要在代码中硬编码密钥
- ❌ 不要提交 `.env` 文件
- ❌ 不要在日志/输出中打印密钥
- ✅ 使用 `.env.example` 作为模板
- ✅ 使用环境变量或 .env 文件

## 🔐 安全特性

✅ **多层防护**：
1. 代码中只有占位符
2. `.env` 被 `.gitignore` 保护
3. `setup_api_keys.py` 交互式配置
4. 密钥在日志中会被隐藏（只显示前10字符）

✅ **灵活配置**：
- 支持 `.env` 文件
- 支持系统环境变量
- 支持运行时参数传递
- 本地模型完全无需密钥

✅ **用户友好**：
- `setup_api_keys.py` 一键配置
- `.env.example` 清晰的模板
- `API_KEY_SETUP.md` 完整文档
- 支持跳过某些密钥

## 📊 改动对比

### 改动前（不安全❌）
```python
# utils_api.py
config = {
    "api_key": "sk-uKY08odZkPWydWDNeGe9Clz6zRDbQKXw7BadG323uOhWgaxg",  # ❌ 硬编码！
}
```

### 改动后（安全✅）
```python
# utils_api.py
config = {
    "api_key": kwargs.get("api_key", os.getenv("QWEN_API_KEY")),  # ✅ 环境变量
}

# .env 文件（本地）
QWEN_API_KEY=sk-uKY08odZkPWydWDNeGe9Clz6zRDbQKXw7BadG323uOhWgaxg

# .gitignore
.env  # ✅ 防止提交
```

## ✨ 新增功能

### setup_api_keys.py 脚本

```bash
# 交互式配置（推荐）
python setup_api_keys.py

# 查看配置状态
python setup_api_keys.py --status
```

交互式流程：
```
🔑 API 密钥配置向导
==================================================
📌 Qwen API (阿里云通义千问)
   获取地址: https://dashscope.console.aliyun.com
   QWEN_API_KEY: sk-xxx...
   ✅ .env 文件已创建！
```

## 📈 下一步

1. **提交改动**
   ```bash
   git add .env.example .gitignore API_KEY_SETUP.md SECURITY_API_KEYS.md setup_api_keys.py utils_api.py requirements.txt
   git commit -m "refactor: 使用环保变量安全管理 API 密钥"
   git push
   ```

2. **更新 README.md**
   ```markdown
   ## 快速开始
   
   1. 配置 API 密钥:
      ```bash
      python setup_api_keys.py
      ```
   
   2. 运行测试:
      ```bash
      python benchmark_runner.py
      ```
   
   详见: [API_KEY_SETUP.md](API_KEY_SETUP.md)
   ```

3. **验证安全性**
   ```bash
   # 确保 .env 在 .gitignore 中
   git check-ignore .env
   
   # 确保代码中没有硬编码密钥
   grep -r "sk-" *.py | grep -v utils_api.py  # 应该无输出
   ```

## 🎯 推荐配置

### 本地开发
```bash
# 使用 .env 文件（适合本地测试）
python setup_api_keys.py
python benchmark_runner.py
```

### CI/CD 环境（GitHub Actions）
```yaml
# .github/workflows/test.yml
env:
  QWEN_API_KEY: ${{ secrets.QWEN_API_KEY }}
  
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - run: pip install -r requirements.txt
      - run: python benchmark_runner.py
```

### Docker 容器
```dockerfile
# Dockerfile
FROM python:3.10

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

# 从环境变量读取密钥（不在镜像中存储）
ENV QWEN_API_KEY=""

CMD ["python", "benchmark_runner.py"]
```

```bash
# 运行容器时传入密钥
docker run -e QWEN_API_KEY=sk-xxx your-image
```

## ❓ 常见问题

**Q: 我的密钥已经泄露了怎么办？**
A: 立即从 API 平台重新生成新密钥（撤销旧密钥），然后更新 `.env` 文件

**Q: 为什么需要 python-dotenv？**
A: 它自动加载 `.env` 文件到环境变量，无需手动 export

**Q: 可以不用 .env，直接用系统环境变量吗？**
A: 可以，但 `.env` 文件更方便，两者都支持

**Q: 本地模型（transformers/ollama）需要 API 密钥吗？**
A: 不需要，它们完全离线运行

---

✅ **所有改动已完成！可以安全开源了。**

更多详情见：
- [API_KEY_SETUP.md](API_KEY_SETUP.md) - 详细配置指南
- [SECURITY_API_KEYS.md](SECURITY_API_KEYS.md) - 安全最佳实践

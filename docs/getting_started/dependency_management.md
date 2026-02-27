# 依赖管理说明

本项目提供两个依赖文件：

## 📋 文件说明

### `requirements.txt` - 灵活版本（推荐日常使用）

```bash
pip install -r requirements.txt
```

**特点**:
- ✅ 使用版本范围（如 `>=1.24.0`）
- ✅ 允许自动升级到兼容版本
- ✅ 更容易与其他项目共存
- ⚠️ 可能在不同时间安装得到不同版本

**适用场景**:
- 日常开发
- 首次安装
- 希望获得最新兼容版本

---

### `requirements.lock` - 固定版本（推荐论文复现）

```bash
pip install -r requirements.lock
```

**特点**:
- ✅ 固定所有包的精确版本（如 `numpy==2.4.1`）
- ✅ 保证100%可复现的环境
- ✅ 包含所有传递依赖（46个包）
- ⚠️ 版本可能过时

**适用场景**:
- 复现实验结果
- 生产环境部署
- 论文投稿时提供环境信息

---

## 🔄 选择建议

| 场景 | 推荐文件 | 命令 |
|------|---------|------|
| **日常开发** | requirements.txt | `pip install -r requirements.txt` |
| **首次安装** | requirements.txt | `pip install -r requirements.txt` |
| **复现实验** | requirements.lock | `pip install -r requirements.lock` |
| **生产部署** | requirements.lock | `pip install -r requirements.lock` |
| **CI/CD** | requirements.lock | `pip install -r requirements.lock` |

---

## 🔧 更新依赖

### 更新到最新兼容版本

```bash
pip install --upgrade -r requirements.txt
pip freeze > requirements.lock  # 保存新的固定版本
```

### 只更新特定包

```bash
pip install --upgrade numpy
pip freeze > requirements.lock  # 保存新的固定版本
```

### 重新生成 requirements.lock

```bash
# 1. 清空虚拟环境
rm -rf .venv
python -m venv .venv
source .venv/bin/activate

# 2. 安装基础依赖
pip install -r requirements.txt

# 3. 生成固定版本
pip freeze > requirements.lock
```

---

## 📊 当前环境信息

**生成时间**: 2026-01-26  
**Python 版本**: 3.12.3  
**操作系统**: Ubuntu 24.04.3 LTS  
**总包数**: 46 个（包含所有传递依赖）

### 核心包版本（requirements.lock）

| 包名 | 版本 | 说明 |
|------|------|------|
| numpy | 2.4.1 | 数值计算 |
| pettingzoo | 1.25.0 | 多智能体环境 |
| gymnasium | 1.2.3 | 环境接口 |
| openai | 2.15.0 | OpenAI API |
| google-generativeai | 0.8.6 | Gemini API |
| imageio | 2.37.2 | 视频保存 |
| imageio-ffmpeg | 0.6.0 | 视频编码 |
| python-dotenv | 1.2.1 | 环境变量 |
| pillow | 12.1.0 | 图像处理 |

---

## 🐛 故障排查

### Q1: requirements.lock 安装失败

**原因**: 包版本在你的系统上不可用（如不同 Python 版本）

**解决方案**:
```bash
# 使用灵活版本
pip install -r requirements.txt

# 重新生成 lock 文件
pip freeze > requirements.lock
```

### Q2: 版本冲突

**原因**: requirements.lock 中的版本与系统包冲突

**解决方案**:
```bash
# 使用虚拟环境隔离
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.lock
```

### Q3: 需要特定版本的包

**方案1**: 修改 requirements.txt
```txt
numpy==1.24.0  # 固定到特定版本
```

**方案2**: 手动安装后更新 lock
```bash
pip install "numpy==1.24.0"
pip freeze > requirements.lock
```

---

## 📚 相关文档

- [环境配置详细指南](environment_setup.md)
- [快速开始](quickstart.md)
- [API 密钥配置](../configuration/api_keys.md)

---

**最后更新**: 2026-01-26  
**验证工具**: `python verify_environment.py`

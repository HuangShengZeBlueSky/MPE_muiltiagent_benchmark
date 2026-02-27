#!/usr/bin/env python3
"""
环境验证脚本 - 检查所有依赖是否正确安装

运行方式:
    python verify_environment.py

输出: 显示每个依赖的安装状态和版本信息
"""

import sys
import importlib.metadata
from typing import List, Tuple


def check_package(package_name: str, min_version: str = None) -> Tuple[bool, str]:
    """检查包是否安装，返回 (是否安装, 版本信息)"""
    try:
        version = importlib.metadata.version(package_name)
        if min_version and version < min_version:
            return False, f"{version} (需要 >={min_version})"
        return True, version
    except importlib.metadata.PackageNotFoundError:
        return False, "未安装"


def check_import(module_name: str, package_name: str = None) -> bool:
    """检查模块是否可导入"""
    try:
        __import__(module_name)
        return True
    except ImportError as e:
        print(f"  ⚠️  导入失败: {e}")
        return False


def main():
    print("=" * 60)
    print("MPE Multi-Agent Benchmark - 环境验证")
    print("=" * 60)
    print()

    # Python 版本检查
    python_version = f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
    print(f"📌 Python 版本: {python_version}")
    if sys.version_info < (3, 8):
        print("  ❌ Python 版本过低，需要 3.8+")
        sys.exit(1)
    else:
        print("  ✅ Python 版本符合要求 (>=3.8)")
    print()

    # 核心依赖检查
    core_packages = [
        ("numpy", "1.24.0", "数值计算"),
        ("imageio", "2.31.0", "视频保存"),
        ("imageio-ffmpeg", "0.4.9", "视频编码"),
        ("pettingzoo", "1.24.0", "多智能体环境"),
        ("gymnasium", "1.2.0", "环境接口"),
        ("openai", "1.0.0", "OpenAI API"),
        ("google-generativeai", "0.3.0", "Gemini API"),
        ("python-dotenv", "1.0.0", "环境变量管理"),
        ("pillow", "10.0.0", "图像处理"),
    ]

    print("📦 核心依赖检查:")
    print("-" * 60)
    all_installed = True
    for package, min_ver, description in core_packages:
        installed, version = check_package(package, min_ver)
        status = "✅" if installed else "❌"
        print(f"{status} {package:25s} {version:15s} - {description}")
        if not installed:
            all_installed = False
    print()

    # 功能性导入测试
    print("🔍 功能模块测试:")
    print("-" * 60)
    
    tests = [
        ("pettingzoo.mpe", "pettingzoo", "PettingZoo MPE 环境"),
        ("openai", "openai", "OpenAI 客户端"),
        ("google.generativeai", "google-generativeai", "Gemini 客户端"),
        ("dotenv", "python-dotenv", ".env 文件加载"),
    ]

    all_functional = True
    for module, package, description in tests:
        if check_import(module, package):
            print(f"✅ {description:30s} - 可用")
        else:
            print(f"❌ {description:30s} - 不可用")
            all_functional = False
    print()

    # PettingZoo 环境测试
    print("🎮 PettingZoo 环境测试:")
    print("-" * 60)
    try:
        from pettingzoo.mpe import simple_spread_v3
        env = simple_spread_v3.parallel_env(N=3)
        observations, infos = env.reset()
        print(f"✅ Simple Spread 环境可用")
        print(f"   - 智能体数量: {len(observations)}")
        print(f"   - 观测空间维度: {len(list(observations.values())[0])}")
        env.close()
        env_ok = True
    except Exception as e:
        print(f"❌ PettingZoo 环境创建失败: {e}")
        env_ok = False
    print()

    # imageio-ffmpeg 测试
    print("🎬 视频编码器测试:")
    print("-" * 60)
    try:
        import imageio_ffmpeg
        ffmpeg_path = imageio_ffmpeg.get_ffmpeg_exe()
        print(f"✅ FFmpeg 可用")
        print(f"   - 路径: {ffmpeg_path}")
        ffmpeg_ok = True
    except Exception as e:
        print(f"❌ FFmpeg 不可用: {e}")
        ffmpeg_ok = False
    print()

    # 总结
    print("=" * 60)
    print("总结:")
    print("-" * 60)
    
    if all_installed and all_functional and env_ok and ffmpeg_ok:
        print("✅ 所有检查通过！环境配置正确。")
        print()
        print("🚀 下一步:")
        print("   1. 配置 API 密钥: python setup_api_keys.py")
        print("   2. 运行测试: python adv_API.py")
        print("   3. 批量测试: python benchmark_runner.py")
        return 0
    else:
        print("❌ 部分检查未通过，请修复以上问题。")
        print()
        print("🔧 修复建议:")
        if not all_installed:
            print("   - 安装缺失的依赖: pip install -r requirements.txt")
        if not all_functional:
            print("   - 重新安装相关包: pip install --force-reinstall <package>")
        if not env_ok:
            print("   - 检查 PettingZoo 安装: pip install pettingzoo[mpe]")
        if not ffmpeg_ok:
            print("   - 安装 FFmpeg: pip install imageio-ffmpeg")
        print()
        print("📚 详细文档: docs/getting_started/environment_setup.md")
        return 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)

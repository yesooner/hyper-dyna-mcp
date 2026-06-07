#!/usr/bin/env python3
"""
环境验证工具
检查 Python 环境、依赖包和配置
"""

import sys
import io
from pathlib import Path
from typing import List, Tuple

import yaml

# 设置标准输出编码为 UTF-8
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')


def check_python_version() -> Tuple[bool, str]:
    """检查 Python 版本"""
    version = sys.version_info
    if version.major >= 3 and version.minor >= 11:
        return True, f"✓ Python 版本: {version.major}.{version.minor}.{version.micro}"
    else:
        return False, f"✗ Python 版本过低: {version.major}.{version.minor}.{version.micro} (需要 3.11+)"


def check_required_packages() -> List[Tuple[bool, str]]:
    """检查必需的 Python 包"""
    results = []
    required_packages = [
        ("mcp", "MCP 协议库"),
        ("pydantic", "数据验证库"),
        ("yaml", "YAML 解析库"),
        ("loguru", "日志库"),
    ]

    for package, description in required_packages:
        try:
            __import__(package)
            results.append((True, f"✓ {package} ({description})"))
        except ImportError:
            results.append((False, f"✗ {package} ({description}) - 未安装"))

    return results


def check_conda_env() -> Tuple[bool, str]:
    """检查 conda 环境"""
    import os

    # 检查是否在 conda 环境中
    conda_env = os.environ.get('CONDA_DEFAULT_ENV')
    if conda_env:
        return True, f"✓ 当前 conda 环境: {conda_env}"
    else:
        return False, "⚠️  未检测到 conda 环境 (可能已激活但未设置 CONDA_DEFAULT_ENV)"


def check_project_structure() -> List[Tuple[bool, str]]:
    """检查项目结构"""
    results = []
    required_dirs = [
        ("program", "MCP 服务器核心"),
        ("program/tools", "工具模块"),
        ("path", "配置文件"),
        ("tests", "测试文件"),
    ]

    for dir_name, description in required_dirs:
        dir_path = Path(dir_name)
        if dir_path.exists() and dir_path.is_dir():
            results.append((True, f"✓ {dir_name}/ ({description})"))
        else:
            results.append((False, f"✗ {dir_name}/ ({description}) - 目录不存在"))

    return results


def check_config_files() -> List[Tuple[bool, str]]:
    """检查配置文件"""
    results = []
    config_files = [
        ("path/local_paths.yaml", "本地路径配置"),
        ("path/hypermesh_paths.yaml", "HyperMesh 配置"),
        ("path/lsdyna_paths.yaml", "LS-DYNA 配置"),
        ("path/lsprepost_paths.yaml", "LS-PrePost 配置"),
        ("path/obsidian_paths.yaml", "Obsidian 配置"),
        ("pyproject.toml", "项目配置"),
    ]

    for file_path, description in config_files:
        if Path(file_path).exists():
            results.append((True, f"✓ {file_path} ({description})"))
        else:
            results.append((False, f"✗ {file_path} ({description}) - 文件不存在"))

    return results


def check_mcp_server() -> Tuple[bool, str]:
    """检查 MCP 服务器是否可以导入"""
    try:
        from program.server import server
        return True, "✓ MCP 服务器模块可以导入"
    except Exception as e:
        return False, f"✗ MCP 服务器模块导入失败: {e}"


def main():
    """主函数"""
    print("=" * 60)
    print("Hyper-Dyna-MCP 环境验证")
    print("=" * 60)
    print()

    all_results = []

    # 检查 Python 版本
    print("Python 版本:")
    print("-" * 40)
    result = check_python_version()
    all_results.append(result)
    print(f"  {result[1]}")
    print()

    # 检查 conda 环境
    print("Conda 环境:")
    print("-" * 40)
    result = check_conda_env()
    all_results.append(result)
    print(f"  {result[1]}")
    print()

    # 检查必需的包
    print("必需的 Python 包:")
    print("-" * 40)
    results = check_required_packages()
    all_results.extend(results)
    for success, message in results:
        print(f"  {message}")
    print()

    # 检查项目结构
    print("项目结构:")
    print("-" * 40)
    results = check_project_structure()
    all_results.extend(results)
    for success, message in results:
        print(f"  {message}")
    print()

    # 检查配置文件
    print("配置文件:")
    print("-" * 40)
    results = check_config_files()
    all_results.extend(results)
    for success, message in results:
        print(f"  {message}")
    print()

    # 检查 MCP 服务器
    print("MCP 服务器:")
    print("-" * 40)
    result = check_mcp_server()
    all_results.append(result)
    print(f"  {result[1]}")
    print()

    # 统计结果
    print("=" * 60)
    total = len(all_results)
    passed = sum(1 for success, _ in all_results if success)
    failed = total - passed

    print(f"验证结果: {passed}/{total} 通过")

    if failed > 0:
        print(f"\n⚠️  有 {failed} 个环境检查失败")
        print("请检查并修复上述标记为 ✗ 的项目")

        # 提供修复建议
        print("\n修复建议:")
        print("1. 安装缺失的包: pip install mcp pydantic pyyaml loguru")
        print("2. 创建 conda 环境: conda create -n hyper-dyna python=3.13")
        print("3. 激活环境: conda activate hyper-dyna")
        print("4. 安装项目: pip install -e .")

        return 1
    else:
        print("\n✅ 所有环境检查通过！")
        print("\n您可以启动 MCP 服务器:")
        print("  python -m program.server")
        return 0


if __name__ == "__main__":
    sys.exit(main())

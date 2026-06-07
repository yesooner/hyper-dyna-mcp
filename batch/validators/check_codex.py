#!/usr/bin/env python3
"""
CODEX 配置验证工具
检查 CODEX MCP 配置是否正确
"""

import sys
import io
from pathlib import Path
from typing import List, Tuple

import yaml

# 设置标准输出编码为 UTF-8
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')


def load_yaml(filepath: Path) -> dict:
    """加载 YAML 文件"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)
    except Exception as e:
        return {}


def check_codex_config_exists() -> Tuple[bool, str]:
    """检查 CODEX 配置文件是否存在"""
    import os

    # 检查 CODEX_HOME 环境变量
    codex_home = os.environ.get('CODEX_HOME')
    if codex_home:
        config_path = Path(codex_home) / "config.toml"
    else:
        config_path = Path.home() / ".codex" / "config.toml"

    if config_path.exists():
        return True, f"✓ CODEX 配置文件: {config_path}"
    else:
        return False, f"✗ CODEX 配置文件不存在: {config_path}"


def check_codex_config_content() -> Tuple[bool, str]:
    """检查 CODEX 配置文件内容"""
    import os

    # 检查 CODEX_HOME 环境变量
    codex_home = os.environ.get('CODEX_HOME')
    if codex_home:
        config_path = Path(codex_home) / "config.toml"
    else:
        config_path = Path.home() / ".codex" / "config.toml"

    if not config_path.exists():
        return False, "✗ 配置文件不存在"

    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            content = f.read()

        if 'hyper-dyna-mcp' in content:
            return True, "✓ 配置文件中包含 hyper-dyna-mcp 配置"
        else:
            return False, "✗ 配置文件中未找到 hyper-dyna-mcp 配置"
    except Exception as e:
        return False, f"✗ 读取配置文件失败: {e}"


def check_codex_installed() -> Tuple[bool, str]:
    """检查 CODEX 是否已安装"""
    import shutil

    codex_path = shutil.which('codex')
    if codex_path:
        return True, f"✓ CODEX 已安装: {codex_path}"
    else:
        return False, "✗ CODEX 未安装或不在 PATH 中"


def check_codex_mcp_command() -> Tuple[bool, str]:
    """检查 CODEX MCP 命令是否可用"""
    import subprocess

    try:
        result = subprocess.run(
            ['codex', 'mcp', 'list'],
            capture_output=True,
            text=True,
            timeout=10
        )
        if result.returncode == 0:
            return True, "✓ CODEX MCP 命令可用"
        else:
            return False, f"✗ CODEX MCP 命令失败: {result.stderr}"
    except FileNotFoundError:
        return False, "✗ CODEX 未安装"
    except subprocess.TimeoutExpired:
        return False, "✗ CODEX MCP 命令超时"
    except Exception as e:
        return False, f"✗ CODEX MCP 命令异常: {e}"


def check_local_paths() -> List[Tuple[bool, str]]:
    """检查本地路径配置"""
    results = []
    config_path = Path("path/local_paths.yaml")

    if not config_path.exists():
        results.append((False, "✗ path/local_paths.yaml 不存在"))
        return results

    config = load_yaml(config_path)
    project = config.get("project", {})

    # 检查项目根目录
    root = project.get("root", "")
    if root and Path(root).exists():
        results.append((True, f"✓ 项目根目录: {root}"))
    else:
        results.append((False, f"✗ 项目根目录不存在: {root}"))

    # 检查 Python 可执行文件
    python_exe = project.get("python_exe", "")
    if python_exe and Path(python_exe).exists():
        results.append((True, f"✓ Python 可执行文件: {python_exe}"))
    else:
        results.append((False, f"✗ Python 可执行文件不存在: {python_exe}"))

    return results


def check_mcp_server() -> Tuple[bool, str]:
    """检查 MCP 服务器是否可以启动"""
    try:
        # 尝试导入 MCP 服务器模块
        from program.server import server
        return True, "✓ MCP 服务器模块可以导入"
    except Exception as e:
        return False, f"✗ MCP 服务器模块导入失败: {e}"


def main():
    """主函数"""
    print("=" * 60)
    print("Hyper-Dyna-MCP CODEX 配置验证")
    print("=" * 60)
    print()

    all_results = []

    # 检查 CODEX 安装
    print("CODEX 安装检查:")
    print("-" * 40)
    result = check_codex_installed()
    all_results.append(result)
    print(f"  {result[1]}")
    print()

    # 检查 CODEX 配置文件
    print("CODEX 配置文件:")
    print("-" * 40)
    result = check_codex_config_exists()
    all_results.append(result)
    print(f"  {result[1]}")

    result = check_codex_config_content()
    all_results.append(result)
    print(f"  {result[1]}")
    print()

    # 检查 CODEX MCP 命令
    print("CODEX MCP 命令:")
    print("-" * 40)
    result = check_codex_mcp_command()
    all_results.append(result)
    print(f"  {result[1]}")
    print()

    # 检查本地路径
    print("本地路径配置:")
    print("-" * 40)
    results = check_local_paths()
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
        print(f"\n⚠️  有 {failed} 个检查失败")
        print("请检查并修复上述标记为 ✗ 的项目")

        # 提供修复建议
        print("\n修复建议:")
        print("1. 安装 CODEX: npm install -g @openai/codex")
        print("2. 生成配置: python batch/generate_codex_config.py")
        print("3. 验证配置: codex mcp list")
        print("4. 启动 MCP 服务器: python -m program.server")

        return 1
    else:
        print("\n✅ 所有 CODEX 配置检查通过！")
        print("\n下一步:")
        print("1. 验证 MCP 服务器: codex mcp list")
        print("2. 测试工具: codex mcp get hyper-dyna-mcp")
        print("3. 启动 MCP 服务器: python -m program.server")
        return 0


if __name__ == "__main__":
    sys.exit(main())

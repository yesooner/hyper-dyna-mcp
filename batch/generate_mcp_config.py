#!/usr/bin/env python3
"""
MCP 配置生成器
生成 Claude Desktop 和 Claude Code 的 MCP 配置文件
"""

import json
import sys
import io
from pathlib import Path
from typing import Dict, Any

import yaml

# 设置标准输出编码为 UTF-8
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')


def load_local_paths() -> Dict[str, Any]:
    """加载本地路径配置"""
    config_path = Path("path/local_paths.yaml")
    if not config_path.exists():
        print("Error: path/local_paths.yaml not found")
        sys.exit(1)

    with open(config_path, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)


def generate_claude_desktop_config(project_root: str, python_exe: str) -> Dict[str, Any]:
    """生成 Claude Desktop 配置"""
    # 确保项目根目录是绝对路径
    abs_project_root = str(Path(project_root).resolve())
    return {
        "mcpServers": {
            "hyper-dyna-mcp": {
                "command": python_exe,
                "args": ["-m", "program.server"],
                "cwd": abs_project_root,
                "env": {
                    "PYTHONPATH": abs_project_root
                }
            }
        }
    }


def generate_claude_code_config(project_root: str, python_exe: str) -> Dict[str, Any]:
    """生成 Claude Code 配置"""
    # 确保项目根目录是绝对路径
    abs_project_root = str(Path(project_root).resolve())
    return {
        "mcpServers": {
            "hyper-dyna-mcp": {
                "command": python_exe,
                "args": ["-m", "program.server"],
                "cwd": abs_project_root,
                "env": {
                    "PYTHONPATH": abs_project_root
                }
            }
        }
    }


def get_claude_desktop_config_path() -> Path:
    """获取 Claude Desktop 配置文件路径"""
    import os
    import platform

    system = platform.system()

    if system == "Windows":
        appdata = os.environ.get('APPDATA', '')
        return Path(appdata) / "Claude" / "claude_desktop_config.json"
    elif system == "Darwin":  # macOS
        return Path.home() / "Library" / "Application Support" / "Claude" / "claude_desktop_config.json"
    else:  # Linux
        return Path.home() / ".config" / "Claude" / "claude_desktop_config.json"


def save_config(config: Dict[str, Any], filepath: Path, name: str) -> None:
    """保存配置文件"""
    # 确保目录存在
    filepath.parent.mkdir(parents=True, exist_ok=True)

    # 如果文件已存在，备份
    if filepath.exists():
        backup_path = filepath.with_suffix('.json.backup')
        filepath.rename(backup_path)
        print(f"  已备份旧配置到: {backup_path}")

    # 保存新配置
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(config, f, indent=2, ensure_ascii=False)

    print(f"  ✓ 已生成 {name} 配置: {filepath}")


def main():
    """主函数"""
    print("=" * 60)
    print("Hyper-Dyna-MCP MCP 配置生成器")
    print("=" * 60)
    print()

    # 加载配置
    config = load_local_paths()
    project = config.get("project", {})
    project_root = project.get("root", "")
    python_exe = project.get("python_exe", "")

    if not project_root or not python_exe:
        print("Error: 无法从 path/local_paths.yaml 读取项目路径")
        sys.exit(1)

    print(f"项目根目录: {project_root}")
    print(f"Python 路径: {python_exe}")
    print()

    # 生成 Claude Desktop 配置
    print("生成 Claude Desktop 配置...")
    desktop_config = generate_claude_desktop_config(project_root, python_exe)
    desktop_path = get_claude_desktop_config_path()
    save_config(desktop_config, desktop_path, "Claude Desktop")
    print()

    # 生成 Claude Code 配置（保存到项目目录）
    print("生成 Claude Code 配置...")
    code_config = generate_claude_code_config(project_root, python_exe)
    code_path = Path("claude_code_mcp.json")
    save_config(code_config, code_path, "Claude Code")
    print()

    # 显示手动配置说明
    print("=" * 60)
    print("配置说明")
    print("=" * 60)
    print()
    print("1. Claude Desktop 配置已自动保存到:")
    print(f"   {desktop_path}")
    print()
    print("2. Claude Code 配置已保存到:")
    print(f"   {code_path.absolute()}")
    print()
    print("3. 如需手动配置 Claude Code，请将以下内容添加到:")
    print("   ~/.claude/settings.json 的 mcpServers 部分")
    print()
    print(json.dumps(code_config, indent=2, ensure_ascii=False))
    print()
    print("4. 重启 Claude Desktop 或 Claude Code 以加载新配置")
    print()


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

#!/usr/bin/env python3
"""
CODEX 配置生成器
生成 OpenAI Codex CLI 的 MCP 配置
"""

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


def generate_codex_config(project_root: str, python_exe: str) -> str:
    """生成 CODEX 配置内容"""
    # 确保路径使用反斜杠（Windows 风格）并转换为绝对路径
    project_root_abs = str(Path(project_root).resolve()).replace('/', '\\')
    python_exe_abs = str(Path(python_exe).resolve()).replace('/', '\\')

    config = f"""# Hyper-Dyna-MCP CODEX 配置
# 由配置向导自动生成

[mcp_servers.hyper-dyna-mcp]
type = "stdio"
command = '{python_exe_abs}'
args = ["-m", "program.server"]
cwd = '{project_root_abs}'
startup_timeout_sec = 30.0
tool_timeout_sec = 120.0
enabled = true
required = false

[mcp_servers.hyper-dyna-mcp.env]
PYTHONPATH = '{project_root_abs}'
PYTHONIOENCODING = "utf-8"
PYTHONUTF8 = "1"
"""
    return config


def get_codex_config_path() -> Path:
    """获取 CODEX 配置文件路径"""
    import os

    # 检查 CODEX_HOME 环境变量
    codex_home = os.environ.get('CODEX_HOME')
    if codex_home:
        return Path(codex_home) / "config.toml"

    # 默认路径
    return Path.home() / ".codex" / "config.toml"


def save_config(config: str, filepath: Path, name: str) -> None:
    """保存配置文件"""
    # 确保目录存在
    filepath.parent.mkdir(parents=True, exist_ok=True)

    # 如果文件已存在，备份
    if filepath.exists():
        backup_path = filepath.with_suffix('.toml.backup')
        filepath.rename(backup_path)
        print(f"  已备份旧配置到: {backup_path}")

    # 保存新配置
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(config)

    print(f"  ✓ 已生成 {name} 配置: {filepath}")


def append_to_existing_config(config_section: str, filepath: Path) -> bool:
    """将配置追加到现有配置文件"""
    if not filepath.exists():
        return False

    # 读取现有配置
    with open(filepath, 'r', encoding='utf-8') as f:
        existing_content = f.read()

    # 检查是否已存在 hyper-dyna-mcp 配置
    if 'hyper-dyna-mcp' in existing_content:
        print(f"  ⚠️  配置文件中已存在 hyper-dyna-mcp 配置")
        return False

    # 追加配置
    with open(filepath, 'a', encoding='utf-8') as f:
        f.write('\n\n' + config_section)

    print(f"  ✓ 已追加配置到: {filepath}")
    return True


def main():
    """主函数"""
    import argparse

    parser = argparse.ArgumentParser(description="Hyper-Dyna-MCP CODEX 配置生成器")
    parser.add_argument("--append", action="store_true", help="追加到现有配置文件")
    parser.add_argument("--show", action="store_true", help="仅显示配置内容")
    parser.add_argument("--output", type=str, help="输出到指定文件")
    args = parser.parse_args()

    print("=" * 60)
    print("Hyper-Dyna-MCP CODEX 配置生成器")
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

    # 生成配置
    print("生成 CODEX 配置...")
    codex_config = generate_codex_config(project_root, python_exe)

    # 获取配置文件路径
    codex_path = get_codex_config_path()
    print(f"CODEX 配置文件路径: {codex_path}")
    print()

    # 处理命令行参数
    if args.show:
        # 仅显示配置
        print("\n生成的配置内容:")
        print("-" * 60)
        print(codex_config)
        print("-" * 60)
        print(f"\n请手动将上述内容添加到: {codex_path}")
    elif args.output:
        # 输出到指定文件
        output_path = Path(args.output)
        save_config(codex_config, output_path, "CODEX")
        print(f"\n配置已保存到: {output_path}")
        print(f"请手动将内容添加到: {codex_path}")
    elif args.append or codex_path.exists():
        # 追加到现有配置
        if codex_path.exists():
            print("检测到现有 CODEX 配置文件")

        config_section = f"""
# Hyper-Dyna-MCP MCP Server
{codex_config}"""
        if append_to_existing_config(config_section, codex_path):
            print("\n配置已成功追加！")
        else:
            print("\n追加失败，请手动添加配置。")
            print("\n生成的配置内容:")
            print("-" * 60)
            print(codex_config)
            print("-" * 60)
    else:
        # 创建新配置文件
        save_config(codex_config, codex_path, "CODEX")

    print()
    print("=" * 60)
    print("配置完成！")
    print("=" * 60)
    print()
    print("下一步:")
    print("1. 重启 CODEX 以加载新配置")
    print("2. 验证 MCP 服务器: codex mcp list")
    print("3. 测试工具: codex mcp get hyper-dyna-mcp")
    print()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n已取消配置。")
        sys.exit(1)
    except Exception as e:
        print(f"\n错误: {e}")
        sys.exit(1)

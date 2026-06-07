#!/usr/bin/env python3
"""
目录重组脚本
将 batch 目录重组为更清晰的结构
"""

import os
import shutil
from pathlib import Path


def create_directory_structure():
    """创建新的目录结构"""
    directories = [
        "batch/core",           # 核心功能
        "batch/generators",     # 配置生成器
        "batch/validators",     # 验证工具
        "batch/templates",      # 模板文件（已存在）
        "batch/docs",           # 文档
        "batch/scripts",        # 安装脚本
    ]

    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
        print(f"✓ 创建目录: {directory}")


def move_files():
    """移动文件到新目录"""
    # 核心功能
    core_files = [
        "batch/auto_detect.py",
        "batch/setup_wizard.py",
        "batch/sync_config.py",
    ]

    # 配置生成器
    generator_files = [
        "batch/generate_mcp_config.py",
        "batch/generate_codex_config.py",
    ]

    # 文档
    doc_files = [
        "batch/README.md",
        "batch/QUICK_START.md",
        "batch/CHANGELOG.md",
        "batch/CONFIG_COMPLETE.md",
    ]

    # 安装脚本
    script_files = [
        "batch/install.bat",
        "batch/install.sh",
    ]

    # 测试文件
    test_files = [
        "batch/test_batch.py",
        "batch/test_batch_simple.py",
    ]

    # 移动文件
    moves = [
        (core_files, "batch/core"),
        (generator_files, "batch/generators"),
        (doc_files, "batch/docs"),
        (script_files, "batch/scripts"),
        (test_files, "batch/tests"),
    ]

    for files, target_dir in moves:
        for file_path in files:
            if Path(file_path).exists():
                target_path = Path(target_dir) / Path(file_path).name
                shutil.move(file_path, target_path)
                print(f"✓ 移动: {file_path} → {target_path}")


def create_init_files():
    """创建 __init__.py 文件"""
    init_dirs = [
        "batch/core",
        "batch/generators",
        "batch/tests",
    ]

    for directory in init_dirs:
        init_path = Path(directory) / "__init__.py"
        if not init_path.exists():
            init_path.write_text("# Hyper-Dyna-MCP Batch Module\n")
            print(f"✓ 创建: {init_path}")


def update_imports():
    """更新导入语句（简化版本，实际需要更复杂的处理）"""
    print("\n注意: 需要手动更新以下文件的导入语句:")
    print("  - batch/validate_all.py")
    print("  - batch/validators/*.py")
    print("  - 其他引用移动文件的脚本")


def main():
    """主函数"""
    print("=" * 60)
    print("Hyper-Dyna-MCP Batch 目录重组")
    print("=" * 60)
    print()

    # 检查是否在正确的目录
    if not Path("batch").exists():
        print("Error: 请在 hyper-dyna-mcp 项目根目录运行此脚本")
        return

    # 创建新目录结构
    print("创建新目录结构...")
    create_directory_structure()
    print()

    # 移动文件
    print("移动文件...")
    move_files()
    print()

    # 创建 __init__.py 文件
    print("创建 __init__.py 文件...")
    create_init_files()
    print()

    # 提示更新导入
    update_imports()

    print()
    print("=" * 60)
    print("目录重组完成！")
    print("=" * 60)
    print()
    print("新目录结构:")
    print("batch/")
    print("├── core/           # 核心功能")
    print("│   ├── auto_detect.py")
    print("│   ├── setup_wizard.py")
    print("│   └── sync_config.py")
    print("├── generators/     # 配置生成器")
    print("│   ├── generate_mcp_config.py")
    print("│   └── generate_codex_config.py")
    print("├── validators/     # 验证工具")
    print("│   ├── check_paths.py")
    print("│   ├── check_env.py")
    print("│   └── check_codex.py")
    print("├── templates/      # 模板文件")
    print("├── docs/           # 文档")
    print("├── scripts/        # 安装脚本")
    print("└── tests/          # 测试文件")
    print()


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
Batch 配置系统简单测试脚本
测试所有 batch 组件文件是否存在
"""

import sys
import io
from pathlib import Path

# 设置标准输出编码为 UTF-8
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')


def test_files():
    """测试所有 batch 文件是否存在"""
    print("=" * 60)
    print("Hyper-Dyna-MCP Batch 配置系统文件检查")
    print("=" * 60)
    print()

    files = [
        # 配置模板
        ("batch/templates/local_paths.yaml", "本地路径配置模板"),
        ("batch/templates/hypermesh_paths.yaml", "HyperMesh 配置模板"),
        ("batch/templates/lsdyna_paths.yaml", "LS-DYNA 配置模板"),
        ("batch/templates/lsprepost_paths.yaml", "LS-PrePost 配置模板"),
        ("batch/templates/obsidian_paths.yaml", "Obsidian 配置模板"),
        ("batch/templates/.env.example", "环境变量模板"),
        ("batch/templates/claude_desktop_config.json", "Claude Desktop 配置模板"),
        ("batch/templates/claude_code_mcp.json", "Claude Code 配置模板"),

        # 脚本文件
        ("batch/setup_wizard.py", "交互式配置向导"),
        ("batch/generate_mcp_config.py", "MCP 配置生成器"),
        ("batch/validators/check_paths.py", "路径验证工具"),
        ("batch/validators/check_env.py", "环境验证工具"),
        ("batch/test_batch.py", "测试脚本"),
        ("batch/test_batch_simple.py", "简单测试脚本"),

        # 安装脚本
        ("install.bat", "Windows 快速安装脚本"),
        ("install.sh", "Linux/macOS 快速安装脚本"),
        ("uninstall.bat", "Windows 卸载脚本"),
        ("uninstall.sh", "Linux/macOS 卸载脚本"),

        # 文档
        ("batch/README.md", "详细配置指南"),
        ("batch/QUICK_START.md", "快速开始"),
        ("batch/CHANGELOG.md", "更新日志"),
    ]

    passed = 0
    failed = 0

    for filepath, description in files:
        if Path(filepath).exists():
            print(f"✓ {filepath} - {description}")
            passed += 1
        else:
            print(f"✗ {filepath} - {description} (不存在)")
            failed += 1

    print()
    print("=" * 60)
    print(f"文件检查结果: {passed}/{passed + failed} 通过")

    if failed == 0:
        print("\n✅ 所有 batch 文件都存在！")
        return 0
    else:
        print(f"\n⚠️  有 {failed} 个文件缺失。")
        return 1


if __name__ == "__main__":
    sys.exit(test_files())

#!/usr/bin/env python3
"""
Batch 配置系统测试脚本
测试所有 batch 组件是否正常工作
"""

import sys
import io
from pathlib import Path

# 设置标准输出编码为 UTF-8
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')


def test_templates():
    """测试配置模板是否存在"""
    print("测试配置模板...")
    templates = [
        "batch/templates/local_paths.yaml",
        "batch/templates/hypermesh_paths.yaml",
        "batch/templates/lsdyna_paths.yaml",
        "batch/templates/lsprepost_paths.yaml",
        "batch/templates/obsidian_paths.yaml",
        "batch/templates/.env.example",
        "batch/templates/claude_desktop_config.json",
        "batch/templates/claude_code_mcp.json",
    ]

    passed = 0
    for template in templates:
        if Path(template).exists():
            print(f"  ✓ {template}")
            passed += 1
        else:
            print(f"  ✗ {template} (不存在)")

    return passed, len(templates)


def test_scripts():
    """测试脚本文件是否存在"""
    print("\n测试脚本文件...")
    scripts = [
        "batch/setup_wizard.py",
        "batch/generate_mcp_config.py",
        "batch/validators/check_paths.py",
        "batch/validators/check_env.py",
        "install.bat",
        "install.sh",
        "uninstall.bat",
        "uninstall.sh",
    ]

    passed = 0
    for script in scripts:
        if Path(script).exists():
            print(f"  ✓ {script}")
            passed += 1
        else:
            print(f"  ✗ {script} (不存在)")

    return passed, len(scripts)


def test_documentation():
    """测试文档文件是否存在"""
    print("\n测试文档文件...")
    docs = [
        "batch/README.md",
        "batch/QUICK_START.md",
        "batch/CHANGELOG.md",
    ]

    passed = 0
    for doc in docs:
        if Path(doc).exists():
            print(f"  ✓ {doc}")
            passed += 1
        else:
            print(f"  ✗ {doc} (不存在)")

    return passed, len(docs)


def test_imports():
    """测试 Python 模块是否可以导入"""
    print("\n测试 Python 模块导入...")
    modules = [
        ("batch.validators.check_paths", "路径验证"),
        ("batch.validators.check_env", "环境验证"),
    ]

    passed = 0
    for module_name, description in modules:
        try:
            # 尝试直接导入模块文件
            if module_name == "batch.validators.check_paths":
                import importlib.util
                spec = importlib.util.spec_from_file_location(
                    "check_paths", "batch/validators/check_paths.py"
                )
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)
            elif module_name == "batch.validators.check_env":
                import importlib.util
                spec = importlib.util.spec_from_file_location(
                    "check_env", "batch/validators/check_env.py"
                )
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)
            print(f"  ✓ {module_name} ({description})")
            passed += 1
        except Exception as e:
            print(f"  ✗ {module_name} ({description}) - {e}")

    return passed, len(modules)


def main():
    """主测试函数"""
    print("=" * 60)
    print("Hyper-Dyna-MCP Batch 配置系统测试")
    print("=" * 60)
    print()

    results = []

    # 运行所有测试
    results.append(test_templates())
    results.append(test_scripts())
    results.append(test_documentation())
    results.append(test_imports())

    # 统计结果
    print("\n" + "=" * 60)
    total_passed = sum(p for p, _ in results)
    total_tests = sum(t for _, t in results)

    print(f"测试结果: {total_passed}/{total_tests} 通过")

    if total_passed == total_tests:
        print("\n✅ 所有测试通过！Batch 配置系统正常工作。")
        return 0
    else:
        print(f"\n⚠️  有 {total_tests - total_passed} 个测试失败。")
        return 1


if __name__ == "__main__":
    sys.exit(main())

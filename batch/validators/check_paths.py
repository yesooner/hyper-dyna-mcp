#!/usr/bin/env python3
"""
路径验证工具
检查所有配置的路径是否存在
"""

import sys
import io
from pathlib import Path
from typing import List, Tuple

import yaml

# 设置标准输出编码为 UTF-8
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')


def load_yaml(filepath: Path) -> dict:
    """加载 YAML 文件"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)
    except Exception as e:
        print(f"Error loading {filepath}: {e}")
        return {}


def check_path(path: str, name: str) -> Tuple[bool, str]:
    """检查路径是否存在"""
    if not path:
        return False, f"{name}: 路径为空"

    path_obj = Path(path)
    if path_obj.exists():
        return True, f"✓ {name}: {path}"
    else:
        return False, f"✗ {name}: {path} (不存在)"


def check_local_paths() -> List[Tuple[bool, str]]:
    """检查 local_paths.yaml"""
    results = []
    config_path = Path("path/local_paths.yaml")

    if not config_path.exists():
        results.append((False, "✗ path/local_paths.yaml 不存在"))
        return results

    config = load_yaml(config_path)
    project = config.get("project", {})

    # 检查项目根目录
    root = project.get("root", "")
    results.append(check_path(root, "项目根目录"))

    # 检查 Python 可执行文件
    python_exe = project.get("python_exe", "")
    results.append(check_path(python_exe, "Python 可执行文件"))

    # 检查 runs 目录
    run = config.get("run", {})
    runs_dir = run.get("runs_dir", "")
    if runs_dir:
        results.append(check_path(runs_dir, "运行目录"))

    reports_dir = run.get("reports_dir", "")
    if reports_dir:
        results.append(check_path(reports_dir, "报告目录"))

    return results


def check_hypermesh_paths() -> List[Tuple[bool, str]]:
    """检查 hypermesh_paths.yaml"""
    results = []
    config_path = Path("path/hypermesh_paths.yaml")

    if not config_path.exists():
        results.append((False, "✗ path/hypermesh_paths.yaml 不存在"))
        return results

    config = load_yaml(config_path)
    hm = config.get("hypermesh", {})

    # 检查安装目录
    install_dir = hm.get("install_dir", "")
    results.append(check_path(install_dir, "HyperMesh 安装目录"))

    # 检查 hmbatch.exe
    hmbatch_exe = hm.get("hmbatch_exe", "")
    results.append(check_path(hmbatch_exe, "hmbatch.exe"))

    # 检查 hmopengl.exe
    hmopengl_exe = hm.get("hmopengl_exe", "")
    results.append(check_path(hmopengl_exe, "hmopengl.exe"))

    return results


def check_lsdyna_paths() -> List[Tuple[bool, str]]:
    """检查 lsdyna_paths.yaml"""
    results = []
    config_path = Path("path/lsdyna_paths.yaml")

    if not config_path.exists():
        results.append((False, "✗ path/lsdyna_paths.yaml 不存在"))
        return results

    config = load_yaml(config_path)
    lsdyna = config.get("lsdyna", {})

    # 检查求解器路径
    solver_exe = lsdyna.get("solver_exe", "")
    results.append(check_path(solver_exe, "LS-DYNA 求解器"))

    return results


def check_lsprepost_paths() -> List[Tuple[bool, str]]:
    """检查 lsprepost_paths.yaml"""
    results = []
    config_path = Path("path/lsprepost_paths.yaml")

    if not config_path.exists():
        results.append((False, "✗ path/lsprepost_paths.yaml 不存在"))
        return results

    config = load_yaml(config_path)
    lsprepost = config.get("lsprepost", {})

    # 检查可执行文件路径
    exe_path = lsprepost.get("exe_path", "")
    results.append(check_path(exe_path, "LS-PrePost 可执行文件"))

    return results


def check_obsidian_paths() -> List[Tuple[bool, str]]:
    """检查 obsidian_paths.yaml"""
    results = []
    config_path = Path("path/obsidian_paths.yaml")

    if not config_path.exists():
        results.append((False, "✗ path/obsidian_paths.yaml 不存在"))
        return results

    config = load_yaml(config_path)
    obsidian = config.get("obsidian", {})

    # 检查根目录
    root = obsidian.get("root", "")
    results.append(check_path(root, "Obsidian 根目录"))

    return results


def main():
    """主函数"""
    print("=" * 60)
    print("Hyper-Dyna-MCP 路径验证")
    print("=" * 60)
    print()

    all_results = []

    # 检查所有配置
    checks = [
        ("本地路径配置", check_local_paths),
        ("HyperMesh 配置", check_hypermesh_paths),
        ("LS-DYNA 配置", check_lsdyna_paths),
        ("LS-PrePost 配置", check_lsprepost_paths),
        ("Obsidian 配置", check_obsidian_paths),
    ]

    for name, check_func in checks:
        print(f"\n{name}:")
        print("-" * 40)
        results = check_func()
        all_results.extend(results)
        for success, message in results:
            print(f"  {message}")

    # 统计结果
    print("\n" + "=" * 60)
    total = len(all_results)
    passed = sum(1 for success, _ in all_results if success)
    failed = total - passed

    print(f"验证结果: {passed}/{total} 通过")

    if failed > 0:
        print(f"\n⚠️  有 {failed} 个路径验证失败")
        print("请检查并修复上述标记为 ✗ 的路径")
        return 1
    else:
        print("\n✅ 所有路径验证通过！")
        return 0


if __name__ == "__main__":
    sys.exit(main())

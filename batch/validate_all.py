#!/usr/bin/env python3
"""
完整配置验证脚本
检查所有配置文件和环境
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


def check_file_exists(filepath: str, name: str) -> Tuple[bool, str]:
    """检查文件是否存在"""
    if Path(filepath).exists():
        return True, f"✓ {name}: {filepath}"
    else:
        return False, f"✗ {name}: {filepath} (不存在)"


def check_path_exists(path: str, name: str) -> Tuple[bool, str]:
    """检查路径是否存在"""
    if not path:
        return False, f"✗ {name}: 路径为空"

    if Path(path).exists():
        return True, f"✓ {name}: {path}"
    else:
        return False, f"✗ {name}: {path} (不存在)"


def check_config_files() -> List[Tuple[bool, str]]:
    """检查配置文件"""
    results = []
    config_files = [
        ("path/local_paths.yaml", "本地路径配置"),
        ("path/hypermesh_paths.yaml", "HyperMesh 配置"),
        ("path/lsdyna_paths.yaml", "LS-DYNA 配置"),
        ("path/lsprepost_paths.yaml", "LS-PrePost 配置"),
        ("path/obsidian_paths.yaml", "Obsidian 配置"),
    ]

    for filepath, name in config_files:
        results.append(check_file_exists(filepath, name))

    return results


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
    results.append(check_path_exists(root, "项目根目录"))

    # 检查 Python 可执行文件
    python_exe = project.get("python_exe", "")
    results.append(check_path_exists(python_exe, "Python 可执行文件"))

    # 检查 runs 目录
    run = config.get("run", {})
    runs_dir = run.get("runs_dir", "")
    if runs_dir:
        results.append(check_path_exists(runs_dir, "运行目录"))

    reports_dir = run.get("reports_dir", "")
    if reports_dir:
        results.append(check_path_exists(reports_dir, "报告目录"))

    return results


def check_hypermesh_paths() -> List[Tuple[bool, str]]:
    """检查 HyperMesh 配置"""
    results = []
    config_path = Path("path/hypermesh_paths.yaml")

    if not config_path.exists():
        results.append((False, "✗ path/hypermesh_paths.yaml 不存在"))
        return results

    config = load_yaml(config_path)
    hm = config.get("hypermesh", {})

    # 检查安装目录
    install_dir = hm.get("install_dir", "")
    results.append(check_path_exists(install_dir, "HyperMesh 安装目录"))

    # 检查 hmbatch.exe
    hmbatch_exe = hm.get("hmbatch_exe", "")
    results.append(check_path_exists(hmbatch_exe, "hmbatch.exe"))

    # 检查 hmopengl.exe
    hmopengl_exe = hm.get("hmopengl_exe", "")
    results.append(check_path_exists(hmopengl_exe, "hmopengl.exe"))

    return results


def check_lsdyna_paths() -> List[Tuple[bool, str]]:
    """检查 LS-DYNA 配置"""
    results = []
    config_path = Path("path/lsdyna_paths.yaml")

    if not config_path.exists():
        results.append((False, "✗ path/lsdyna_paths.yaml 不存在"))
        return results

    config = load_yaml(config_path)
    lsdyna = config.get("lsdyna", {})

    # 检查求解器路径
    solver_exe = lsdyna.get("solver_exe", "")
    results.append(check_path_exists(solver_exe, "LS-DYNA 求解器"))

    return results


def check_lsprepost_paths() -> List[Tuple[bool, str]]:
    """检查 LS-PrePost 配置"""
    results = []
    config_path = Path("path/lsprepost_paths.yaml")

    if not config_path.exists():
        results.append((False, "✗ path/lsprepost_paths.yaml 不存在"))
        return results

    config = load_yaml(config_path)
    lsprepost = config.get("lsprepost", {})

    # 检查可执行文件路径
    exe_path = lsprepost.get("exe_path", lsprepost.get("exe", ""))
    results.append(check_path_exists(exe_path, "LS-PrePost 可执行文件"))

    return results


def check_obsidian_paths() -> List[Tuple[bool, str]]:
    """检查 Obsidian 配置"""
    results = []
    config_path = Path("path/obsidian_paths.yaml")

    if not config_path.exists():
        results.append((False, "✗ path/obsidian_paths.yaml 不存在"))
        return results

    config = load_yaml(config_path)
    obsidian = config.get("obsidian", {})

    # 检查根目录
    root = obsidian.get("root", "")
    results.append(check_path_exists(root, "Obsidian 根目录"))

    return results


def check_batch_files() -> List[Tuple[bool, str]]:
    """检查 batch 文件"""
    results = []
    batch_files = [
        ("batch/setup_wizard.py", "配置向导"),
        ("batch/generate_mcp_config.py", "MCP 配置生成器"),
        ("batch/generate_codex_config.py", "CODEX 配置生成器"),
        ("batch/sync_config.py", "配置同步工具"),
        ("batch/validators/check_paths.py", "路径验证工具"),
        ("batch/validators/check_env.py", "环境验证工具"),
        ("batch/validators/check_codex.py", "CODEX 验证工具"),
    ]

    for filepath, name in batch_files:
        results.append(check_file_exists(filepath, name))

    return results


def main():
    """主函数"""
    print("=" * 60)
    print("Hyper-Dyna-MCP 完整配置验证")
    print("=" * 60)
    print()

    all_results = []

    # 检查配置文件
    print("配置文件检查:")
    print("-" * 40)
    results = check_config_files()
    all_results.extend(results)
    for success, message in results:
        print(f"  {message}")
    print()

    # 检查本地路径
    print("本地路径配置:")
    print("-" * 40)
    results = check_local_paths()
    all_results.extend(results)
    for success, message in results:
        print(f"  {message}")
    print()

    # 检查 HyperMesh 配置
    print("HyperMesh 配置:")
    print("-" * 40)
    results = check_hypermesh_paths()
    all_results.extend(results)
    for success, message in results:
        print(f"  {message}")
    print()

    # 检查 LS-DYNA 配置
    print("LS-DYNA 配置:")
    print("-" * 40)
    results = check_lsdyna_paths()
    all_results.extend(results)
    for success, message in results:
        print(f"  {message}")
    print()

    # 检查 LS-PrePost 配置
    print("LS-PrePost 配置:")
    print("-" * 40)
    results = check_lsprepost_paths()
    all_results.extend(results)
    for success, message in results:
        print(f"  {message}")
    print()

    # 检查 Obsidian 配置
    print("Obsidian 配置:")
    print("-" * 40)
    results = check_obsidian_paths()
    all_results.extend(results)
    for success, message in results:
        print(f"  {message}")
    print()

    # 检查 batch 文件
    print("Batch 工具文件:")
    print("-" * 40)
    results = check_batch_files()
    all_results.extend(results)
    for success, message in results:
        print(f"  {message}")
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
        return 1
    else:
        print("\n✅ 所有配置验证通过！")
        print("\n下一步:")
        print("1. 生成 Claude MCP 配置: python batch/generate_mcp_config.py")
        print("2. 生成 CODEX MCP 配置: python batch/generate_codex_config.py")
        print("3. 启动 MCP 服务器: python -m program.server")
        return 0


if __name__ == "__main__":
    sys.exit(main())

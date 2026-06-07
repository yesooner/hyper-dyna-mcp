#!/usr/bin/env python3
"""
自动环境检测工具
检测 Python/Conda 环境和 HyperMesh 安装路径
"""

import os
import sys
import io
from pathlib import Path
from typing import Optional, Tuple

# 设置标准输出编码为 UTF-8
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')


def detect_conda_env() -> Optional[Tuple[str, str]]:
    """
    检测 conda 环境中的 Python 路径
    返回: (python_exe, conda_env_name) 或 None
    """
    print("检测 Conda 环境...")

    # 常见的 conda 安装路径
    conda_paths = [
        Path.home() / "anaconda3",
        Path.home() / "miniconda3",
        Path("E:/anaconda3/anzhuang"),
        Path("C:/ProgramData/anaconda3"),
        Path("C:/ProgramData/miniconda3"),
    ]

    # 查找 hyper-dyna 环境
    env_name = "hyper-dyna"

    for conda_path in conda_paths:
        if not conda_path.exists():
            continue

        # Windows 路径
        python_path = conda_path / "envs" / env_name / "python.exe"
        if python_path.exists():
            print(f"  ✓ 找到 {env_name} 环境: {python_path}")
            return (str(python_path), env_name)

        # Linux/macOS 路径
        python_path = conda_path / "envs" / env_name / "bin" / "python"
        if python_path.exists():
            print(f"  ✓ 找到 {env_name} 环境: {python_path}")
            return (str(python_path), env_name)

    # 如果没找到 hyper-dyna，查找其他环境
    print(f"  ⚠️  未找到 {env_name} 环境")
    print("  请先创建环境: conda create -n hyper-dyna python=3.13")
    return None


def detect_hypermesh() -> Optional[Tuple[str, str, str, str]]:
    """
    检测 HyperMesh 安装路径
    返回: (install_dir, hmbatch_exe, hmopengl_exe, version) 或 None
    """
    print("检测 HyperMesh 安装...")

    # 常见的 HyperMesh 安装路径
    possible_paths = [
        ("C:/Program Files/Altair/2024/hw/bin/win64", "2024"),
        ("C:/Program Files/Altair/2023/hw/bin/win64", "2023"),
        ("C:/Program Files/Altair/2022/hw/bin/win64", "2022"),
        ("C:/Program Files/Altair/2021/hw/bin/win64", "2021"),
        ("E:/HM2021/2021/hwdesktop/hm/bin/win64", "2021"),
    ]

    for install_dir, version in possible_paths:
        install_path = Path(install_dir)
        if not install_path.exists():
            continue

        # 检查 hmbatch.exe
        hmbatch_exe = install_path / "hmbatch.exe"
        if not hmbatch_exe.exists():
            continue

        # 检查 hmopengl.exe
        hmopengl_exe = install_path / "hmopengl.exe"
        if not hmopengl_exe.exists():
            continue

        # 获取父目录作为安装目录
        parent_dir = install_path.parent.parent.parent

        print(f"  ✓ 找到 HyperMesh {version}: {parent_dir}")
        return (str(parent_dir), str(hmbatch_exe), str(hmopengl_exe), version)

    print("  ⚠️  未找到 HyperMesh 安装")
    print("  请手动配置 path/hypermesh_paths.yaml")
    return None


def generate_config_files(
    project_root: str,
    python_exe: str,
    conda_env: str,
    hypermesh: Optional[Tuple[str, str, str, str]]
) -> None:
    """
    生成配置文件
    """
    import yaml

    print("\n生成配置文件...")

    # 确保 path 目录存在
    path_dir = Path(project_root) / "path"
    path_dir.mkdir(exist_ok=True)

    # 1. 生成 local_paths.yaml
    local_config = {
        "project": {
            "root": project_root.replace("\\", "/"),
            "conda_env": conda_env,
            "python_exe": python_exe.replace("\\", "/"),
            "python_version": "3.13"
        },
        "run": {
            "default_dry_run": True,
            "runs_dir": f"{project_root}/runs".replace("\\", "/"),
            "reports_dir": f"{project_root}/reports".replace("\\", "/")
        }
    }

    local_path = path_dir / "local_paths.yaml"
    with open(local_path, 'w', encoding='utf-8') as f:
        yaml.dump(local_config, f, default_flow_style=False, allow_unicode=True)
    print(f"  ✓ 生成 {local_path}")

    # 2. 生成 hypermesh_paths.yaml
    if hypermesh:
        install_dir, hmbatch_exe, hmopengl_exe, version = hypermesh
        hm_config = {
            "hypermesh": {
                "install_dir": install_dir.replace("\\", "/"),
                "hmbatch_exe": hmbatch_exe.replace("\\", "/"),
                "hmopengl_exe": hmopengl_exe.replace("\\", "/"),
                "version": version,
                "gui_port": 47882,
                "default_timeout": 300
            }
        }
    else:
        hm_config = {
            "hypermesh": {
                "install_dir": "<YOUR_HYPERMESH_INSTALL_DIR>",
                "hmbatch_exe": "<YOUR_HYPERMESH_INSTALL_DIR>/hm/bin/win64/hmbatch.exe",
                "hmopengl_exe": "<YOUR_HYPERMESH_INSTALL_DIR>/hm/bin/win64/hmopengl.exe",
                "version": "2024",
                "gui_port": 47882,
                "default_timeout": 300
            }
        }

    hm_path = path_dir / "hypermesh_paths.yaml"
    with open(hm_path, 'w', encoding='utf-8') as f:
        yaml.dump(hm_config, f, default_flow_style=False, allow_unicode=True)
    print(f"  ✓ 生成 {hm_path}")

    # 3. 生成其他配置文件模板
    template_files = [
        "lsdyna_paths.yaml",
        "lsprepost_paths.yaml",
        "obsidian_paths.yaml"
    ]

    for template_name in template_files:
        template_path = Path(project_root) / "batch" / "templates" / template_name
        target_path = path_dir / template_name

        if template_path.exists() and not target_path.exists():
            import shutil
            shutil.copy(template_path, target_path)
            print(f"  ✓ 复制 {template_name}")


def main():
    """主函数"""
    print("=" * 60)
    print("Hyper-Dyna-MCP 自动环境检测")
    print("=" * 60)
    print()

    # 获取项目根目录
    project_root = str(Path.cwd())
    print(f"项目根目录: {project_root}")
    print()

    # 检测 Python/Conda 环境
    conda_result = detect_conda_env()
    if conda_result:
        python_exe, conda_env = conda_result
    else:
        python_exe = sys.executable
        conda_env = "base"
        print(f"  使用当前 Python: {python_exe}")
    print()

    # 检测 HyperMesh
    hypermesh_result = detect_hypermesh()
    print()

    # 生成配置文件
    generate_config_files(
        project_root,
        python_exe,
        conda_env,
        hypermesh_result
    )

    print()
    print("=" * 60)
    print("环境检测完成！")
    print("=" * 60)
    print()
    print("下一步:")
    print("1. 检查生成的配置文件 (path/*.yaml)")
    print("2. 根据需要修改其他配置（LS-DYNA、LS-PrePost、Obsidian）")
    print("3. 运行验证: python batch/validate_all.py")
    print()


if __name__ == "__main__":
    main()

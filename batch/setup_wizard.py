#!/usr/bin/env python3
"""
Hyper-Dyna-MCP 配置向导
交互式引导用户配置所有必要的路径和环境
"""

import os
import sys
import shutil
from pathlib import Path
from typing import Optional


def get_input(prompt: str, default: str = "") -> str:
    """获取用户输入，支持默认值"""
    if default:
        user_input = input(f"{prompt} [{default}]: ").strip()
        return user_input if user_input else default
    else:
        while True:
            user_input = input(f"{prompt}: ").strip()
            if user_input:
                return user_input
            print("此字段不能为空，请重新输入。")


def check_path_exists(path: str) -> bool:
    """检查路径是否存在"""
    return Path(path).exists()


def find_python_in_conda(env_name: str) -> Optional[str]:
    """在 conda 环境中查找 Python 路径"""
    # 常见的 conda 安装路径
    conda_paths = [
        Path.home() / "anaconda3",
        Path.home() / "miniconda3",
        Path("E:/anaconda3/anzhuang"),
        Path("C:/ProgramData/anaconda3"),
        Path("C:/ProgramData/miniconda3"),
    ]

    for conda_path in conda_paths:
        if conda_path.exists():
            # Windows
            python_path = conda_path / "envs" / env_name / "python.exe"
            if python_path.exists():
                return str(python_path)
            # Linux/macOS
            python_path = conda_path / "envs" / env_name / "bin" / "python"
            if python_path.exists():
                return str(python_path)
    return None


def find_hypermesh_install() -> Optional[str]:
    """查找 HyperMesh 安装目录"""
    # 常见的安装路径
    possible_paths = [
        Path("C:/Program Files/Altair/2024/hw/bin/win64"),
        Path("C:/Program Files/Altair/2023/hw/bin/win64"),
        Path("C:/Program Files/Altair/2022/hw/bin/win64"),
        Path("C:/Program Files/Altair/2021/hw/bin/win64"),
    ]

    for path in possible_paths:
        if path.exists():
            return str(path)
    return None


def find_lsdyna_solver() -> Optional[str]:
    """查找 LS-DYNA 求解器路径"""
    # 常见的安装路径
    possible_paths = [
        Path("C:/Program Files/LSTC/ls-dyna_smp_d_R13.1_216-g83709a1_winx64_ifort190.exe"),
        Path("C:/Program Files/LSTC/ls-dyna_smp_d_R12.2_216-g83709a1_winx64_ifort190.exe"),
        Path("C:/Program Files/LSTC/ls-dyna_smp_d_R11.2_216-g83709a1_winx64_ifort190.exe"),
    ]

    for path in possible_paths:
        if path.exists():
            return str(path)
    return None


def find_lsprepost_exe() -> Optional[str]:
    """查找 LS-PrePost 可执行文件路径"""
    # 常见的安装路径
    possible_paths = [
        Path("C:/Program Files/LSTC/LS-PrePost4.9/lsprepost4.9_x64.exe"),
        Path("C:/Program Files/LSTC/LS-PrePost4.8/lsprepost4.8_x64.exe"),
    ]

    for path in possible_paths:
        if path.exists():
            return str(path)
    return None


def create_local_paths_config(project_root: str, conda_env: str, python_exe: str) -> dict:
    """创建 local_paths.yaml 配置"""
    return {
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


def create_hypermesh_config(install_dir: str) -> dict:
    """创建 hypermesh_paths.yaml 配置"""
    return {
        "hypermesh": {
            "install_dir": install_dir.replace("\\", "/"),
            "hmbatch_exe": f"{install_dir}/hmbatch.exe".replace("\\", "/"),
            "hmopengl_exe": f"{install_dir}/hmopengl.exe".replace("\\", "/"),
            "version": "2024",
            "gui_port": 47882,
            "default_timeout": 300
        }
    }


def create_lsdyna_config(solver_exe: str) -> dict:
    """创建 lsdyna_paths.yaml 配置"""
    return {
        "lsdyna": {
            "solver_exe": solver_exe.replace("\\", "/"),
            "version": "R13.1",
            "default_ncpus": 4,
            "default_memory": "200m",
            "default_timeout": 3600
        }
    }


def create_lsprepost_config(exe_path: str) -> dict:
    """创建 lsprepost_paths.yaml 配置"""
    return {
        "lsprepost": {
            "exe_path": exe_path.replace("\\", "/"),
            "version": "4.9",
            "default_timeout": 600,
            "output_dir": "F:/hyper-dyna-mcp/output"
        }
    }


def create_obsidian_config(root: str) -> dict:
    """创建 obsidian_paths.yaml 配置"""
    return {
        "obsidian": {
            "root": root.replace("\\", "/"),
            "workflow_log": f"{root}/Agent/dyna mcp/workflow_log.md".replace("\\", "/"),
            "execution_log": f"{root}/Agent/dyna mcp/execution_log.md".replace("\\", "/"),
            "validation_log": f"{root}/Agent/dyna mcp/validation_log.md".replace("\\", "/"),
            "handoff_dir": f"{root}/Agent/dyna mcp/handoff".replace("\\", "/"),
            "plan_dir": f"{root}/Agent/dyna mcp/plan".replace("\\", "/")
        }
    }


def write_yaml_file(filepath: Path, data: dict) -> None:
    """写入 YAML 文件"""
    import yaml

    with open(filepath, 'w', encoding='utf-8') as f:
        yaml.dump(data, f, default_flow_style=False, allow_unicode=True)


def write_env_file(filepath: Path, hm_dir: str, lsdyna_solver: str, lsprepost_exe: str, obsidian_root: str) -> None:
    """写入 .env 文件"""
    content = f"""# Dyna-mcp environment variables
# Generated by setup wizard

# HyperMesh
HM_INSTALL_DIR={hm_dir}

# LS-DYNA
LSDYNA_SOLVER={lsdyna_solver}

# LS-PrePost
LSPREPOST_EXE={lsprepost_exe}

# Obsidian vault
OBSIDIAN_ROOT={obsidian_root}
"""
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)


def main():
    """主函数"""
    print("=" * 60)
    print("Hyper-Dyna-MCP 配置向导")
    print("=" * 60)
    print()
    print("此向导将引导您配置 Hyper-Dyna-MCP 的所有必要路径。")
    print("请按照提示输入您的实际路径。")
    print()

    # 获取项目根目录
    project_root = str(Path.cwd())
    print(f"当前项目目录: {project_root}")
    print()

    # 1. Conda 环境配置
    print("1. Conda 环境配置")
    print("-" * 40)
    conda_env = get_input("Conda 环境名称", "hyper-dyna")

    # 尝试自动查找 Python 路径
    auto_python = find_python_in_conda(conda_env)
    if auto_python:
        print(f"   自动找到 Python 路径: {auto_python}")
        python_exe = get_input("Python 可执行文件路径", auto_python)
    else:
        python_exe = get_input("Python 可执行文件路径", "E:/anaconda3/anzhuang/envs/hyper-dyna/python.exe")

    print()

    # 2. HyperMesh 配置
    print("2. HyperMesh 配置")
    print("-" * 40)
    auto_hm = find_hypermesh_install()
    if auto_hm:
        print(f"   自动找到 HyperMesh 安装目录: {auto_hm}")
        hm_install_dir = get_input("HyperMesh 安装目录", auto_hm)
    else:
        hm_install_dir = get_input("HyperMesh 安装目录", "C:/Program Files/Altair/2024/hw/bin/win64")

    print()

    # 3. LS-DYNA 配置
    print("3. LS-DYNA 配置")
    print("-" * 40)
    auto_lsdyna = find_lsdyna_solver()
    if auto_lsdyna:
        print(f"   自动找到 LS-DYNA 求解器: {auto_lsdyna}")
        lsdyna_solver = get_input("LS-DYNA 求解器路径", auto_lsdyna)
    else:
        lsdyna_solver = get_input("LS-DYNA 求解器路径", "C:/Program Files/LSTC/ls-dyna_smp_d_R13.1_216-g83709a1_winx64_ifort190.exe")

    print()

    # 4. LS-PrePost 配置
    print("4. LS-PrePost 配置")
    print("-" * 40)
    auto_lsprepost = find_lsprepost_exe()
    if auto_lsprepost:
        print(f"   自动找到 LS-PrePost: {auto_lsprepost}")
        lsprepost_exe = get_input("LS-PrePost 可执行文件路径", auto_lsprepost)
    else:
        lsprepost_exe = get_input("LS-PrePost 可执行文件路径", "C:/Program Files/LSTC/LS-PrePost4.9/lsprepost4.9_x64.exe")

    print()

    # 5. Obsidian 配置
    print("5. Obsidian 配置")
    print("-" * 40)
    obsidian_root = get_input("Obsidian 知识库根目录", "D:/Zotero/ZoteroNote")

    print()

    # 确认配置
    print("=" * 60)
    print("配置摘要")
    print("=" * 60)
    print(f"项目根目录: {project_root}")
    print(f"Conda 环境: {conda_env}")
    print(f"Python 路径: {python_exe}")
    print(f"HyperMesh 目录: {hm_install_dir}")
    print(f"LS-DYNA 求解器: {lsdyna_solver}")
    print(f"LS-PrePost: {lsprepost_exe}")
    print(f"Obsidian 根目录: {obsidian_root}")
    print()

    confirm = input("确认配置并生成文件？(y/n) [y]: ").strip().lower()
    if confirm not in ('', 'y', 'yes'):
        print("已取消配置。")
        return

    print()
    print("正在生成配置文件...")

    # 创建 path 目录
    path_dir = Path(project_root) / "path"
    path_dir.mkdir(exist_ok=True)

    # 生成配置文件
    configs = [
        ("local_paths.yaml", create_local_paths_config(project_root, conda_env, python_exe)),
        ("hypermesh_paths.yaml", create_hypermesh_config(hm_install_dir)),
        ("lsdyna_paths.yaml", create_lsdyna_config(lsdyna_solver)),
        ("lsprepost_paths.yaml", create_lsprepost_config(lsprepost_exe)),
        ("obsidian_paths.yaml", create_obsidian_config(obsidian_root)),
    ]

    for filename, data in configs:
        filepath = path_dir / filename
        write_yaml_file(filepath, data)
        print(f"  ✓ Created {filepath}")

    # 生成 .env 文件
    env_path = Path(project_root) / ".env"
    write_env_file(env_path, hm_install_dir, lsdyna_solver, lsprepost_exe, obsidian_root)
    print(f"  ✓ Created {env_path}")

    print()
    print("=" * 60)
    print("配置完成！")
    print("=" * 60)
    print()
    print("下一步:")
    print("1. 检查生成的配置文件是否正确")
    print("2. 运行验证脚本: python batch/validators/check_paths.py")
    print("3. 启动 MCP 服务器: python -m program.server")
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

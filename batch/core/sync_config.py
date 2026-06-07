#!/usr/bin/env python3
"""
配置同步工具
将实际配置文件同步到标准格式
"""

import sys
import io
from pathlib import Path
from typing import Dict, Any

import yaml

# 设置标准输出编码为 UTF-8
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')


def load_yaml(filepath: Path) -> Dict[str, Any]:
    """加载 YAML 文件"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)
    except Exception as e:
        print(f"Error loading {filepath}: {e}")
        return {}


def save_yaml(filepath: Path, data: Dict[str, Any]) -> None:
    """保存 YAML 文件"""
    with open(filepath, 'w', encoding='utf-8') as f:
        yaml.dump(data, f, default_flow_style=False, allow_unicode=True)


def sync_hypermesh_config() -> None:
    """同步 HyperMesh 配置"""
    config_path = Path("path/hypermesh_paths.yaml")
    if not config_path.exists():
        print("⚠️  path/hypermesh_paths.yaml 不存在")
        return

    config = load_yaml(config_path)
    hm = config.get("hypermesh", {})

    # 提取实际值
    install_dir = hm.get("install_dir", "")
    hmbatch_exe = hm.get("hmbatch_exe", "")
    version = hm.get("version", "2021")

    # 构建标准格式
    standard_config = {
        "hypermesh": {
            "install_dir": install_dir,
            "hmbatch_exe": hmbatch_exe,
            "hmopengl_exe": f"{install_dir}/hmopengl.exe" if install_dir else "",
            "version": version,
            "gui_port": 47882,
            "default_timeout": 300
        }
    }

    # 保存标准格式
    save_yaml(config_path, standard_config)
    print(f"✓ 已同步 {config_path}")


def sync_lsdyna_config() -> None:
    """同步 LS-DYNA 配置"""
    config_path = Path("path/lsdyna_paths.yaml")
    if not config_path.exists():
        print("⚠️  path/lsdyna_paths.yaml 不存在")
        return

    config = load_yaml(config_path)
    lsdyna = config.get("lsdyna", {})

    # 提取实际值
    solver_exe = lsdyna.get("solver_exe", "")
    version = lsdyna.get("version", "R13.1")
    ncpus = lsdyna.get("ncpus_default", lsdyna.get("default_ncpus", 4))
    memory = lsdyna.get("memory_default", lsdyna.get("default_memory", "200m"))

    # 构建标准格式
    standard_config = {
        "lsdyna": {
            "solver_exe": solver_exe,
            "version": version,
            "default_ncpus": ncpus,
            "default_memory": memory,
            "default_timeout": 3600
        }
    }

    # 保存标准格式
    save_yaml(config_path, standard_config)
    print(f"✓ 已同步 {config_path}")


def sync_lsprepost_config() -> None:
    """同步 LS-PrePost 配置"""
    config_path = Path("path/lsprepost_paths.yaml")
    if not config_path.exists():
        print("⚠️  path/lsprepost_paths.yaml 不存在")
        return

    config = load_yaml(config_path)
    lsprepost = config.get("lsprepost", {})

    # 提取实际值
    exe_path = lsprepost.get("exe", lsprepost.get("exe_path", ""))
    version = lsprepost.get("version", "4.8")

    # 构建标准格式
    standard_config = {
        "lsprepost": {
            "exe_path": exe_path,
            "version": version,
            "default_timeout": 600,
            "output_dir": "F:/hyper-dyna-mcp/output"
        }
    }

    # 保存标准格式
    save_yaml(config_path, standard_config)
    print(f"✓ 已同步 {config_path}")


def sync_obsidian_config() -> None:
    """同步 Obsidian 配置"""
    config_path = Path("path/obsidian_paths.yaml")
    if not config_path.exists():
        print("⚠️  path/obsidian_paths.yaml 不存在")
        return

    config = load_yaml(config_path)
    obsidian = config.get("obsidian", {})

    # 提取实际值
    root = obsidian.get("root", "")
    workflow_log = obsidian.get("workflow_log", "")
    execution_log = obsidian.get("execution_log", "")
    validation_log = obsidian.get("validation_log", "")

    # 构建标准格式
    standard_config = {
        "obsidian": {
            "root": root,
            "workflow_log": workflow_log,
            "execution_log": execution_log,
            "validation_log": validation_log,
            "handoff_dir": f"{root}/handoff" if root else "",
            "plan_dir": f"{root}/plan" if root else ""
        }
    }

    # 保存标准格式
    save_yaml(config_path, standard_config)
    print(f"✓ 已同步 {config_path}")


def main():
    """主函数"""
    print("=" * 60)
    print("Hyper-Dyna-MCP 配置同步工具")
    print("=" * 60)
    print()

    # 同步所有配置
    sync_hypermesh_config()
    sync_lsdyna_config()
    sync_lsprepost_config()
    sync_obsidian_config()

    print()
    print("=" * 60)
    print("配置同步完成！")
    print("=" * 60)
    print()
    print("下一步:")
    print("1. 检查同步后的配置文件")
    print("2. 运行验证: python batch/validators/check_paths.py")
    print()


if __name__ == "__main__":
    main()

# Hyper-Dyna-MCP Batch 配置系统

本目录包含将 Hyper-Dyna-MCP 从个人版适配到大众版的配置文件和脚本。

## 目录结构

```
batch/
├── core/                      # 核心功能
│   ├── auto_detect.py         # 自动环境检测
│   ├── setup_wizard.py        # 交互式配置向导
│   └── sync_config.py         # 配置同步工具
├── generators/                # 配置生成器
│   ├── generate_mcp_config.py # Claude MCP 配置生成器
│   └── generate_codex_config.py # CODEX MCP 配置生成器
├── validators/                # 验证工具
│   ├── check_paths.py         # 路径验证
│   ├── check_env.py           # 环境验证
│   └── check_codex.py         # CODEX 配置验证
├── templates/                 # 配置模板
│   ├── local_paths.yaml       # 本地路径配置模板
│   ├── hypermesh_paths.yaml   # HyperMesh 配置模板
│   ├── lsdyna_paths.yaml      # LS-DYNA 配置模板
│   ├── lsprepost_paths.yaml   # LS-PrePost 配置模板
│   ├── obsidian_paths.yaml    # Obsidian 配置模板
│   ├── .env.example           # 环境变量模板
│   ├── claude_desktop_config.json
│   ├── claude_code_mcp.json
│   └── codex_config.toml
├── docs/                      # 文档
│   ├── README.md              # 详细配置指南
│   ├── QUICK_START.md         # 快速开始
│   ├── CHANGELOG.md           # 更新日志
│   └── CONFIG_COMPLETE.md     # 完成总结
├── scripts/                   # 安装脚本
│   ├── install.bat            # Windows 安装脚本
│   └── install.sh             # Linux/macOS 安装脚本
├── tests/                     # 测试文件
│   ├── test_batch.py          # 测试脚本
│   └── test_batch_simple.py   # 简单测试脚本
└── validate_all.py            # 完整配置验证
```

## 快速开始

### 方式一：自动安装（推荐）

```bash
# Windows
install.bat

# Linux/macOS
chmod +x install.sh
./install.sh
```

**自动检测功能：**
- ✅ Python/Conda 环境
- ✅ HyperMesh 安装路径
- ⚠️ LS-DYNA、LS-PrePost、Obsidian（需手动配置）

### 方式二：手动配置

1. 运行自动检测：
   ```bash
   python batch/core/auto_detect.py
   ```

2. 运行配置向导：
   ```bash
   python batch/core/setup_wizard.py
   ```

3. 验证配置：
   ```bash
   python batch/validate_all.py
   ```

4. 生成 MCP 配置：
   ```bash
   python batch/generators/generate_mcp_config.py      # Claude
   python batch/generators/generate_codex_config.py    # CODEX
   ```

## MCP 配置

### Claude Desktop / Claude Code

```bash
python batch/generators/generate_mcp_config.py
```

### CODEX (OpenAI Codex CLI)

```bash
python batch/generators/generate_codex_config.py --append
```

## 验证工具

```bash
# 完整验证
python batch/validate_all.py

# 路径验证
python batch/validators/check_paths.py

# 环境验证
python batch/validators/check_env.py

# CODEX 验证
python batch/validators/check_codex.py
```

## 文档

- 📖 [详细配置指南](./docs/README.md)
- 🚀 [快速开始](./docs/QUICK_START.md)
- 📋 [更新日志](./docs/CHANGELOG.md)
- ✅ [完成总结](./docs/CONFIG_COMPLETE.md)

## 支持

如有问题，请查看：
- [项目文档](../docs/)
- [GitHub Issues](https://github.com/your-username/hyper-dyna-mcp/issues)

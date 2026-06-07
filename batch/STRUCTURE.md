# Hyper-Dyna-MCP Batch 目录结构

## 📁 目录组织

```
batch/
├── core/                      # 核心功能模块
│   ├── __init__.py
│   ├── auto_detect.py         # 自动环境检测
│   ├── setup_wizard.py        # 交互式配置向导
│   └── sync_config.py         # 配置同步工具
│
├── generators/                # 配置生成器
│   ├── __init__.py
│   ├── generate_mcp_config.py # Claude MCP 配置生成器
│   └── generate_codex_config.py # CODEX MCP 配置生成器
│
├── validators/                # 验证工具
│   ├── __init__.py
│   ├── check_paths.py         # 路径验证
│   ├── check_env.py           # 环境验证
│   └── check_codex.py         # CODEX 配置验证
│
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
│
├── docs/                      # 文档
│   ├── README.md              # 详细配置指南
│   ├── QUICK_START.md         # 快速开始
│   ├── CHANGELOG.md           # 更新日志
│   └── CONFIG_COMPLETE.md     # 完成总结
│
├── scripts/                   # 安装脚本
│   ├── install.bat            # Windows 安装脚本
│   └── install.sh             # Linux/macOS 安装脚本
│
├── tests/                     # 测试文件
│   ├── __init__.py
│   ├── test_batch.py          # 测试脚本
│   └── test_batch_simple.py   # 简单测试脚本
│
├── __init__.py
├── README.md                  # 本文件
├── STRUCTURE.md               # 目录结构说明
└── validate_all.py            # 完整配置验证
```

## 🎯 模块职责

### core/ - 核心功能
- **auto_detect.py**: 自动检测 Python/Conda 环境和 HyperMesh 安装路径
- **setup_wizard.py**: 交互式配置向导，引导用户配置所有路径
- **sync_config.py**: 将实际配置同步到标准格式

### generators/ - 配置生成器
- **generate_mcp_config.py**: 生成 Claude Desktop 和 Claude Code 的 MCP 配置
- **generate_codex_config.py**: 生成 CODEX (OpenAI Codex CLI) 的 MCP 配置

### validators/ - 验证工具
- **check_paths.py**: 验证所有配置的路径是否存在
- **check_env.py**: 验证 Python 环境和依赖包
- **check_codex.py**: 验证 CODEX 安装和配置

### templates/ - 配置模板
- 包含所有配置文件的模板
- 使用占位符或默认值
- 安装时自动复制到 `path/` 目录

### docs/ - 文档
- **README.md**: 详细配置指南
- **QUICK_START.md**: 30 秒快速开始
- **CHANGELOG.md**: 更新日志
- **CONFIG_COMPLETE.md**: 完成总结

### scripts/ - 安装脚本
- **install.bat**: Windows 快速安装脚本
- **install.sh**: Linux/macOS 快速安装脚本

### tests/ - 测试文件
- **test_batch.py**: Batch 系统测试脚本
- **test_batch_simple.py**: 简单测试脚本

## 🚀 使用流程

### 1. 自动安装（推荐）
```bash
# Windows
install.bat

# Linux/macOS
./install.sh
```

### 2. 手动配置
```bash
# 自动检测环境
python batch/core/auto_detect.py

# 运行配置向导
python batch/core/setup_wizard.py

# 验证配置
python batch/validate_all.py

# 生成 MCP 配置
python batch/generators/generate_mcp_config.py      # Claude
python batch/generators/generate_codex_config.py    # CODEX
```

### 3. 验证配置
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

## 📝 设计原则

1. **模块化**: 每个模块有明确的职责
2. **可扩展**: 易于添加新的配置生成器或验证工具
3. **向后兼容**: 保持与现有配置的兼容性
4. **用户友好**: 提供自动检测和交互式配置
5. **文档完善**: 每个模块都有详细的文档

## 🔗 相关链接

- [详细配置指南](./docs/README.md)
- [快速开始](./docs/QUICK_START.md)
- [更新日志](./docs/CHANGELOG.md)
- [完成总结](./docs/CONFIG_COMPLETE.md)

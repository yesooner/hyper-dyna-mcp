# Batch 配置系统更新日志

## v1.0.0 (2026-06-07)

### 新增功能

- ✅ **批处理安装脚本**
  - `install.bat` - Windows 安装脚本
  - `install.sh` - Linux/macOS 安装脚本
  - 自动复制配置模板到 `path/` 目录

- ✅ **交互式配置向导**
  - `batch/setup_wizard.py` - 引导用户配置所有路径
  - 自动检测 HyperMesh、LS-DYNA、LS-PrePost 安装路径
  - 自动生成 `.env` 文件

- ✅ **配置模板**
  - `batch/templates/local_paths.yaml` - 本地路径配置模板
  - `batch/templates/hypermesh_paths.yaml` - HyperMesh 配置模板
  - `batch/templates/lsdyna_paths.yaml` - LS-DYNA 配置模板
  - `batch/templates/lsprepost_paths.yaml` - LS-PrePost 配置模板
  - `batch/templates/obsidian_paths.yaml` - Obsidian 配置模板
  - `batch/templates/.env.example` - 环境变量模板

- ✅ **MCP 配置生成器**
  - `batch/generate_mcp_config.py` - 生成 Claude Desktop 和 Claude Code 配置
  - 自动检测操作系统并保存到正确位置
  - 支持备份旧配置

- ✅ **验证工具**
  - `batch/validators/check_paths.py` - 验证所有配置路径
  - `batch/validators/check_env.py` - 验证 Python 环境和依赖
  - 支持 UTF-8 编码输出

- ✅ **卸载脚本**
  - `uninstall.bat` - Windows 卸载脚本
  - `uninstall.sh` - Linux/macOS 卸载脚本
  - 安全清理生成的配置文件

- ✅ **文档**
  - `batch/README.md` - 详细配置指南
  - `batch/QUICK_START.md` - 30 秒快速开始
  - `batch/CHANGELOG.md` - 更新日志

### 改进

- 📝 更新项目 README.md，添加 batch 配置说明
- 📝 更新版本历史，添加 batch 配置系统
- 🔧 更新 `.gitignore`，排除生成的配置文件

### 文件结构

```
batch/
├── __init__.py
├── README.md
├── QUICK_START.md
├── CHANGELOG.md
├── install.bat
├── install.sh
├── setup_wizard.py
├── generate_mcp_config.py
├── templates/
│   ├── local_paths.yaml
│   ├── hypermesh_paths.yaml
│   ├── lsdyna_paths.yaml
│   ├── lsprepost_paths.yaml
│   ├── obsidian_paths.yaml
│   ├── .env.example
│   ├── claude_desktop_config.json
│   └── claude_code_mcp.json
└── validators/
    ├── __init__.py
    ├── check_paths.py
    └── check_env.py
```

### 使用方法

#### 快速安装

```bash
# Windows
install.bat

# Linux/macOS
chmod +x install.sh
./install.sh
```

#### 手动配置

1. 复制 `batch/templates/` 目录下的模板文件到 `path/` 目录
2. 根据实际环境修改配置文件
3. 运行验证脚本检查配置

#### 生成 MCP 配置

```bash
python batch/generate_mcp_config.py
```

### 兼容性

- ✅ Windows 10/11
- ✅ macOS 10.15+
- ✅ Linux (Ubuntu 20.04+, CentOS 7+)
- ✅ Python 3.11+
- ✅ Conda 4.10+

### 已知问题

- 暂无

### 下一步计划

- [ ] 添加 GUI 配置界面
- [ ] 支持 Docker 容器化部署
- [ ] 添加自动更新功能
- [ ] 支持多语言配置

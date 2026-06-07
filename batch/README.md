# Hyper-Dyna-MCP Batch 配置

本目录包含将 Hyper-Dyna-MCP 从个人版适配到大众版的配置文件和脚本。

## 目录结构

```
batch/
├── README.md                    # 本文件
├── install.bat                  # Windows 安装脚本
├── install.sh                   # Linux/macOS 安装脚本
├── setup_wizard.py              # 交互式配置向导
├── templates/
│   ├── local_paths.yaml         # 本地路径配置模板
│   ├── hypermesh_paths.yaml     # HyperMesh 路径配置模板
│   ├── lsdyna_paths.yaml        # LS-DYNA 路径配置模板
│   ├── lsprepost_paths.yaml     # LS-PrePost 路径配置模板
│   ├── obsidian_paths.yaml      # Obsidian 路径配置模板
│   ├── .env.example             # 环境变量模板
│   ├── claude_desktop_config.json  # Claude Desktop MCP 配置模板
│   └── claude_code_mcp.json     # Claude Code MCP 配置模板
└── validators/
    ├── check_paths.py           # 路径验证工具
    └── check_env.py             # 环境验证工具
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

### 方式二：手动配置

1. 复制 `templates/` 目录下的所有模板文件到项目根目录的 `path/` 目录
2. 根据你的环境修改每个 YAML 文件中的路径
3. 复制 `.env.example` 到项目根目录并重命名为 `.env`
4. 根据你的环境修改 `.env` 文件

### 方式三：使用配置向导

```bash
python batch/setup_wizard.py
```

## 配置说明

### 路径配置

所有路径配置都在 `path/` 目录下的 YAML 文件中：

- `local_paths.yaml` — 项目根目录、conda 环境名、Python 路径
- `hypermesh_paths.yaml` — HyperMesh 安装目录、hmbatch.exe 路径
- `lsdyna_paths.yaml` — LS-DYNA 求解器路径、许可证文件
- `lsprepost_paths.yaml` — LS-PrePost 可执行文件路径
- `obsidian_paths.yaml` — Obsidian 知识库路径、日志文件路径

### 环境变量

`.env` 文件包含敏感或可选的配置：

- `HM_INSTALL_DIR` — HyperMesh 安装目录
- `LSDYNA_SOLVER` — LS-DYNA 求解器路径
- `LSPREPOST_EXE` — LS-PrePost 可执行文件路径
- `OBSIDIAN_ROOT` — Obsidian 知识库根目录

### Claude Desktop 配置

将 `templates/claude_desktop_config.json` 复制到 Claude Desktop 配置目录：

- **Windows**: `%APPDATA%\Claude\claude_desktop_config.json`
- **macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
- **Linux**: `~/.config/Claude/claude_desktop_config.json`

### Claude Code 配置

将 `templates/claude_code_mcp.json` 的内容添加到 Claude Code 的 MCP 配置中。

## 验证配置

运行验证脚本检查配置是否正确：

```bash
# 验证路径
python batch/validators/check_paths.py

# 验证环境
python batch/validators/check_env.py
```

## 常见问题

### Q: 如何找到我的 HyperMesh 安装路径？

**Windows 默认路径**: `C:\Program Files\Altair\2024\hw\bin\win64`

可以通过以下方式查找：
1. 右键点击 HyperMesh 快捷方式 → 属性 → 目标
2. 在文件资源管理器中搜索 `hmopengl.exe`

### Q: 如何找到我的 LS-DYNA 求解器路径？

**Windows 默认路径**: `C:\Program Files\LSTC\ls-dyna_smp_d_R13.1_216-g83709a1_winx64_ifort190.exe`

可以通过以下方式查找：
1. 检查 LS-DYNA 安装目录
2. 在开始菜单中搜索 LS-DYNA

### Q: 如何配置 Obsidian 知识库？

1. 打开 Obsidian
2. 点击左下角的设置图标
3. 在 "文件与链接" 中查看知识库路径
4. 将路径填入 `obsidian_paths.yaml`

### Q: 如何测试 MCP 服务器是否正常工作？

```bash
# 启动 MCP 服务器
python -m program.server

# 在另一个终端中运行测试
python -m pytest tests/
```

## 支持

如有问题，请查看：
- [项目文档](../docs/)
- [GitHub Issues](https://github.com/your-username/hyper-dyna-mcp/issues)

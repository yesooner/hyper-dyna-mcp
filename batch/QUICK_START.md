# Hyper-Dyna-MCP 快速开始

## 30 秒快速安装

```bash
# 1. 克隆仓库
git clone https://github.com/your-username/hyper-dyna-mcp.git
cd hyper-dyna-mcp

# 2. 运行安装脚本（自动检测环境）
./install.sh  # Linux/macOS
# 或
install.bat   # Windows

# 3. 检查自动生成的配置文件 (path/*.yaml)
#    - Python/Conda 环境会自动检测
#    - HyperMesh 路径会自动检测
#    - 其他软件路径需要手动配置

# 4. 启动 MCP 服务器
python -m program.server
```

## 配置文件位置

| 文件 | 用途 |
|------|------|
| `path/local_paths.yaml` | 项目根目录、conda 环境 |
| `path/hypermesh_paths.yaml` | HyperMesh 安装路径 |
| `path/lsdyna_paths.yaml` | LS-DYNA 求解器路径 |
| `path/lsprepost_paths.yaml` | LS-PrePost 路径 |
| `path/obsidian_paths.yaml` | Obsidian 知识库路径 |
| `.env` | 环境变量 |

## 常用命令

```bash
# 验证配置
python batch/validators/check_paths.py
python batch/validators/check_env.py

# 生成 MCP 配置
python batch/generate_mcp_config.py      # Claude Desktop/Code
python batch/generate_codex_config.py    # CODEX (OpenAI Codex CLI)

# 运行测试
python -m pytest

# 启动 MCP 服务器
python -m program.server
```

## MCP 配置

### Claude Desktop / Claude Code

```bash
python batch/generate_mcp_config.py
```

配置文件自动保存到：
- Claude Desktop: `%APPDATA%\Claude\claude_desktop_config.json`
- Claude Code: `claude_code_mcp.json`

### CODEX (OpenAI Codex CLI)

```bash
python batch/generate_codex_config.py
```

配置文件追加到：`~/.codex/config.toml`

**验证 CODEX 配置：**

```bash
codex mcp list
codex mcp get hyper-dyna-mcp
```

## 常见问题

### Q: 如何找到我的软件安装路径？

**HyperMesh:**
- Windows: `C:\Program Files\Altair\2024\hw\bin\win64`
- 查找方法: 右键 HyperMesh 快捷方式 → 属性 → 目标

**LS-DYNA:**
- Windows: `C:\Program Files\LSTC\ls-dyna_smp_d_R13.1_216-g83709a1_winx64_ifort190.exe`
- 查找方法: 开始菜单搜索 LS-DYNA

**LS-PrePost:**
- Windows: `C:\Program Files\LSTC\LS-PrePost4.9\lsprepost4.9_x64.exe`
- 查找方法: 开始菜单搜索 LS-PrePost

### Q: 如何配置 Claude Desktop？

1. 运行 `python batch/generate_mcp_config.py`
2. 配置文件会自动保存到正确位置
3. 重启 Claude Desktop

### Q: 如何配置 Claude Code？

1. 运行 `python batch/generate_mcp_config.py`
2. 将生成的 `claude_code_mcp.json` 内容添加到 `~/.claude/settings.json`

### Q: 如何配置 CODEX？

1. 运行 `python batch/generate_codex_config.py`
2. 配置会自动追加到 `~/.codex/config.toml`
3. 重启 CODEX 或运行 `codex mcp list` 验证

### Q: Claude Desktop、Claude Code 和 CODEX 有什么区别？

| 特性 | Claude Desktop | Claude Code | CODEX |
|------|----------------|-------------|-------|
| **配置格式** | JSON | JSON | TOML |
| **配置文件** | `%APPDATA%\Claude\claude_desktop_config.json` | `~/.claude.json` | `~/.codex/config.toml` |
| **传输方式** | stdio | stdio | stdio, streamable_http |
| **分层配置** | 否 | 否 | 是 |
| **工具过滤** | 否 | 否 | 是 |
| **超时配置** | 否 | 否 | 是 |

### Q: 如何更新配置？

1. 编辑 `path/` 目录下的 YAML 文件
2. 运行 `python batch/validators/check_paths.py` 验证
3. 重启 MCP 服务器

## 获取帮助

- 📖 完整文档: [batch/README.md](./README.md)
- 🐛 报告问题: GitHub Issues
- 💬 讨论: GitHub Discussions

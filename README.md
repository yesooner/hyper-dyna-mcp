# 🏗️ Hyper-Dyna-MCP

<p align="center">
  <a href="./README.md"><img alt="中文" src="https://img.shields.io/badge/语言-中文-blue"></a>
  <a href="./README.en.md"><img alt="English" src="https://img.shields.io/badge/Language-English-lightgrey"></a>
  <a href="./LICENSE"><img alt="License" src="https://img.shields.io/badge/License-MIT-green"></a>
  <a href="https://github.com/hyper-dyna-mcp/releases"><img alt="Release" src="https://img.shields.io/badge/Release-v0.1.0-orange"></a>
</p>

**Hyper-Dyna-MCP** 是一个基于 **MCP (Model Context Protocol)** 的 CAE 工作流自动化服务器，连接自然语言规划与 **HyperMesh** 前处理、**LS-DYNA** 关键字文件处理、**LS-PrePost** 后处理以及 **Obsidian** 日志记录。

> 🎯 **核心目标**：让工程师通过自然语言描述，自动完成复杂的 CAE 前处理工作流。

![Hyper-Dyna-MCP 架构](./docs/images/architecture.png)

## ✨ 功能特点

- 📚 **1935 个 LS-DYNA 关键字模板** — MAT、SECTION、CONTACT、BOUNDARY、LOAD、CONTROL、DATABASE、SET 等
- 🔗 **HyperMesh GUI 集成** — Socket 通信（端口 47882）+ IPC 文件队列双通道
- 📝 **K 文件解析/生成** — 解析、验证、生成 LS-DYNA .k 关键字文件
- 🔧 **模型操作** — 读写材料、属性、组件、截面等
- 🛡️ **安全策略** — Tcl 脚本策略强制执行、MCP_SCRIPT 标记、逐命令执行
- 🔄 **工作流编排** — LS-DYNA、HyperMesh 和混合流水线
- 📊 **Obsidian 日志** — 自动记录执行日志到 Obsidian 知识库

## 🧩 接口类型

### MCP 协议接口

本项目实现标准 **MCP (Model Context Protocol)** 协议，支持：

- **工具调用 (Tools)** — 19 个专业 CAE 工具
- **提示词 (Prompts)** — 工作流规划、执行、验证
- **资源 (Resources)** — 路径配置、环境信息

### 通信接口

```mermaid
graph LR
    A[Agent/Claude Code] -->|MCP Protocol| B[MCP Server]
    B -->|Socket:47882| C[HyperMesh GUI]
    B -->|IPC File Queue| D[HyperMesh Batch]
    B -->|Direct API| E[LS-DYNA/LS-PrePost]
    B -->|REST API| F[Obsidian Vault]
```

## 📦 安装方法

### 环境要求

- **Python**: 3.11+ (推荐 3.13)
- **HyperMesh**: 2021+
- **LS-DYNA**: R13+
- **LS-PrePost**: 4.8+
- **Conda**: 用于环境管理

### 安装步骤

#### 1️⃣ 克隆仓库

```bash
git clone https://github.com/your-username/hyper-dyna-mcp.git
cd hyper-dyna-mcp
```

#### 2️⃣ 创建 Conda 环境

```bash
conda create -n hyper-dyna python=3.13
conda activate hyper-dyna
```

#### 3️⃣ 安装依赖

```bash
# 安装项目依赖
pip install -e .

# 或者安装开发依赖
pip install -e ".[dev]"
```

#### 4️⃣ 配置路径

编辑 `path/local_paths.yaml`：

```yaml
project:
  root: "F:/hyper-dyna-mcp"
  conda_env: "hyper-dyna"
  python_exe: "E:/anaconda3/anzhuang/envs/hyper-dyna/python.exe"
```

#### 5️⃣ 验证安装

```bash
# 运行测试
pytest

# 检查环境
python -c "from program.server import main; print('✅ MCP Server ready')"
```

## 🚀 使用方法

### 方式一：直接启动 MCP 服务器

```bash
# 启动 MCP 服务器
python -m program.server
```

### 方式二：通过 HyperMesh GUI

1. **双击启动** `start_mcp.bat`
2. **打开 HyperMesh GUI**
3. **在 HyperMesh Tcl 控制台中执行**：
   ```tcl
   source F:/hyper-dyna-mcp/hmcustom.tcl
   mcp_start
   ```
4. **或者**：HyperMesh → MCP 标签页 → 点击 "Start MCP" 按钮

### 方式三：Claude Code 集成

在 Claude Code 中直接使用 MCP 工具：

```
用户: 帮我创建一个混凝土柱的 LS-DYNA 模型
Claude: 我将使用 Hyper-Dyna-MCP 工具为您创建模型...
```

## 🔧 MCP 工具列表

### 核心工具 (19 个)

| 工具名称 | 功能描述 | 接口类型 |
|----------|----------|----------|
| `hm_set_keyword` | 设置 LS-DYNA 关键字 | Socket/IPC |
| `hm_keyword_help` | 获取关键字帮助 | 本地查询 |
| `hm_check_model` | 查询当前模型状态 | Socket/IPC |
| `hm_convert_model` | 转换模型为 LS-DYNA 格式 | Socket/IPC |
| `hm_read_materials` | 读取所有材料 | Socket/IPC |
| `hm_read_components` | 读取所有组件 | Socket/IPC |
| `execute_tcl_gui` | 在 HyperMesh GUI 中执行 Tcl | Socket |
| `execute_hmbatch` | 通过 hmbatch.exe 执行 | IPC |
| `generate_tcl_script` | 生成 Tcl 脚本 | 本地生成 |
| `check_hypermesh_connection` | 检查 hmbatch.exe 连接 | 本地检查 |
| `parse_k_file` | 解析 .k 文件 | 本地解析 |
| `write_k_file` | 生成 .k 文件 | 本地生成 |
| `generate_lsdyna_command` | 生成求解器命令 | 本地生成 |
| `parse_solver_log` | 解析求解器日志 | 本地解析 |
| `execute_lsprepost` | 执行 LS-PrePost cfile | 直接调用 |
| `generate_cfile` | 生成 cfile 脚本 | 本地生成 |
| `generate_post_processing_cfile` | 生成后处理 cfile | 本地生成 |
| `check_environment` | 检查 Python/conda/包 | 本地检查 |
| `load_path_config` | 加载 YAML 配置 | 本地加载 |
| `validate_path` | 检查路径是否存在 | 本地检查 |
| `write_obsidian_log` | 写入 Obsidian 日志 | REST API |

## 🏗️ 项目结构

```
hyper-dyna-mcp/
├── 📁 program/                    # MCP 服务器核心
│   ├── 🐍 server.py              # MCP 入口点（19 个工具）
│   ├── 🔄 transport_manager.py   # Socket/IPC 双通道管理
│   ├── 📨 plugin_loop.py         # IPC 命令分发器
│   └── 🛠️ tools/                 # 24 个工具模块
│       ├── hm_gui.py             # HyperMesh GUI 通信
│       ├── hm_runner.py          # HyperMesh 批处理
│       ├── k_parser.py           # K 文件解析器
│       ├── k_writer.py           # K 文件生成器
│       └── ...                   # 其他工具
├── 📁 templates/keyword/         # 1935 个 Tcl 模板
│   ├── mat/                      # 材料模板
│   ├── section/                  # 截面模板
│   ├── contact/                  # 接触模板
│   └── ...                       # 其他关键字
├── 📁 path/                      # YAML 配置文件
├── 📁 tests/                     # 132 个测试
├── 📁 docs/                      # 文档
├── 📁 output/                    # 生成的模型文件
├── 📄 hmcustom.tcl               # HyperMesh 自动加载脚本
└── 📄 pyproject.toml             # 项目配置
```

## 📊 技术架构

```mermaid
graph TB
    subgraph "用户层"
        A[Claude Code / Agent]
        B[HyperMesh GUI]
    end
    
    subgraph "MCP 服务器层"
        C[Server Entry Point]
        D[Transport Manager]
        E[Tool Registry]
        F[Template Engine]
    end
    
    subgraph "通信层"
        G[Socket:47882]
        H[IPC File Queue]
        I[REST API]
    end
    
    subgraph "执行层"
        J[HyperMesh GUI]
        K[HyperMesh Batch]
        L[LS-DYNA Solver]
        M[LS-PrePost]
    end
    
    A -->|MCP Protocol| C
    C --> D
    D --> G
    D --> H
    C --> E
    E --> F
    F --> G
    F --> H
    G --> J
    H --> K
    E --> L
    E --> M
    C --> I
    I --> N[Obsidian Vault]
```

## 🔌 连接模式

### 模式 1：Socket 直连（推荐）

- **端口**: 47882
- **延迟**: < 10ms
- **适用**: HyperMesh GUI 已打开

### 模式 2：IPC 文件队列（备用）

- **目录**: `ipc/commands/`, `ipc/results/`
- **延迟**: 100-500ms
- **适用**: Socket 连接失败时自动切换

### 模式 3：批处理模式

- **执行**: hmbatch.exe
- **延迟**: 1-5s
- **适用**: 无 GUI 环境

## 📈 性能指标

- **关键字模板**: 1935 个
- **工具数量**: 19 个
- **测试覆盖**: 132 个测试用例
- **连接延迟**: Socket < 10ms, IPC < 500ms
- **模型处理**: 支持 100MB+ .k 文件

## 🧪 测试

```bash
# 运行所有测试
pytest

# 运行特定测试
pytest tests/test_minimum_model.py

# 生成覆盖率报告
pytest --cov=program --cov-report=html
```

## 📚 文档

- 📖 [API 文档](./docs/api.md)
- 🏗️ [架构设计](./docs/architecture.md)
- 🔧 [工具参考](./docs/tools.md)
- 📝 [示例工作流](./docs/examples.md)

## 🤝 贡献指南

欢迎贡献！请遵循以下步骤：

1. Fork 本仓库
2. 创建特性分支 (`git checkout -b feature/amazing-feature`)
3. 提交更改 (`git commit -m 'Add amazing feature'`)
4. 推送到分支 (`git push origin feature/amazing-feature`)
5. 创建 Pull Request

## 📋 版本历史

### v0.1.0 (当前版本)

- ✅ MCP 服务器核心架构
- ✅ 19 个 CAE 工具实现
- ✅ 1935 个 LS-DYNA 关键字模板
- ✅ HyperMesh GUI 集成
- ✅ Socket/IPC 双通道通信
- ✅ K 文件解析/生成
- ✅ Obsidian 日志集成
- ✅ 132 个测试用例

## 📄 许可证

本项目采用 [MIT License](./LICENSE)。

## 🙏 致谢

- [LS-DYNA](https://www.lstc.com/) — 有限元求解器
- [HyperMesh](https://www.altair.com/hypermesh/) — 前处理软件
- [MCP Protocol](https://modelcontextprotocol.io/) — 模型上下文协议
- [Obsidian](https://obsidian.md/) — 知识管理工具

## 📞 联系方式

- **Issues**: [GitHub Issues](https://github.com/your-username/hyper-dyna-mcp/issues)
- **Discussions**: [GitHub Discussions](https://github.com/your-username/hyper-dyna-mcp/discussions)

---

<p align="center">
  Made with ❤️ for CAE Engineers
</p>

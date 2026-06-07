# 🏗️ Hyper-Dyna-MCP v0.1.0

## 🎉 首次发布

**Hyper-Dyna-MCP** 是一个基于 MCP (Model Context Protocol) 的 CAE 工作流自动化服务器，连接自然语言规划与 HyperMesh 前处理、LS-DYNA 关键字文件处理、LS-PrePost 后处理。

## ✨ 主要功能

### 📚 1935 个 LS-DYNA 关键字模板
- 完整的 LS-DYNA 关键字库
- 支持 MAT、SECTION、CONTACT、BOUNDARY、LOAD、CONTROL、DATABASE、SET 等
- 基于 Tcl 的模板引擎

### 🔗 HyperMesh GUI 集成
- Socket 直连通信（端口 47882）
- IPC 文件队列双通道
- 自动故障转移和恢复

### 📝 K 文件处理
- 解析 LS-DYNA .k 关键字文件
- 验证和生成 K 文件
- 支持 100MB+ 大文件

### 🔧 模型操作
- 读写材料、属性、组件、截面
- 模型状态查询
- 格式转换

### 🛡️ 安全策略
- Tcl 脚本策略强制执行
- MCP_SCRIPT 标记
- 逐命令执行和验证

### 🔄 工作流编排
- LS-DYNA、HyperMesh 和混合流水线
- 自然语言到工作流转换
- 执行状态跟踪

## 🔧 MCP 工具 (18 个)

| 工具 | 描述 |
|------|------|
| `hm_set_keyword` | 设置 LS-DYNA 关键字 |
| `hm_keyword_help` | 获取关键字帮助 |
| `hm_check_model` | 查询当前模型状态 |
| `hm_convert_model` | 转换模型为 LS-DYNA 格式 |
| `hm_read_materials` | 读取所有材料 |
| `hm_read_components` | 读取所有组件 |
| `execute_tcl_gui` | 在 HyperMesh GUI 中执行 Tcl |
| `execute_hmbatch` | 通过 hmbatch.exe 执行 |
| `generate_tcl_script` | 生成 Tcl 脚本 |
| `check_hypermesh_connection` | 检查 hmbatch.exe 连接 |
| `parse_k_file` | 解析 .k 文件 |
| `write_k_file` | 生成 .k 文件 |
| `generate_lsdyna_command` | 生成求解器命令 |
| `parse_solver_log` | 解析求解器日志 |
| `execute_lsprepost` | 执行 LS-PrePost cfile |
| `generate_cfile` | 生成 cfile 脚本 |
| `generate_post_processing_cfile` | 生成后处理 cfile |
| `check_environment` | 检查 Python/conda/包 |
| `load_path_config` | 加载 YAML 配置 |
| `validate_path` | 检查路径是否存在 |

## 📦 安装方法

### 环境要求
- Python 3.11+ (推荐 3.13)
- HyperMesh 2021+
- LS-DYNA R13+
- LS-PrePost 4.8+
- Conda 环境管理

### 快速安装
```bash
# 克隆仓库
git clone https://github.com/your-username/hyper-dyna-mcp.git
cd hyper-dyna-mcp

# 创建环境
conda create -n hyper-dyna python=3.13
conda activate hyper-dyna

# 安装依赖
pip install -e .

# 验证安装
pytest
```

## 🚀 使用方法

### 方式一：直接启动
```bash
python -m program.server
```

### 方式二：HyperMesh GUI 集成
1. 双击 `start_mcp.bat`
2. 打开 HyperMesh GUI
3. 在 Tcl 控制台执行：
   ```tcl
   source hmcustom.tcl
   mcp_start
   ```

### 方式三：Claude Code 集成
直接在 Claude Code 中使用 MCP 工具。

## 📊 性能指标

- **关键字模板**: 1935 个
- **工具数量**: 18 个
- **测试覆盖**: 132 个测试用例
- **连接延迟**: Socket < 10ms, IPC < 500ms
- **模型处理**: 支持 100MB+ .k 文件

## 📚 文档

- 📖 API 文档
- 🏗️ 架构设计
- 🔧 工具参考
- 📝 示例工作流

## 🤝 贡献

欢迎贡献！请遵循以下步骤：
1. Fork 本仓库
2. 创建特性分支
3. 提交更改
4. 推送到分支
5. 创建 Pull Request

## 📄 许可证

本项目采用 [MIT License](./LICENSE)。

## 🙏 致谢

- LS-DYNA — 有限元求解器
- HyperMesh — 前处理软件
- MCP Protocol — 模型上下文协议

---

**完整更新日志**: https://github.com/your-username/hyper-dyna-mcp/commits/v0.1.0

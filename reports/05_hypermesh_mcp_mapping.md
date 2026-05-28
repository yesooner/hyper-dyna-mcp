# 05 — HyperMesh MCP 项目匹配分析

Generated: 2026-05-27
Source: `lib/hypermesh-mcp` (forked from times1234/hypermesh-mcp)

## 1. 架构对比

### hypermesh-mcp 架构（已验证可运行）
```
LLM Agent
  → FastMCP server (Python)
    → generate_*_tcl() 生成 Tcl 脚本
    → execute_tcl() / execute_tcl_gui()
      → hmbatch.exe 批处理
      → GUI listener (socket 127.0.0.1:47881)
```

### Dyna-mcp 目标架构
```
LLM Agent
  → FastMCP server (Python)
    → k_parser.py 解析 .k
    → k_writer.py 生成 .k
    → lsdyna_runner.py 调用求解器
    → hm_tcl_generator.py 生成 Tcl（待做）
    → hm_runner.py 调用 hmbatch（待做）
    → lsprepost_runner.py 调用 LS-PrePost（待做）
```

**匹配结论：** 架构一致，都是 Python 编排 + 原生语言执行。

## 2. MCP Tool 映射

### hypermesh-mcp 工具列表 → Dyna-mcp 对应

| hypermesh-mcp Tool | 功能 | Dyna-mcp 现状 | 需要做什么 |
|---------------------|------|---------------|-----------|
| `locate_hypermesh` | 查找 hmbatch.exe | `path/hypermesh_paths.yaml` | 已有配置，需增加自动检测 |
| `check_hypermesh_connection` | 验证 hmbatch 可用 | `env_check.py` | 需增加 HM 连接检查 |
| `execute_tcl` | hmbatch 执行 Tcl | `hm_runner.py` (占位) | **需实现：核心执行器** |
| `execute_tcl_gui` | GUI listener 执行 | 无 | Phase 2 扩展 |
| `execute_tcl_gui_async` | 异步 GUI 执行 | 无 | Phase 2 扩展 |
| `generate_geometry_probe_tcl` | 生成探针 Tcl | 无 | 可复用 |
| `run_geometry_probe_gui` | GUI 执行探针 | 无 | 可复用 |
| `classify_all_solids_from_probe` | 几何分类 | 无 | 可复用 |
| `generate_phase2_finalize_tcl` | 重命名/着色 | 无 | 可复用 |
| `generate_plain_tetra_tcl` | 生成 tetra Tcl | 无 | 可复用 |
| `generate_guarded_drag_hex_tcl` | 生成 drag hex Tcl | 无 | 可复用 |
| `generate_cutsection_spin_hex_tcl` | 生成 spin hex Tcl | 无 | 可复用 |
| `generate_batched_*_tcl` | 批处理版本 | 无 | 可复用 |
| `get_hypermesh_meshing_strategy` | 网格策略文档 | 无 | 可复用 |
| `get_meshing_rules` | 网格规则 | 无 | 可复用 |

### LS-DYNA 相关（hyper-mcp 不覆盖，需自建）

| Dyna-mcp Tool | 功能 | 现状 |
|---------------|------|------|
| `k_parser.py` | 解析 .k 关键字文件 | **已实现最小版本** |
| `k_writer.py` | 生成 .k 关键字文件 | **已实现最小版本** |
| `lsdyna_runner.py` | 生成 LS-DYNA 命令（dry_run） | **已实现最小版本** |
| `lsdyna_log_parser.py` | 解析 LS-DYNA 输出日志 | 占位 |
| `lsprepost_runner.py` | LS-PrePost cfile 执行 | 占位 |

## 3. 可复用关键技术模式

### 3.1 Tcl 执行模式（从 hypermesh-mcp）

**批处理模式：**
```python
# Python 生成 Tcl 脚本字符串
tcl_script = generate_tcl_script(params)

# 写入临时文件
tcl_path = RUNS_DIR / f"batch_{uuid4()}.tcl"
tcl_path.write_text(tcl_script)

# 调用 hmbatch
cmd = [hmbatch_path, "-tcl", str(tcl_path)]
result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
```

**GUI Listener 模式：**
```python
# 通过 socket 发送 Tcl 到已打开的 HyperMesh GUI
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.connect(("127.0.0.1", 47881))
sock.sendall(tcl_script.encode())
response = sock.recv(4096)
sock.close()
```

### 3.2 Tcl 脚本保护机制

```tcl
# MCP_SCRIPT_BEGIN
# 只有带标记的脚本才被允许执行网格化命令
*meshdragelements2 ...
# MCP_SCRIPT_END
```

Python 端验证：
```python
if "MCP_SCRIPT_BEGIN" not in tcl_script:
    raise ValueError("Untrusted Tcl script rejected")
```

### 3.3 批处理 + 检查点

- 每处理 N 个 solid 保存一次 .hm 文件
- 高风险实体单独成批
- 失败记录并继续（不中断整个流程）

### 3.4 文件队列 IPC（从 ANSYS-Workbench-mcp，适用于 LS-PrePost）

```python
# 写命令
cmd_path = COMMANDS_DIR / f"{timestamp}.json"
cmd_path.write_text(json.dumps({"action": "export_png", "args": {...}}))

# 轮询结果
while True:
    result_path = RESULTS_DIR / f"{timestamp}.json"
    if result_path.exists():
        return json.loads(result_path.read_text())
    time.sleep(1)
```

## 4. 对 Dyna-mcp 的改造建议

### Phase 1（当前）：LS-DYNA .k 文件 + 路径管理
- ✅ `k_parser.py` — 继续自建，无复用源
- ✅ `k_writer.py` — 继续自建
- ✅ `path_tools.py` — 已有
- ✅ `env_check.py` — 已有
- ✅ `lsdyna_runner.py` — 已有最小版本

### Phase 2：HyperMesh 集成
- **直接复用** hypermesh-mcp 的 `hm_runner.py` 执行模式
- **直接复用** 核心 Tcl 生成器（probe、classify、mesh）
- **适配** HM 2021 路径（原项目针对 HM 2020）
- **集成** 到我们的 MCP server，注册为 tools

### Phase 3：LS-PrePost 集成
- **参考** ANSYS-Workbench-mcp 的文件队列 IPC
- **自建** cfile 生成器
- **自建** lsprepost_runner.py

### Phase 4：整体工作流
- **参考** hypermesh-mcp 的四阶段工作流（Probe → Classify → Mesh → Report）
- **设计** LS-DYNA 工作流（Parse → Validate → Generate → Solve → Post）

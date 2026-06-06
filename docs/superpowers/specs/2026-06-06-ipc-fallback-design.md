# IPC Fallback 设计文档

**Date:** 2026-06-06
**Status:** Pending User Review

---

## 1. 目标

Socket 命令失败时自动降级到 IPC，恢复后自动切回。对上层透明。

## 2. 接口

```python
execute_tcl_gui(script, mode="auto", retry=3, fallback=True)
```

| 参数 | 类型 | 默认 | 说明 |
|------|------|------|------|
| script | str | 必填 | Tcl 脚本 |
| mode | str | "auto" | "auto"/"socket"/"ipc" |
| retry | int | 3 | Socket 失败重试次数 |
| fallback | bool | True | Socket 失败后是否降级到 IPC |

## 3. 执行流程

```
1. 生成 command_id (uuid)
2. 检查 transport_state
3. socket_active:
   → socket 执行
   → 通信失败 → 重试 (最多 retry 次)
   → 3 次失败 → 切换到 ipc
4. ipc_active:
   → 写 commands/{command_id}.json
   → 轮询 results/{command_id}.json
5. 后台心跳检测 socket listener
6. socket 连续恢复 → 切回 socket
7. 返回统一 result object
```

## 4. 统一返回格式

```python
{
    "success": True,
    "command_id": "cmd_abc123",
    "transport": "socket",        # "socket" | "ipc"
    "fallback_used": False,       # 是否触发了降级
    "retry_count": 0,             # socket 重试次数
    "response": "OK\n...",        # 原始响应
    "error_type": None,           # None | "connection_error" | "execution_error" | "timeout"
    "message": None               # 错误信息
}
```

## 5. transport_state 管理

```python
class TransportState:
    socket_active: bool = True
    ipc_active: bool = False
    consecutive_socket_failures: int = 0
    consecutive_socket_successes: int = 0
    last_heartbeat: float = 0
    
    def should_use_socket(self) -> bool:
        return self.socket_active
    
    def record_socket_failure(self):
        self.consecutive_socket_failures += 1
        self.consecutive_socket_successes = 0
        if self.consecutive_socket_failures >= 3:
            self.socket_active = False
            self.ipc_active = True
    
    def record_socket_success(self):
        self.consecutive_socket_failures = 0
        self.consecutive_socket_successes += 1
    
    def record_ipc_success(self):
        # IPC 成功后检查 socket 是否恢复
        pass
```

## 6. 心跳检测

```python
def heartbeat_check():
    """后台线程定期检查 socket 状态"""
    while True:
        if not state.socket_active:
            # Socket 不活跃，尝试恢复
            if try_socket_ping():
                state.socket_active = True
                state.ipc_active = False
                state.consecutive_socket_failures = 0
        time.sleep(5)  # 每 5 秒检查一次
```

## 7. IPC 命令格式

```python
# 写入 ipc/commands/{command_id}.json
{
    "id": "cmd_abc123",
    "type": "execute_tcl",
    "script": "*createentity mats name=TEST",
    "timestamp": 1234567890.0
}

# 读取 ipc/results/{command_id}.json
{
    "id": "cmd_abc123",
    "ok": True,
    "payload": {
        "success": True,
        "response": "OK\n1"
    },
    "timestamp": 1234567891.0
}
```

## 8. 文件结构

```
program/
├── transport_manager.py    # 新：TransportState + heartbeat
├── hm_gui.py              # 修改：execute_tcl_gui 加入 fallback
├── plugin_loop.py          # 已有：IPC 轮询（无需修改）
```

## 9. 实现顺序

1. 创建 `transport_manager.py`（TransportState + heartbeat）
2. 修改 `hm_gui.py` 的 `execute_tcl_gui` 加入 fallback
3. 测试：正常 socket → 断开 → 自动降级 IPC → 恢复 → 切回
4. 提交

## 10. 验收标准

1. Socket 正常时走 socket，返回 `transport: "socket"`
2. Socket 连续失败 3 次后自动降级到 IPC
3. IPC 执行成功，返回 `transport: "ipc", fallback_used: true`
4. Socket 恢复后自动切回
5. 对上层 `hm_set_keyword` 等函数透明，无需修改

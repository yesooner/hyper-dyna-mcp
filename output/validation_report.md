# Hyper-Dyna-MCP Validation Report

**Date:** 2026-06-07
**Model:** test8_daota_lou.hm (倒塌楼, 2020 工程模型)
**Status:** PASS

---

## 1. 模型信息

| 项目 | 值 |
|------|-----|
| 文件 | test8_daota_lou.hm |
| Components | 5 (Part 1-4 + Undefined_1) |
| Nodes | 168,480 |
| Elements | 78,180 |
| Materials | 5 |
| Properties | 6 |

## 2. MCP 功能验证

| 功能 | 状态 | 说明 |
|------|------|------|
| Socket 连接 | ✓ | 端口 47882 |
| IPC Fallback | ✓ | Socket 失败自动降级 |
| 模型查询 | ✓ | query_model_info |
| LS-DYNA 模板激活 | ✓ | activate_lsdyne_template |
| 材料设置 | ✓ | MAT_ELASTIC |
| 控制卡片 | ✓ | CONTROL_TERMINATION |
| 数据库输出 | ✓ | DATABASE_BINARY_D3PLOT |
| 截面设置 | ✓ | SECTION_SHELL |
| 逐条发送 | ✓ | 避免 HyperMesh 崩溃 |

## 3. 模板验证

| 类别 | 总数 | 通过 | 失败 |
|------|------|------|------|
| mat | 292 | 292 | 0 |
| control | 260 | 260 | 0 |
| define | 208 | 208 | 0 |
| database | 162 | 162 | 0 |
| contact | 151 | 151 | 0 |
| boundary | 120 | 120 | 0 |
| constrained | 111 | 111 | 0 |
| load | 96 | 96 | 0 |
| initial | 83 | 83 | 0 |
| element | 74 | 74 | 0 |
| set | 61 | 61 | 0 |
| **总计** | **1935** | **1935** | **0** |

## 4. 已知限制

1. Component 名称解析格式需改进（空格问题）
2. 材料 RHO/E/PR 查询依赖 cardimage 类型
3. 端口 47881 僵尸占用需重启释放

## 5. 环境

- Python: 3.13.5 (hyper-dyna conda env)
- HyperMesh: 2021 (E:/HM2021)
- LS-PrePost: 4.8 (E:/ANSYS2022)
- LS-DYNA: R13.1

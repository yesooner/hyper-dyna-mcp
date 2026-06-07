# Task Progress Hook

## 规则

当完成计划中的一个 Task 时，自动执行以下操作：

1. 更新 Obsidian 中的进度文件
2. 提交代码到 Git
3. 写入 handoff

## 进度文件

路径：`D:/Zotero/ZoteroNote/Agent/dyna mcp/plan/progress_YYMM.md`

格式：
```markdown
# Progress — 2026-06

## Task 1: [名称]
- 状态: ✓ 完成
- 文件: xxx.py, yyy.py
- 测试: X/Y 通过
- 提交: abc1234

## Task 2: [名称]
- 状态: ⏳ 进行中
- ...
```

## 触发条件

当以下任一条件满足时，自动保存进度：
1. 一个 Task 的所有 Step 完成
2. 一个 Task 的测试全部通过
3. 用户说 "保存进度" 或 "save progress"

## 保存内容

1. 更新 `progress_YYMM.md` 中对应 Task 的状态
2. `git add -A && git commit`
3. 写入 `handoff_YYMMDD.md`

## 示例

```python
# 完成 Task 1 后自动执行：
save_progress(
    task_name="K Parser 增强",
    status="完成",
    files=["program/tools/k_parser.py", "tests/test_k_parser.py"],
    tests_passed=19,
    tests_total=19,
    commit_hash="abc1234"
)
```

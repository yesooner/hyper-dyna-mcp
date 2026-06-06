# auto-handoff.ps1
# PostToolUse hook: every 5 tool calls, emit a handoff instruction to stdout.
# 每日固定一个文件 handoff_YYMMDD.md，触发时追加到文末。

$ErrorActionPreference = "SilentlyContinue"

# --- 配置 ---
$counterFile = Join-Path $PSScriptRoot ".handoff-turn-count"
$handoffDir  = "D:\Zotero\ZoteroNote\Agent\dyna mcp\handoff"
$interval    = 5

# --- 读取计数 ---
$count = 0
if (Test-Path $counterFile) {
    $raw = (Get-Content $counterFile -Raw).Trim()
    if ($raw -match '^\d+$') {
        $count = [int]$raw
    }
}
$count++

# --- 写回计数 ---
Set-Content -Path $counterFile -Value $count -NoNewline

# --- 未到阈值，静默退出 ---
if ($count -lt $interval) {
    exit 0
}

# --- 到达阈值：重置计数，输出 handoff 指令 ---
Set-Content -Path $counterFile -Value 0 -NoNewline

# 每日固定文件名
$today = Get-Date -Format "yyMMdd"
$filename = "handoff_${today}.md"
$filepath = Join-Path $handoffDir $filename

# 判断文件是否已存在
$exists = Test-Path $filepath

# 输出指令给 Claude Code
Write-Host ""
Write-Host "=== AUTO-HANDOFF TRIGGER (turn ${count}/${interval}) ==="
if ($exists) {
    Write-Host "Mode: APPEND to existing daily handoff"
} else {
    Write-Host "Mode: CREATE new daily handoff"
}
Write-Host "Output file: $filepath"
Write-Host "Generate a handoff summary. Use Edit (append) if file exists, Write if new."
Write-Host "=== END AUTO-HANDOFF ==="

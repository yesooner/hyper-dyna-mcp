@echo off
REM Hyper-Dyna-MCP 卸载脚本
REM 此脚本将清理生成的配置文件

echo ========================================
echo Hyper-Dyna-MCP 卸载
echo ========================================
echo.

REM 检查是否在正确的目录
if not exist "program\server.py" (
    echo Error: 请在 hyper-dyna-mcp 项目根目录运行此脚本
    echo 当前目录: %CD%
    pause
    exit /b 1
)

echo 警告: 此操作将删除以下文件:
echo - path\local_paths.yaml
echo - path\hypermesh_paths.yaml
echo - path\lsdyna_paths.yaml
echo - path\lsprepost_paths.yaml
echo - path\obsidian_paths.yaml
echo - .env
echo - claude_code_mcp.json
echo.
echo 注意: 不会删除项目核心文件和测试文件
echo.

set /p confirm="确认卸载？(y/n) [n]: "
if /i not "%confirm%"=="y" (
    echo 已取消卸载。
    pause
    exit /b 0
)

echo.
echo 正在清理配置文件...

REM 删除配置文件
if exist "path\local_paths.yaml" (
    del "path\local_paths.yaml"
    echo 删除 path\local_paths.yaml
)

if exist "path\hypermesh_paths.yaml" (
    del "path\hypermesh_paths.yaml"
    echo 删除 path\hypermesh_paths.yaml
)

if exist "path\lsdyna_paths.yaml" (
    del "path\lsdyna_paths.yaml"
    echo 删除 path\lsdyna_paths.yaml
)

if exist "path\lsprepost_paths.yaml" (
    del "path\lsprepost_paths.yaml"
    echo 删除 path\lsprepost_paths.yaml
)

if exist "path\obsidian_paths.yaml" (
    del "path\obsidian_paths.yaml"
    echo 删除 path\obsidian_paths.yaml
)

if exist ".env" (
    del ".env"
    echo 删除 .env
)

if exist "claude_code_mcp.json" (
    del "claude_code_mcp.json"
    echo 删除 claude_code_mcp.json
)

echo.
echo ========================================
echo 卸载完成！
echo ========================================
echo.
echo 注意: 项目核心文件和测试文件已保留
echo 如需完全删除项目，请手动删除整个目录
echo.
pause

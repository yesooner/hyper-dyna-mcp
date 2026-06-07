@echo off
REM Hyper-Dyna-MCP 快速安装脚本
REM 自动检测环境并生成配置文件

echo ========================================
echo Hyper-Dyna-MCP 快速安装
echo ========================================
echo.

REM 检查是否在正确的目录
if not exist "program\server.py" (
    echo Error: 请在 hyper-dyna-mcp 项目根目录运行此脚本
    echo 当前目录: %CD%
    pause
    exit /b 1
)

REM 检查 Python 是否可用
python --version >nul 2>&1
if errorlevel 1 (
    echo Error: Python 未安装或不在 PATH 中
    echo 请先安装 Python 3.11+
    pause
    exit /b 1
)

REM 运行自动环境检测
echo 运行自动环境检测...
echo.
python batch/auto_detect.py

REM 询问是否运行配置向导
echo.
set /p run_wizard="是否运行完整配置向导？(y/n) [n]: "
if /i "%run_wizard%"=="y" (
    echo.
    echo 启动配置向导...
    python batch/setup_wizard.py
)

REM 运行验证
echo.
set /p run_check="是否运行环境验证？(y/n) [y]: "
if /i "%run_check%"=="" set run_check=y
if /i "%run_check%"=="y" (
    echo.
    echo 运行环境验证...
    python batch/validate_all.py
)

echo.
echo ========================================
echo 安装完成！
echo ========================================
echo.
echo 后续步骤:
echo 1. 检查并修改 path/ 目录下的配置文件
echo 2. 生成 MCP 配置:
echo    - Claude: python batch/generate_mcp_config.py
echo    - CODEX: python batch/generate_codex_config.py --append
echo 3. 启动 MCP 服务器: python -m program.server
echo.
pause

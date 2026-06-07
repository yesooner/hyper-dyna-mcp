@echo off
REM Hyper-Dyna-MCP 快速安装脚本
REM 此脚本将调用 batch 目录中的安装脚本

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

REM 检查 batch 目录是否存在
if not exist "batch\install.bat" (
    echo Error: batch\install.bat 不存在
    echo 请确保项目完整
    pause
    exit /b 1
)

REM 调用 batch 安装脚本
call batch\install.bat

REM 运行配置向导
echo.
echo 是否运行配置向导？(推荐首次安装时使用)
set /p run_wizard="运行配置向导？(y/n) [y]: "
if /i "%run_wizard%"=="" set run_wizard=y
if /i "%run_wizard%"=="y" (
    echo.
    echo 启动配置向导...
    python batch\setup_wizard.py
)

REM 生成 MCP 配置
echo.
echo 是否生成 MCP 配置文件？
set /p gen_mcp="生成 MCP 配置？(y/n) [y]: "
if /i "%gen_mcp%"=="" set gen_mcp=y
if /i "%gen_mcp%"=="y" (
    echo.
    echo 生成 MCP 配置...
    python batch\generate_mcp_config.py
)

REM 运行验证
echo.
echo 是否运行环境验证？
set /p run_check="运行验证？(y/n) [y]: "
if /i "%run_check%"=="" set run_check=y
if /i "%run_check%"=="y" (
    echo.
    echo 运行环境验证...
    python batch\validators\check_env.py
    echo.
    echo 运行路径验证...
    python batch\validators\check_paths.py
)

echo.
echo ========================================
echo 安装完成！
echo ========================================
echo.
echo 后续步骤:
echo 1. 检查并修改 path/ 目录下的配置文件
echo 2. 检查并修改 .env 文件
echo 3. 重启 Claude Desktop 或 Claude Code 以加载 MCP 配置
echo 4. 启动 MCP 服务器: python -m program.server
echo.
pause

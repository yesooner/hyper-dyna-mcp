#!/bin/bash
# Hyper-Dyna-MCP 快速安装脚本
# 自动检测环境并生成配置文件

echo "========================================"
echo "Hyper-Dyna-MCP 快速安装"
echo "========================================"
echo ""

# 检查是否在正确的目录
if [ ! -f "program/server.py" ]; then
    echo "Error: 请在 hyper-dyna-mcp 项目根目录运行此脚本"
    echo "当前目录: $(pwd)"
    exit 1
fi

# 检查 Python 是否可用
if ! command -v python3 &> /dev/null; then
    echo "Error: Python3 未安装或不在 PATH 中"
    echo "请先安装 Python 3.11+"
    exit 1
fi

# 运行自动环境检测
echo "运行自动环境检测..."
echo ""
python3 batch/core/auto_detect.py

# 询问是否运行配置向导
echo ""
read -p "是否运行完整配置向导？(y/n) [n]: " run_wizard
if [ "$run_wizard" = "y" ] || [ "$run_wizard" = "Y" ]; then
    echo ""
    echo "启动配置向导..."
    python3 batch/core/setup_wizard.py
fi

# 运行验证
echo ""
read -p "是否运行环境验证？(y/n) [y]: " run_check
run_check=${run_check:-y}
if [ "$run_check" = "y" ] || [ "$run_check" = "Y" ]; then
    echo ""
    echo "运行环境验证..."
    python3 batch/validate_all.py
fi

echo ""
echo "========================================"
echo "安装完成！"
echo "========================================"
echo ""
echo "后续步骤:"
echo "1. 检查并修改 path/ 目录下的配置文件"
echo "2. 生成 MCP 配置:"
echo "   - Claude: python3 batch/generate_mcp_config.py"
echo "   - CODEX: python3 batch/generate_codex_config.py --append"
echo "3. 启动 MCP 服务器: python3 -m program.server"
echo ""

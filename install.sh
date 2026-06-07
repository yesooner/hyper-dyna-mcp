#!/bin/bash
# Hyper-Dyna-MCP 快速安装脚本
# 此脚本将调用 batch 目录中的安装脚本

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

# 检查 batch 目录是否存在
if [ ! -f "batch/install.sh" ]; then
    echo "Error: batch/install.sh 不存在"
    echo "请确保项目完整"
    exit 1
fi

# 调用 batch 安装脚本
chmod +x batch/install.sh
./batch/install.sh

# 运行配置向导
echo ""
echo "是否运行配置向导？(推荐首次安装时使用)"
read -p "运行配置向导？(y/n) [y]: " run_wizard
run_wizard=${run_wizard:-y}
if [ "$run_wizard" = "y" ] || [ "$run_wizard" = "Y" ]; then
    echo ""
    echo "启动配置向导..."
    python3 batch/setup_wizard.py
fi

# 生成 MCP 配置
echo ""
echo "是否生成 MCP 配置文件？"
read -p "生成 MCP 配置？(y/n) [y]: " gen_mcp
gen_mcp=${gen_mcp:-y}
if [ "$gen_mcp" = "y" ] || [ "$gen_mcp" = "Y" ]; then
    echo ""
    echo "生成 MCP 配置..."
    python3 batch/generate_mcp_config.py
fi

# 运行验证
echo ""
echo "是否运行环境验证？"
read -p "运行验证？(y/n) [y]: " run_check
run_check=${run_check:-y}
if [ "$run_check" = "y" ] || [ "$run_check" = "Y" ]; then
    echo ""
    echo "运行环境验证..."
    python3 batch/validators/check_env.py
    echo ""
    echo "运行路径验证..."
    python3 batch/validators/check_paths.py
fi

echo ""
echo "========================================"
echo "安装完成！"
echo "========================================"
echo ""
echo "后续步骤:"
echo "1. 检查并修改 path/ 目录下的配置文件"
echo "2. 检查并修改 .env 文件"
echo "3. 重启 Claude Desktop 或 Claude Code 以加载 MCP 配置"
echo "4. 启动 MCP 服务器: python -m program.server"
echo ""

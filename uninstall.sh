#!/bin/bash
# Hyper-Dyna-MCP 卸载脚本
# 此脚本将清理生成的配置文件

echo "========================================"
echo "Hyper-Dyna-MCP 卸载"
echo "========================================"
echo ""

# 检查是否在正确的目录
if [ ! -f "program/server.py" ]; then
    echo "Error: 请在 hyper-dyna-mcp 项目根目录运行此脚本"
    echo "当前目录: $(pwd)"
    exit 1
fi

echo "警告: 此操作将删除以下文件:"
echo "- path/local_paths.yaml"
echo "- path/hypermesh_paths.yaml"
echo "- path/lsdyna_paths.yaml"
echo "- path/lsprepost_paths.yaml"
echo "- path/obsidian_paths.yaml"
echo "- .env"
echo "- claude_code_mcp.json"
echo ""
echo "注意: 不会删除项目核心文件和测试文件"
echo ""

read -p "确认卸载？(y/n) [n]: " confirm
if [ "$confirm" != "y" ] && [ "$confirm" != "Y" ]; then
    echo "已取消卸载。"
    exit 0
fi

echo ""
echo "正在清理配置文件..."

# 删除配置文件
if [ -f "path/local_paths.yaml" ]; then
    rm "path/local_paths.yaml"
    echo "删除 path/local_paths.yaml"
fi

if [ -f "path/hypermesh_paths.yaml" ]; then
    rm "path/hypermesh_paths.yaml"
    echo "删除 path/hypermesh_paths.yaml"
fi

if [ -f "path/lsdyna_paths.yaml" ]; then
    rm "path/lsdyna_paths.yaml"
    echo "删除 path/lsdyna_paths.yaml"
fi

if [ -f "path/lsprepost_paths.yaml" ]; then
    rm "path/lsprepost_paths.yaml"
    echo "删除 path/lsprepost_paths.yaml"
fi

if [ -f "path/obsidian_paths.yaml" ]; then
    rm "path/obsidian_paths.yaml"
    echo "删除 path/obsidian_paths.yaml"
fi

if [ -f ".env" ]; then
    rm ".env"
    echo "删除 .env"
fi

if [ -f "claude_code_mcp.json" ]; then
    rm "claude_code_mcp.json"
    echo "删除 claude_code_mcp.json"
fi

echo ""
echo "========================================"
echo "卸载完成！"
echo "========================================"
echo ""
echo "注意: 项目核心文件和测试文件已保留"
echo "如需完全删除项目，请手动删除整个目录"
echo ""

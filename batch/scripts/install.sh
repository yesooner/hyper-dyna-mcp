#!/bin/bash
# Hyper-Dyna-MCP Batch Installation Script
# 此脚本将配置文件从模板复制到实际位置

echo "========================================"
echo "Hyper-Dyna-MCP Batch Installation"
echo "========================================"
echo ""

# 检查是否在正确的目录
if [ ! -f "program/server.py" ]; then
    echo "Error: 请在 hyper-dyna-mcp 项目根目录运行此脚本"
    echo "当前目录: $(pwd)"
    exit 1
fi

# 创建 path 目录（如果不存在）
if [ ! -d "path" ]; then
    echo "Creating path directory..."
    mkdir -p path
fi

# 复制模板文件
echo "Copying configuration templates..."

# 复制本地路径配置
if [ ! -f "path/local_paths.yaml" ]; then
    cp "batch/templates/local_paths.yaml" "path/local_paths.yaml"
    echo "Created path/local_paths.yaml"
else
    echo "path/local_paths.yaml already exists, skipping..."
fi

# 复制 HyperMesh 路径配置
if [ ! -f "path/hypermesh_paths.yaml" ]; then
    cp "batch/templates/hypermesh_paths.yaml" "path/hypermesh_paths.yaml"
    echo "Created path/hypermesh_paths.yaml"
else
    echo "path/hypermesh_paths.yaml already exists, skipping..."
fi

# 复制 LS-DYNA 路径配置
if [ ! -f "path/lsdyna_paths.yaml" ]; then
    cp "batch/templates/lsdyna_paths.yaml" "path/lsdyna_paths.yaml"
    echo "Created path/lsdyna_paths.yaml"
else
    echo "path/lsdyna_paths.yaml already exists, skipping..."
fi

# 复制 LS-PrePost 路径配置
if [ ! -f "path/lsprepost_paths.yaml" ]; then
    cp "batch/templates/lsprepost_paths.yaml" "path/lsprepost_paths.yaml"
    echo "Created path/lsprepost_paths.yaml"
else
    echo "path/lsprepost_paths.yaml already exists, skipping..."
fi

# 复制 Obsidian 路径配置
if [ ! -f "path/obsidian_paths.yaml" ]; then
    cp "batch/templates/obsidian_paths.yaml" "path/obsidian_paths.yaml"
    echo "Created path/obsidian_paths.yaml"
else
    echo "path/obsidian_paths.yaml already exists, skipping..."
fi

# 复制 .env 文件
if [ ! -f ".env" ]; then
    cp "batch/templates/.env.example" ".env"
    echo "Created .env"
else
    echo ".env already exists, skipping..."
fi

echo ""
echo "========================================"
echo "Configuration files created!"
echo "========================================"
echo ""
echo "Next steps:"
echo ""
echo "1. Edit the configuration files in path/ directory:"
echo "   - path/local_paths.yaml"
echo "   - path/hypermesh_paths.yaml"
echo "   - path/lsdyna_paths.yaml"
echo "   - path/lsprepost_paths.yaml"
echo "   - path/obsidian_paths.yaml"
echo ""
echo "2. Edit .env file with your actual paths"
echo ""
echo "3. Copy MCP configuration to Claude Desktop:"
echo "   - Windows: %APPDATA%\\Claude\\claude_desktop_config.json"
echo "   - macOS: ~/Library/Application Support/Claude/claude_desktop_config.json"
echo ""
echo "4. Run validation:"
echo "   python batch/validators/check_paths.py"
echo "   python batch/validators/check_env.py"
echo ""
echo "5. Start MCP server:"
echo "   python -m program.server"
echo ""

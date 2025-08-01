#!/bin/bash

# VSCode Calendar Extension 打包脚本

set -e

echo "📦 开始打包 VSCode Calendar Extension..."

# 检查是否安装了 vsce
if ! command -v vsce &> /dev/null; then
    echo "❌ 未找到 vsce，正在安装..."
    npm install -g @vscode/vsce
fi

# 检查 publisher 是否已设置
PUBLISHER=$(node -p "require('./package.json').publisher")
if [ "$PUBLISHER" == "your-publisher-name" ] || [ -z "$PUBLISHER" ]; then
    echo "⚠️  警告: package.json 中的 publisher 字段需要设置"
    echo "   请编辑 package.json，将 'publisher' 改为你的发布者名称"
    echo "   或者使用: vsce package --publisher your-publisher-name"
    read -p "是否继续打包？(y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# 安装依赖
echo "📥 安装依赖..."
npm install

# 打包
echo "🔨 开始打包..."
vsce package

echo "✅ 打包完成！"
echo "📦 生成的 .vsix 文件在当前目录"
echo ""
echo "安装方式："
echo "1. VSCode: 扩展视图 -> ... -> Install from VSIX"
echo "2. Cursor: 扩展视图 -> ... -> Install from VSIX"
echo "3. 命令行: code --install-extension *.vsix"
echo "           或 cursor --install-extension *.vsix"

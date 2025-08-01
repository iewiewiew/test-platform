#!/bin/bash
# Chrome 扩展打包脚本
# 使用方法: ./package.sh

# 获取脚本所在目录
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PARENT_DIR="$(dirname "$SCRIPT_DIR")"
EXTENSION_NAME="test-data-generator"
ZIP_FILE="${PARENT_DIR}/${EXTENSION_NAME}.zip"

echo "开始打包 Chrome 扩展..."
echo "扩展目录: ${SCRIPT_DIR}"
echo "输出文件: ${ZIP_FILE}"

# 进入扩展目录
cd "${SCRIPT_DIR}"

# 创建临时目录
TEMP_DIR=$(mktemp -d)
echo "临时目录: ${TEMP_DIR}"

# 复制必要文件到临时目录
echo "复制文件..."
cp manifest.json "${TEMP_DIR}/"
cp popup.html "${TEMP_DIR}/"
cp popup.js "${TEMP_DIR}/"
cp popup.css "${TEMP_DIR}/"

# 如果有 icons 目录且包含图标文件，则复制
if [ -d "icons" ]; then
    mkdir -p "${TEMP_DIR}/icons"
    # 只复制 .png 文件
    find icons -name "*.png" -exec cp {} "${TEMP_DIR}/icons/" \;
fi

# 创建 ZIP 文件
cd "${TEMP_DIR}"
zip -r "${ZIP_FILE}" . -q
cd - > /dev/null

# 清理临时目录
rm -rf "${TEMP_DIR}"

# 显示结果
if [ -f "${ZIP_FILE}" ]; then
    FILE_SIZE=$(du -h "${ZIP_FILE}" | cut -f1)
    echo "✓ 打包完成!"
    echo "  文件: ${ZIP_FILE}"
    echo "  大小: ${FILE_SIZE}"
    echo ""
    echo "安装方法:"
    echo "1. 在 Chrome 中访问 chrome://extensions/"
    echo "2. 开启'开发者模式'"
    echo "3. 点击'加载已解压的扩展程序'"
    echo "4. 选择解压后的目录或直接加载 ZIP 文件"
else
    echo "✗ 打包失败!"
    exit 1
fi







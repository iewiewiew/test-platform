# Chrome 扩展打包指南

本文档介绍如何将测试数据生成器扩展打包为 `.crx` 文件或 `.zip` 文件。

## 方法一：使用 Chrome 浏览器打包（推荐）

### 步骤 1：打开扩展管理页面

1. 打开 Chrome 浏览器
2. 访问 `chrome://extensions/`
3. 确保右上角的"开发者模式"已开启

### 步骤 2：打包扩展

1. 点击页面顶部的"打包扩展程序"按钮
2. 在弹出的对话框中：
   - **扩展程序根目录**：选择 `backend/chrome/test-data-generator` 目录
   - **私有密钥文件（可选）**：首次打包留空，Chrome 会自动生成
3. 点击"打包扩展程序"按钮

### 步骤 3：获取打包文件

打包完成后，会在扩展目录的**上一级目录**（即 `backend/chrome/`）生成两个文件：

- `test-data-generator.crx` - 打包后的扩展文件（可直接安装）
- `test-data-generator.pem` - 私有密钥文件（**重要：请妥善保管，用于后续更新**）

### 步骤 4：安装打包后的扩展

**方式 A：直接安装 .crx 文件**
1. 将 `.crx` 文件拖拽到 `chrome://extensions/` 页面
2. 点击"添加扩展程序"确认安装

**方式 B：解压安装**
1. 将 `.crx` 文件重命名为 `.zip`
2. 解压到任意目录
3. 在 `chrome://extensions/` 页面点击"加载已解压的扩展程序"
4. 选择解压后的目录

## 方法二：手动创建 ZIP 文件

### 步骤 1：准备文件

确保以下文件都在 `test-data-generator` 目录中：

```
test-data-generator/
├── manifest.json
├── popup.html
├── popup.js
├── popup.css
└── icons/          # 如果有图标文件
    ├── icon16.png
    ├── icon48.png
    └── icon128.png
```

**注意**：不要包含以下文件：
- `README.md`
- `PACKAGE.md`
- `create_icons.py`
- `generate_icons.html`
- `.git` 目录
- 其他开发文件

### 步骤 2：创建 ZIP 文件

**macOS/Linux:**
```bash
cd backend/chrome
zip -r test-data-generator.zip test-data-generator/ \
  -x "*.md" \
  -x "*.py" \
  -x "*.html" \
  -x ".git/*" \
  -x "__pycache__/*"
```

**Windows (PowerShell):**
```powershell
cd backend\chrome
Compress-Archive -Path test-data-generator\* -DestinationPath test-data-generator.zip -Force
```

**或使用图形界面：**
1. 进入 `backend/chrome/test-data-generator` 目录
2. 选择所有需要的文件（排除开发文件）
3. 右键选择"压缩"或"添加到压缩文件"
4. 命名为 `test-data-generator.zip`

### 步骤 3：安装 ZIP 文件

1. 将 `.zip` 文件重命名为 `.crx`（可选，Chrome 也支持直接加载 ZIP）
2. 在 `chrome://extensions/` 页面开启"开发者模式"
3. 点击"加载已解压的扩展程序"
4. 选择 ZIP 文件或解压后的目录

## 方法三：使用命令行工具（高级）

### 安装 Chrome 扩展打包工具

```bash
# 使用 npm 安装 crx 工具
npm install -g crx

# 或使用 yarn
yarn global add crx
```

### 打包扩展

```bash
cd backend/chrome/test-data-generator

# 生成 .crx 文件（会自动生成密钥）
crx pack . -o ../test-data-generator.crx

# 使用指定密钥打包
crx pack . -p /path/to/key.pem -o ../test-data-generator.crx
```

## 打包前的检查清单

在打包前，请确保：

- [ ] `manifest.json` 文件格式正确
- [ ] 所有引用的文件（HTML、JS、CSS）都存在
- [ ] 图标文件（如果配置了）存在于指定路径
- [ ] 版本号已更新（如果需要）
- [ ] 已移除所有调试代码和注释（可选）
- [ ] 已测试扩展功能正常

## 版本更新

### 更新版本号

在 `manifest.json` 中更新版本号：

```json
{
  "version": "1.0.1"  // 从 1.0.0 更新到 1.0.1
}
```

### 使用相同密钥重新打包

如果之前已经打包过，请使用相同的 `.pem` 密钥文件重新打包：

1. 在"打包扩展程序"对话框中
2. **扩展程序根目录**：选择 `test-data-generator` 目录
3. **私有密钥文件**：选择之前生成的 `test-data-generator.pem` 文件
4. 点击"打包扩展程序"

这样可以确保扩展 ID 不变，用户更新时不会丢失数据。

## 发布到 Chrome Web Store（可选）

如果要发布到 Chrome 网上应用店：

1. 访问 [Chrome Web Store 开发者控制台](https://chrome.google.com/webstore/devconsole)
2. 支付一次性注册费用（$5）
3. 上传打包后的 `.zip` 文件（不是 `.crx`）
4. 填写扩展信息、截图、描述等
5. 提交审核

**注意**：发布到商店需要：
- 提供 128x128 的图标
- 提供至少一张截图
- 填写详细的描述和隐私政策
- 通过 Google 的审核

## 常见问题

### Q: 打包后文件太大怎么办？

A: 检查是否包含了不必要的文件：
- 移除 `node_modules`（如果有）
- 移除开发工具和脚本
- 压缩图片资源
- 压缩 JavaScript 和 CSS 文件

### Q: 打包后无法安装？

A: 检查：
- `manifest.json` 格式是否正确
- 所有引用的文件路径是否正确
- 文件权限是否正确

### Q: 如何更新已安装的扩展？

A: 
- 如果是从 `.crx` 安装的：重新打包后拖拽安装，Chrome 会自动更新
- 如果是解压安装的：重新加载扩展即可

### Q: 密钥文件丢失了怎么办？

A: 如果 `.pem` 文件丢失：
- 可以重新生成新的密钥打包
- 但扩展 ID 会改变，用户需要重新安装
- 建议将 `.pem` 文件备份到安全的地方

## 快速打包脚本

创建一个简单的打包脚本 `package.sh`：

```bash
#!/bin/bash
cd "$(dirname "$0")"
cd ..
zip -r test-data-generator.zip test-data-generator/ \
  -x "*.md" \
  -x "*.py" \
  -x "*.html" \
  -x ".git/*" \
  -x "__pycache__/*" \
  -x "*.DS_Store"
echo "打包完成: test-data-generator.zip"
```

使用方法：
```bash
chmod +x package.sh
./package.sh
```







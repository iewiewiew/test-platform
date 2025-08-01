# VSCode Calendar Extension

一个简单的 VSCode 日历插件，显示当月日历，支持鼠标悬停交互。兼容 VSCode、Cursor 等基于 VSCode 的编辑器。

## 功能特性

- 📅 显示当月日历
- 🖱️ 鼠标悬停显示日期详细信息
- ⬅️➡️ 支持切换月份
- 🎨 适配 VSCode 主题颜色
- ✨ 平滑的动画效果

## 安装和运行

### 前置要求

- Node.js (建议 v16 或更高版本)
- VSCode (1.60.0 或更高版本)

### 步骤

1. **安装依赖**

   ```bash
   cd backend/extensions/vscode-calendar
   npm install
   ```

2. **在 VSCode 中打开插件文件夹**

   - 打开 VSCode
   - 选择 `File` -> `Open Folder...`
   - 选择 `backend/extensions/vscode-calendar` 文件夹

3. **运行扩展**

   **方法一：使用 F5 键（推荐）**

   - 确保在 VSCode 中打开了插件文件夹
   - 按 `F5` 键启动扩展开发宿主窗口
   - 如果 F5 没有反应，可能是 macOS 系统快捷键冲突，请尝试以下方法：
     - 打开 `系统设置` -> `键盘` -> `快捷键` -> `功能键`，确保 F5 没有被占用
     - 或者使用 `Fn + F5` 组合键

   **方法二：使用命令面板**

   - 按 `Cmd + Shift + P` (macOS) 或 `Ctrl + Shift + P` (Windows/Linux)
   - 输入 `Debug: Start Debugging` 并选择
   - 或者输入 `Run Extension` 并选择

   **方法三：使用调试面板**

   - 点击左侧活动栏的调试图标（或按 `Cmd + Shift + D`）
   - 在顶部下拉菜单中选择 "Run Extension"
   - 点击绿色的播放按钮

4. **测试插件**
   - 扩展开发宿主窗口会自动打开
   - 在左侧资源管理器侧边栏找到 "Calendar" 视图
   - 如果看不到，可以点击资源管理器图标展开侧边栏

## 使用方法

1. 打开 VSCode 或 Cursor
2. 在左侧资源管理器侧边栏找到 "Calendar" 视图
3. 鼠标移动到日历上的任意日期，会显示日期详细信息
4. 点击左右箭头按钮可以切换月份

## 快速打包和安装

### 快速打包（3 步）

1. **安装依赖**：

   ```bash
   cd backend/extensions/vscode-calendar
   npm install
   ```

2. **设置 Publisher**（首次打包需要）：

   编辑 `package.json`，将 `"publisher": "your-publisher-name"` 改为你的发布者名称，例如：

   ```json
   "publisher": "myusername"
   ```

   或者使用命令行参数：

   ```bash
   vsce package --publisher your-publisher-name
   ```

3. **打包扩展**：

   **方法一：使用脚本（推荐）**

   ```bash
   ./package.sh
   ```

   **方法二：使用 npm**

   ```bash
   npm run package
   ```

   **方法三：直接使用 vsce**

   ```bash
   # 如果还没安装 vsce
   npm install -g @vscode/vsce

   # 打包
   vsce package
   ```

   打包成功后会在当前目录生成 `vscode-calendar-0.0.1.vsix` 文件。

### 安装扩展

#### 在 VSCode / Cursor 中安装

方法一：

1. 打开编辑器（VSCode 或 Cursor）
2. 按 `Cmd + Shift + X` (macOS) 或 `Ctrl + Shift + X` (Windows/Linux) 打开扩展视图
3. 点击右上角的 `...` 菜单，选择 `Install from VSIX...`
4. 选择生成的 `.vsix` 文件
5. 重新加载窗口：`Cmd + Shift + P` -> `Developer: Reload Window`

方法二：

1. 使用快捷键 Ctrl+Shift+P （在 macOS 上是 Cmd+Shift+P）打开命令面板。
2. 在命令面板的输入框中，键入 Install from VSIX。
3. 在弹出的窗口中，找到并选择你的 .vsix 文件即可开始安装。

#### 使用命令行安装

**VSCode**：

```bash
code --install-extension vscode-calendar-0.0.1.vsix
```

**Cursor**：

```bash
cursor --install-extension vscode-calendar-0.0.1.vsix
```

### 兼容性

本扩展兼容以下编辑器：

- ✅ Visual Studio Code (1.60.0+)
- ✅ Cursor
- ✅ VSCodium
- ✅ GitHub Codespaces
- ✅ 其他基于 VSCode 的编辑器

## 详细打包说明

### 前置要求

- Node.js (v16 或更高版本)
- npm 或 yarn

### 安装 vsce 打包工具

**全局安装（推荐）**：

```bash
npm install -g @vscode/vsce
```

**本地安装**（已添加到 devDependencies）：

```bash
npm install
```

### 打包选项

**基本打包**：

```bash
npm run package
```

或直接使用 vsce：

```bash
vsce package
```

**指定输出文件名**：

```bash
npm run package:patch
# 或
vsce package --out ./vscode-calendar.vsix
```

**打包并更新版本号**：

```bash
# 更新小版本号 (0.0.1 -> 0.1.0)
npm run package:minor

# 更新主版本号 (0.0.1 -> 1.0.0)
npm run package:major
```

### 分发方式

#### 1. 本地分发

直接将 `.vsix` 文件分享给其他用户，他们可以按照上述安装步骤安装。

#### 2. 发布到 VSCode Marketplace

如果需要发布到官方市场：

1. **创建 Azure DevOps 账户**（如果还没有）
2. **创建 Personal Access Token**：
   - 访问 https://dev.azure.com
   - 创建新的 Personal Access Token，权限包括 `Marketplace (Manage)`
3. **创建发布者**：
   ```bash
   vsce create-publisher your-publisher-name
   ```
4. **登录**：
   ```bash
   vsce login your-publisher-name
   ```
5. **发布**：
   ```bash
   vsce publish
   ```

#### 3. 发布到 Open VSX Registry

Open VSX 是开源的扩展市场，支持 VSCode、VSCodium 等：

1. **安装 ovsx**：
   ```bash
   npm install -g ovsx
   ```
2. **创建账户**：访问 https://open-vsx.org
3. **发布**：
   ```bash
   ovsx publish vscode-calendar-0.0.1.vsix
   ```

### 打包文件说明

打包时会包含以下文件：

- `extension.js` - 主入口文件
- `package.json` - 扩展配置
- `media/` - 资源文件（CSS、JS）
- `README.md` - 说明文档

以下文件会被排除（在 `.vscodeignore` 中）：

- `node_modules/` - 依赖包
- `.vscode/` - 开发配置
- `.git/` - Git 仓库
- `*.vsix` - 已打包的文件
- `.DS_Store` - macOS 系统文件

## 开发

### 文件结构

```
vscode-calendar/
├── .vscode/
│   ├── launch.json       # 调试配置文件
│   └── tasks.json        # 任务配置文件
├── extension.js          # 插件主入口文件
├── package.json          # 插件配置文件
├── media/
│   ├── calendar.css     # 日历样式文件
│   └── calendar.js       # 日历逻辑文件
└── README.md            # 说明文档
```

### 调试

1. 在 VSCode 中打开插件文件夹
2. 安装依赖：`npm install`
3. 按 `F5` 启动扩展开发宿主窗口（如果 F5 不工作，使用命令面板或调试面板）
4. 在扩展开发宿主窗口中测试插件功能

### 常见问题

**Q: macOS 上按 F5 没有反应？**

- A: macOS 系统可能占用了 F5 键。解决方法：
  1. 检查系统设置中的键盘快捷键
  2. 尝试使用 `Fn + F5`
  3. 使用命令面板：`Cmd + Shift + P` -> `Debug: Start Debugging`
  4. 使用调试面板：点击左侧调试图标，选择 "Run Extension" 并点击播放按钮

**Q: 找不到 Calendar 视图？**

- A: 按以下步骤操作：

  1. **显示侧边栏**：

     - 如果看不到左侧活动栏（资源管理器图标等），按 `Cmd + B` (macOS) 或 `Ctrl + B` (Windows/Linux) 切换侧边栏显示
     - 或者点击菜单：`View` -> `Appearance` -> `Show Primary Side Bar`

  2. **打开资源管理器**：

     - 点击左侧活动栏最上方的资源管理器图标（文件夹图标）
     - 或者按 `Cmd + Shift + E` (macOS) 或 `Ctrl + Shift + E` (Windows/Linux)

  3. **查找 Calendar 视图**：

     - 在资源管理器侧边栏中向下滚动
     - Calendar 视图应该在资源管理器下方
     - 如果还是看不到，尝试：
       - 按 `Cmd + Shift + P` 打开命令面板
       - 输入 `View: Show Calendar` 或 `Calendar: Focus Calendar View`
       - 或者右键点击资源管理器标题栏，查看是否有 Calendar 选项

  4. **检查扩展是否激活**：
     - 查看 VSCode 输出面板：`View` -> `Output`
     - 在输出面板的下拉菜单中选择 "Log (Extension Host)"
     - 应该能看到 "Calendar extension is now active!" 的日志
     - 如果看到 "Calendar view is being resolved"，说明视图正在加载

**Q: 扩展没有加载？**

- A: 检查：
  1. 是否在 VSCode 中打开了正确的插件文件夹
  2. 是否已安装依赖：`npm install`
  3. 查看 VSCode 的输出面板（`View` -> `Output`）查看错误信息

**Q: 打包时提示缺少 publisher？**

- A: 在 `package.json` 中添加 `publisher` 字段，或使用 `--publisher` 参数：
  ```bash
  vsce package --publisher your-publisher-name
  ```

**Q: 打包时提示文件过大？**

- A: 检查 `.vscodeignore` 文件，确保排除了不必要的文件（如 `node_modules`、`.git` 等）。

**Q: 在 Cursor 中安装后无法使用？**

- A: 确保 `package.json` 中的 `engines.vscode` 版本兼容。Cursor 通常支持 VSCode 1.60.0+ 的扩展。

**Q: 如何更新已安装的扩展？**

- A: 重新打包新版本，然后：
  - 卸载旧版本
  - 安装新版本的 `.vsix` 文件
  - 或使用 `--force` 参数强制安装：`code --install-extension vscode-calendar-0.0.1.vsix --force`

**Q: 如何卸载 Calendar 扩展？**

- A: 根据安装方式选择卸载方法：

  **方法一：通过扩展视图卸载（推荐）**

  1. **在 VSCode 中**：

     - 按 `Cmd + Shift + X` (macOS) 或 `Ctrl + Shift + X` (Windows/Linux) 打开扩展视图
     - 在搜索框中输入 "Calendar"
     - 找到 "Calendar" 扩展，点击右侧的齿轮图标（⚙️）
     - 选择 "Uninstall"
     - 重新加载窗口：`Cmd + Shift + P` -> `Developer: Reload Window`

  2. **在 Cursor 中**：
     - 按 `Cmd + Shift + X` (macOS) 或 `Ctrl + Shift + X` (Windows/Linux) 打开扩展视图
     - 在搜索框中输入 "Calendar"
     - 找到 "Calendar" 扩展，点击右侧的齿轮图标（⚙️）
     - 选择 "Uninstall"
     - 重新加载窗口（如果需要）

  **方法二：通过命令面板卸载**

  1. 按 `Cmd + Shift + P` (macOS) 或 `Ctrl + Shift + P` (Windows/Linux) 打开命令面板
  2. 输入 `Extensions: Show Installed Extensions`
  3. 找到 "Calendar" 扩展，点击卸载按钮
  4. 重新加载窗口

  **方法三：使用命令行卸载**

  **VSCode**：

  ```bash
  code --uninstall-extension your-publisher-name.vscode-calendar
  ```

  或使用扩展 ID：

  ```bash
  code --uninstall-extension vscode-calendar
  ```

  **Cursor**：

  ```bash
  cursor --uninstall-extension your-publisher-name.vscode-calendar
  ```

  或使用扩展 ID：

  ```bash
  cursor --uninstall-extension vscode-calendar
  ```

  **查看已安装的扩展**：

  ```bash
  # VSCode
  code --list-extensions

  # Cursor
  cursor --list-extensions
  ```

  **方法四：手动删除（如果上述方法无效）**

  1. **关闭编辑器**（VSCode 或 Cursor）

  2. **删除扩展目录**：

     **macOS**：

     ```bash
     rm -rf ~/.vscode/extensions/your-publisher-name.vscode-calendar-*
     ```

     **Windows**：

     ```powershell
     Remove-Item -Recurse -Force "$env:USERPROFILE\.vscode\extensions\your-publisher-name.vscode-calendar-*"
     ```

     **Linux**：

     ```bash
     rm -rf ~/.vscode/extensions/your-publisher-name.vscode-calendar-*
     ```

  3. **对于 Cursor**，路径类似：
     ```bash
     # macOS
     rm -rf ~/.cursor/extensions/your-publisher-name.vscode-calendar-*
     ```

  **注意**：`your-publisher-name` 需要替换为你在 `package.json` 中设置的 publisher 名称。

  **开发模式卸载**：

  如果你是在开发模式下运行（按 F5 启动扩展开发宿主窗口），只需：

  - 关闭扩展开发宿主窗口
  - 停止调试（在原始 VSCode 窗口中停止调试会话）

## 许可证

MIT

# VSCode Calendar 扩展代码解释

本文档详细解释 VSCode Calendar 扩展的代码结构和实现原理。

## 目录结构

```
vscode-calendar/
├── extension.js          # 扩展主入口文件（Node.js 环境）
├── package.json          # 扩展配置文件
├── media/
│   ├── calendar.js       # 日历前端逻辑（浏览器环境）
│   └── calendar.css      # 日历样式文件
└── README.md            # 说明文档
```

## 1. package.json - 扩展配置

### 核心配置说明

```json
{
  "main": "./extension.js", // 扩展入口文件
  "activationEvents": ["onStartupFinished"], // 激活时机：VSCode 启动完成后
  "engines": {
    "vscode": "^1.60.0" // 最低支持的 VSCode 版本
  }
}
```

### 视图注册

```json
"views": {
  "explorer": [                       // 在资源管理器侧边栏注册视图
    {
      "id": "calendarView",           // 视图 ID，用于代码中引用
      "name": "Calendar",             // 显示名称
      "type": "webview",              // 视图类型：WebView
      "when": "true"                  // 显示条件：始终显示
    }
  ]
}
```

**说明**：

- `explorer` 表示视图注册在资源管理器侧边栏
- `id` 必须与代码中注册的视图 ID 一致
- `type: "webview"` 表示这是一个 WebView 视图，可以加载 HTML/CSS/JS

### 命令注册

```json
"commands": [
  {
    "command": "calendar.refresh",     // 命令 ID
    "title": "Refresh Calendar",      // 命令显示名称
    "icon": "$(refresh)"              // 图标（使用 Codicons）
  }
]
```

**说明**：

- 命令可以在命令面板中调用
- 图标使用 VSCode 内置的 Codicons 图标集

### 菜单配置

```json
"menus": {
  "view/title": [                     // 视图标题栏菜单
    {
      "command": "calendar.refresh",  // 绑定的命令
      "when": "view == calendarView", // 显示条件
      "group": "navigation"            // 菜单组
    }
  ]
}
```

**说明**：

- `view/title` 表示在视图标题栏添加按钮
- `when` 条件确保只在 Calendar 视图中显示

---

## 2. extension.js - 扩展主入口

### 架构说明

扩展使用 **WebView** 技术实现日历界面：

- **后端（Node.js）**：`extension.js` 运行在 Node.js 环境，负责注册视图和命令
- **前端（浏览器）**：`media/calendar.js` 运行在 WebView 中，负责日历渲染和交互

### activate() 函数 - 扩展激活

```javascript
function activate(context) {
  // 1. 创建视图提供者
  const provider = new CalendarViewProvider(context.extensionUri);

  // 2. 注册 WebView 视图提供者
  context.subscriptions.push(vscode.window.registerWebviewViewProvider("calendarView", provider));

  // 3. 注册命令
  // ...
}
```

**关键点**：

- `context.extensionUri`：扩展的 URI，用于加载资源文件
- `registerWebviewViewProvider`：将视图 ID 与提供者绑定
- `context.subscriptions`：管理扩展生命周期，自动清理资源

### CalendarViewProvider 类

#### 构造函数

```javascript
constructor(_extensionUri) {
  this._extensionUri = _extensionUri;  // 扩展 URI，用于构建资源路径
  this._view = null;                   // WebView 视图实例
}
```

#### resolveWebviewView() - 视图解析

当 VSCode 需要显示视图时调用此方法：

```javascript
resolveWebviewView(webviewView, context, _token) {
  // 1. 配置 WebView 选项
  webviewView.webview.options = {
    enableScripts: true,                    // 启用 JavaScript
    localResourceRoots: [this._extensionUri] // 允许加载的资源根目录
  };

  // 2. 设置 HTML 内容
  webviewView.webview.html = this._getHtmlForWebview(webviewView.webview);

  // 3. 监听来自 WebView 的消息
  webviewView.webview.onDidReceiveMessage((message) => {
    // 处理消息...
  });
}
```

**关键点**：

- `enableScripts: true`：允许在 WebView 中执行 JavaScript
- `localResourceRoots`：安全限制，只允许加载指定目录的资源
- `onDidReceiveMessage`：双向通信机制，WebView 可以发送消息给扩展

#### \_getHtmlForWebview() - 生成 HTML

```javascript
_getHtmlForWebview(webview) {
  // 1. 将本地文件路径转换为 WebView 可访问的 URI
  const scriptUri = webview.asWebviewUri(
    vscode.Uri.joinPath(this._extensionUri, "media", "calendar.js")
  );
  const styleUri = webview.asWebviewUri(
    vscode.Uri.joinPath(this._extensionUri, "media", "calendar.css")
  );

  // 2. 返回 HTML 字符串
  return `<!DOCTYPE html>...`;
}
```

**关键点**：

- `asWebviewUri()`：将本地文件路径转换为 WebView 可访问的特殊 URI（`vscode-webview://`）
- 这是 VSCode 的安全机制，防止直接访问文件系统

#### refresh() - 刷新视图

```javascript
refresh() {
  if (this._view) {
    this._view.webview.html = this._getHtmlForWebview(this._view.webview);
  }
}
```

**说明**：重新生成 HTML 内容，实现刷新功能。

---

## 3. media/calendar.js - 日历前端逻辑

### 架构说明

这个文件运行在 **WebView 的浏览器环境**中，使用标准的 DOM API。

### 初始化

```javascript
(function () {
  const vscode = acquireVsCodeApi(); // 获取 VSCode API，用于与扩展通信

  let currentYear = new Date().getFullYear();
  let currentMonth = new Date().getMonth();

  // 初始化
  initCalendar();
})();
```

**关键点**：

- `acquireVsCodeApi()`：VSCode 提供的全局函数，获取通信 API
- 使用 IIFE（立即执行函数）避免污染全局作用域

### renderCalendar() - 渲染日历

这是核心渲染函数：

```javascript
function renderCalendar() {
  // 1. 设置月份标题
  monthYearElement.textContent = `${currentYear}年 ${monthNames[currentMonth]}`;

  // 2. 计算日期信息
  const firstDay = new Date(currentYear, currentMonth, 1);
  const lastDay = new Date(currentYear, currentMonth + 1, 0);
  const firstDayOfWeek = firstDay.getDay(); // 0=周日, 1=周一, ...
  const daysInMonth = lastDay.getDate();

  // 3. 填充上个月的日期（补全第一行）
  for (let i = firstDayOfWeek - 1; i >= 0; i--) {
    // 创建日期元素...
  }

  // 4. 填充当月的日期
  for (let day = 1; day <= daysInMonth; day++) {
    // 创建日期元素...
  }

  // 5. 填充下个月的日期（补全最后一行，共42个格子）
  const remainingCells = 42 - totalCells;
  for (let day = 1; day <= remainingCells; day++) {
    // 创建日期元素...
  }
}
```

**算法说明**：

- 日历网格固定为 6 行 × 7 列 = 42 个格子
- 需要计算当月第一天是星期几（`firstDayOfWeek`）
- 填充上个月的日期补全第一行
- 填充下个月的日期补全最后一行

### createDayElement() - 创建日期元素

```javascript
function createDayElement(day, isOtherMonth, isToday = false) {
  // 1. 创建 DOM 元素
  const dayElement = document.createElement("div");
  dayElement.className = "day";
  dayElement.textContent = day;

  // 2. 添加样式类
  if (isOtherMonth) {
    dayElement.classList.add("other-month"); // 非当月日期样式
  }
  if (isToday) {
    dayElement.classList.add("today"); // 今天高亮
  }

  // 3. 创建工具提示（Tooltip）
  const tooltip = document.createElement("div");
  tooltip.className = "day-tooltip";

  // 4. 添加鼠标悬停事件
  if (!isOtherMonth) {
    dayElement.addEventListener("mouseenter", function () {
      // 格式化日期信息
      const dateInfo = formatDateInfo(date);
      tooltip.textContent = dateInfo;

      // 发送消息到扩展（可选）
      vscode.postMessage({
        command: "dateHover",
        date: dateStr,
        dateInfo: dateInfo,
      });
    });
  }

  return dayElement;
}
```

**关键点**：

- `vscode.postMessage()`：向扩展发送消息，实现双向通信
- 工具提示使用 CSS 控制显示/隐藏

### setupEventListeners() - 事件监听

```javascript
function setupEventListeners() {
  // 上一个月按钮
  prevBtn.addEventListener("click", () => {
    currentMonth--;
    if (currentMonth < 0) {
      currentMonth = 11; // 12月
      currentYear--;
    }
    renderCalendar(); // 重新渲染
  });

  // 下一个月按钮
  nextBtn.addEventListener("click", () => {
    currentMonth++;
    if (currentMonth > 11) {
      currentMonth = 0; // 1月
      currentYear++;
    }
    renderCalendar(); // 重新渲染
  });
}
```

**说明**：处理月份切换逻辑，注意边界情况（跨年）。

---

## 4. media/calendar.css - 样式文件

### VSCode 主题变量

```css
body {
  font-family: var(--vscode-font-family); /* 使用 VSCode 字体 */
  color: var(--vscode-foreground); /* 前景色 */
  background-color: var(--vscode-editor-background); /* 背景色 */
}
```

**关键点**：

- 使用 CSS 变量（`var(--vscode-*)`）自动适配 VSCode 主题
- 支持亮色/暗色主题切换

### 网格布局

```css
.calendar-days {
  display: grid;
  grid-template-columns: repeat(7, 1fr); /* 7 列等宽 */
  gap: 2px; /* 间距 */
}
```

**说明**：使用 CSS Grid 实现日历网格布局。

### 日期单元格

```css
.day {
  aspect-ratio: 1; /* 保持正方形 */
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: all 0.2s; /* 动画过渡 */
}

.day:hover {
  transform: scale(1.1); /* 悬停放大 */
  z-index: 10;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.2);
}
```

**说明**：

- `aspect-ratio: 1`：保持正方形
- `transform: scale(1.1)`：悬停时放大 10%
- `z-index`：确保悬停元素在上层

### 工具提示

```css
.day-tooltip {
  position: absolute;
  bottom: 100%; /* 在日期上方 */
  left: 50%;
  transform: translateX(-50%); /* 居中 */
  opacity: 0; /* 默认隐藏 */
  pointer-events: none; /* 不阻挡鼠标事件 */
}

.day:hover .day-tooltip {
  opacity: 1; /* 悬停时显示 */
}
```

**说明**：使用 CSS 实现工具提示，无需 JavaScript。

---

## 5. 通信机制

### WebView → 扩展

```javascript
// 在 calendar.js 中
vscode.postMessage({
  command: "dateHover",
  date: "2024-12-12",
  dateInfo: "2024年12月12日 星期四",
});
```

### 扩展 → WebView

```javascript
// 在 extension.js 中
webviewView.webview.postMessage({
  command: "updateCalendar",
  data: { year: 2024, month: 12 },
});
```

**说明**：双向通信机制，但当前实现只使用了 WebView → 扩展的单向通信。

---

## 6. 数据流

```
用户操作
  ↓
calendar.js (WebView)
  ↓ (DOM 事件)
更新 currentYear/currentMonth
  ↓
renderCalendar()
  ↓
createDayElement() × N
  ↓
DOM 更新
  ↓
用户看到新日历
```

---

## 7. 关键设计模式

### 1. WebView 模式

- 扩展后端（Node.js）负责注册和配置
- WebView 前端（浏览器）负责 UI 和交互
- 通过消息机制通信

### 2. 响应式设计

- 使用 CSS Grid 自适应布局
- 使用 VSCode 主题变量适配主题

### 3. 事件驱动

- DOM 事件处理用户交互
- VSCode 事件处理扩展生命周期

---

## 8. 扩展点

### 可以添加的功能

1. **日期点击事件**：

   ```javascript
   dayElement.addEventListener("click", () => {
     vscode.postMessage({ command: "dateClick", date: dateStr });
   });
   ```

2. **事件标记**：

   - 在特定日期显示标记
   - 从扩展读取事件数据

3. **主题定制**：

   - 添加配置选项
   - 自定义颜色和样式

4. **国际化**：
   - 支持多语言
   - 使用 VSCode 的国际化 API

---

## 9. 调试技巧

### 调试扩展代码（Node.js）

```javascript
console.log("Debug message"); // 输出到 "Log (Extension Host)"
```

### 调试 WebView 代码（浏览器）

1. 在 WebView 中右键 → "Inspect"
2. 打开浏览器开发者工具
3. 查看 Console、Network 等

### 查看日志

- **扩展日志**：`View` → `Output` → 选择 "Log (Extension Host)"
- **WebView 日志**：在 WebView 的开发者工具中查看

---

## 总结

这个扩展展示了 VSCode 扩展开发的核心概念：

1. **扩展注册**：通过 `package.json` 声明扩展点
2. **WebView 视图**：使用 WebView 创建自定义 UI
3. **双向通信**：扩展与 WebView 之间的消息传递
4. **主题适配**：使用 CSS 变量适配 VSCode 主题
5. **生命周期管理**：使用 `context.subscriptions` 管理资源

代码结构清晰，易于理解和扩展。

const vscode = require("vscode");
const path = require("path");

/**
 * @param {vscode.ExtensionContext} context
 */
function activate(context) {
  console.log("Calendar extension is now active!");

  // 创建日历视图
  const provider = new CalendarViewProvider(context.extensionUri);

  context.subscriptions.push(vscode.window.registerWebviewViewProvider("calendarView", provider));

  // 注册刷新命令
  const refreshCommand = vscode.commands.registerCommand("calendar.refresh", () => {
    console.log("Refresh calendar command triggered");
    provider.refresh();
  });
  context.subscriptions.push(refreshCommand);

  // 注册聚焦视图命令
  const focusCommand = vscode.commands.registerCommand("calendar.focus", async () => {
    console.log("Focus calendar view command triggered");
    await vscode.commands.executeCommand("calendarView.focus");
  });
  context.subscriptions.push(focusCommand);

  // 显示通知提示用户如何找到视图
  vscode.window.showInformationMessage('Calendar extension activated! Look for "Calendar" in the Explorer sidebar.', "Open Calendar View").then((selection) => {
    if (selection === "Open Calendar View") {
      vscode.commands.executeCommand("calendarView.focus");
    }
  });
}

class CalendarViewProvider {
  constructor(_extensionUri) {
    this._extensionUri = _extensionUri;
    this._view = null;
  }

  resolveWebviewView(webviewView, context, _token) {
    console.log("Calendar view is being resolved");
    this._view = webviewView;

    webviewView.webview.options = {
      enableScripts: true,
      localResourceRoots: [this._extensionUri],
    };

    webviewView.webview.html = this._getHtmlForWebview(webviewView.webview);

    // 当视图可见性改变时记录日志
    webviewView.onDidChangeVisibility(() => {
      console.log("Calendar view visibility changed:", webviewView.visible);
    });

    webviewView.webview.onDidReceiveMessage(
      (message) => {
        switch (message.command) {
          case "dateHover":
            // 可以在这里处理日期悬停事件
            console.log("Date hovered:", message.date);
            break;
        }
      },
      null,
      context.subscriptions
    );
  }

  refresh() {
    if (this._view) {
      this._view.webview.html = this._getHtmlForWebview(this._view.webview);
    }
  }

  _getHtmlForWebview(webview) {
    const scriptUri = webview.asWebviewUri(vscode.Uri.joinPath(this._extensionUri, "media", "calendar.js"));
    const styleUri = webview.asWebviewUri(vscode.Uri.joinPath(this._extensionUri, "media", "calendar.css"));

    return `<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <link href="${styleUri}" rel="stylesheet">
    <title>Calendar</title>
</head>
<body>
    <div class="calendar-container">
        <div class="calendar-header">
            <button id="prevMonth" class="nav-btn">‹</button>
            <h2 id="monthYear"></h2>
            <button id="nextMonth" class="nav-btn">›</button>
        </div>
        <div class="calendar-weekdays">
            <div class="weekday">日</div>
            <div class="weekday">一</div>
            <div class="weekday">二</div>
            <div class="weekday">三</div>
            <div class="weekday">四</div>
            <div class="weekday">五</div>
            <div class="weekday">六</div>
        </div>
        <div id="calendarDays" class="calendar-days"></div>
    </div>
    <script src="${scriptUri}"></script>
</body>
</html>`;
  }
}

function deactivate() {}

module.exports = {
  activate,
  deactivate,
};

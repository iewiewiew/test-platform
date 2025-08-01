<template>
  <div class="common-list-container">
    <div class="common-header-bar">
      <div class="common-search-bar">
        <el-form :inline="true" :model="searchForm" class="demo-form-inline">
          <el-form-item label="服务器名称">
            <el-input v-model="searchForm.server_name" placeholder="请输入服务器名称" clearable @input="handleInputSearch" />
          </el-form-item>
          <el-form-item label="主机地址">
            <el-input v-model="searchForm.host" placeholder="请输入主机地址" clearable @input="handleInputSearch" />
          </el-form-item>
          <el-form-item>
            <el-button @click="resetSearch">重置</el-button>
          </el-form-item>
        </el-form>
      </div>

      <div class="common-action-bar">
        <el-button type="primary" @click="showCreateDialog = true">
          <el-icon><Plus /></el-icon>
          添加服务器
        </el-button>
      </div>
    </div>

    <el-table :data="store.servers" style="width: 100%" v-loading="store.loading" :row-class-name="getRowClassName" empty-text="暂无数据">
      <el-table-column prop="id" label="ID" width="60" />
      <el-table-column prop="server_name" label="服务器名称" width="140">
        <template #default="scope">
          <el-popover placement="right" :width="320" trigger="hover" :show-after="300" popper-class="server-info-popover">
            <template #reference>
              <span class="server-name-cell">{{ scope.row.server_name }}</span>
            </template>
            <div class="server-info-popover-content">
              <div class="server-info-item">
                <span class="info-label">服务器名称：</span>
                <span class="info-value">{{ scope.row.server_name }}</span>
              </div>
              <div class="server-info-item">
                <span class="info-label">主机地址：</span>
                <span class="info-value">{{ scope.row.host }}</span>
              </div>
              <div class="server-info-item">
                <span class="info-label">端口：</span>
                <span class="info-value">{{ scope.row.port || 22 }}</span>
              </div>
              <div class="server-info-item">
                <span class="info-label">用户名：</span>
                <span class="info-value">{{ scope.row.username }}</span>
              </div>
              <div class="server-info-item" v-if="scope.row.password">
                <span class="info-label">密码：</span>
                <span class="info-value password-value">{{ maskPassword(scope.row.password) }}</span>
              </div>
              <div class="server-info-item" v-else-if="scope.row.private_key">
                <span class="info-label">认证方式：</span>
                <span class="info-value">私钥认证</span>
              </div>
              <div class="server-info-item" v-if="scope.row.password || scope.row.private_key">
                <span class="info-label">连接命令：</span>
                <span class="info-value">{{ getServerConnectionCommand(scope.row) }}</span>
              </div>
              <el-button size="small" type="primary" :icon="DocumentCopy" @click="copyAllServerInfo(scope.row)" class="copy-all-btn">复制全部信息</el-button>
            </div>
          </el-popover>
        </template>
      </el-table-column>
      <el-table-column prop="host" label="主机地址" width="120" />
      <el-table-column prop="port" label="端口" width="80" align="center" />
      <el-table-column prop="username" label="用户名" width="120" />
      <el-table-column prop="description" label="描述" show-overflow-tooltip />
      <el-table-column prop="creator_name" label="创建人" width="120" />
      <el-table-column prop="updater_name" label="更新人" width="120" />
      <el-table-column prop="created_at" label="创建时间" width="160" sortable :formatter="formatDate" />
      <el-table-column prop="updated_at" label="更新时间" width="160" sortable :formatter="formatDate" />

      <el-table-column label="操作" width="350" fixed="right">
        <template #default="scope">
          <el-button size="default" @click="openTerminalDrawer(scope.row)">连接</el-button>
          <el-button size="default" type="warning" @click="showServerInfoDrawer(scope.row)">服务器信息</el-button>
          <el-button size="default" type="primary" @click="editServer(scope.row)">编辑</el-button>
          <el-button size="default" type="danger" @click="deleteServer(scope.row)">删除</el-button>
        </template>
      </el-table-column>
    </el-table>

    <!-- 分页 -->
    <div class="pagination">
      <el-pagination
        v-model:current-page="currentPage"
        v-model:page-size="pageSize"
        :page-sizes="[10, 20, 50, 100]"
        :total="store.pagination.total"
        :background="true"
        layout="total, sizes, prev, pager, next, jumper"
        @update:current-page="handlePageChange"
        @update:page-size="handleSizeChange"
      />
    </div>

    <!-- 添加服务器对话框 -->
    <el-dialog v-model="showCreateDialog" title="添加服务器" width="600px" @close="handleCreateDialogClose">
      <el-form :model="newServer" label-width="120px" :rules="serverRules" ref="createFormRef">
        <el-form-item label="服务器名称" prop="server_name" required>
          <el-input v-model="newServer.server_name" placeholder="请输入服务器名称" />
        </el-form-item>
        <el-form-item label="主机地址" prop="host" required>
          <el-input v-model="newServer.host" placeholder="请输入主机IP或域名" />
        </el-form-item>
        <el-form-item label="端口" prop="port">
          <el-input-number v-model="newServer.port" :min="1" :max="65535" />
        </el-form-item>
        <el-form-item label="用户名" prop="username" required>
          <el-input v-model="newServer.username" placeholder="请输入用户名" />
        </el-form-item>
        <el-form-item label="密码">
          <el-input v-model="newServer.password" type="password" placeholder="请输入密码" show-password />
        </el-form-item>
        <el-form-item label="私钥">
          <el-input v-model="newServer.private_key" type="textarea" :rows="4" placeholder="请输入SSH私钥内容（cat ~/.ssh/id_rsa 如果使用私钥认证）" />
        </el-form-item>
        <el-form-item label="描述">
          <el-input v-model="newServer.description" type="textarea" placeholder="请输入服务器描述" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showCreateDialog = false" :disabled="loading">取消</el-button>
        <el-button type="primary" @click="createServer" :loading="loading">确定</el-button>
      </template>
    </el-dialog>

    <!-- 编辑服务器对话框 -->
    <el-dialog v-model="showEditDialog" title="编辑" width="600px" @close="handleEditDialogClose">
      <el-form :model="editServerForm" label-width="120px" :rules="serverRules" ref="editFormRef">
        <el-form-item label="服务器名称" prop="server_name" required>
          <el-input v-model="editServerForm.server_name" placeholder="请输入服务器名称" />
        </el-form-item>
        <el-form-item label="主机地址" prop="host" required>
          <el-input v-model="editServerForm.host" placeholder="请输入主机IP或域名" />
        </el-form-item>
        <el-form-item label="端口" prop="port">
          <el-input-number v-model="editServerForm.port" :min="1" :max="65535" />
        </el-form-item>
        <el-form-item label="用户名" prop="username" required>
          <el-input v-model="editServerForm.username" placeholder="请输入用户名" />
        </el-form-item>
        <el-form-item label="密码">
          <el-input v-model="editServerForm.password" type="password" placeholder="请输入密码（留空则不修改）" show-password />
        </el-form-item>
        <el-form-item label="私钥">
          <el-input v-model="editServerForm.private_key" type="textarea" :rows="4" placeholder="请输入SSH私钥内容（留空则不修改）" />
        </el-form-item>
        <el-form-item label="描述">
          <el-input v-model="editServerForm.description" type="textarea" placeholder="请输入服务器描述" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showEditDialog = false" :disabled="loading">取消</el-button>
        <el-button type="primary" @click="updateServer" :loading="loading">确定</el-button>
      </template>
    </el-dialog>

    <!-- 终端抽屉 -->
    <el-drawer
      v-model="terminalDrawerVisible"
      :title="`终端 - ${selectedServer?.server_name} (${selectedServer?.username}@${selectedServer?.host})`"
      size="800px"
      direction="rtl"
      destroy-on-close
      @close="handleTerminalClose"
    >
      <div class="terminal-drawer-container">
        <!-- 终端控制栏 -->
        <div class="terminal-controls">
          <div class="server-info">
            <el-tag size="small" type="info">{{ selectedServer?.server_name }}</el-tag>
            <el-tag size="small">{{ selectedServer?.username }}@{{ selectedServer?.host }}:{{ selectedServer?.port }}</el-tag>
            <el-tag size="small" :type="connectionStatus.type">{{ connectionStatus.text }}</el-tag>
          </div>
          <div class="control-buttons">
            <el-button size="small" @click="clearTerminal">
              <el-icon><Delete /></el-icon>
              清屏
            </el-button>
            <el-button size="small" @click="copyTerminalContent">
              <el-icon><DocumentCopy /></el-icon>
              复制
            </el-button>
            <el-button size="small" type="primary" @click="reconnect" :loading="connecting">
              <el-icon><Connection /></el-icon>
              重连
            </el-button>
          </div>
        </div>

        <!-- 终端内容区域 -->
        <div class="terminal-content" ref="terminalRef">
          <!-- 欢迎信息 -->
          <div v-if="showWelcome" class="welcome-message">
            <div class="welcome-line">=== Web SSH 终端 ===</div>
            <div class="welcome-line">连接到: {{ selectedServer?.server_name }} ({{ selectedServer?.username }}@{{ selectedServer?.host }})</div>
            <div class="welcome-line">输入命令并按 Enter 执行</div>
            <div class="welcome-line">使用 ↑↓ 箭头键浏览命令历史</div>
            <div class="welcome-line">输入 'help' 查看可用命令</div>
            <div class="welcome-line">----------------------------------------</div>
          </div>

          <!-- 终端输出行 -->
          <div
            v-for="(line, index) in terminalLines"
            :key="index"
            class="terminal-line"
            :class="{
              'command-line': line.type === 'command',
              'output-line': line.type === 'output',
              'error-line': line.type === 'error',
              'info-line': line.type === 'info'
            }"
          >
            <span v-if="line.type === 'command'" class="prompt">{{ line.prompt || getPrompt() }}</span>
            <span v-else-if="line.type === 'info'" class="info-prefix">[INFO]</span>
            <pre v-if="line.type === 'output' || line.type === 'error'" class="line-content">{{ line.content }}</pre>
            <span v-else class="line-content">{{ line.content }}</span>
          </div>

          <!-- 命令执行状态 -->
          <div v-if="executingCommand" class="executing-indicator">
            <span class="prompt">{{ getPrompt() }}</span>
            <span class="executing-command">{{ currentExecutingCommand }}</span>
            <span class="executing-dots">
              <span class="dot">.</span>
              <span class="dot">.</span>
              <span class="dot">.</span>
            </span>
          </div>

          <!-- 当前输入行 -->
          <div class="terminal-input-line" v-if="!executingCommand">
            <span class="prompt">{{ getPrompt() }}</span>
            <div class="input-container">
              <input
                ref="terminalInputRef"
                v-model="currentInput"
                type="text"
                class="terminal-input"
                :disabled="executingCommand"
                @keydown="handleTerminalKeydown"
                @focus="scrollToBottom"
                spellcheck="false"
              />
              <span class="cursor" :class="{ blinking: !executingCommand }">|</span>
            </div>
          </div>
        </div>

        <!-- 快速命令 -->
        <div class="quick-commands-bar">
          <div class="quick-commands-title">快捷命令:</div>
          <div class="quick-commands-list">
            <el-tag v-for="cmd in quickCommands" :key="cmd.name" class="quick-command-tag" size="small" @click="insertQuickCommand(cmd.command)">
              {{ cmd.name }}
            </el-tag>
          </div>
        </div>
      </div>
    </el-drawer>

    <!-- 服务器信息抽屉 -->
    <el-drawer v-model="serverInfoDrawerVisible" title="服务器信息" size="600px" direction="rtl" destroy-on-close @close="handleServerInfoClose">
      <div class="server-info-drawer-container" v-loading="serverInfoLoading">
        <div class="server-info-header">
          <div class="server-basic-info">
            <h3>{{ selectedServer?.server_name }}</h3>
            <p class="server-connection-info">{{ selectedServer?.username }}@{{ selectedServer?.host }}:{{ selectedServer?.port }}</p>
          </div>
          <el-button size="small" @click="refreshServerInfo" :loading="serverInfoLoading">
            <el-icon><Refresh /></el-icon>
            刷新
          </el-button>
        </div>

        <div class="server-info-content" v-if="store.serverInfo">
          <el-collapse v-model="activeCollapseItems" accordion>
            <el-collapse-item v-for="(value, key) in store.serverInfo" :key="key" :name="key" :title="getInfoTitle(key)">
              <div class="info-content">
                <pre>{{ formatServerInfoValue(value) }}</pre>
              </div>
            </el-collapse-item>
          </el-collapse>
        </div>

        <div class="server-info-empty" v-else>
          <el-empty description="暂无服务器信息">
            <el-button type="primary" @click="refreshServerInfo" :loading="serverInfoLoading">获取服务器信息</el-button>
          </el-empty>
        </div>
      </div>
    </el-drawer>
  </div>
</template>

<script setup>
import { ref, onMounted, computed, nextTick } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus, Delete, DocumentCopy, Connection, Refresh } from '@element-plus/icons-vue'
import { useLinuxInfoStore } from '@/stores/tool/linuxInfoStore'
import { formatDateTime } from '@/utils/date'

const store = useLinuxInfoStore()

// 响应式数据
const loading = ref(false)
const showCreateDialog = ref(false)
const showEditDialog = ref(false)
const terminalDrawerVisible = ref(false)
const serverInfoDrawerVisible = ref(false)
const serverInfoLoading = ref(false)
const selectedServer = ref(null)
const createFormRef = ref(null)
const editFormRef = ref(null)
const activeCollapseItems = ref([])

// 终端相关
const terminalRef = ref(null)
const terminalInputRef = ref(null)
const terminalLines = ref([])
const currentInput = ref('')
const executingCommand = ref(false)
const connecting = ref(false)
const commandHistory = ref([])
const historyIndex = ref(-1)
const showWelcome = ref(true)
const currentExecutingCommand = ref('')

// 快速命令
const quickCommands = ref([
  { name: '系统信息', command: 'uname -a' },
  { name: '磁盘空间', command: 'df -h' },
  { name: '内存使用', command: 'free -h' },
  { name: '运行进程', command: 'ps aux | head -20' },
  { name: '网络连接', command: 'netstat -tulpn' },
  { name: '服务状态', command: 'systemctl list-units --type=service' },
  { name: '当前目录', command: 'pwd' },
  { name: '目录列表', command: 'ls -la' },
  { name: '系统负载', command: 'uptime' },
  { name: '登录用户', command: 'who' }
])

// 搜索表单
const searchForm = ref({
  server_name: '',
  host: ''
})

// 分页相关
const currentPage = ref(1)
const pageSize = ref(10)

// 防抖计时器
let searchTimer = null

// 新服务器表单
const newServer = ref({
  server_name: '服务器名称示例',
  host: '127.0.0.1',
  port: 22,
  username: 'root',
  password: '',
  private_key: '',
  description: ''
})

// 编辑服务器表单
const editServerForm = ref({
  server_name: '',
  host: '',
  port: 22,
  username: '',
  password: '',
  private_key: '',
  description: ''
})

// 表单验证规则
const serverRules = {
  server_name: [{ required: true, message: '请输入服务器名称', trigger: 'blur' }],
  host: [{ required: true, message: '请输入主机地址', trigger: 'blur' }],
  username: [{ required: true, message: '请输入用户名', trigger: 'blur' }],
  port: [{ type: 'number', min: 1, max: 65535, message: '端口范围 1-65535', trigger: 'blur' }]
}

// 计算属性
const connectionStatus = computed(() => {
  if (executingCommand.value) return { type: 'warning', text: '执行中...' }
  if (connecting.value) return { type: 'warning', text: '连接中...' }
  return { type: 'success', text: '已连接' }
})

// 方法
const fetchData = async () => {
  try {
    await store.fetchServers({
      page: currentPage.value,
      per_page: pageSize.value,
      server_name: searchForm.value.server_name || undefined,
      host: searchForm.value.host || undefined
    })
  } catch (error) {
    ElMessage.error('获取服务器列表失败: ' + (error.message || '未知错误'))
  }
}

// 搜索输入防抖
const handleInputSearch = () => {
  clearTimeout(searchTimer)
  searchTimer = setTimeout(() => {
    currentPage.value = 1
    fetchData()
  }, 500)
}

// 重置搜索
const resetSearch = () => {
  searchForm.value.server_name = ''
  searchForm.value.host = ''
  currentPage.value = 1
  fetchData()
}

// 分页变化
const handlePageChange = (p) => {
  currentPage.value = p
  fetchData()
}

// 分页大小变化
const handleSizeChange = (s) => {
  pageSize.value = s
  currentPage.value = 1
  fetchData()
}

const showServerInfoDrawer = async (server) => {
  selectedServer.value = server
  serverInfoDrawerVisible.value = true
  await refreshServerInfo()
}

const refreshServerInfo = async () => {
  if (!selectedServer.value) return

  serverInfoLoading.value = true
  try {
    await store.fetchServerInfo(selectedServer.value.id)
    if (store.error) {
      ElMessage.error('获取服务器信息失败: ' + store.error)
    } else {
      // 默认展开第一个项目
      if (store.serverInfo && Object.keys(store.serverInfo).length > 0) {
        activeCollapseItems.value = Object.keys(store.serverInfo)[0]
      }
    }
  } catch (error) {
    ElMessage.error('获取服务器信息失败: ' + (error.message || '未知错误'))
  } finally {
    serverInfoLoading.value = false
  }
}

const handleServerInfoClose = () => {
  store.clearServerInfo()
  selectedServer.value = null
}

const formatServerInfoValue = (value) => {
  if (typeof value === 'string') {
    return value
  }
  return JSON.stringify(value, null, 2)
}

// 终端相关方法保持不变
const openTerminalDrawer = async (server) => {
  selectedServer.value = server
  terminalLines.value = []
  currentInput.value = ''
  commandHistory.value = []
  historyIndex.value = -1
  showWelcome.value = true
  terminalDrawerVisible.value = true

  await nextTick()
  focusTerminalInput()
  scrollToBottom()
}

const focusTerminalInput = () => {
  if (terminalInputRef.value) {
    terminalInputRef.value.focus()
  }
}

const scrollToBottom = () => {
  nextTick(() => {
    if (terminalRef.value) {
      terminalRef.value.scrollTop = terminalRef.value.scrollHeight
    }
  })
}

const getPrompt = () => {
  if (!selectedServer.value) return '$ '
  return `[${selectedServer.value.username}@${selectedServer.value.server_name}]$ `
}

const handleTerminalKeydown = async (event) => {
  switch (event.key) {
    case 'Enter':
      event.preventDefault()
      await executeCurrentCommand()
      break
    case 'ArrowUp':
      event.preventDefault()
      navigateHistory(-1)
      break
    case 'ArrowDown':
      event.preventDefault()
      navigateHistory(1)
      break
    case 'Tab':
      event.preventDefault()
      break
    case 'l':
      if (event.ctrlKey) {
        event.preventDefault()
        clearTerminal()
      }
      break
  }
}

const navigateHistory = (direction) => {
  if (commandHistory.value.length === 0) return

  if (direction === -1) {
    // 上箭头
    if (historyIndex.value < commandHistory.value.length - 1) {
      historyIndex.value++
    }
  } else {
    // 下箭头
    if (historyIndex.value > 0) {
      historyIndex.value--
    } else if (historyIndex.value === 0) {
      historyIndex.value = -1
      currentInput.value = ''
      return
    }
  }

  if (historyIndex.value >= 0) {
    currentInput.value = commandHistory.value[historyIndex.value]
  }
}

const executeCurrentCommand = async () => {
  const command = currentInput.value.trim()
  if (!command) {
    // 空命令也显示提示符
    addTerminalLine('command', '', getPrompt())
    currentInput.value = ''
    scrollToBottom()
    focusTerminalInput()
    return
  }

  // 特殊命令处理
  if (command === 'clear' || command === 'cls') {
    clearTerminal()
    currentInput.value = ''
    scrollToBottom()
    focusTerminalInput()
    return
  }

  if (command === 'exit' || command === 'quit') {
    terminalDrawerVisible.value = false
    return
  }

  if (command === 'help') {
    showHelp()
    currentInput.value = ''
    scrollToBottom()
    focusTerminalInput()
    return
  }

  // 显示执行的命令
  addTerminalLine('command', command, getPrompt())

  // 添加到历史记录
  if (commandHistory.value[0] !== command) {
    commandHistory.value.unshift(command)
    // 限制历史记录数量
    if (commandHistory.value.length > 100) {
      commandHistory.value = commandHistory.value.slice(0, 100)
    }
  }

  historyIndex.value = -1
  currentInput.value = ''
  currentExecutingCommand.value = command
  executingCommand.value = true

  scrollToBottom()

  try {
    const result = await store.executeCommand(selectedServer.value.id, command)
    console.log(result)
    // 直接显示后端返回的 output
    if (result) {
      // 将输出内容按行分割并逐行显示
      const outputLines = result.output.split('\n')
      outputLines.forEach((line) => {
        if (line.trim()) {
          addTerminalLine('output', line)
        }
      })
    }

    // 如果有错误输出也显示
    if (result && result.error) {
      const errorLines = result.error.split('\n')
      errorLines.forEach((line) => {
        if (line.trim()) {
          addTerminalLine('error', line)
        }
      })
    }

    // 显示执行状态
    const exitCode = result?.exit_status || 0
    if (exitCode === 0) {
      addTerminalLine('info', `命令执行完成 (退出码: ${exitCode})`)
    } else {
      addTerminalLine('error', `命令执行完成 (退出码: ${exitCode})`)
    }
  } catch (error) {
    addTerminalLine('error', `执行命令失败: ${error.message || '未知错误'}`)
  } finally {
    executingCommand.value = false
    currentExecutingCommand.value = ''
    scrollToBottom()
    focusTerminalInput()
  }
}

const showHelp = () => {
  addTerminalLine('info', '可用命令:')
  addTerminalLine('output', '  clear/cls        - 清空终端屏幕')
  addTerminalLine('output', '  exit/quit        - 退出终端')
  addTerminalLine('output', '  help             - 显示此帮助信息')
  addTerminalLine('output', '  ↑↓               - 浏览命令历史')
  addTerminalLine('output', '  Ctrl+L           - 清屏')
  addTerminalLine('info', '快捷命令栏提供了常用命令，点击即可插入')
}

const addTerminalLine = (type, content, prompt = '') => {
  terminalLines.value.push({
    type,
    content,
    prompt,
    timestamp: new Date()
  })
  // 显示命令后隐藏欢迎信息
  if (type === 'command' && showWelcome.value) {
    showWelcome.value = false
  }
  scrollToBottom()
}

const clearTerminal = () => {
  terminalLines.value = []
  showWelcome.value = false
}

const copyTerminalContent = async () => {
  let content = ''

  if (showWelcome.value) {
    content += '=== Web SSH 终端 ===\n'
    content += `连接到: ${selectedServer.value?.server_name} (${selectedServer.value?.username}@${selectedServer.value?.host})\n`
    content += '----------------------------------------\n'
  }

  content += terminalLines.value
    .map((line) => {
      const prefix = line.prompt || (line.type === 'info' ? '[INFO] ' : '')
      return prefix + line.content
    })
    .join('\n')

  try {
    await navigator.clipboard.writeText(content)
    ElMessage.success('终端内容已复制到剪贴板')
  } catch (err) {
    ElMessage.error('复制失败')
  }
}

const reconnect = async () => {
  connecting.value = true
  addTerminalLine('info', '重新连接服务器...')

  // 模拟重新连接
  setTimeout(() => {
    connecting.value = false
    addTerminalLine('info', '连接已恢复')
    focusTerminalInput()
  }, 1000)
}

const insertQuickCommand = (command) => {
  currentInput.value = command
  focusTerminalInput()
}

const handleTerminalClose = () => {
  terminalLines.value = []
  currentInput.value = ''
  commandHistory.value = []
  historyIndex.value = -1
  showWelcome.value = true
}

// 其他现有方法保持不变...
const formatDate = (row, column, cellValue) => {
  return cellValue ? formatDateTime(cellValue) : '-'
}

const createServer = async () => {
  if (!createFormRef.value) return

  try {
    const valid = await createFormRef.value.validate()
    if (!valid) return

    loading.value = true
    const result = await store.createServer(newServer.value)
    console.log(result)
    if (result && result.success === true) {
      ElMessage.success('服务器添加成功')
      showCreateDialog.value = false
      resetNewServer()
      await fetchData()
    } else {
      const errorMsg = result?.error || '添加服务器失败'
      ElMessage.error(errorMsg)
    }
  } catch (error) {
    if (error && error.errors) {
      ElMessage.warning('请完善表单信息')
    } else {
      ElMessage.error('添加服务器失败: ' + (error?.message || '未知错误'))
    }
  } finally {
    loading.value = false
  }
}

const resetNewServer = () => {
  newServer.value = {
    server_name: '',
    host: '',
    port: 22,
    username: '',
    password: '',
    private_key: '',
    description: ''
  }
  nextTick(() => {
    if (createFormRef.value) {
      createFormRef.value.clearValidate()
    }
  })
}

const editServer = async (server) => {
  selectedServer.value = server
  editServerForm.value = {
    server_name: server.server_name,
    host: server.host,
    port: server.port,
    username: server.username,
    password: '',
    private_key: server.private_key || '',
    description: server.description || ''
  }

  nextTick(() => {
    if (editFormRef.value) {
      editFormRef.value.clearValidate()
    }
  })

  showEditDialog.value = true
}

const updateServer = async () => {
  if (!editFormRef.value) return

  try {
    const valid = await editFormRef.value.validate()
    if (!valid) return

    loading.value = true

    const updateData = { ...editServerForm.value }
    if (!updateData.password) {
      delete updateData.password
    }
    if (!updateData.private_key) {
      delete updateData.private_key
    }

    const result = await store.updateServer(selectedServer.value.id, updateData)
    if (result) {
      ElMessage.success('服务器更新成功')
      showEditDialog.value = false
      await fetchData()
    } else {
      ElMessage.error('更新服务器失败')
    }
  } catch (error) {
    if (error && error.errors) {
      ElMessage.warning('请完善表单信息')
    } else {
      ElMessage.error('更新服务器失败: ' + (error?.message || '未知错误'))
    }
  } finally {
    loading.value = false
  }
}

const deleteServer = async (server) => {
  try {
    await ElMessageBox.confirm(`确定要删除服务器 "${server.server_name}" 吗？`, '删除确认', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })

    loading.value = true
    const success = await store.deleteServer(server.id)
    if (success) {
      ElMessage.success('服务器删除成功')
      await fetchData()
    } else {
      ElMessage.error('删除服务器失败: ' + (store.error || '未知错误'))
    }
  } catch (error) {
    if (error === 'cancel' || error === 'close') {
      ElMessage.info('已取消删除')
    } else {
      ElMessage.error('删除操作失败: ' + (error.message || '未知错误'))
    }
  } finally {
    loading.value = false
  }
}

const getInfoTitle = (key) => {
  const titles = {
    hostname: '主机名',
    os_info: '系统信息',
    kernel: '内核版本',
    uptime: '运行时间',
    memory: '内存信息',
    disk: '磁盘信息',
    cpu_info: 'CPU信息'
  }
  return titles[key] || key
}

const handleCreateDialogClose = () => {
  resetNewServer()
}

const handleEditDialogClose = () => {
  if (editFormRef.value) {
    editFormRef.value.clearValidate()
  }
}

// 生成服务器连接命令
const getServerConnectionCommand = (server) => {
  const host = server.host || 'localhost'
  const port = server.port || 22
  const username = server.username || ''
  const password = server.password || ''
  const hasPrivateKey = !!server.private_key

  // 如果有密码，使用密码连接
  if (password) {
    // 使用 sshpass 连接（有密码的情况）
    // 格式: sshpass -p '密码' ssh -t 用户名@主机
    if (port === 22) {
      return `sshpass -p '${password}' ssh -t ${username}@${host}`
    } else {
      return `sshpass -p '${password}' ssh -t -p ${port} ${username}@${host}`
    }
  }

  // 如果是私钥验证，使用 password 作为占位符
  if (hasPrivateKey) {
    if (port === 22) {
      return `sshpass -p 'password' ssh -t ${username}@${host}`
    } else {
      return `sshpass -p 'password' ssh -t -p ${port} ${username}@${host}`
    }
  }

  // 默认情况（无密码也无私钥）
  if (port === 22) {
    return `ssh -t ${username}@${host}`
  } else {
    return `ssh -t -p ${port} ${username}@${host}`
  }
}

// 复制相关方法
const copyAllServerInfo = async (server) => {
  const info = [`服务器名称：${server.server_name}`, `主机地址：${server.host}`, `端口：${server.port || 22}`, `用户名：${server.username}`]

  if (server.password) {
    info.push(`密码：${server.password}`)
  } else if (server.private_key) {
    info.push('认证方式：私钥认证')
  }

  if (server.description) {
    info.push(`描述：${server.description}`)
  }

  // 添加服务器连接命令
  info.push('')
  info.push(`服务器连接：${getServerConnectionCommand(server)}`)

  const infoText = info.join('\n')

  try {
    await navigator.clipboard.writeText(infoText)
    ElMessage.success('服务器信息已复制到剪贴板')
  } catch (err) {
    ElMessage.error('复制失败，请手动复制')
  }
}

const maskPassword = (password) => {
  if (!password) return ''
  return '•'.repeat(Math.min(password.length, 12))
}

const getRowClassName = ({ row, rowIndex }) => {
  return 'server-info-row'
}

// 生命周期
onMounted(() => {
  fetchData()
})
</script>

<style scoped>
/* 组件特有样式：搜索栏最小宽度 */
.common-search-bar {
  min-width: 400px;
}

/* 服务器名称单元格样式 */
.server-name-cell {
  cursor: pointer;
  color: #1890ff;
  transition: color 0.2s;
}

.server-name-cell:hover {
  color: #40a9ff;
  text-decoration: underline;
}

/* 服务器信息行样式 */
:deep(.server-info-row) {
  cursor: pointer;
}

:deep(.server-info-row:hover) {
  background-color: #f5f7fa;
}

.pagination {
  padding: 16px;
  display: flex;
  justify-content: flex-end;
  border-top: 1px solid #ebeef5;
  flex-shrink: 0;
}
</style>

<style>
/* 服务器信息 Popover 全局样式 */
.server-info-popover {
  padding: 0 !important;
  border-radius: 8px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}

.server-info-popover-content {
  padding: 16px;
  min-width: 280px;
}

.server-info-title {
  font-size: 16px;
  font-weight: 600;
  color: #303133;
  margin-bottom: 16px;
  padding-bottom: 12px;
  border-bottom: 1px solid #e4e7ed;
}

.server-info-item {
  display: flex;
  align-items: center;
  margin-bottom: 12px;
  padding: 8px;
  border-radius: 4px;
  transition: background-color 0.2s;
}

.server-info-item:hover {
  background-color: #f5f7fa;
}

.info-label {
  font-size: 13px;
  color: #909399;
  min-width: 80px;
  margin-right: 8px;
  flex-shrink: 0;
}

.info-value {
  font-size: 13px;
  color: #303133;
  font-weight: 500;
  flex: 1;
  word-break: break-all;
}

.password-value {
  font-family: 'Monaco', 'Menlo', 'Ubuntu Mono', monospace;
  letter-spacing: 2px;
}

.server-info-divider {
  height: 1px;
  background-color: #e4e7ed;
  margin: 12px 0;
}

.copy-all-btn {
  width: 100%;
  margin-top: 8px;
}
</style>

<style scoped>
/* 服务器信息抽屉样式 */
.server-info-drawer-container {
  height: 100%;
  display: flex;
  flex-direction: column;
  padding: 0;
}

.server-info-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  padding: 1px 24px 0;
  margin-bottom: 16px;
}

.server-basic-info h3 {
  margin: 0 0 8px 0;
  color: #303133;
  font-size: 18px;
}

.server-connection-info {
  margin: 0;
  color: #909399;
  font-size: 14px;
}

.server-info-content {
  flex: 1;
  overflow-y: auto;
  padding: 0 24px 20px;
}

.info-content {
  background: #f8f9fa;
  border-radius: 4px;
  padding: 12px;
  max-height: 400px;
  overflow-y: auto;
}

.info-content pre {
  margin: 0;
  white-space: pre-wrap;
  word-break: break-all;
  font-family: 'Monaco', 'Menlo', 'Ubuntu Mono', monospace;
  font-size: 12px;
  line-height: 1.4;
  color: #333;
}

.server-info-empty {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 40px 24px;
}

/* 终端样式 */
.terminal-drawer-container {
  height: 100%;
  display: flex;
  flex-direction: column;
  background: #1e1e1e;
  color: #f0f0f0;
  font-family: 'Monaco', 'Menlo', 'Ubuntu Mono', monospace;
  font-size: 14px;
  line-height: 1.4;
}

.terminal-controls {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 16px;
  background: #2d2d2d;
  border-bottom: 1px solid #404040;
  flex-shrink: 0;
}

.server-info {
  display: flex;
  gap: 8px;
  align-items: center;
}

.control-buttons {
  display: flex;
  gap: 8px;
}

.terminal-content {
  flex: 1;
  padding: 16px;
  overflow-y: auto;
  background: #1e1e1e;
  min-height: 0;
}

.welcome-message {
  color: #6796e6;
  margin-bottom: 16px;
}

.welcome-line {
  margin-bottom: 4px;
}

.terminal-line {
  margin-bottom: 4px;
  word-break: break-all;
}

.command-line {
  color: #f0f0f0;
}

.output-line {
  color: #d4d4d4;
}

.error-line {
  color: #f44747;
}

.info-line {
  color: #6796e6;
}

.prompt {
  color: #4ec9b0;
  font-weight: bold;
  margin-right: 8px;
  user-select: none;
}

.info-prefix {
  color: #6796e6;
  font-weight: bold;
  margin-right: 8px;
  user-select: none;
}

.line-content {
  white-space: pre-wrap;
  font-family: 'Monaco', 'Menlo', 'Ubuntu Mono', monospace;
  margin: 0;
  padding: 0;
}

.executing-indicator {
  display: flex;
  align-items: center;
  color: #ffcc02;
  margin-bottom: 8px;
}

.executing-command {
  margin: 0 4px;
}

.executing-dots {
  display: inline-flex;
}

.dot {
  animation: dotPulse 1.5s infinite;
}

.dot:nth-child(2) {
  animation-delay: 0.2s;
}

.dot:nth-child(3) {
  animation-delay: 0.4s;
}

@keyframes dotPulse {
  0%,
  20% {
    opacity: 0;
  }
  50% {
    opacity: 1;
  }
  100% {
    opacity: 0;
  }
}

.terminal-input-line {
  display: flex;
  align-items: center;
  margin-top: 8px;
}

.input-container {
  position: relative;
  flex: 1;
  display: flex;
  align-items: center;
}

.terminal-input {
  flex: 1;
  background: transparent;
  border: none;
  outline: none;
  color: #f0f0f0;
  font-family: 'Monaco', 'Menlo', 'Ubuntu Mono', monospace;
  font-size: 14px;
  padding: 0;
  margin: 0;
  caret-color: #4ec9b0;
}

.cursor {
  color: #4ec9b0;
  margin-left: 2px;
  font-weight: bold;
}

.cursor.blinking {
  animation: blink 1s infinite;
}

@keyframes blink {
  0%,
  50% {
    opacity: 1;
  }
  51%,
  100% {
    opacity: 0;
  }
}

.quick-commands-bar {
  padding: 12px 16px;
  background: #2d2d2d;
  border-top: 1px solid #404040;
  flex-shrink: 0;
}

.quick-commands-title {
  color: #858585;
  font-size: 12px;
  margin-bottom: 8px;
}

.quick-commands-list {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
}

.quick-command-tag {
  cursor: pointer;
  transition: all 0.2s;
  background: #404040;
  border: none;
  color: #d4d4d4;
}

.quick-command-tag:hover {
  background: #4ec9b0;
  color: #1e1e1e;
  transform: translateY(-1px);
}

/* 滚动条样式 */
.terminal-content::-webkit-scrollbar {
  width: 8px;
}

.terminal-content::-webkit-scrollbar-track {
  background: #2d2d2d;
}

.terminal-content::-webkit-scrollbar-thumb {
  background: #404040;
  border-radius: 4px;
}

.terminal-content::-webkit-scrollbar-thumb:hover {
  background: #4a4a4a;
}

.server-info-content::-webkit-scrollbar {
  width: 6px;
}

.server-info-content::-webkit-scrollbar-track {
  background: #f5f5f5;
}

.server-info-content::-webkit-scrollbar-thumb {
  background: #c0c4cc;
  border-radius: 3px;
}

.server-info-content::-webkit-scrollbar-thumb:hover {
  background: #909399;
}

@media (max-width: 768px) {
  /* 公共响应式样式已在 common.css 中统一处理 */

  .common-search-bar {
    min-width: auto;
  }

  :deep(.el-drawer) {
    width: 100% !important;
  }

  .terminal-controls {
    flex-direction: column;
    gap: 12px;
    align-items: flex-start;
  }

  .control-buttons {
    width: 100%;
    justify-content: flex-end;
  }

  .quick-commands-list {
    justify-content: center;
  }

  .server-info-header {
    flex-direction: column;
    gap: 12px;
    align-items: flex-start;
  }
}
</style>

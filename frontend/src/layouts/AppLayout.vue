<template>
  <div class="app-container">
    <!-- 左侧导航栏 -->
    <div class="sidebar">
      <div class="logo-container">
        <div class="logo">
          Test
          <span class="logo-highlight">Platform</span>
        </div>
        <div class="logo-subtitle">测试平台</div>
      </div>

      <el-menu :default-active="activeMenu" router class="sidebar-menu" background-color="#001529" text-color="#b7bdc3" active-text-color="#ffffff">
        <!-- 工作台 -->
        <el-menu-item index="/dashboard" route="/dashboard">
          <el-icon><DataBoard /></el-icon>
          <span>我的工作台</span>
        </el-menu-item>

        <el-menu-divider />

        <!-- 自动化测试 -->
        <el-sub-menu index="automation-test">
          <template #title>
            <el-icon><Document /></el-icon>
            <span>自动化测试</span>
          </template>
          <el-menu-item index="/test-cases" route="/test-cases">
            <span>测试用例</span>
          </el-menu-item>
          <el-menu-item index="/test-reports" route="/test-reports">
            <span>测试报告</span>
          </el-menu-item>
          <el-menu-item index="/test-environments" route="/test-environments">
            <span>测试环境</span>
          </el-menu-item>
          <el-menu-item index="/business" route="/business">
            <span>通用业务</span>
          </el-menu-item>
        </el-sub-menu>

        <!-- 开发工具 -->
        <el-sub-menu index="dev-tools">
          <template #title>
            <el-icon><Connection /></el-icon>
            <span>测试工具</span>
          </template>
          <el-menu-item index="/api-tree" route="/api-tree">
            <el-icon><Connection /></el-icon>
            <span>HTTP接口</span>
          </el-menu-item>
          <el-menu-item index="/mock-list" route="/mock-list">
            <el-icon><icon-menu /></el-icon>
            <span>Mock列表</span>
          </el-menu-item>
          <el-menu-item index="/mock-data" route="/mock-data">
            <el-icon><Tools /></el-icon>
            <span>造数管理</span>
          </el-menu-item>
          <el-menu-item index="/script-management" route="/script-management">
            <el-icon><Document /></el-icon>
            <span>脚本管理</span>
          </el-menu-item>
          <el-menu-item index="/tools/mcp" route="/tools/mcp">
            <el-icon><Connection /></el-icon>
            <span>MCP工具</span>
          </el-menu-item>
          <el-menu-item index="/tools/image-bed" route="/tools/image-bed">
            <el-icon><Picture /></el-icon>
            <span>图床管理</span>
          </el-menu-item>
        </el-sub-menu>

        <!-- 通用工具集 -->
        <el-sub-menu index="tools-management">
          <template #title>
            <el-icon><Tools /></el-icon>
            <span>通用工具集</span>
          </template>
          <el-menu-item index="/tools/encode-decode" route="/tools/encode-decode">
            <span>编码/解码</span>
          </el-menu-item>
          <el-menu-item index="/tools/format-convert" route="/tools/format-convert">
            <span>格式转换</span>
          </el-menu-item>
          <el-menu-item index="/tools/encrypt-decrypt" route="/tools/encrypt-decrypt">
            <span>加密/解密</span>
          </el-menu-item>
          <el-menu-item index="/tools/text-process" route="/tools/text-process">
            <span>文本处理</span>
          </el-menu-item>
        </el-sub-menu>

        <!-- 数据库管理 -->
        <el-sub-menu index="sql-management">
          <template #title>
            <el-icon><SetUp /></el-icon>
            <span>数据库管理</span>
          </template>
          <el-menu-item index="/sql-tool-box/database-info" route="/sql-tool-box/database-info">
            <el-icon><DataBoard /></el-icon>
            <span>数据库信息</span>
          </el-menu-item>
          <el-menu-item index="/sql-tool-box/redis" route="/sql-tool-box/redis">
            <el-icon><Connection /></el-icon>
            <span>Redis 数据库</span>
          </el-menu-item>
          <el-menu-item index="/sql-tool-box/database-conn" route="/sql-tool-box/database-conn">
            <span>数据库连接</span>
          </el-menu-item>
          <el-menu-item index="/sql-tool-box" route="/sql-tool-box">
            <span>SQL模板库</span>
          </el-menu-item>
        </el-sub-menu>

        <!-- 环境管理 -->
        <el-sub-menu index="environment-management">
          <template #title>
            <el-icon><Monitor /></el-icon>
            <span>环境管理</span>
          </template>
          <el-menu-item index="/environment-list" route="/environment-list">
            <el-icon><Monitor /></el-icon>
            <span>环境列表</span>
          </el-menu-item>
          <el-menu-item index="/linux-info" route="/linux-info">
            <el-icon><Monitor /></el-icon>
            <span>服务器信息</span>
          </el-menu-item>
          <el-menu-item index="/environment-dashboard" route="/environment-dashboard">
            <el-icon><DataBoard /></el-icon>
            <span>环境资源</span>
          </el-menu-item>
          <el-menu-item index="/environment-health-scan" route="/environment-health-scan">
            <el-icon><Refresh /></el-icon>
            <span>环境健康扫描</span>
          </el-menu-item>
        </el-sub-menu>

        <!-- 系统管理 -->
        <el-sub-menu index="system-management">
          <template #title>
            <el-icon><Setting /></el-icon>
            <span>系统管理</span>
          </template>
          <el-menu-item index="/project-list" route="/project-list">
            <span>项目列表</span>
          </el-menu-item>
          <el-menu-item index="/users" route="/users">
            <span>用户列表</span>
          </el-menu-item>
          <el-menu-item index="/roles" route="/roles">
            <span>角色列表</span>
          </el-menu-item>
          <el-menu-item index="/operation-logs" route="/operation-logs">
            <span>操作日志</span>
          </el-menu-item>
          <el-menu-item index="/notifications" route="/notifications">
            <span>消息通知</span>
          </el-menu-item>
        </el-sub-menu>

        <!-- 示例模块 -->
        <el-sub-menu index="example-management">
          <template #title>
            <el-icon><Document /></el-icon>
            <span>示例模块</span>
          </template>
          <el-menu-item index="/example-list" route="/example-list">
            <span>示例列表</span>
          </el-menu-item>
        </el-sub-menu>

        <!-- 常用文档 -->
        <el-menu-item index="/docs" route="/docs">
          <el-icon><Document /></el-icon>
          <span>常用文档</span>
        </el-menu-item>
      </el-menu>
    </div>

    <!-- 右侧内容区 -->
    <div class="main-container">
      <!-- 顶部导航栏 -->
      <div class="top-navbar">
        <div class="navbar-left">
          <el-breadcrumb separator="/">
            <el-breadcrumb-item :to="{ path: '/' }">首页</el-breadcrumb-item>
            <el-breadcrumb-item>{{ pageTitle }}</el-breadcrumb-item>
          </el-breadcrumb>
        </div>

        <div class="navbar-right">
          <!-- 暗黑模式切换按钮 -->
          <el-tooltip :content="themeStore.isDark ? '切换到浅色模式' : '切换到暗黑模式'" placement="bottom">
            <el-button :icon="themeStore.isDark ? Sunny : Moon" circle class="theme-toggle-btn" @click="themeStore.toggleTheme()" />
          </el-tooltip>

          <!-- GitHub 源码链接 -->
          <a href="https://github.com/iewiewiew/test-platform" target="_blank" rel="noopener noreferrer" class="github-link">源码</a>

          <el-dropdown @command="handleCommand" class="user-dropdown">
            <span class="user-info">
              <el-avatar :size="32" class="user-avatar" :src="avatarUrl">
                {{ avatarAbbreviation }}
              </el-avatar>
              <span class="user-name">{{ username }}</span>
              <el-icon class="dropdown-icon"><arrow-down /></el-icon>
            </span>
            <template #dropdown>
              <el-dropdown-menu>
                <el-dropdown-item command="profile">
                  <el-icon><User /></el-icon>
                  个人资料
                </el-dropdown-item>
                <el-dropdown-item divided command="logout">
                  <el-icon><SwitchButton /></el-icon>
                  退出登录
                </el-dropdown-item>
              </el-dropdown-menu>
            </template>
          </el-dropdown>
        </div>
      </div>

      <!-- 标签页容器 -->
      <div class="tabs-container" v-if="tabs.length > 0">
        <div class="tabs-wrapper" ref="tabsWrapperRef">
          <div
            v-for="tab in tabs"
            :key="tab.path"
            :class="['tab-item', { 'is-active': tab.path === route.path }]"
            @click="handleTabClick(tab.path)"
            @contextmenu.prevent="handleTabContextMenu($event, tab)"
          >
            <span class="tab-title">{{ tab.title }}</span>
            <el-icon class="tab-close" @click.stop="handleCloseTab(tab.path)" v-if="tabs.length > 1">
              <Close />
            </el-icon>
          </div>
        </div>
        <el-dropdown v-if="tabs.length > 1" @command="handleTabDropdownCommand" trigger="click" class="tabs-dropdown">
          <el-icon class="dropdown-trigger"><MoreFilled /></el-icon>
          <template #dropdown>
            <el-dropdown-menu>
              <el-dropdown-item command="close-others">关闭其他</el-dropdown-item>
              <el-dropdown-item command="close-left">关闭左侧</el-dropdown-item>
              <el-dropdown-item command="close-right">关闭右侧</el-dropdown-item>
              <el-dropdown-item divided command="close-all">关闭所有</el-dropdown-item>
            </el-dropdown-menu>
          </template>
        </el-dropdown>
      </div>

      <!-- 右键菜单 -->
      <div v-if="contextMenuVisible" class="context-menu" :style="{ left: contextMenuPosition.x + 'px', top: contextMenuPosition.y + 'px' }" @click.stop>
        <div class="context-menu-item" @click="handleContextMenuClose">关闭</div>
        <div class="context-menu-item" @click="handleContextMenuCloseOthers">关闭其他</div>
        <div class="context-menu-item" @click="handleContextMenuCloseLeft">关闭左侧</div>
        <div class="context-menu-item" @click="handleContextMenuCloseRight">关闭右侧</div>
        <div class="context-menu-divider"></div>
        <div class="context-menu-item" @click="handleContextMenuCloseAll">关闭所有</div>
      </div>

      <!-- 页面内容 -->
      <div class="content">
        <router-view />
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed, ref, onMounted, watch, nextTick } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { useAuthStore } from '@/stores/auth/authStore'
import { useThemeStore } from '@/stores/theme/themeStore'
import apiClient from '@/utils/request'
import {
  Document,
  DataBoard,
  Menu as IconMenu,
  FolderOpened,
  Setting,
  Connection,
  Tools,
  Monitor,
  SetUp,
  User,
  ArrowDown,
  SwitchButton,
  Close,
  MoreFilled,
  Moon,
  Sunny,
  Key,
  Refresh,
  Picture
} from '@element-plus/icons-vue'

const route = useRoute()
const router = useRouter()
const authStore = useAuthStore()
const themeStore = useThemeStore()

// 用户信息
const username = computed(() => {
  return authStore.user?.username || authStore.user?.name || '用户'
})

// 生成头像缩写（仅首字母）
const getAvatarAbbreviation = (name) => {
  if (!name) return 'U'

  // 去除首尾空格后取首字母
  const trimmedName = name.trim()
  if (trimmedName.length === 0) return 'U'

  // 判断是否为中文（包含中文字符）
  const hasChinese = /[\u4e00-\u9fa5]/.test(trimmedName)

  if (hasChinese) {
    // 中文：取第一个字符
    return trimmedName.charAt(0)
  } else {
    // 英文：取首字母（大写）
    return trimmedName.charAt(0).toUpperCase()
  }
}

const avatarAbbreviation = computed(() => {
  return getAvatarAbbreviation(username.value)
})

// 头像URL（用户未上传则为空，使用字母头像）
const avatarUrl = computed(() => {
  const url = authStore.user?.avatar_url
  if (!url) return ''
  const origin = (apiClient.defaults.baseURL || '').replace(/\/?api\/?$/i, '')
  return `${origin}${url}`
})

// 检查登录状态
const checkAuth = () => {
  // 从 authStore 检查登录状态
  if (!authStore.isAuthenticated || !authStore.user) {
    router.push('/login')
  }
}

// 页面标题映射 - 更新以包含新的路由
const pageTitles = {
  '/dashboard': '我的工作台',
  '/example-list': '示例列表',
  '/users': '用户列表',
  '/roles': '角色列表',
  '/mock-list': 'Mock列表',
  '/project-list': '项目列表',
  '/environment-list': '环境列表',
  '/mock-data': '造数管理',
  '/api-tree': 'HTTP接口',
  '/linux-info': '服务器信息',
  '/environment-health-scan': '环境健康扫描',
  '/sql-tool-box': 'SQL模板库',
  '/sql-tool-box/database-info': '数据库信息',
  '/sql-tool-box/redis': 'Redis 数据库',
  '/sql-tool-box/database-conn': '数据库连接',
  '/script-management': '脚本管理',
  '/environment-dashboard': '环境资源',
  '/tools': '通用工具集',
  '/tools/encode-decode': '编码/解码',
  '/tools/format-convert': '格式转换',
  '/tools/encrypt-decrypt': '加密/解密',
  '/tools/text-process': '文本处理',
  '/tools/mcp': 'MCP工具',
  '/tools/image-bed': '图床管理',
  '/profile': '个人资料',
  '/test-cases': '测试用例',
  '/test-reports': '测试报告',
  '/test-environments': '测试环境',
  '/business': '通用业务',
  '/operation-logs': '操作日志',
  '/notifications': '消息通知',
  '/docs': '常用文档'
}

const pageTitle = computed(() => pageTitles[route.path] || 'Mock 系统')
const activeMenu = computed(() => route.path)

// 标签页管理
const tabs = ref([])
const tabsWrapperRef = ref(null)
const contextMenuVisible = ref(false)
const contextMenuPosition = ref({ x: 0, y: 0 })
const contextMenuTab = ref(null)

// 初始化标签页（默认打开工作台）
const initTabs = () => {
  const defaultPath = '/dashboard'
  if (tabs.value.length === 0) {
    tabs.value.push({
      path: defaultPath,
      title: pageTitles[defaultPath] || '我的工作台'
    })
  }
}

// 添加标签页
const addTab = (path) => {
  // 排除登录页
  if (path === '/login') return

  // 检查标签页是否已存在
  const existingTab = tabs.value.find((tab) => tab.path === path)
  if (existingTab) {
    return
  }

  // 添加新标签页
  const title = pageTitles[path] || '未知页面'
  tabs.value.push({ path, title })

  // 滚动到新标签页
  nextTick(() => {
    scrollToTab(path)
  })
}

// 关闭标签页
const handleCloseTab = (path) => {
  if (tabs.value.length <= 1) {
    ElMessage.warning('至少保留一个标签页')
    return
  }

  const index = tabs.value.findIndex((tab) => tab.path === path)
  if (index === -1) return

  // 如果关闭的是当前激活的标签页，需要切换到其他标签页
  if (path === route.path) {
    // 优先切换到右侧标签页，如果没有则切换到左侧
    if (index < tabs.value.length - 1) {
      router.push(tabs.value[index + 1].path)
    } else if (index > 0) {
      router.push(tabs.value[index - 1].path)
    }
  }

  tabs.value.splice(index, 1)
}

// 点击标签页
const handleTabClick = (path) => {
  router.push(path)
}

// 关闭其他标签页
const closeOtherTabs = (currentPath) => {
  tabs.value = tabs.value.filter((tab) => tab.path === currentPath)
}

// 关闭左侧标签页
const closeLeftTabs = (currentPath) => {
  const currentIndex = tabs.value.findIndex((tab) => tab.path === currentPath)
  if (currentIndex > 0) {
    tabs.value = tabs.value.slice(currentIndex)
  }
}

// 关闭右侧标签页
const closeRightTabs = (currentPath) => {
  const currentIndex = tabs.value.findIndex((tab) => tab.path === currentPath)
  if (currentIndex >= 0 && currentIndex < tabs.value.length - 1) {
    tabs.value = tabs.value.slice(0, currentIndex + 1)
  }
}

// 关闭所有标签页
const closeAllTabs = () => {
  tabs.value = []
  // 跳转到工作台
  router.push('/dashboard')
  // 重新初始化
  nextTick(() => {
    initTabs()
  })
}

// 标签页下拉菜单命令处理
const handleTabDropdownCommand = (command) => {
  const currentPath = route.path
  switch (command) {
    case 'close-others':
      closeOtherTabs(currentPath)
      break
    case 'close-left':
      closeLeftTabs(currentPath)
      break
    case 'close-right':
      closeRightTabs(currentPath)
      break
    case 'close-all':
      closeAllTabs()
      break
  }
}

// 右键菜单处理
const handleTabContextMenu = (event, tab) => {
  contextMenuPosition.value = { x: event.clientX, y: event.clientY }
  contextMenuTab.value = tab
  contextMenuVisible.value = true

  // 点击其他地方关闭右键菜单
  const closeMenu = () => {
    contextMenuVisible.value = false
    document.removeEventListener('click', closeMenu)
  }
  nextTick(() => {
    document.addEventListener('click', closeMenu)
  })
}

// 右键菜单 - 关闭
const handleContextMenuClose = () => {
  if (contextMenuTab.value) {
    handleCloseTab(contextMenuTab.value.path)
  }
  contextMenuVisible.value = false
}

// 右键菜单 - 关闭其他
const handleContextMenuCloseOthers = () => {
  if (contextMenuTab.value) {
    closeOtherTabs(contextMenuTab.value.path)
  }
  contextMenuVisible.value = false
}

// 右键菜单 - 关闭左侧
const handleContextMenuCloseLeft = () => {
  if (contextMenuTab.value) {
    closeLeftTabs(contextMenuTab.value.path)
  }
  contextMenuVisible.value = false
}

// 右键菜单 - 关闭右侧
const handleContextMenuCloseRight = () => {
  if (contextMenuTab.value) {
    closeRightTabs(contextMenuTab.value.path)
  }
  contextMenuVisible.value = false
}

// 右键菜单 - 关闭所有
const handleContextMenuCloseAll = () => {
  closeAllTabs()
  contextMenuVisible.value = false
}

// 滚动到指定标签页
const scrollToTab = (path) => {
  if (!tabsWrapperRef.value) return

  nextTick(() => {
    const tabElements = tabsWrapperRef.value.querySelectorAll('.tab-item')
    const targetTab = Array.from(tabElements).find((el, index) => {
      return tabs.value[index]?.path === path
    })

    if (targetTab) {
      targetTab.scrollIntoView({ behavior: 'smooth', block: 'nearest', inline: 'center' })
    }
  })
}

// 监听路由变化，自动添加标签页
watch(
  () => route.path,
  (newPath) => {
    addTab(newPath)
  },
  { immediate: true }
)

// 处理下拉菜单命令
const handleCommand = async (command) => {
  switch (command) {
    case 'profile':
      router.push('/profile')
      break
    case 'logout':
      await handleLogout()
      break
  }
}

// 处理退出登录
const handleLogout = async () => {
  try {
    // 清除登录状态
    authStore.logout()

    ElMessage.success('退出登录成功')

    // 跳转到登录页
    router.push('/login')
  } catch (error) {
    // 用户取消退出
    console.log('取消退出登录')
  }
}

// 页面加载时检查认证状态
onMounted(() => {
  checkAuth()
  initTabs()
  // 如果当前路由不在标签页中，添加它
  if (route.path !== '/login') {
    addTab(route.path)
  }
  // 初始化主题
  themeStore.initTheme()
})
</script>

<style scoped>
/* 整体布局 */
.app-container {
  display: flex;
  min-height: 100vh;
  width: 100%;
  background-color: #f0f2f5;
  overflow: hidden;
}

/* 左侧导航栏 */
.sidebar {
  width: 240px;
  min-width: 240px;
  max-width: 240px;
  background-color: #001529;
  color: #fff;
  position: fixed;
  height: 100vh;
  overflow-y: auto;
  z-index: 1000;
  display: flex;
  flex-direction: column;
  box-shadow: 2px 0 8px 0 rgba(29, 35, 41, 0.1);
}

/* Logo区域 */
.logo-container {
  padding: 20px 16px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}

.logo {
  font-size: 20px;
  font-weight: 600;
  color: #ffffff;
  line-height: 1.5;
}

.logo-highlight {
  color: #1890ff;
}

.logo-subtitle {
  font-size: 12px;
  color: rgba(255, 255, 255, 0.65);
  margin-top: 4px;
}

/* 菜单样式 */
.sidebar-menu {
  border-right: none;
  width: 100%;
  flex: 1;
}

:deep(.el-menu-item) {
  height: 48px;
  line-height: 48px;
  margin: 4px 8px;
  border-radius: 4px;
  transition: all 0.3s;
}

:deep(.el-menu-item:hover) {
  background-color: rgba(24, 144, 255, 0.1) !important;
}

:deep(.el-menu-item.is-active) {
  background-color: #1890ff !important;
  color: #fff !important;
}

:deep(.el-menu-item .el-icon) {
  font-size: 16px;
  margin-right: 8px;
  vertical-align: middle;
}

/* 子菜单项图标 */
:deep(.el-sub-menu .el-menu-item .el-icon) {
  font-size: 14px;
  margin-right: 6px;
}

/* 子菜单样式 */
:deep(.el-sub-menu .el-menu-item) {
  padding-left: 48px !important;
  margin: 2px 8px;
  min-height: 44px;
  line-height: 44px;
}

:deep(.el-sub-menu__title) {
  height: 48px;
  line-height: 48px;
  margin: 4px 8px;
  border-radius: 4px;
  transition: all 0.3s;
  font-weight: 500;
}

:deep(.el-sub-menu__title:hover) {
  background-color: rgba(24, 144, 255, 0.1) !important;
}

:deep(.el-sub-menu.is-active .el-sub-menu__title) {
  color: #ffffff !important;
}

:deep(.el-sub-menu.is-opened .el-sub-menu__title) {
  color: rgba(255, 255, 255, 0.9) !important;
}

:deep(.el-sub-menu .el-icon) {
  font-size: 16px;
  margin-right: 8px;
}

/* 菜单分隔线样式 */
:deep(.el-menu-divider) {
  margin: 8px 16px;
  background-color: rgba(255, 255, 255, 0.1);
  height: 1px;
}

/* 右侧内容区 */
.main-container {
  flex: 1;
  display: flex;
  flex-direction: column;
  margin-left: 240px;
  width: calc(100% - 240px);
  min-height: 100vh;
  overflow: hidden;
}

/* 顶部导航栏 */
.top-navbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 20px;
  background-color: #fff;
  border-bottom: 1px solid #e8e8e8;
  box-shadow: 0 1px 4px rgba(0, 21, 41, 0.08);
  height: 60px;
  box-sizing: border-box;
}

.navbar-left {
  flex: 1;
}

.navbar-right {
  display: flex;
  align-items: center;
  gap: 12px;
}

/* 主题切换按钮 */
.theme-toggle-btn {
  border: none;
  background-color: transparent;
}

.theme-toggle-btn:hover {
  background-color: #f5f5f5;
}

/* GitHub 源码链接 */
.github-link {
  display: inline-flex;
  align-items: center;
  padding: 6px 12px;
  color: #333;
  text-decoration: none;
  font-size: 14px;
  border-radius: 6px;
  transition: all 0.3s;
  white-space: nowrap;
}

.github-link:hover {
  background-color: #f5f5f5;
  color: #1890ff;
}

/* 用户信息下拉菜单 */
.user-info {
  display: flex;
  align-items: center;
  padding: 6px 12px;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.3s;
  color: #333;
  gap: 4px;
}

.user-info:hover {
  background-color: #f5f5f5;
}

/* 去除右上角头像/用户信息悬停或聚焦的蓝色粗边框阴影 */
.user-dropdown:focus,
.user-dropdown:focus-visible,
.user-info:focus,
.user-info:focus-visible {
  outline: none !important;
  box-shadow: none !important;
}
.user-dropdown :deep(*:focus),
.user-dropdown :deep(*:focus-visible) {
  outline: none !important;
  box-shadow: none !important;
}
.user-dropdown :deep(.el-avatar),
.user-dropdown :deep(.el-avatar.is-active) {
  outline: none !important;
  box-shadow: none !important;
}

.user-avatar {
  margin-right: 10px;
  background: linear-gradient(135deg, #1890ff 0%, #096dd9 100%);
  color: #fff;
  font-weight: 600;
  flex-shrink: 0;
}

.user-name {
  font-size: 15px;
  font-weight: normal;
  margin-right: 10px;
  color: #262626;
  max-width: 120px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.dropdown-icon {
  color: #999;
  font-size: 12px;
  transition: transform 0.3s;
}

.user-dropdown:hover .dropdown-icon {
  transform: rotate(180deg);
}

/* 下拉菜单样式 */
:deep(.el-dropdown-menu) {
  border-radius: 8px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

:deep(.el-dropdown-menu__item) {
  display: flex;
  align-items: center;
  padding: 8px 16px;
  font-size: 14px;
}

:deep(.el-dropdown-menu__item .el-icon) {
  margin-right: 8px;
  font-size: 16px;
}

:deep(.el-dropdown-menu__item--divided) {
  border-top: 1px solid #f0f0f0;
}

:deep(.el-dropdown-menu__item:not(.is-disabled):hover) {
  background-color: #f5f7fa;
  color: #1890ff;
}

/* 内容区域 */
.content {
  flex: 1;
  padding: 0px; /* 内容和边框之间的间距 */
  background-color: #f0f2f5;
  overflow: hidden;
  min-height: 0; /* 确保flex子元素可以正确收缩 */
  max-height: 100%; /* 限制最大高度 */
  display: flex;
  flex-direction: column;
}

/* 确保router-view正确继承高度 */
.content > * {
  flex: 1;
  min-height: 0;
  overflow: hidden;
  display: flex;
  flex-direction: column;
}

/* 滚动条美化 */
.sidebar::-webkit-scrollbar {
  width: 6px;
}

.sidebar::-webkit-scrollbar-thumb {
  background-color: rgba(255, 255, 255, 0.2);
  border-radius: 3px;
}

.sidebar::-webkit-scrollbar-track {
  background-color: transparent;
}

/* 响应式调整 */
@media (max-width: 768px) {
  .sidebar {
    width: 200px;
    min-width: 200px;
    max-width: 200px;
  }

  .main-container {
    margin-left: 200px;
    width: calc(100% - 200px);
  }

  .user-name {
    max-width: 80px;
    font-size: 14px;
  }

  .top-navbar {
    padding: 12px 16px;
  }
}

@media (max-width: 480px) {
  .user-name {
    display: none;
  }

  .user-avatar {
    margin-right: 4px;
  }
}

/* 面包屑样式调整 */
:deep(.el-breadcrumb) {
  line-height: 1.5;
  font-size: 14px;
}

/* 标签页容器 */
.tabs-container {
  display: flex;
  align-items: center;
  background-color: #fff;
  border-bottom: 1px solid #e8e8e8;
  padding: 0 8px;
  height: 40px;
  box-sizing: border-box;
  overflow: hidden;
}

.tabs-wrapper {
  display: flex;
  align-items: center;
  flex: 1;
  overflow-x: auto;
  overflow-y: hidden;
  scroll-behavior: smooth;
  gap: 4px;
  padding: 4px 0;
}

.tabs-wrapper::-webkit-scrollbar {
  height: 4px;
}

.tabs-wrapper::-webkit-scrollbar-thumb {
  background-color: rgba(0, 0, 0, 0.2);
  border-radius: 2px;
}

.tabs-wrapper::-webkit-scrollbar-track {
  background-color: transparent;
}

/* 标签项 */
.tab-item {
  display: flex;
  align-items: center;
  padding: 6px 12px;
  background-color: #f5f5f5;
  border: 1px solid #e8e8e8;
  border-radius: 4px 4px 0 0;
  cursor: pointer;
  transition: all 0.3s;
  white-space: nowrap;
  min-width: 80px;
  max-width: 200px;
  position: relative;
  user-select: none;
}

.tab-item:hover {
  background-color: #e6f7ff;
  border-color: #91d5ff;
}

.tab-item.is-active {
  background-color: #1890ff;
  border-color: #1890ff;
  color: #fff;
  z-index: 1;
}

.tab-title {
  flex: 1;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  font-size: 13px;
  line-height: 1.5;
}

.tab-close {
  margin-left: 8px;
  font-size: 12px;
  opacity: 0.6;
  transition: opacity 0.3s;
  flex-shrink: 0;
  padding: 2px;
  border-radius: 2px;
}

.tab-close:hover {
  opacity: 1;
  background-color: rgba(0, 0, 0, 0.1);
}

.tab-item.is-active .tab-close {
  color: #fff;
}

.tab-item.is-active .tab-close:hover {
  background-color: rgba(255, 255, 255, 0.2);
}

/* 标签页下拉菜单 */
.tabs-dropdown {
  flex-shrink: 0;
  margin-left: 4px;
  padding: 4px 8px;
  cursor: pointer;
  border-radius: 4px;
  transition: background-color 0.3s;
}

.tabs-dropdown:hover {
  background-color: #f5f5f5;
}

.dropdown-trigger {
  font-size: 16px;
  color: #666;
}

/* 右键菜单 */
.context-menu {
  position: fixed;
  background-color: #fff;
  border: 1px solid #e8e8e8;
  border-radius: 4px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.15);
  z-index: 9999;
  min-width: 120px;
  padding: 4px 0;
}

.context-menu-item {
  padding: 8px 16px;
  font-size: 14px;
  color: #333;
  cursor: pointer;
  transition: background-color 0.2s;
}

.context-menu-item:hover {
  background-color: #f5f5f5;
}

.context-menu-divider {
  height: 1px;
  background-color: #e8e8e8;
  margin: 4px 0;
}

/* 暗黑模式样式 */
:deep(.dark) .app-container {
  background-color: #141414;
}

:deep(.dark) .main-container {
  background-color: #141414;
}

:deep(.dark) .top-navbar {
  background-color: #1f1f1f;
  border-bottom-color: #303030;
  color: #e5e5e5;
}

:deep(.dark) .navbar-right .theme-toggle-btn:hover {
  background-color: #303030;
}

:deep(.dark) .github-link {
  color: #e5e5e5;
}

:deep(.dark) .github-link:hover {
  background-color: #303030;
  color: #1890ff;
}

:deep(.dark) .user-info {
  color: #e5e5e5;
}

:deep(.dark) .user-info:hover {
  background-color: #303030;
}

:deep(.dark) .user-name {
  color: #e5e5e5;
}

:deep(.dark) .content {
  background-color: #141414;
}

:deep(.dark) .tabs-container {
  background-color: #1f1f1f;
  border-bottom-color: #303030;
}

:deep(.dark) .tab-item {
  background-color: #262626;
  border-color: #303030;
  color: #e5e5e5;
}

:deep(.dark) .tab-item:hover {
  background-color: #303030;
  border-color: #434343;
}

:deep(.dark) .tab-item.is-active {
  background-color: #1890ff;
  border-color: #1890ff;
  color: #fff;
}

:deep(.dark) .tabs-dropdown:hover {
  background-color: #303030;
}

:deep(.dark) .dropdown-trigger {
  color: #e5e5e5;
}

:deep(.dark) .context-menu {
  background-color: #1f1f1f;
  border-color: #303030;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.3);
}

:deep(.dark) .context-menu-item {
  color: #e5e5e5;
}

:deep(.dark) .context-menu-item:hover {
  background-color: #303030;
}

:deep(.dark) .context-menu-divider {
  background-color: #303030;
}

:deep(.dark) .el-breadcrumb {
  color: #e5e5e5;
}

:deep(.dark) .el-breadcrumb__inner {
  color: #e5e5e5;
}

:deep(.dark) .el-breadcrumb__inner.is-link {
  color: #1890ff;
}

:deep(.dark) .el-breadcrumb__inner.is-link:hover {
  color: #40a9ff;
}
</style>

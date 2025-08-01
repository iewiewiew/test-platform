import { createRouter, createWebHistory } from 'vue-router'
import AppLayout from '@/layouts/AppLayout.vue'
import LoginView2 from '@/views/auth/LoginView.vue'
import UserView from '@/views/auth/UserView.vue'
import RoleView from '@/views/auth/RoleView.vue'
import Dashboard from '@/views/common/Dashboard.vue'
import ExampleView from '@/views/tool/ExampleView.vue'
import MockListView from '@/views/mock/MockListView.vue'
import ProjectListView from '@/views/project/ProjectListView.vue'
import ApiDocumentation from '@/views/tool/ApiDocView.vue'
import EnvironmentView from '@/views/project/EnvironmentView.vue'
import MockDataView from '@/views/mock/MockDataView.vue'
import LinuxInfoView from '@/views/tool/LinuxInfoView.vue'
import EnvironmentDashboardView from '@/views/project/EnvironmentDashboardView.vue'
import EnvironmentHealthScanView from '@/views/project/EnvironmentHealthScanView.vue'
import SQLToolbox from '@/views/database/SQLToolbox.vue'
import DatabaseConnView from '@/views/database/DatabaseConnView.vue'
import DatabaseInfoView from '@/views/database/DatabaseInfoView.vue'
import RedisView from '@/views/database/RedisView.vue'
import ScriptManagementView from '@/views/tool/ScriptManagementView.vue'
import ToolView from '@/views/tool/ToolView.vue'
import EncodeDecodeView from '@/views/tool/EncodeDecodeView.vue'
import FormatConvertView from '@/views/tool/FormatConvertView.vue'
import EncryptDecryptView from '@/views/tool/EncryptDecryptView.vue'
import TextProcessView from '@/views/tool/TextProcessView.vue'
import McpToolView from '@/views/tool/McpToolView.vue'
import ImageBedView from '@/views/tool/ImageBedView.vue'
import ProfileView from '@/views/auth/ProfileView.vue'
import OperationLogView from '@/views/auth/OperationLogView.vue'
import DocsView from '@/views/tool/DocsView.vue'
import TestCaseView from '@/views/test/TestCaseView.vue'
import TestReportView from '@/views/test/TestReportView.vue'
import TestEnvironmentView from '@/views/test/TestEnvironmentView.vue'
import BusinessView from '@/views/business/BusinessView.vue'
import NotificationView from '@/views/notification/NotificationView.vue'
import { useAuthStore } from '@/stores/auth/authStore'

const routes = [
  {
    path: '/login',
    name: 'Login',
    component: LoginView2,
    meta: { requiresGuest: true }
  },
  {
    path: '/',
    component: AppLayout,
    meta: { requiresAuth: true },
    redirect: '/dashboard',
    children: [
      {
        path: '/dashboard',
        name: 'Dashboard',
        component: Dashboard
      },
      {
        path: '/profile',
        name: 'Profile',
        component: ProfileView
      },
      {
        path: '/users',
        name: 'Users',
        component: UserView
      },
      {
        path: '/roles',
        name: 'Roles',
        component: RoleView
      },
      {
        path: '/operation-logs',
        name: 'OperationLogs',
        component: OperationLogView
      },
      {
        path: '/example-list',
        name: 'ExampleView',
        component: ExampleView
      },
      {
        path: '/mock-list',
        name: 'MockList',
        component: MockListView
      },
      {
        path: '/project-list',
        name: 'ProjectList',
        component: ProjectListView
      },
      {
        path: '/environment-list',
        name: 'EnvironmentView',
        component: EnvironmentView
      },
      {
        path: '/mock-data',
        name: 'MockDataView',
        component: MockDataView
      },
      {
        path: '/api-tree',
        name: 'ApiTree',
        component: ApiDocumentation
      },
      {
        path: '/linux-info',
        name: 'LinuxInfo',
        component: LinuxInfoView
      },
      {
        path: '/environment-dashboard',
        name: 'EnvironmentDashboard',
        component: EnvironmentDashboardView
      },
      {
        path: '/environment-health-scan',
        name: 'EnvironmentHealthScan',
        component: EnvironmentHealthScanView
      },
      {
        path: '/sql-tool-box',
        name: 'SQLToolbox',
        component: SQLToolbox
      },
      {
        path: '/sql-tool-box/database-conn',
        name: 'DatabaseConn',
        component: DatabaseConnView
      },
      {
        path: '/sql-tool-box/database-info',
        name: 'DatabaseInfo',
        component: DatabaseInfoView
      },
      {
        path: '/sql-tool-box/redis',
        name: 'Redis',
        component: RedisView
      },
      {
        path: '/script-management',
        name: 'ScriptManagement',
        component: ScriptManagementView
      },
      {
        path: '/tools',
        name: 'Tools',
        component: ToolView
      },
      {
        path: '/tools/encode-decode',
        name: 'EncodeDecode',
        component: EncodeDecodeView
      },
      {
        path: '/tools/format-convert',
        name: 'FormatConvert',
        component: FormatConvertView
      },
      {
        path: '/tools/encrypt-decrypt',
        name: 'EncryptDecrypt',
        component: EncryptDecryptView
      },
      {
        path: '/tools/text-process',
        name: 'TextProcess',
        component: TextProcessView
      },
      {
        path: '/tools/mcp',
        name: 'McpTool',
        component: McpToolView
      },
      {
        path: '/tools/image-bed',
        name: 'ImageBed',
        component: ImageBedView
      },
      {
        path: '/docs',
        name: 'Docs',
        component: DocsView
      },
      {
        path: '/docs/:name',
        name: 'DocDetail',
        component: DocsView
      },
      {
        path: '/test-cases',
        name: 'TestCases',
        component: TestCaseView
      },
      {
        path: '/test-reports',
        name: 'TestReports',
        component: TestReportView
      },
      {
        path: '/test-environments',
        name: 'TestEnvironments',
        component: TestEnvironmentView
      },
      {
        path: '/business',
        name: 'Business',
        component: BusinessView
      },
      {
        path: '/notifications',
        name: 'Notifications',
        component: NotificationView
      }
    ]
  },
  // 404 页面处理
  {
    path: '/:pathMatch(.*)*',
    redirect: '/dashboard'
  }
]

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes
})

// 路由守卫
router.beforeEach(async (to, from, next) => {
  const authStore = useAuthStore()

  console.log('🛡️ 路由守卫 - 导航:', from.path, '->', to.path)
  console.log('🔑 路由守卫 - 认证状态:', authStore.isAuthenticated)
  console.log('📝 路由守卫 - 目标路由元信息:', to.meta)

  // 如果需要认证的页面
  if (to.meta.requiresAuth) {
    if (authStore.isAuthenticated) {
      // 已认证，检查 token 是否有效
      try {
        const isValid = await authStore.checkAuth()
        if (isValid) {
          console.log('✅ 路由守卫 - Token 有效，允许访问')
          next()
        } else {
          console.log('❌ 路由守卫 - Token 无效，跳转到登录页')
          const returnUrl = encodeURIComponent(to.fullPath)
          next(`/login?returnUrl=${returnUrl}`)
        }
      } catch (error) {
        console.error('🚨 路由守卫 - 认证检查错误:', error)
        const returnUrl = encodeURIComponent(to.fullPath)
        next(`/login?returnUrl=${returnUrl}`)
      }
    } else {
      console.log('❌ 路由守卫 - 未认证，跳转到登录页')
      const returnUrl = encodeURIComponent(to.fullPath)
      next(`/login?returnUrl=${returnUrl}`)
    }
  }
  // 如果要求未登录的页面（如登录页）
  else if (to.meta.requiresGuest) {
    if (authStore.isAuthenticated) {
      console.log('✅ 路由守卫 - 已登录，检查返回URL')

      const returnUrl = to.query.returnUrl
      if (returnUrl) {
        // 解码并跳转到原页面
        const targetPath = decodeURIComponent(returnUrl)
        console.log('🔀 路由守卫 - 跳转到返回URL:', targetPath)

        // 确保目标路径是有效的应用内路径
        if (targetPath.startsWith('/') && targetPath !== '/login') {
          next(targetPath)
        } else {
          next('/dashboard')
        }
      } else {
        // 没有返回URL，检查是否从其他页面跳转过来
        if (from.path !== '/' && from.path !== '/login' && from.meta.requiresAuth) {
          console.log('🔀 路由守卫 - 跳转回来源页面:', from.path)
          next(from.path)
        } else {
          console.log('🔀 路由守卫 - 跳转到默认页面')
          next('/dashboard')
        }
      }
    } else {
      console.log('✅ 路由守卫 - 未登录，允许访问登录页')
      next()
    }
  }
  // 其他页面（没有元信息的页面）
  else {
    console.log('✅ 路由守卫 - 公共页面，允许访问')
    next()
  }
})

// 路由错误处理
router.onError((error) => {
  console.error('❌ 路由错误:', error)
})

export default router

<template>
  <div class="dashboard-container">
    <!-- 页面标题 -->
    <div class="page-header">
      <h1 class="page-title">我的工作台</h1>
      <p class="page-desc">欢迎回来，{{ username }}！这里是您的个人工作台。</p>
    </div>

    <!-- 快捷操作 -->
    <el-card class="quick-actions-card" shadow="never">
      <template #header>
        <div class="card-header">
          <span class="card-title">
            <el-icon><Lightning /></el-icon>
            快捷操作
          </span>
        </div>
      </template>
      <div class="actions-grid">
        <div class="action-item" @click="handleQuickAction('newProject')">
          <div class="action-icon" style="background-color: #1890ff;">
            <el-icon><Plus /></el-icon>
          </div>
          <span class="action-text">创建项目</span>
        </div>
        <div class="action-item" @click="handleQuickAction('mockData')">
          <div class="action-icon" style="background-color: #52c41a;">
            <el-icon><Tools /></el-icon>
          </div>
          <span class="action-text">造数管理</span>
        </div>
        <div class="action-item" @click="handleQuickAction('apiTest')">
          <div class="action-icon" style="background-color: #faad14;">
            <el-icon><Connection /></el-icon>
          </div>
          <span class="action-text">接口测试</span>
        </div>
        <div class="action-item" @click="handleQuickAction('sqlTool')">
          <div class="action-icon" style="background-color: #722ed1;">
            <el-icon><SetUp /></el-icon>
          </div>
          <span class="action-text">SQL工具</span>
        </div>
        <div class="action-item" @click="handleQuickAction('scriptManagement')">
          <div class="action-icon" style="background-color: #13c2c2;">
            <el-icon><Document /></el-icon>
          </div>
          <span class="action-text">脚本管理</span>
        </div>
        <div class="action-item" @click="handleQuickAction('exampleList')">
          <div class="action-icon" style="background-color: #f5222d;">
            <el-icon><Document /></el-icon>
          </div>
          <span class="action-text">示例列表</span>
        </div>
        <div class="action-item" @click="handleQuickAction('environment')">
          <div class="action-icon" style="background-color: #13c2c2;">
            <el-icon><Setting /></el-icon>
          </div>
          <span class="action-text">环境管理</span>
        </div>
        <div class="action-item" @click="handleQuickAction('linuxInfo')">
          <div class="action-icon" style="background-color: #eb2f96;">
            <el-icon><Monitor /></el-icon>
          </div>
          <span class="action-text">服务器信息</span>
        </div>
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import {
  Plus,
  Tools,
  Connection,
  SetUp,
  Document,
  Setting,
  Monitor,
  Lightning
} from '@element-plus/icons-vue'

const router = useRouter()
const username = ref(localStorage.getItem('username') || '管理员')

// 处理快捷操作
const handleQuickAction = (action) => {
  const actions = {
    newProject: () => router.push('/project-list'),
    mockData: () => router.push('/mock-data'),
    apiTest: () => router.push('/api-tree'),
    sqlTool: () => router.push('/sql-tool-box'),
    scriptManagement: () => router.push('/script-management'),
    exampleList: () => router.push('/example-list'),
    environment: () => router.push('/environment-list'),
    linuxInfo: () => router.push('/linux-info'),
    mockList: () => router.push('/mock-list')
  }
  
  if (actions[action]) {
    actions[action]()
  } else {
    ElMessage.info('功能开发中...')
  }
}
</script>

<style scoped>
.dashboard-container {
  padding: 0;
}

.page-header {
  margin-bottom: 32px;
  text-align: center;
}

.page-title {
  font-size: 28px;
  font-weight: 600;
  color: #1f2d3d;
  margin: 0 0 12px 0;
  background: linear-gradient(135deg, #1890ff 0%, #722ed1 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.page-desc {
  color: #8492a6;
  margin: 0;
  font-size: 16px;
}

/* 快捷操作卡片 */
.quick-actions-card {
  height: 100%;
  border-radius: 12px;
  border: 1px solid #e8e8e8;
}

.card-header {
  padding: 8px 0;
  display: flex;
  align-items: center;
  gap: 8px;
}

.card-title {
  font-size: 18px;
  font-weight: 600;
  color: #1f2d3d;
  display: flex;
  align-items: center;
  gap: 8px;
}

.card-title .el-icon {
  color: #1890ff;
}

/* 快捷操作网格 */
.actions-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 20px;
  padding: 8px;
}

.action-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 24px 16px;
  border-radius: 12px;
  border: 2px solid #f0f0f0;
  background: #fff;
  cursor: pointer;
  transition: all 0.3s ease;
  text-decoration: none;
}

.action-item:hover {
  border-color: #1890ff;
  background: linear-gradient(135deg, #f6ffed 0%, #e6f7ff 100%);
  box-shadow: 0 4px 16px rgba(24, 144, 255, 0.15);
  transform: translateY(-2px);
}

.action-icon {
  width: 60px;
  height: 60px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 12px;
  transition: all 0.3s ease;
}

.action-item:hover .action-icon {
  transform: scale(1.1);
}

.action-icon .el-icon {
  font-size: 28px;
  color: white;
}

.action-text {
  font-size: 16px;
  font-weight: 500;
  color: #1f2d3d;
  text-align: center;
}

.action-item:hover .action-text {
  color: #1890ff;
  font-weight: 600;
}

/* 响应式调整 */
@media (max-width: 768px) {
  .page-title {
    font-size: 24px;
  }
  
  .page-desc {
    font-size: 14px;
  }
  
  .actions-grid {
    grid-template-columns: repeat(2, 1fr);
    gap: 16px;
  }
  
  .action-item {
    padding: 20px 12px;
  }
  
  .action-icon {
    width: 50px;
    height: 50px;
  }
  
  .action-icon .el-icon {
    font-size: 24px;
  }
  
  .action-text {
    font-size: 14px;
  }
}

@media (max-width: 480px) {
  .actions-grid {
    grid-template-columns: 1fr;
    gap: 12px;
  }
  
  .action-item {
    padding: 16px 12px;
    flex-direction: row;
    justify-content: flex-start;
  }
  
  .action-icon {
    width: 44px;
    height: 44px;
    margin-bottom: 0;
    margin-right: 12px;
  }
  
  .action-icon .el-icon {
    font-size: 20px;
  }
  
  .action-text {
    font-size: 14px;
    text-align: left;
  }
}
</style>

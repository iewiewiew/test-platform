<template>
  <!-- 环境健康扫描 -->
  <div class="common-list-container">
    <!-- 搜索区域 -->
    <div class="common-header-bar">
      <div class="common-search-bar">
        <el-form :inline="true" :model="searchForm" class="demo-form-inline" label-width="auto">
          <el-form-item label="环境名称">
            <el-input v-model="searchForm.name" placeholder="请输入环境名称" clearable @input="handleInputSearch" />
          </el-form-item>
          <el-form-item label="基础URL">
            <el-input v-model="searchForm.base_url" placeholder="请输入基础URL" clearable @input="handleInputSearch" />
          </el-form-item>
          <el-form-item>
            <el-button @click="resetSearch">重置</el-button>
          </el-form-item>
        </el-form>
      </div>

      <div class="common-action-bar">
        <el-button type="primary" @click="startScan" :loading="scanning" :disabled="scanning">
          <el-icon><Refresh /></el-icon>
          {{ scanning ? '扫描中...' : '开始扫描' }}
        </el-button>
        <el-button @click="refreshEnvironments" :loading="loading">
          <el-icon><Refresh /></el-icon>
          刷新列表
        </el-button>
      </div>
    </div>

    <!-- 环境健康扫描表格 -->
    <el-table :data="environments" v-loading="loading" style="width: 100%" empty-text="暂无环境数据">
      <el-table-column prop="id" label="ID" width="60" />
      <el-table-column prop="name" label="环境名称" min-width="150" show-overflow-tooltip />
      <el-table-column prop="base_url" label="基础URL" min-width="200" show-overflow-tooltip />
      <el-table-column prop="description" label="描述" min-width="150" show-overflow-tooltip />
      <el-table-column label="健康状态" width="120">
        <template #default="scope">
          <el-tag :type="getHealthStatusType(scope.row.health_status)" size="small">
            {{ getHealthStatusText(scope.row.health_status) }}
          </el-tag>
          <el-tooltip v-if="scope.row.error_message" :content="scope.row.error_message" placement="top">
            <el-icon style="margin-left: 4px; color: #f56c6c; cursor: help"><Warning /></el-icon>
          </el-tooltip>
        </template>
      </el-table-column>
      <el-table-column label="HTTP状态码" width="120">
        <template #default="scope">
          <el-tag v-if="scope.row.status_code" :type="getStatusCodeType(scope.row.status_code)" size="small">
            {{ scope.row.status_code }}
          </el-tag>
          <span v-else style="color: #909399">-</span>
        </template>
      </el-table-column>
      <el-table-column label="响应时间" width="120">
        <template #default="scope">
          <span v-if="scope.row.response_time !== null && scope.row.response_time !== undefined">{{ scope.row.response_time }}ms</span>
          <span v-else style="color: #909399">-</span>
        </template>
      </el-table-column>
      <el-table-column label="扫描时间" width="160">
        <template #default="scope">
          {{ scope.row.scanned_at ? formatDate(scope.row.scanned_at) : '-' }}
        </template>
      </el-table-column>
      <el-table-column prop="creator_name" label="创建人" width="120" />
      <el-table-column prop="created_at" label="创建时间" width="160" :formatter="formatDate" />
      <el-table-column label="操作" width="120" fixed="right">
        <template #default="scope">
          <el-button size="small" type="primary" @click="scanSingleEnvironment(scope.row)" :loading="scope.row.scanning">扫描</el-button>
        </template>
      </el-table-column>
    </el-table>

    <!-- 分页 -->
    <div class="pagination">
      <el-pagination
        v-model:current-page="currentPage"
        v-model:page-size="pageSize"
        :page-sizes="[10, 20, 50, 100]"
        :total="pagination.total"
        :background="true"
        layout="total, sizes, prev, pager, next, jumper"
        @update:current-page="handlePageChange"
        @update:page-size="handleSizeChange"
      />
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, onUnmounted } from 'vue'
import { ElMessage } from 'element-plus'
import { Refresh, Warning } from '@element-plus/icons-vue'
import { environmentService } from '@/services/project/environmentService'
import { formatDateTime } from '@/utils/date'

const loading = ref(false)
const scanning = ref(false)

// 搜索表单
const searchForm = ref({
  name: '',
  base_url: ''
})

// 分页相关状态
const currentPage = ref(1)
const pageSize = ref(10)
const pagination = reactive({
  total: 0
})

// 环境列表数据
const environments = ref([])

// 防抖计时器
let searchTimer = null

// 统一的数据获取方法
const fetchEnvironments = async () => {
  loading.value = true

  try {
    const params = {
      page: currentPage.value,
      per_page: pageSize.value,
      search: searchForm.value.name || searchForm.value.base_url ? `${searchForm.value.name} ${searchForm.value.base_url}`.trim() : ''
    }

    const response = await environmentService.getEnvironments(params)
    environments.value = response.data.map((env) => ({
      ...env,
      health_status: env.health_status || 'unknown',
      response_time: env.response_time || null,
      scanned_at: env.scanned_at || null,
      status_code: env.status_code || null,
      error_message: env.error_message || null,
      scanning: false
    }))
    pagination.total = response.total
  } catch (error) {
    console.error('Error fetching environments:', error)
    ElMessage.error('获取环境数据失败')
  } finally {
    loading.value = false
  }
}

// 输入搜索处理（防抖）
const handleInputSearch = () => {
  clearTimeout(searchTimer)
  searchTimer = setTimeout(() => {
    currentPage.value = 1
    fetchEnvironments()
  }, 500)
}

// 重置搜索
const resetSearch = () => {
  searchForm.value = {
    name: '',
    base_url: ''
  }
  currentPage.value = 1
  fetchEnvironments()
}

// 分页处理
const handlePageChange = (newPage) => {
  currentPage.value = newPage
  fetchEnvironments()
}

const handleSizeChange = (newSize) => {
  pageSize.value = newSize
  currentPage.value = 1
  fetchEnvironments()
}

// 日期格式化
const formatDate = (row, column, cellValue) => {
  return cellValue ? formatDateTime(cellValue) : '-'
}

// 获取健康状态类型
const getHealthStatusType = (status) => {
  switch (status) {
    case 'healthy':
      return 'success'
    case 'warning':
      return 'warning'
    case 'unhealthy':
      return 'danger'
    default:
      return 'info'
  }
}

// 获取健康状态文本
const getHealthStatusText = (status) => {
  switch (status) {
    case 'healthy':
      return '健康'
    case 'warning':
      return '警告'
    case 'unhealthy':
      return '异常'
    default:
      return '未扫描'
  }
}

// 获取HTTP状态码类型
const getStatusCodeType = (statusCode) => {
  if (!statusCode) return 'info'
  if (statusCode >= 200 && statusCode < 300) {
    return 'success'
  } else if (statusCode >= 300 && statusCode < 400) {
    return 'warning'
  } else {
    return 'danger'
  }
}

// 扫描单个环境（使用后端API代理，避免CORS问题）
const scanSingleEnvironment = async (environment) => {
  if (!environment.base_url) {
    ElMessage.warning('环境基础URL为空，无法扫描')
    return
  }

  // 设置扫描状态
  environment.scanning = true

  try {
    // 调用后端健康检查API
    const result = await environmentService.healthCheck(environment.id)

    // 更新环境健康状态
    environment.health_status = result.health_status || 'unknown'
    environment.response_time = result.response_time || null
    environment.scanned_at = result.scanned_at || new Date().toISOString()
    environment.status_code = result.status_code || null
    environment.error_message = result.error_message || null

    // 显示消息
    if (result.health_status === 'healthy') {
      ElMessage.success(`环境 ${environment.name} 扫描完成 - 状态码: ${result.status_code}`)
    } else if (result.health_status === 'warning') {
      ElMessage.warning(`环境 ${environment.name} 扫描完成 - 状态码: ${result.status_code}`)
    } else {
      const errorMsg = result.error_message ? ` - ${result.error_message}` : ''
      ElMessage.error(`环境 ${environment.name} 扫描完成 - 状态码: ${result.status_code || 'N/A'}${errorMsg}`)
    }
  } catch (error) {
    console.error('扫描环境失败:', error)

    environment.health_status = 'unhealthy'
    environment.response_time = null
    environment.scanned_at = new Date().toISOString()
    environment.status_code = null
    environment.error_message = error.response?.data?.message || error.message || '未知错误'

    ElMessage.error(`环境 ${environment.name} 扫描失败: ${environment.error_message}`)
  } finally {
    environment.scanning = false
  }
}

// 扫描所有环境
const startScan = async () => {
  if (environments.value.length === 0) {
    ElMessage.warning('没有可扫描的环境')
    return
  }

  scanning.value = true
  ElMessage.info(`开始扫描 ${environments.value.length} 个环境...`)

  // 逐个扫描环境（避免并发过多）
  for (let i = 0; i < environments.value.length; i++) {
    const env = environments.value[i]
    if (env.base_url) {
      await scanSingleEnvironment(env)
      // 添加短暂延迟，避免请求过于频繁
      if (i < environments.value.length - 1) {
        await new Promise((resolve) => setTimeout(resolve, 500))
      }
    }
  }

  scanning.value = false
  ElMessage.success('所有环境扫描完成')
}

// 刷新环境列表
const refreshEnvironments = () => {
  fetchEnvironments()
}

// 生命周期
onMounted(() => {
  fetchEnvironments()
})

onUnmounted(() => {
  if (searchTimer) {
    clearTimeout(searchTimer)
  }
})
</script>

<style scoped>
/* 样式继承自 common.css */
</style>

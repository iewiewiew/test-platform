<template>
    <div class="query-history">
      <el-card>
        <template #header>
          <div class="card-header">
            <span>查询历史记录</span>
            <el-button 
              type="primary" 
              link 
              :loading="loading"
              @click="refreshHistory"
            >
              <el-icon><Refresh /></el-icon>
              刷新
            </el-button>
          </div>
        </template>
  
        <el-table
          :data="historyList"
          v-loading="loading"
          border
          stripe
          style="width: 100%"
        >
          <el-table-column prop="sql_query" label="SQL查询" min-width="300" show-overflow-tooltip />
          <el-table-column prop="execution_time" label="执行时间" width="120">
            <template #default="{ row }">
              <el-tag :type="getTimeTagType(row.execution_time)">
                {{ row.execution_time?.toFixed(3) }}s
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="success" label="状态" width="100">
            <template #default="{ row }">
              <el-tag :type="row.success ? 'success' : 'danger'">
                {{ row.success ? '成功' : '失败' }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="error_message" label="错误信息" min-width="200" show-overflow-tooltip>
            <template #default="{ row }">
              <span v-if="!row.success" style="color: #f56c6c;">
                {{ row.error_message }}
              </span>
              <span v-else style="color: #67c23a;">-</span>
            </template>
          </el-table-column>
          <el-table-column prop="created_at" label="执行时间" width="180">
            <template #default="{ row }">
              {{ formatDate(row.created_at) }}
            </template>
          </el-table-column>
        </el-table>
  
        <!-- 空状态 -->
        <el-empty 
          v-if="historyList.length === 0 && !loading" 
          description="暂无查询历史"
        />
      </el-card>
    </div>
  </template>
  
  <script setup>
  import { ref, computed, onMounted } from 'vue'
  import { ElMessage } from 'element-plus'
  import { Refresh } from '@element-plus/icons-vue'
  import { useSQLStore } from '@/stores/database/sqlStore'
  
  const sqlStore = useSQLStore()
  
  // 响应式数据
  const loading = ref(false)
  
  // 计算属性
  const historyList = computed(() => sqlStore.queryHistory)
  
  // 方法
  const refreshHistory = async () => {
    loading.value = true
    try {
      await sqlStore.loadHistory()
      // ElMessage.success('历史记录已刷新')
    } catch (error) {
      ElMessage.error('刷新失败: ' + (error.message || '未知错误'))
    } finally {
      loading.value = false
    }
  }
  
  const getTimeTagType = (executionTime) => {
    if (!executionTime) return 'info'
    if (executionTime < 1) return 'success'
    if (executionTime < 5) return 'warning'
    return 'danger'
  }
  
  const formatDate = (dateString) => {
    if (!dateString) return '-'
    const date = new Date(dateString)
    return date.toLocaleString('zh-CN', {
      year: 'numeric',
      month: '2-digit',
      day: '2-digit',
      hour: '2-digit',
      minute: '2-digit',
      second: '2-digit'
    }).replace(/\//g, '-')
  }
  
  // 生命周期
  onMounted(() => {
    refreshHistory()
  })
  </script>
  
  <style scoped>
  .query-history {
    padding: 20px;
  }
  
  .card-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
  }
  
  :deep(.el-table .cell) {
    word-break: break-word;
  }
  </style>
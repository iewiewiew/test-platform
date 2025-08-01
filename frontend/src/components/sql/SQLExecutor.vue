<template>
  <div class="sql-executor">
    <el-card class="query-card">
      <template #header>
        <div class="card-header">
          <span>SQL查询编辑器</span>
          <div class="header-actions">
            <el-select
              v-model="selectedConnectionId"
              placeholder="选择数据库连接（可选）"
              clearable
              filterable
              style="width: 280px; margin-right: 12px;"
              :loading="connectionsLoading"
              @visible-change="onConnectionSelectVisible"
              @change="onConnectionChange"
            >
              <el-option
                v-for="conn in connections"
                :key="conn.id"
                :label="`${conn.name} (${conn.host}/${conn.database})`"
                :value="conn.id"
              />
            </el-select>
            <el-select
              v-model="selectedDatabaseName"
              placeholder="选择数据库（可选）"
              clearable
              filterable
              style="width: 200px; margin-right: 12px;"
              :loading="databasesLoading"
              :disabled="!selectedConnectionId"
              @visible-change="onDatabaseSelectVisible"
            >
              <el-option
                v-for="db in databases"
                :key="db"
                :label="db"
                :value="db"
              />
            </el-select>
            <el-button 
              type="primary" 
              :loading="loading" 
              @click="executeQuery"
              :disabled="!sqlQuery.trim()"
            >
              执行查询
            </el-button>
          </div>
        </div>
      </template>

      <!-- SQL编辑器 -->
      <el-input
        v-model="sqlQuery"
        type="textarea"
        :rows="8"
        placeholder="请输入SQL查询语句..."
        resize="none"
      />

      <!-- 当前模板显示 -->
      <div v-if="currentTemplate" class="current-template">
        <el-tag type="info">{{ currentTemplate.category }}</el-tag>
        <span class="template-name">{{ currentTemplate.name }}</span>
        <el-button link @click="clearTemplate">清除</el-button>
      </div>

      <!-- 查询结果 - 直接展示原始数据 -->
      <div v-if="queryResult" class="query-result">
        <div class="result-header">
          <div class="result-info">
            <span>查询结果 ({{ queryResult.row_count }} 行)</span>
            <span v-if="currentConnectionInfo" class="connection-info">
              连接: {{ currentConnectionInfo.name }}
              <span v-if="currentConnectionInfo.database"> / {{ currentConnectionInfo.database }}</span>
            </span>
          </div>
          <span class="execution-time">执行时间: {{ executionTime.toFixed(3) }}s</span>
        </div>
        
        <!-- 直接展示数据 -->
        <div class="raw-data-container" v-loading="loading">
          <pre class="raw-data">{{ formattedData }}</pre>
        </div>
      </div>

      <!-- 错误信息 -->
      <div v-if="errorMessage" class="error-message">
        <el-alert
          :title="errorMessage"
          type="error"
          show-icon
          :closable="false"
        />
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { ref, computed, watch, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { useSQLStore } from '@/stores/database/sqlStore'
import databaseConnService from '@/services/database/databaseConnService'
import databaseInfoService from '@/services/database/databaseInfoService'

const sqlStore = useSQLStore()

// 响应式数据
const sqlQuery = ref('')
const errorMessage = ref('')
const selectedConnectionId = ref(null)
const selectedDatabaseName = ref(null)
const connections = ref([])
const databases = ref([])
const connectionsLoading = ref(false)
const databasesLoading = ref(false)

// 计算属性
const loading = computed(() => sqlStore.loading)
const queryResult = computed(() => sqlStore.queryResult)
const executionTime = computed(() => sqlStore.executionTime)
const currentTemplate = computed(() => sqlStore.currentTemplate)

// 当前连接信息
const currentConnectionInfo = computed(() => {
  if (!selectedConnectionId.value) return null
  const conn = connections.value.find(c => c.id === selectedConnectionId.value)
  if (!conn) return null
  return {
    name: conn.name,
    database: selectedDatabaseName.value || conn.database
  }
})

// 格式化数据用于显示
const formattedData = computed(() => {
  if (!queryResult.value || !queryResult.value.data) {
    return '暂无数据'
  }
  
  try {
    return JSON.stringify(queryResult.value.data, null, 2)
  } catch (error) {
    return queryResult.value.data.toString()
  }
})

// 方法
const executeQuery = async () => {
  errorMessage.value = ''
  
  // 如果选择了数据库但没选择连接，提示错误
  if (selectedDatabaseName.value && !selectedConnectionId.value) {
    ElMessage.warning('选择数据库时，请先选择数据库连接')
    return
  }
  
  try {
    await sqlStore.executeQuery(
      sqlQuery.value, 
      1000, 
      selectedConnectionId.value || null, 
      selectedDatabaseName.value || null
    )
    ElMessage.success('查询执行成功')
  } catch (error) {
    errorMessage.value = error.message || '执行查询时发生错误'
    ElMessage.error('查询执行失败')
  }
}

// 加载数据库连接列表
const loadConnections = async () => {
  connectionsLoading.value = true
  try {
    const response = await databaseConnService.getDatabaseConnectionsForSelect()
    connections.value = response.data || []
  } catch (error) {
    ElMessage.error('加载数据库连接列表失败')
  } finally {
    connectionsLoading.value = false
  }
}

// 加载数据库列表
const loadDatabases = async () => {
  if (!selectedConnectionId.value) {
    databases.value = []
    return
  }
  
  databasesLoading.value = true
  try {
    const response = await databaseInfoService.getDatabases(selectedConnectionId.value)
    databases.value = response.data || []
  } catch (error) {
    ElMessage.error('加载数据库列表失败')
    databases.value = []
  } finally {
    databasesLoading.value = false
  }
}

// 数据库连接下拉框显示/隐藏
const onConnectionSelectVisible = async (visible) => {
  if (visible && connections.value.length === 0) {
    await loadConnections()
  }
}

// 数据库下拉框显示/隐藏
const onDatabaseSelectVisible = async (visible) => {
  if (visible && selectedConnectionId.value) {
    await loadDatabases()
  }
}

// 数据库连接变化
const onConnectionChange = () => {
  // 连接改变时，清空数据库选择并重新加载数据库列表
  selectedDatabaseName.value = null
  databases.value = []
  if (selectedConnectionId.value) {
    loadDatabases()
  }
}

const clearTemplate = () => {
  sqlStore.setCurrentTemplate(null)
}

// 监听当前模板变化
watch(currentTemplate, (newTemplate) => {
  if (newTemplate) {
    sqlQuery.value = newTemplate.sql_content
  }
})

// 生命周期
onMounted(() => {
  loadConnections()
})
</script>

<style scoped>
.sql-executor {
  padding: 20px;
}

.query-card {
  min-height: 600px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.header-actions {
  display: flex;
  align-items: center;
}

.current-template {
  margin-top: 10px;
  padding: 8px 12px;
  background: #f8f9fa;
  border-radius: 4px;
  display: flex;
  align-items: center;
  gap: 8px;
}

.template-name {
  flex: 1;
  font-weight: 500;
}

.query-result {
  margin-top: 20px;
}

.result-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 10px;
  padding: 8px 0;
  border-bottom: 1px solid #e4e7ed;
}

.result-info {
  display: flex;
  align-items: center;
  gap: 16px;
}

.connection-info {
  font-size: 12px;
  color: #909399;
  padding: 2px 8px;
  background: #f0f2f5;
  border-radius: 4px;
}

.execution-time {
  color: #909399;
  font-size: 12px;
}

.error-message {
  margin-top: 20px;
}

.raw-data-container {
  border: 1px solid #e4e7ed;
  border-radius: 4px;
  background: #f8f9fa;
  max-height: 400px;
  overflow: auto;
}

.raw-data {
  margin: 0;
  padding: 12px;
  font-family: 'Monaco', 'Menlo', 'Ubuntu Mono', monospace;
  font-size: 14px;
  line-height: 1.5;
  white-space: pre-wrap;
  word-wrap: break-word;
}
</style>
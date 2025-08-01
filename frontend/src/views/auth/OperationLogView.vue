<template>
  <div class="common-list-container">
    <div class="common-header-bar">
      <div class="common-search-bar">
        <el-form :inline="true" :model="searchForm" class="demo-form-inline">
          <el-form-item label="搜索">
            <el-input v-model="searchForm.search" placeholder="请输入用户名、IP或操作描述" clearable @input="handleInputSearch" :prefix-icon="Search" />
          </el-form-item>
          <el-form-item label="用户名">
            <el-input v-model="searchForm.username" placeholder="请输入用户名" clearable @input="handleInputSearch" />
          </el-form-item>
          <el-form-item label="操作类型">
            <el-select v-model="searchForm.operation_type" placeholder="请选择操作类型" clearable @change="handleInputSearch" style="width: 150px">
              <el-option label="登录" value="login" />
              <el-option label="登出" value="logout" />
              <el-option label="创建" value="create" />
              <el-option label="更新" value="update" />
              <el-option label="删除" value="delete" />
              <el-option label="查询" value="query" />
              <el-option label="其他" value="other" />
            </el-select>
          </el-form-item>
          <el-form-item label="操作状态">
            <el-select v-model="searchForm.operation_status" placeholder="请选择操作状态" clearable @change="handleInputSearch" style="width: 150px">
              <el-option label="成功" value="success" />
              <el-option label="失败" value="failed" />
            </el-select>
          </el-form-item>
          <el-form-item>
            <el-button @click="resetSearch">重置</el-button>
          </el-form-item>
        </el-form>
      </div>
    </div>

    <el-table :data="operationLogStore.operationLogs" style="width: 100%" v-loading="loading">
      <el-table-column prop="id" label="ID" width="60" />
      <el-table-column prop="username" label="用户名" width="120" />
      <el-table-column prop="operation_type" label="操作类型" width="100" align="center">
        <template #default="{ row }">
          <el-tag :type="getOperationTypeTagType(row.operation_type)">
            {{ getOperationTypeLabel(row.operation_type) }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="operation_module" label="操作模块" width="100" />
      <el-table-column prop="operation_desc" label="操作描述" width="200" show-overflow-tooltip />
      <el-table-column prop="request_ip" label="请求IP" width="140" />
      <el-table-column prop="api_path" label="接口路径" width="200" show-overflow-tooltip />
      <el-table-column prop="request_method" label="请求方法" width="100" align="center">
        <template #default="{ row }">
          <el-tag :type="getMethodTagType(row.request_method)">
            {{ row.request_method }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="operation_status" label="操作状态" width="100" align="center">
        <template #default="{ row }">
          <el-tag :type="row.operation_status === 'success' ? 'success' : 'danger'">
            {{ row.operation_status === 'success' ? '成功' : '失败' }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="status_code" label="状态码" width="100" align="center">
        <template #default="{ row }">
          <el-tag :type="getStatusTagType(row.status_code)">
            {{ row.status_code || '-' }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="failure_reason" label="失败原因" width="150" show-overflow-tooltip />
      <el-table-column prop="operation_time" label="操作时间" width="180" :formatter="formatDate" />

      <el-table-column label="操作" width="120" fixed="right">
        <template #default="scope">
          <el-button size="small" type="danger" @click="deleteLog(scope.row)" v-permission="'user:delete'">删除</el-button>
        </template>
      </el-table-column>
    </el-table>

    <div class="pagination">
      <el-pagination
        v-model:current-page="currentPage"
        v-model:page-size="pageSize"
        :total="operationLogStore.pagination.total"
        :page-sizes="[10, 20, 50, 100]"
        :background="true"
        layout="total, sizes, prev, pager, next, jumper"
        @update:current-page="handlePageChange"
        @update:page-size="handleSizeChange"
      />
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Search } from '@element-plus/icons-vue'
import { formatDateTime } from '@/utils/date'
import { useOperationLogStore } from '@/stores/auth/operationLogStore'

const loading = ref(false)
const operationLogStore = useOperationLogStore()

// 搜索表单
const searchForm = ref({
  search: '',
  username: '',
  operation_type: '',
  operation_status: ''
})

// 分页相关状态
const currentPage = ref(1)
const pageSize = ref(10)

// 防抖计时器
let searchTimer = null

// 输入搜索处理
const handleInputSearch = () => {
  clearTimeout(searchTimer)
  searchTimer = setTimeout(() => {
    currentPage.value = 1
    fetchData()
  }, 500)
}

// 重置搜索
const resetSearch = () => {
  searchForm.value = {
    search: '',
    username: '',
    operation_type: '',
    operation_status: ''
  }
  currentPage.value = 1
  fetchData()
}

// 获取数据方法
const fetchData = async () => {
  loading.value = true
  try {
    const params = {
      page: currentPage.value,
      per_page: pageSize.value
    }

    if (searchForm.value.search.trim()) {
      params.search = searchForm.value.search.trim()
    }
    if (searchForm.value.username.trim()) {
      params.username = searchForm.value.username.trim()
    }
    if (searchForm.value.operation_type) {
      params.operation_type = searchForm.value.operation_type
    }
    if (searchForm.value.operation_status) {
      params.operation_status = searchForm.value.operation_status
    }

    await operationLogStore.fetchOperationLogs(params)
  } catch (error) {
    ElMessage.error('获取操作日志列表失败: ' + (error.response?.data?.message || error.message))
  } finally {
    loading.value = false
  }
}

// 格式化日期
const formatDate = (row, column, cellValue) => {
  return cellValue ? formatDateTime(cellValue) : '-'
}

// 获取请求方法的标签类型
const getMethodTagType = (method) => {
  const methodMap = {
    GET: 'success',
    POST: 'warning',
    PUT: 'info',
    DELETE: 'danger',
    PATCH: ''
  }
  return methodMap[method] || ''
}

// 获取状态码的标签类型
const getStatusTagType = (statusCode) => {
  if (!statusCode) return ''
  if (statusCode >= 200 && statusCode < 300) return 'success'
  if (statusCode >= 300 && statusCode < 400) return 'info'
  if (statusCode >= 400 && statusCode < 500) return 'warning'
  if (statusCode >= 500) return 'danger'
  return ''
}

// 获取操作类型的标签类型
const getOperationTypeTagType = (type) => {
  const typeMap = {
    login: 'primary',
    logout: 'info',
    create: 'success',
    update: 'warning',
    delete: 'danger',
    query: 'info',
    api_access: 'info',
    other: ''
  }
  return typeMap[type] || ''
}

// 获取操作类型的标签
const getOperationTypeLabel = (type) => {
  const labelMap = {
    login: '登录',
    logout: '登出',
    create: '创建',
    update: '更新',
    delete: '删除',
    query: '查询',
    export: '导出',
    import: '导入',
    api_access: 'API访问',
    other: '其他'
  }
  return labelMap[type] || type
}

// 删除日志
const deleteLog = async (log) => {
  try {
    await ElMessageBox.confirm(`确定要删除这条操作日志吗？`, '删除确认', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })

    loading.value = true
    await operationLogStore.deleteOperationLog(log.id)
    ElMessage.success('删除成功')

    // 如果删除的是当前页最后一条，且不是第一页，则返回上一页
    if (operationLogStore.operationLogs.length === 0 && currentPage.value > 1) {
      currentPage.value -= 1
    }

    fetchData()
  } catch (error) {
    if (error === 'cancel' || error === 'close') {
      ElMessage.info('已取消删除')
    } else {
      ElMessage.error('删除失败: ' + (error.response?.data?.message || error.message))
    }
  } finally {
    loading.value = false
  }
}

// 分页变化
const handlePageChange = (newPage) => {
  currentPage.value = newPage
  fetchData()
}

// 分页大小变化
const handleSizeChange = (newSize) => {
  pageSize.value = newSize
  currentPage.value = 1
  fetchData()
}

// 组件挂载时获取操作日志列表
onMounted(fetchData)
</script>

<style scoped>
/* 使用公共样式，无需额外样式 */
</style>

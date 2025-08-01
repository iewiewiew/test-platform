<template>
  <div class="common-list-container">
    <div class="common-header-bar">
      <div class="common-search-bar">
        <el-form :inline="true" :model="searchForm" class="demo-form-inline">
          <el-form-item label="环境名称">
            <el-input v-model="searchForm.search" placeholder="请输入环境名称" clearable @input="handleInputSearch" />
          </el-form-item>
          <el-form-item>
            <el-button @click="resetSearch">重置</el-button>
          </el-form-item>
        </el-form>
      </div>

      <div class="common-action-bar">
        <el-button type="primary" @click="handleParseEnvironments" :loading="parseLoading">解析配置文件</el-button>
        <el-button type="primary" @click="showCreateDialog = true">新增环境</el-button>
        <el-dropdown @command="(format) => handleExportAll(format)" trigger="click">
          <el-button type="primary" :loading="exportLoading">
            导出所有环境
            <el-icon><ArrowDown /></el-icon>
          </el-button>
          <template #dropdown>
            <el-dropdown-menu>
              <el-dropdown-item command="json">导出为 JSON</el-dropdown-item>
              <el-dropdown-item command="yaml">导出为 YAML</el-dropdown-item>
            </el-dropdown-menu>
          </template>
        </el-dropdown>
      </div>
    </div>

    <el-table :data="tableData" style="width: 100%" v-loading="store.loading" empty-text="暂无数据">
      <el-table-column prop="id" label="ID" width="80" />
      <el-table-column prop="env_name" label="环境名称" width="200" show-overflow-tooltip />
      <el-table-column prop="host" label="Host" width="200" show-overflow-tooltip />
      <el-table-column prop="description" label="描述" show-overflow-tooltip />
      <el-table-column prop="creator_name" label="创建人" width="120" show-overflow-tooltip>
        <template #default="{ row }">
          {{ row.creator_name || '-' }}
        </template>
      </el-table-column>
      <el-table-column prop="updater_name" label="更新人" width="120" show-overflow-tooltip>
        <template #default="{ row }">
          {{ row.updater_name || '-' }}
        </template>
      </el-table-column>
      <el-table-column prop="created_at" label="创建时间" width="160" :formatter="formatDate" />
      <el-table-column prop="updated_at" label="更新时间" width="160" :formatter="formatDate" />

      <el-table-column label="操作" width="150" fixed="right">
        <template #default="scope">
          <el-button size="small" @click="editEnvironment(scope.row)">编辑</el-button>
          <el-button size="small" type="danger" @click="confirmDelete(scope.row)">删除</el-button>
        </template>
      </el-table-column>
    </el-table>

    <div class="pagination">
      <el-pagination
        v-model:current-page="store.pagination.currentPage"
        v-model:page-size="store.pagination.pageSize"
        :total="store.pagination.total"
        :page-sizes="[10, 20, 50, 100]"
        :background="true"
        layout="total, sizes, prev, pager, next, jumper"
        @update:current-page="handlePageChange"
        @update:page-size="handleSizeChange"
      />
    </div>

    <!-- 创建/编辑对话框 -->
    <el-dialog v-model="showCreateDialog" :title="editingItem ? '编辑环境' : '新增环境'" width="60%" :before-close="handleDialogClose">
      <el-form :model="formData" label-width="120px" v-loading="dialogLoading">
        <el-form-item label="环境名称" required>
          <el-input v-model="formData.env_name" placeholder="请输入环境名称" />
        </el-form-item>
        <el-form-item label="描述">
          <el-input v-model="formData.description" type="textarea" :rows="3" placeholder="请输入描述" />
        </el-form-item>
        <el-form-item label="环境配置" required>
          <el-input v-model="formData.env_config_str" type="textarea" :rows="15" placeholder="请输入YAML格式的环境配置" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showCreateDialog = false">取消</el-button>
        <el-button type="primary" @click="handleSubmit" :loading="dialogLoading">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted, computed, watch } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { ArrowDown } from '@element-plus/icons-vue'
import { useTestEnvironmentStore } from '@/stores/test/testEnvironmentStore'
import { testEnvironmentService } from '@/services/test/testEnvironmentService'
import { formatDateTime } from '@/utils/date'
import * as yaml from 'yaml'

const store = useTestEnvironmentStore()

const parseLoading = ref(false)
const showCreateDialog = ref(false)
const dialogLoading = ref(false)
const editingItem = ref(null)
const exportLoading = ref(false)

const searchForm = ref({
  search: ''
})

const formData = ref({
  env_name: '',
  description: '',
  env_config_str: ''
})

const tableData = computed(() => {
  return Array.isArray(store.testEnvironments) ? store.testEnvironments : []
})

const formatDate = (row, column, cellValue) => {
  return cellValue ? formatDateTime(cellValue) : '-'
}

let searchTimer = null

const handleInputSearch = () => {
  clearTimeout(searchTimer)
  searchTimer = setTimeout(() => {
    handleSearch()
  }, 500)
}

const handleSearch = async () => {
  try {
    await store.fetchTestEnvironments({
      page: 1,
      search: searchForm.value.search.trim()
    })
  } catch (error) {
    if (store.error) {
      ElMessage.error(store.error)
    }
  }
}

const resetSearch = async () => {
  searchForm.value = { search: '' }
  try {
    await store.fetchTestEnvironments({ page: 1 })
  } catch (error) {
    if (store.error) {
      ElMessage.error(store.error)
    }
  }
}

const handleParseEnvironments = async () => {
  try {
    parseLoading.value = true
    const result = await store.parseTestEnvironments()
    ElMessage.success(result.message || '解析成功')
    await store.fetchTestEnvironments()
  } catch (error) {
    ElMessage.error(store.error || '解析失败')
  } finally {
    parseLoading.value = false
  }
}

const editEnvironment = async (row) => {
  try {
    await store.fetchTestEnvironment(row.id)
    editingItem.value = store.currentEnvironment
    if (editingItem.value) {
      // 将环境配置转换为 YAML 格式显示
      let envConfig = editingItem.value.env_config
      if (typeof envConfig === 'string') {
        try {
          envConfig = JSON.parse(envConfig)
        } catch (e) {
          // 如果解析失败，尝试作为 YAML 解析
          try {
            envConfig = yaml.parse(envConfig)
          } catch (e2) {
            // 如果都解析失败，直接使用原字符串
            envConfig = envConfig
          }
        }
      }

      // 转换为 YAML 格式，保持与 config.yaml 一致的格式
      const yamlStr = yaml.stringify(envConfig, {
        indent: 2,
        lineWidth: 0,
        quotingType: '"',
        blockQuote: false,
        simpleKeys: false,
        defaultStringType: 'PLAIN'
      })

      formData.value = {
        env_name: editingItem.value.env_name || '',
        description: editingItem.value.description || '',
        env_config_str: yamlStr
      }
      showCreateDialog.value = true
    }
  } catch (error) {
    ElMessage.error(store.error || '获取环境详情失败')
  }
}

const handleDialogClose = (done) => {
  if (!dialogLoading.value) {
    editingItem.value = null
    formData.value = {
      env_name: '',
      description: '',
      env_config_str: ''
    }
    done()
  }
}

const handleSubmit = async () => {
  if (!formData.value.env_name) {
    ElMessage.warning('请输入环境名称')
    return
  }
  if (!formData.value.env_config_str) {
    ElMessage.warning('请输入环境配置')
    return
  }

  try {
    dialogLoading.value = true
    let envConfig
    try {
      // 尝试解析 YAML 格式
      envConfig = yaml.parse(formData.value.env_config_str)
      if (!envConfig || typeof envConfig !== 'object') {
        throw new Error('YAML 解析结果不是对象')
      }
    } catch (e) {
      ElMessage.error('环境配置必须是有效的YAML格式: ' + (e.message || '解析失败'))
      return
    }

    const submitData = {
      env_name: formData.value.env_name,
      description: formData.value.description,
      env_config: envConfig
    }

    if (editingItem.value) {
      await store.updateTestEnvironment(editingItem.value.id, submitData)
      ElMessage.success('更新成功')
    } else {
      await store.createTestEnvironment(submitData)
      ElMessage.success('创建成功')
    }
    showCreateDialog.value = false
    editingItem.value = null
    formData.value = {
      env_name: '',
      description: '',
      env_config_str: ''
    }
  } catch (error) {
    ElMessage.error(store.error || '操作失败')
  } finally {
    dialogLoading.value = false
  }
}

const confirmDelete = (row) => {
  ElMessageBox.confirm(`确定要删除测试环境 "${row.env_name}" 吗？`, '删除确认', {
    confirmButtonText: '确定',
    cancelButtonText: '取消',
    type: 'warning'
  })
    .then(async () => {
      await store.deleteTestEnvironment(row.id)
      ElMessage.success('删除成功')
    })
    .catch(() => {})
}

const handlePageChange = async (newPage) => {
  try {
    await store.fetchTestEnvironments({
      page: newPage,
      search: searchForm.value.search.trim()
    })
  } catch (error) {
    if (store.error) {
      ElMessage.error(store.error)
    }
  }
}

const handleSizeChange = async (newSize) => {
  try {
    await store.fetchTestEnvironments({
      page: 1,
      pageSize: newSize,
      search: searchForm.value.search.trim()
    })
  } catch (error) {
    if (store.error) {
      ElMessage.error(store.error)
    }
  }
}

const handleExportAll = async (format) => {
  try {
    exportLoading.value = true

    const response = await testEnvironmentService.exportAllTestEnvironments(format)

    // 创建下载链接
    const blob = new Blob([response.data], {
      type: format === 'yaml' ? 'application/x-yaml;charset=utf-8' : 'application/json;charset=utf-8'
    })
    const url = window.URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url

    // 从响应头获取文件名，如果没有则生成默认文件名
    const contentDisposition = response.headers['content-disposition']
    let filename = `config_${formatDateTime(new Date()).replace(/[: ]/g, '_')}.${format}`
    if (contentDisposition) {
      const filenameMatch = contentDisposition.match(/filename[^;=\n]*=((['"]).*?\2|[^;\n]*)/)
      if (filenameMatch && filenameMatch[1]) {
        filename = filenameMatch[1].replace(/['"]/g, '')
        // 处理URL编码的文件名
        try {
          filename = decodeURIComponent(filename)
        } catch (e) {
          // 如果解码失败，使用原始文件名
        }
      }
    }

    link.download = filename
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
    window.URL.revokeObjectURL(url)

    ElMessage.success(`成功导出所有环境为 ${format.toUpperCase()} 文件`)
  } catch (error) {
    console.error('导出失败:', error)
    // 如果是blob响应但解析失败，尝试读取错误信息
    if (error.response?.data instanceof Blob) {
      const reader = new FileReader()
      reader.onload = () => {
        try {
          const text = reader.result
          const errorData = JSON.parse(text)
          ElMessage.error('导出失败: ' + (errorData.error || errorData.message || '未知错误'))
        } catch (e) {
          ElMessage.error('导出失败，请检查网络连接')
        }
      }
      reader.readAsText(error.response.data)
    } else {
      ElMessage.error('导出失败: ' + (error.response?.data?.error || error.message || '未知错误'))
    }
  } finally {
    exportLoading.value = false
  }
}

onMounted(async () => {
  await store.fetchTestEnvironments()
})
</script>

<style scoped>
.common-list-container {
  padding: 20px;
}

.common-header-bar {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 20px;
}

.common-search-bar {
  flex: 1;
}

.common-action-bar {
  display: flex;
  gap: 10px;
}

.pagination {
  margin-top: 20px;
  display: flex;
  justify-content: flex-end;
}
</style>

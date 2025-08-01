<template>
  <div class="common-list-container">
    <div class="common-header-bar">
      <div class="common-search-bar">
        <el-form :inline="true" :model="searchForm" class="demo-form-inline">
          <el-form-item label="环境名称">
            <el-input v-model="searchForm.search" placeholder="请输入环境名称" clearable @input="handleInputSearch"/>
          </el-form-item>
          <el-form-item>
            <el-button @click="resetSearch">重置</el-button>
          </el-form-item>
        </el-form>
      </div>

      <div class="common-action-bar">
        <el-button type="primary" @click="handleParseEnvironments" :loading="parseLoading">
          解析配置文件
        </el-button>
        <el-button type="primary" @click="showCreateDialog = true">新增环境</el-button>
      </div>
    </div>

    <el-table 
      :data="tableData" 
      style="width: 100%" 
      v-loading="store.loading"
      empty-text="暂无数据"
    >
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
      <el-table-column prop="created_at" label="创建时间" width="160" :formatter="formatDate"/>
      <el-table-column prop="updated_at" label="更新时间" width="160" :formatter="formatDate"/>

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
    <el-dialog 
      v-model="showCreateDialog" 
      :title="editingItem ? '编辑环境' : '新增环境'" 
      width="60%"
      :before-close="handleDialogClose"
    >
      <el-form :model="formData" label-width="120px" v-loading="dialogLoading">
        <el-form-item label="环境名称" required>
          <el-input v-model="formData.env_name" placeholder="请输入环境名称" />
        </el-form-item>
        <el-form-item label="描述">
          <el-input v-model="formData.description" type="textarea" :rows="3" placeholder="请输入描述" />
        </el-form-item>
        <el-form-item label="环境配置" required>
          <el-input 
            v-model="formData.env_config_str" 
            type="textarea" 
            :rows="15" 
            placeholder="请输入JSON格式的环境配置"
          />
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
import { useTestEnvironmentStore } from '@/stores/test/testEnvironmentStore'
import { formatDateTime } from '@/utils/date'

const store = useTestEnvironmentStore()

const parseLoading = ref(false)
const showCreateDialog = ref(false)
const dialogLoading = ref(false)
const editingItem = ref(null)

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
      formData.value = {
        env_name: editingItem.value.env_name || '',
        description: editingItem.value.description || '',
        env_config_str: typeof editingItem.value.env_config === 'string' 
          ? editingItem.value.env_config 
          : JSON.stringify(editingItem.value.env_config, null, 2)
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
      envConfig = JSON.parse(formData.value.env_config_str)
    } catch (e) {
      ElMessage.error('环境配置必须是有效的JSON格式')
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
  ElMessageBox.confirm(
    `确定要删除测试环境 "${row.env_name}" 吗？`,
    '删除确认',
    {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    }
  )
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


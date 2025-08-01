<template>
  <!-- 环境列表 -->
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
        <el-button type="primary" @click="showEnvironmentDialog()">创建</el-button>
      </div>
    </div>

    <!-- 环境表格 -->
    <el-table :data="environmentStore.environments" v-loading="environmentStore.loading" style="width: 100%"
      empty-text="暂无环境数据">
      <el-table-column prop="id" label="ID" width="60" />
      <el-table-column prop="name" label="环境名称" min-width="150" show-overflow-tooltip />
      <el-table-column prop="base_url" label="基础URL" min-width="200" show-overflow-tooltip />
      <el-table-column prop="username" label="用户名" min-width="100" show-overflow-tooltip />
      <el-table-column prop="description" label="描述" min-width="150" show-overflow-tooltip />
      <el-table-column prop="parameter_count" label="参数数量" width="100">
        <template #default="scope">
          <el-link type="primary" @click="showParameterDrawer(scope.row)">
            {{ scope.row.parameter_count }}
          </el-link>
        </template>
      </el-table-column>
      <el-table-column label="服务器名称" width="150">
        <template #default="scope">
          <el-link v-if="scope.row.server" type="primary" @click="goToServerInfo(scope.row.server.id)">
            {{ scope.row.server.server_name }}
          </el-link>
          <span v-else style="color: #909399;">未关联</span>
        </template>
      </el-table-column>
      <el-table-column prop="creator_name" label="创建人" width="120" />
      <el-table-column prop="updater_name" label="更新人" width="120" />
      <el-table-column prop="created_at" label="创建时间" width="160" :formatter="formatDate" />
      <el-table-column prop="updated_at" label="更新时间" width="160" :formatter="formatDate" />
      <el-table-column label="操作" width="150" fixed="right">
        <template #default="scope">
          <el-button size="small" @click="showEnvironmentDialog(scope.row)">编辑</el-button>
          <el-button size="small" type="danger" @click="handleDeleteEnvironment(scope.row.id)">删除</el-button>
        </template>
      </el-table-column>
    </el-table>

    <!-- 分页 -->
    <div class="pagination">
      <el-pagination v-model:current-page="currentPage" v-model:page-size="pageSize" :page-sizes="[10, 20, 50, 100]"
        :total="environmentStore.pagination.total" :background="true" layout="total, sizes, prev, pager, next, jumper"
        @update:current-page="handlePageChange" @update:page-size="handleSizeChange" />
    </div>
  </div>

  <!-- 环境编辑对话框 -->
  <el-dialog v-model="environmentDialog.visible" :title="environmentDialog.isEdit ? '编辑' : '创建'" width="500px">
    <el-form ref="environmentFormRef" :model="environmentDialog.form" :rules="environmentRules" label-width="100px">
      <el-form-item label="环境名称" prop="name">
        <el-input v-model="environmentDialog.form.name" placeholder="请输入环境名称" />
      </el-form-item>
      <el-form-item label="基础URL" prop="base_url">
        <el-input v-model="environmentDialog.form.base_url" placeholder="请输入基础URL" />
      </el-form-item>
      <el-form-item label="用户名">
        <el-input v-model="environmentDialog.form.username" placeholder="请输入用户名" />
      </el-form-item>
      <el-form-item label="密码">
        <el-input v-model="environmentDialog.form.password" type="password" placeholder="请输入密码" show-password />
      </el-form-item>
      <el-form-item label="服务器名称">
        <el-select v-model="environmentDialog.form.server_id" placeholder="请选择服务器" clearable filterable style="width: 100%">
          <el-option
            v-for="server in serverOptions"
            :key="server.id"
            :label="server.server_name"
            :value="server.id"
          >
            <span>{{ server.server_name }}</span>
            <span style="color: #8492a6; font-size: 13px; margin-left: 10px;">{{ server.host }}</span>
          </el-option>
        </el-select>
      </el-form-item>
      <el-form-item label="描述">
        <el-input v-model="environmentDialog.form.description" type="textarea" :rows="3" placeholder="请输入环境描述" />
      </el-form-item>
    </el-form>
    <template #footer>
      <span class="dialog-footer">
        <el-button @click="environmentDialog.visible = false">取消</el-button>
        <el-button type="primary" @click="handleEnvironmentSubmit">确定</el-button>
      </span>
    </template>
  </el-dialog>

  <!-- 参数管理抽屉 -->
  <el-drawer v-model="parameterDrawer.visible" :title="`${parameterDrawer.environmentName} - 参数管理`" size="45%" direction="rtl">
    <template #header>
      <div class="card-header">
        <div class="header-title">{{ parameterDrawer.environmentName }} - 参数管理</div>
        <div>
          <el-button @click="handleAddInlineRow">创建</el-button>
        </div>
      </div>
    </template>

    <!-- 左侧：参数列表与搜索 -->
    <div class="common-header-bar">
      <div class="common-search-bar">
        <el-form :inline="true" :model="parameterSearchForm" class="demo-form-inline" label-width="auto">
          <el-form-item label="参数键">
            <el-input v-model="parameterSearchForm.param_key" placeholder="请输入参数键" clearable @input="handleParameterInputSearch" style="width: 180px" />
          </el-form-item>
          <el-form-item label="描述">
            <el-input v-model="parameterSearchForm.description" placeholder="请输入描述" clearable @input="handleParameterInputSearch" style="width: 180px" />
          </el-form-item>
          <el-form-item>
            <el-button @click="resetParameterSearch">重置</el-button>
          </el-form-item>
        </el-form>
      </div>
    </div>

    <el-table :data="tableParameters" v-loading="environmentStore.loading" style="width: 100%" empty-text="暂无参数数据">
      <el-table-column prop="id" label="ID" width="60" />
      <el-table-column label="参数键" min-width="160">
        <template #default="scope">
          <el-input v-model="scope.row.param_key" placeholder="请输入参数键" @blur="() => handleRowBlur(scope.row)" clearable />
        </template>
      </el-table-column>
      <el-table-column label="参数值" min-width="220">
        <template #default="scope">
          <el-input v-model="scope.row.param_value" type="textarea" :rows="1" placeholder="请输入参数值" @blur="() => handleRowBlur(scope.row)" />
        </template>
      </el-table-column>
      <el-table-column label="描述" min-width="180">
        <template #default="scope">
          <el-input v-model="scope.row.description" placeholder="请输入描述" @blur="() => handleRowBlur(scope.row)" clearable />
        </template>
      </el-table-column>
      <el-table-column prop="creator_name" label="创建人" width="120" />
      <el-table-column prop="updater_name" label="更新人" width="120" />
      <el-table-column prop="created_at" label="创建时间" width="160" :formatter="formatDate" />
      <el-table-column prop="updated_at" label="更新时间" width="160" :formatter="formatDate" />
      <el-table-column label="操作" width="80" fixed="right">
        <template #default="scope">
          <el-button size="small" type="danger" @click="handleDeleteParameter(scope.row.id)" :disabled="scope.row._isNew">删除</el-button>
        </template>
      </el-table-column>
    </el-table>

    <div class="pagination">
      <el-pagination v-model:current-page="parameterCurrentPage" v-model:page-size="parameterPageSize" :page-sizes="[10, 20, 50, 100]" :total="environmentStore.parameterPagination.total" :background="true" layout="total, sizes, prev, pager, next, jumper" @update:current-page="handleParameterPageChange" @update:page-size="handleParameterSizeChange" />
    </div>
  </el-drawer>
</template>

<script setup>
import { ref, reactive, onMounted, onUnmounted } from 'vue'
import { computed } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { useEnvironmentStore } from '@/stores/project/environmentStore'
import { linuxInfoService } from '@/services/tool/linuxInfoService'
import { formatDateTime } from '@/utils/date'

const loading = ref(false)
const router = useRouter()

const environmentStore = useEnvironmentStore()
const serverOptions = ref([])

// 搜索表单
const searchForm = ref({
  name: '',
  base_url: '',
  description: ''
})

const parameterSearchForm = ref({
  param_key: '',
  description: ''
})

// 分页相关状态
const currentPage = ref(1)
const pageSize = ref(10)
const parameterCurrentPage = ref(1)
const parameterPageSize = ref(10)

// 防抖计时器
let searchTimer = null
let parameterSearchTimer = null


// 环境对话框
const environmentDialog = reactive({
  visible: false,
  isEdit: false,
  form: {
    name: '',
    base_url: '',
    username: '',
    password: '',
    description: '',
    server_id: null
  }
})

// 参数抽屉 + 行内创建/编辑
const parameterDrawer = reactive({
  visible: false,
  environmentName: ''
})

const inlineNewRowActive = ref(false)
const inlineNewRow = reactive({ param_key: '', param_value: '', description: '', _isNew: true })
const savingMap = reactive({})

const tableParameters = computed(() => {
  const base = environmentStore.parameters || []
  return inlineNewRowActive.value ? [...base, inlineNewRow] : base
})

// 表单引用
const environmentFormRef = ref()
const parameterFormRef = ref()

// 表单验证规则
const environmentRules = {
  name: [{ required: true, message: '请输入环境名称', trigger: 'blur' }],
  base_url: [{ required: true, message: '请输入基础URL', trigger: 'blur' }]
}

const parameterRules = {
  param_key: [{ required: true, message: '请输入参数键', trigger: 'blur' }],
  param_value: [{ required: true, message: '请输入参数值', trigger: 'blur' }]
}

// 统一的数据获取方法
const fetchEnvironments = async () => {
  loading.value = true

  try {
    const params = {
      page: currentPage.value,
      pageSize: pageSize.value,
      search: searchForm.value.name || searchForm.value.base_url || searchForm.value.description 
        ? `${searchForm.value.name} ${searchForm.value.base_url} ${searchForm.value.description}`.trim()
        : ''
    }
    
    await environmentStore.fetchEnvironments(params)
  } catch (error) {
    console.error('Error fetching environments:', error)
    ElMessage.error('获取环境数据失败')
  }
}

const fetchParameters = async () => {
  if (!environmentStore.currentEnvironment) return
  
  try {
    const params = {
      page: parameterCurrentPage.value,
      pageSize: parameterPageSize.value,
      search: parameterSearchForm.value.param_key || parameterSearchForm.value.description
        ? `${parameterSearchForm.value.param_key} ${parameterSearchForm.value.description}`.trim()
        : ''
    }
    
    await environmentStore.fetchEnvironmentParameters(environmentStore.currentEnvironment.id, params)
  } catch (error) {
    console.error('Error fetching parameters:', error)
    ElMessage.error('获取参数数据失败')
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

const handleParameterInputSearch = () => {
  clearTimeout(parameterSearchTimer)
  parameterSearchTimer = setTimeout(() => {
    parameterCurrentPage.value = 1
    fetchParameters()
  }, 500)
}

// 重置搜索
const resetSearch = () => {
  searchForm.value = {
    name: '',
    base_url: '',
    description: ''
  }
  currentPage.value = 1
  fetchEnvironments()
}

const resetParameterSearch = () => {
  parameterSearchForm.value = {
    param_key: '',
    description: ''
  }
  parameterCurrentPage.value = 1
  fetchParameters()
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

const handleParameterPageChange = (newPage) => {
  parameterCurrentPage.value = newPage
  fetchParameters()
}

const handleParameterSizeChange = (newSize) => {
  parameterPageSize.value = newSize
  parameterCurrentPage.value = 1
  fetchParameters()
}

// 日期格式化
const formatDate = (row, column, cellValue) => {
  return cellValue ? formatDateTime(cellValue) : '-'
}

// 获取服务器列表
const fetchServerOptions = async () => {
  try {
    const response = await linuxInfoService.getServers({ page: 1, per_page: 1000 })
    serverOptions.value = response.data || []
  } catch (error) {
    console.error('获取服务器列表失败:', error)
  }
}

// 跳转到服务器信息页
const goToServerInfo = (serverId) => {
  router.push(`/linux-info`)
}

// 生命周期
onMounted(() => {
  fetchEnvironments()
  fetchServerOptions()
})

// 环境管理方法
const showEnvironmentDialog = (environment = null) => {
  environmentDialog.isEdit = !!environment
  environmentDialog.form = environment
    ? { ...environment, server_id: environment.server_id || null }
    : { name: '', base_url: '', username: '', password: '', description: '', server_id: null }
  environmentDialog.visible = true
}

const handleEnvironmentSubmit = async () => {
  if (!environmentFormRef.value) return

  await environmentFormRef.value.validate(async (valid) => {
    if (valid) {
      try {
        if (environmentDialog.isEdit) {
          await environmentStore.updateEnvironment(environmentDialog.form.id, environmentDialog.form)
          ElMessage.success('环境更新成功')
        } else {
          await environmentStore.createEnvironment(environmentDialog.form)
          ElMessage.success('环境创建成功')
        }
        environmentDialog.visible = false
        fetchEnvironments()
      } catch (error) {
        console.error('环境操作失败:', error)
        ElMessage.error(`操作失败: ${environmentStore.error || error.message || '未知错误'}`)
      }
    }
  })
}

const handleDeleteEnvironment = async (id) => {
  try {
    await ElMessageBox.confirm('确定要删除这个环境吗？', '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })
    await environmentStore.deleteEnvironment(id)
    ElMessage.success('删除成功')
    fetchEnvironments()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('删除失败')
    }
  }
}

// 参数管理方法
const showParameterDrawer = async (environment) => {
  try {
    environmentStore.setCurrentEnvironment(environment)
    parameterDrawer.environmentName = environment.name
    parameterDrawer.visible = true
    
    // 重置参数搜索和分页
    resetParameterSearch()
    await fetchParameters()
    // 关闭可能遗留的行内创建
    inlineNewRowActive.value = false
  } catch (error) {
    console.error('打开参数对话框失败:', error)
    ElMessage.error('加载参数失败')
  }
}

const handleAddInlineRow = () => {
  inlineNewRow.param_key = ''
  inlineNewRow.param_value = ''
  inlineNewRow.description = ''
  inlineNewRowActive.value = true
}

const handleRowBlur = async (row) => {
  if (!environmentStore.currentEnvironment) return

  // 防重复提交
  const key = row._isNew ? 'new' : row.id
  if (savingMap[key]) return

  // 创建：仅当必填项具备时保存
  if (row._isNew) {
    if (!row.param_key || !row.param_value) return
    try {
      savingMap[key] = true
      await environmentStore.createEnvironmentParameter(environmentStore.currentEnvironment.id, {
        param_key: row.param_key,
        param_value: row.param_value,
        description: row.description || ''
      })
      ElMessage.success('参数创建成功')
      inlineNewRowActive.value = false
      await fetchParameters()
    } catch (error) {
      ElMessage.error(`创建失败: ${environmentStore.error || error.message || '未知错误'}`)
    } finally {
      savingMap[key] = false
    }
    return
  }

  // 更新：当任一字段发生变更时保存（这里直接提交整行字段）
  try {
    if (!row.param_key || !row.param_value) return
    savingMap[key] = true
    await environmentStore.updateEnvironmentParameter(row.id, {
      param_key: row.param_key,
      param_value: row.param_value,
      description: row.description || ''
    })
    ElMessage.success('已保存')
  } catch (error) {
    ElMessage.error(`保存失败: ${environmentStore.error || error.message || '未知错误'}`)
  } finally {
    savingMap[key] = false
  }
}

const handleDeleteParameter = async (id) => {
  try {
    await ElMessageBox.confirm('确定要删除这个参数吗？', '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })
    await environmentStore.deleteEnvironmentParameter(id)
    ElMessage.success('删除成功')
    await fetchParameters()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('删除失败')
    }
  }
}
</script>

<style scoped>
/* 对话框内参数管理的头部栏样式 */
.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 20px;
  border-bottom: 1px solid #ebeef5;
}

.header-title {
  font-size: 16px;
  font-weight: 600;
  color: #303133;
}
</style>
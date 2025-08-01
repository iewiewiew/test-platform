<template>
  <div class="common-list-container">
    <div class="test-case-header">
      <div class="common-search-bar">
        <el-form :inline="true" :model="searchForm" class="demo-form-inline search-form-inline">
          <el-form-item label="用例名称">
            <el-input v-model="searchForm.search" placeholder="请输入用例名称" clearable @input="handleInputSearch" style="width: 180px"/>
          </el-form-item>
          <el-form-item label="组件名称">
            <el-select v-model="searchForm.component_name" placeholder="请选择或搜索组件名称" clearable filterable @change="handleSearch" style="width: 180px">
              <el-option v-for="component in componentNames" :key="component" :label="component" :value="component" />
            </el-select>
          </el-form-item>
          <el-form-item label="模块名称">
            <el-select 
              v-model="searchForm.module_name" 
              placeholder="请选择或搜索模块名称" 
              clearable 
              filterable
              @change="handleSearch" 
              style="width: 180px"
            >
              <el-option 
                v-for="module in moduleNames" 
                :key="module" 
                :label="module" 
                :value="module" 
              />
            </el-select>
          </el-form-item>
          <el-form-item label="测试环境">
            <el-select v-model="searchForm.environment" placeholder="请选择测试环境" clearable @change="handleSearch" style="width: 180px">
              <el-option 
                v-for="env in environments" 
                :key="env.id" 
                :label="env.env_name" 
                :value="env.env_name" 
              />
            </el-select>
          </el-form-item>
          <el-form-item>
            <el-button @click="resetSearch">重置</el-button>
          </el-form-item>
        </el-form>
      </div>
      <div class="common-action-bar">
        <el-button type="primary" @click="handleAdd">新增测试用例</el-button>
        <el-button type="primary" @click="handleParseTestCases" :loading="parseLoading">
          解析测试用例
        </el-button>
        <div style="display: flex; align-items: center; gap: 8px;">
          <el-tooltip 
            :content="pytestLoading ? '正在执行测试用例，请前往测试报告查看详情' : '执行Pytest测试'" 
            placement="top"
          >
            <el-button type="success" @click="handleExecutePytest" :loading="pytestLoading" :disabled="!searchForm.environment">
              执行Pytest测试
            </el-button>
          </el-tooltip>
          <el-tooltip content="请先选择测试组件或者测试模块，必须选择测试环境，测试执行后请前往测试报告查看结果" placement="top">
            <el-icon :size="16" style="cursor: pointer; color: #909399;">
              <QuestionFilled />
            </el-icon>
          </el-tooltip>
        </div>
      </div>
    </div>

    <el-table 
      :data="tableData" 
      style="width: 100%" 
      v-loading="store.loading"
      empty-text="暂无数据"
    >
      <el-table-column prop="id" label="ID" width="80" />
      <el-table-column prop="test_case_id" label="用例ID" width="80" />
      <el-table-column prop="component_name" label="组件名称" width="100" show-overflow-tooltip />
      <el-table-column prop="test_module_name" label="模块名称" width="120" show-overflow-tooltip />
      <el-table-column prop="test_case_name" label="用例名称" width="200" show-overflow-tooltip />
      <el-table-column prop="request_method" label="请求方法" width="100">
        <template #default="{ row }">
          <el-tag :type="getMethodType(row.request_method)">
            {{ row.request_method }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="path" label="请求路径" width="220" show-overflow-tooltip />
      <el-table-column prop="request_body" label="请求体" width="120">
        <template #default="{ row }">
          <div class="request-body-cell">
            <span v-if="!row.request_body || row.request_body === 'None'">-</span>
            <el-tooltip 
              v-else
              placement="top"
              effect="light"
              :raw-content="true"
              popper-class="request-body-tooltip"
            >
              <template #content>
                <pre class="tooltip-json-content">{{ formatRequestBodyForTooltip(row.request_body) }}</pre>
              </template>
              <span class="request-body-text">Body</span>
            </el-tooltip>
          </div>
        </template>
      </el-table-column>
      <el-table-column prop="assert_status" label="断言状态码" width="120">
        <template #default="{ row }"></template>
      </el-table-column>
      <el-table-column prop="is_skip" label="是否跳过" width="100">
        <template #default="{ row }">
          <el-tag :type="row.is_skip === 'yes' ? 'warning' : 'success'">
            {{ row.is_skip === 'yes' ? '是' : '否' }}
          </el-tag>
        </template>
      </el-table-column>
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
          <el-button size="small" type="primary" @click="handleEdit(scope.row)">编辑</el-button>
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

    <!-- 执行结果对话框 -->
    <el-dialog v-model="showResultDialog" title="测试执行结果" width="80%">
      <div v-if="testResult">
        <el-descriptions title="请求信息" :column="2" border>
          <el-descriptions-item label="URL">{{ testResult.request?.url }}</el-descriptions-item>
          <el-descriptions-item label="方法">{{ testResult.request?.method }}</el-descriptions-item>
          <el-descriptions-item label="请求头" :span="2">
            <pre>{{ JSON.stringify(testResult.request?.headers, null, 2) }}</pre>
          </el-descriptions-item>
          <el-descriptions-item label="请求参数" :span="2">
            <pre>{{ JSON.stringify(testResult.request?.params, null, 2) }}</pre>
          </el-descriptions-item>
          <el-descriptions-item label="请求体" :span="2">
            <pre>{{ JSON.stringify(testResult.request?.body, null, 2) }}</pre>
          </el-descriptions-item>
        </el-descriptions>
        <el-descriptions title="响应信息" :column="2" border style="margin-top: 20px">
          <el-descriptions-item label="状态码">
            <el-tag :type="testResult.response?.status_code < 400 ? 'success' : 'danger'">
              {{ testResult.response?.status_code }}
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="响应数据" :span="2">
            <pre>{{ JSON.stringify(testResult.response?.data, null, 2) }}</pre>
          </el-descriptions-item>
        </el-descriptions>
        <div v-if="testResult.assert_result" style="margin-top: 20px">
          <el-alert 
            :title="testResult.assert_result.status_assert ? '断言通过' : '断言失败'"
            :type="testResult.assert_result.status_assert ? 'success' : 'error'"
            :description="`期望状态码: ${testResult.assert_result.expected_status}, 实际状态码: ${testResult.assert_result.actual_status}`"
            show-icon
          />
        </div>
      </div>
    </el-dialog>

    <!-- 请求体查看对话框 -->
    <el-dialog v-model="showRequestBodyDialog" title="请求体详情" width="50%">
      <div v-if="currentRequestBody">
        <pre class="request-body-dialog-content">{{ currentRequestBody }}</pre>
        <div style="margin-top: 20px; text-align: right;">
          <el-button @click="copyRequestBody">复制内容</el-button>
        </div>
      </div>
    </el-dialog>

    <!-- 新增/编辑测试用例对话框 -->
    <el-dialog v-model="showEditDialog" :title="isEditMode ? '编辑测试用例' : '新增测试用例'" width="50%" @close="resetEditForm">
      <el-form :model="editForm" :rules="editRules" ref="editFormRef" label-width="120px">
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="用例ID" prop="test_case_id">
              <el-input v-model="editForm.test_case_id" placeholder="请输入用例ID" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="用例名称" prop="test_case_name">
              <el-input v-model="editForm.test_case_name" placeholder="请输入用例名称" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="模块名称" prop="test_module_name">
              <el-input v-model="editForm.test_module_name" placeholder="请输入模块名称" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="组件名称" prop="component_name">
              <el-select v-model="editForm.component_name" placeholder="请选择组件名称" clearable filterable style="width: 100%">
                <el-option v-for="component in componentNames" :key="component" :label="component" :value="component" />
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="请求方法" prop="request_method">
              <el-select v-model="editForm.request_method" placeholder="请选择请求方法" style="width: 100%">
                <el-option label="GET" value="GET" />
                <el-option label="POST" value="POST" />
                <el-option label="PUT" value="PUT" />
                <el-option label="DELETE" value="DELETE" />
                <el-option label="PATCH" value="PATCH" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="是否跳过" prop="is_skip">
              <el-select v-model="editForm.is_skip" placeholder="请选择" style="width: 100%">
                <el-option label="否" value="no" />
                <el-option label="是" value="yes" />
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>
        <el-form-item label="请求路径" prop="path">
          <el-input v-model="editForm.path" placeholder="请输入请求路径" />
        </el-form-item>
        <el-form-item label="请求参数">
          <el-input 
            v-model="editForm.request_param" 
            type="textarea" 
            :rows="3"
            placeholder="请输入请求参数（JSON格式）" 
          />
        </el-form-item>
        <el-form-item label="请求体">
          <el-input 
            v-model="editForm.request_body" 
            type="textarea" 
            :rows="3"
            placeholder="请输入请求体（JSON格式）" 
          />
        </el-form-item>
        <el-form-item label="响应体">
          <el-input 
            v-model="editForm.response_body" 
            type="textarea" 
            :rows="1"
            placeholder="请输入响应体" 
          />
        </el-form-item>
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="断言状态码">
              <el-input v-model="editForm.assert_status" placeholder="请输入断言状态码，多个用逗号分隔" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="断言值">
              <el-input v-model="editForm.assert_value" placeholder="请输入断言值" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-form-item label="Pytest注解">
          <el-input 
            v-model="editForm.pytest_annotation" 
            type="textarea" 
            :rows="1"
            placeholder="请输入Pytest注解" 
          />
        </el-form-item>
        <el-form-item label="文件路径">
          <el-input v-model="editForm.file_path" placeholder="请输入文件路径" />
        </el-form-item>
      </el-form>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="showEditDialog = false">取消</el-button>
          <el-button type="primary" @click="handleSaveEdit" :loading="editLoading">
            {{ isEditMode ? '保存' : '创建' }}
          </el-button>
        </span>
      </template>
    </el-dialog>

  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { ElMessage, ElMessageBox, ElIcon } from 'element-plus'
import { QuestionFilled } from '@element-plus/icons-vue'
import { useTestCaseStore } from '@/stores/test/testCaseStore'
import { useTestEnvironmentStore } from '@/stores/test/testEnvironmentStore'
import { pytestExecutorService } from '@/services/test/pytestExecutorService'
import { formatDateTime } from '@/utils/date'

const store = useTestCaseStore()
const envStore = useTestEnvironmentStore()

const parseLoading = ref(false)
const pytestLoading = ref(false)
const showResultDialog = ref(false)
const showRequestBodyDialog = ref(false)
const showEditDialog = ref(false)
const editLoading = ref(false)
const isEditMode = ref(false)
const currentRequestBody = ref(null)
const testResult = ref(null)
const environments = ref([])
const editFormRef = ref(null)
const editForm = ref({
  id: null,
  test_case_id: '',
  test_case_name: '',
  test_module_name: '',
  component_name: '',
  request_method: 'GET',
  path: '',
  request_body: '',
  request_param: '',
  response_body: '',
  assert_status: '',
  assert_value: '',
  pytest_annotation: '',
  is_skip: 'no',
  file_path: ''
})
const editRules = {
  test_case_name: [
    { required: true, message: '请输入用例名称', trigger: 'blur' }
  ],
  test_module_name: [
    { required: true, message: '请输入模块名称', trigger: 'blur' }
  ],
  request_method: [
    { required: true, message: '请选择请求方法', trigger: 'change' }
  ],
  path: [
    { required: true, message: '请输入请求路径', trigger: 'blur' }
  ]
}

const searchForm = ref({
  search: '',
  component_name: '',
  module_name: '',
  environment: 'premium_k8s'
})

const tableData = computed(() => {
  return Array.isArray(store.testCases) ? store.testCases : []
})

// 模块名称列表（从所有测试用例中获取）
const moduleNames = computed(() => {
  return store.moduleNames || []
})

// 组件名称列表（从testdata目录获取）
const componentNames = computed(() => {
  return store.componentNames || []
})

const getMethodType = (method) => {
  const methodMap = {
    'GET': 'info',
    'POST': 'success',
    'PUT': 'warning',
    'DELETE': 'danger',
    'PATCH': 'warning'
  }
  return methodMap[method] || ''
}

const formatDate = (row, column, cellValue) => {
  return cellValue ? formatDateTime(cellValue) : '-'
}

const formatRequestBody = (requestBody) => {
  if (!requestBody || requestBody === 'None') {
    return '-'
  }
  
  // 尝试解析为JSON并格式化
  try {
    const parsed = JSON.parse(requestBody)
    const formatted = JSON.stringify(parsed, null, 2)
    // 如果格式化后太长，只显示前几行
    const lines = formatted.split('\n')
    if (lines.length > 3) {
      return lines.slice(0, 3).join('\n') + '\n...'
    }
    return formatted
  } catch (e) {
    // 如果不是JSON，直接返回原文本（截断过长的内容）
    return requestBody.length > 100 ? requestBody.substring(0, 100) + '...' : requestBody
  }
}

const formatRequestBodyFull = (requestBody) => {
  if (!requestBody || requestBody === 'None') {
    return '-'
  }
  
  // 尝试解析为JSON并格式化（完整版本，用于tooltip）
  try {
    const parsed = JSON.parse(requestBody)
    return JSON.stringify(parsed, null, 2)
  } catch (e) {
    // 如果不是JSON，返回原文本
    return requestBody
  }
}

const formatRequestBodyForTooltip = (requestBody) => {
  if (!requestBody || requestBody === 'None') {
    return '无请求体'
  }
  
  // 尝试解析为JSON并格式化（用于tooltip显示）
  try {
    const parsed = JSON.parse(requestBody)
    return JSON.stringify(parsed, null, 2)
  } catch (e) {
    // 如果不是JSON，返回原文本
    return requestBody
  }
}

const openRequestBodyDialog = (requestBody) => {
  if (!requestBody || requestBody === 'None') {
    ElMessage.info('该测试用例没有请求体')
    return
  }
  currentRequestBody.value = requestBody
  showRequestBodyDialog.value = true
}

const copyRequestBody = async () => {
  if (!currentRequestBody.value) return
  
  try {
    const textToCopy = formatRequestBodyFull(currentRequestBody.value)
    await navigator.clipboard.writeText(textToCopy)
    ElMessage.success('已复制到剪贴板')
  } catch (error) {
    // 降级方案
    const textArea = document.createElement('textarea')
    textArea.value = formatRequestBodyFull(currentRequestBody.value)
    textArea.style.position = 'fixed'
    textArea.style.opacity = '0'
    document.body.appendChild(textArea)
    textArea.select()
    try {
      document.execCommand('copy')
      ElMessage.success('已复制到剪贴板')
    } catch (err) {
      ElMessage.error('复制失败')
    }
    document.body.removeChild(textArea)
  }
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
    await store.fetchTestCases({
      page: 1,
      search: searchForm.value.search.trim(),
      component_name: searchForm.value.component_name,
      module_name: searchForm.value.module_name,
      environment: searchForm.value.environment
    })
  } catch (error) {
    if (store.error) {
      ElMessage.error(store.error)
    }
  }
}

const resetSearch = async () => {
  searchForm.value = { search: '', component_name: '', module_name: '', environment: 'premium_k8s' }
  try {
    await store.fetchTestCases({ 
      page: 1,
      component_name: '',
      module_name: '',
      environment: 'premium_k8s'
    })
  } catch (error) {
    if (store.error) {
      ElMessage.error(store.error)
    }
  }
}

const handleParseTestCases = async () => {
  try {
    parseLoading.value = true
    const result = await store.parseTestCases()
    
    // 显示详细的结果信息
    let message = result.message || '解析成功'
    if (result.created_count !== undefined && result.updated_count !== undefined) {
      if (result.created_count > 0 && result.updated_count > 0) {
        message = `成功处理 ${result.total_count || 0} 条测试用例（新增 ${result.created_count} 条，更新 ${result.updated_count} 条）`
      } else if (result.created_count > 0) {
        message = `成功新增 ${result.created_count} 条测试用例`
      } else if (result.updated_count > 0) {
        message = `成功更新 ${result.updated_count} 条测试用例`
      }
    }
    
    ElMessage.success(message)
    await store.fetchTestCases()
    // 解析后刷新模块名称和组件名称列表
    await store.fetchModuleNames()
    await store.fetchComponentNames()
  } catch (error) {
    ElMessage.error(store.error || '解析失败')
  } finally {
    parseLoading.value = false
  }
}

const handleExecutePytest = async () => {
  // 必须选择测试环境，且至少选择测试组件或测试模块之一
  if (!searchForm.value.environment || (!searchForm.value.component_name && !searchForm.value.module_name)) {
    ElMessage.warning('请先选择测试组件或者测试模块，必须选择测试环境')
    return
  }

  try {
    pytestLoading.value = true
    // 过滤空字符串，只传递有效值
    const params = {
      environment_name: searchForm.value.environment
    }
    
    // 传递组件名称（如果选择了）
    if (searchForm.value.component_name && searchForm.value.component_name.trim()) {
      params.component_name = searchForm.value.component_name.trim()
    }
    
    // 传递模块名称（如果选择了）
    // 以用户最终筛选的条件为准，不需要考虑默认值
    if (searchForm.value.module_name && searchForm.value.module_name.trim()) {
      params.module_name = searchForm.value.module_name.trim()
    }
    
    console.log('执行Pytest测试，参数：', params)
    const response = await pytestExecutorService.executePytest(params)
    
    if (response.data.code === 0) {
      ElMessage.success('Pytest测试执行完成，请前往测试报告页面查看详情')
    } else {
      ElMessage.error(response.data.message || '执行失败')
    }
  } catch (error) {
    // 处理不同类型的错误
    console.error('Pytest执行错误详情:', error)
    if (error.code === 'ECONNABORTED' || error.message?.includes('timeout')) {
      // 超时错误：可能是执行时间过长，但后端可能已经成功执行
      ElMessage.warning('请求超时，但测试可能仍在执行中。请稍后查看测试报告页面。')
    } else if (error.response) {
      // 有响应但状态码不是2xx
      const errorMsg = error.response.data?.error || error.response.data?.message || '执行失败'
      console.error('后端错误信息:', errorMsg)
      ElMessage.error(`执行失败: ${errorMsg}`)
    } else if (error.request) {
      // 请求已发出但没有收到响应
      ElMessage.error('网络错误，请检查网络连接或稍后重试')
    } else {
      // 其他错误
      ElMessage.error(error.message || '执行失败')
    }
  } finally {
    pytestLoading.value = false
  }
}


const executeTestCase = async (row) => {
  try {
    const result = await store.executeTestCase(row.id, {
      environment_name: searchForm.value.environment
    })
    if (result.code === 0) {
      testResult.value = result
      showResultDialog.value = true
    } else {
      ElMessage.error(result.message || '执行失败')
    }
  } catch (error) {
    ElMessage.error(store.error || '执行失败')
  }
}

const handleAdd = () => {
  isEditMode.value = false
  resetEditForm()
  showEditDialog.value = true
}

const handleEdit = (row) => {
  isEditMode.value = true
  editForm.value = {
    id: row.id,
    test_case_id: row.test_case_id || '',
    test_case_name: row.test_case_name || '',
    test_module_name: row.test_module_name || '',
    component_name: row.component_name || '',
    request_method: row.request_method || 'GET',
    path: row.path || '',
    request_body: row.request_body || '',
    request_param: row.request_param || '',
    response_body: row.response_body || '',
    assert_status: row.assert_status || '',
    assert_value: row.assert_value || '',
    pytest_annotation: row.pytest_annotation || '',
    is_skip: row.is_skip || 'no',
    file_path: row.file_path || ''
  }
  showEditDialog.value = true
}

const resetEditForm = () => {
  editFormRef.value?.resetFields()
  editForm.value = {
    id: null,
    test_case_id: '',
    test_case_name: '',
    test_module_name: '',
    component_name: '',
    request_method: 'GET',
    path: '',
    request_body: '',
    request_param: '',
    response_body: '',
    assert_status: '',
    assert_value: '',
    pytest_annotation: '',
    is_skip: 'no',
    file_path: ''
  }
  isEditMode.value = false
}

const handleSaveEdit = async () => {
  if (!editFormRef.value) return
  
  try {
    await editFormRef.value.validate()
    editLoading.value = true
    
    const formData = {
      test_case_id: editForm.value.test_case_id,
      test_case_name: editForm.value.test_case_name,
      test_module_name: editForm.value.test_module_name,
      component_name: editForm.value.component_name,
      request_method: editForm.value.request_method,
      path: editForm.value.path,
      request_body: editForm.value.request_body,
      request_param: editForm.value.request_param,
      response_body: editForm.value.response_body,
      assert_status: editForm.value.assert_status,
      assert_value: editForm.value.assert_value,
      pytest_annotation: editForm.value.pytest_annotation,
      is_skip: editForm.value.is_skip,
      file_path: editForm.value.file_path
    }
    
    if (isEditMode.value) {
      // 编辑模式：更新测试用例
      await store.updateTestCase(editForm.value.id, formData)
      ElMessage.success('更新成功')
    } else {
      // 新增模式：创建测试用例
      await store.createTestCase(formData)
      ElMessage.success('创建成功')
    }
    
    showEditDialog.value = false
  } catch (error) {
    if (error !== false) { // 表单验证失败时 error 为 false
      ElMessage.error(store.error || (isEditMode.value ? '更新失败' : '创建失败'))
    }
  } finally {
    editLoading.value = false
  }
}

const confirmDelete = (row) => {
  ElMessageBox.confirm(
    `确定要删除测试用例 "${row.test_case_name}" 吗？`,
    '删除确认',
    {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    }
  )
    .then(async () => {
      await store.deleteTestCase(row.id)
      ElMessage.success('删除成功')
    })
    .catch(() => {})
}

const handlePageChange = async (newPage) => {
  try {
    await store.fetchTestCases({
      page: newPage,
      search: searchForm.value.search.trim(),
      component_name: searchForm.value.component_name,
      module_name: searchForm.value.module_name,
      environment: searchForm.value.environment
    })
  } catch (error) {
    if (store.error) {
      ElMessage.error(store.error)
    }
  }
}

const handleSizeChange = async (newSize) => {
  try {
    await store.fetchTestCases({
      page: 1,
      pageSize: newSize,
      search: searchForm.value.search.trim(),
      component_name: searchForm.value.component_name,
      module_name: searchForm.value.module_name,
      environment: searchForm.value.environment
    })
  } catch (error) {
    if (store.error) {
      ElMessage.error(store.error)
    }
  }
}

onMounted(async () => {
  // 先获取环境和模块列表
  environments.value = await envStore.fetchTestEnvironmentsForSelect()
  await store.fetchModuleNames()
  await store.fetchComponentNames()
  
  // 验证默认值是否存在，如果不存在则清空
  if (searchForm.value.component_name && !store.componentNames.includes(searchForm.value.component_name)) {
    searchForm.value.component_name = ''
  }
  if (searchForm.value.module_name && !store.moduleNames.includes(searchForm.value.module_name)) {
    searchForm.value.module_name = ''
  }
  if (searchForm.value.environment && !environments.value.find(env => env.env_name === searchForm.value.environment)) {
    searchForm.value.environment = ''
  }
  
  // 使用默认值加载数据
  await store.fetchTestCases({
    page: 1,
    component_name: searchForm.value.component_name || undefined,
    module_name: searchForm.value.module_name || undefined,
    environment: searchForm.value.environment || undefined
  })
})
</script>

<style scoped>
/* 使用公共样式，移除重复定义 */
/* 页面特定样式 */

/* 测试用例头部布局 - 搜索栏和操作按钮分行显示 */
.test-case-header {
  display: flex;
  flex-direction: column;
  gap: 16px;
  margin-bottom: 20px;
}

/* 搜索栏占满整行 */
.test-case-header .common-search-bar {
  width: 100%;
}

/* 操作按钮区域 */
.test-case-header .common-action-bar {
  display: flex;
  align-items: center;
  gap: 10px;
  flex-shrink: 0;
}

/* 搜索表单保持在同一行 */
.search-form-inline {
  display: flex;
  flex-wrap: nowrap;
  align-items: center;
  overflow-x: auto;
  overflow-y: hidden;
  white-space: nowrap;
}

.search-form-inline :deep(.el-form-item) {
  flex-shrink: 0;
  margin-right: 16px;
  margin-bottom: 0;
  white-space: nowrap;
}

.search-form-inline :deep(.el-form-item__label) {
  white-space: nowrap;
  flex-shrink: 0;
}

.search-form-inline :deep(.el-form-item__content) {
  flex-shrink: 0;
}

/* 搜索栏容器样式 */
.common-search-bar {
  overflow-x: auto;
  overflow-y: hidden;
  min-width: 0;
}

.common-search-bar::-webkit-scrollbar {
  height: 6px;
}

.common-search-bar::-webkit-scrollbar-track {
  background: #f1f1f1;
  border-radius: 3px;
}

.common-search-bar::-webkit-scrollbar-thumb {
  background: #c1c1c1;
  border-radius: 3px;
}

.common-search-bar::-webkit-scrollbar-thumb:hover {
  background: #a8a8a8;
}

.request-body-cell {
  max-width: 300px;
}

.request-body-text {
  font-family: 'Courier New', monospace;
  font-size: 12px;
  white-space: pre-wrap;
  word-wrap: break-word;
  word-break: break-all;
  display: block;
  max-height: 60px;
  overflow: hidden;
  text-overflow: ellipsis;
  line-height: 1.4;
}

.request-body-clickable {
  cursor: pointer;
  color: #409eff;
  transition: color 0.3s;
}

.request-body-clickable:hover {
  color: #66b1ff;
  text-decoration: underline;
}

.request-body-dialog-content {
  font-family: 'Courier New', monospace;
  font-size: 13px;
  white-space: pre-wrap;
  word-wrap: break-word;
  word-break: break-all;
  max-height: 500px;
  overflow: auto;
  margin: 0;
  padding: 15px;
  background: #f5f5f5;
  border-radius: 4px;
  border: 1px solid #e4e7ed;
  line-height: 1.6;
  width: 100%;
  box-sizing: border-box;
  overflow-x: hidden;
}

/* Tooltip样式 - 使用深度选择器 */
:deep(.request-body-tooltip) {
  max-width: 600px !important;
  padding: 0 !important;
  background: linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%) !important;
  border: 1px solid #cbd5e1 !important;
  box-shadow: 0 4px 16px 0 rgba(0, 0, 0, 0.12) !important;
  border-radius: 8px !important;
}

.tooltip-json-content {
  margin: 0;
  padding: 15px;
  white-space: pre-wrap;
  word-wrap: break-word;
  max-width: 600px;
  max-height: 400px;
  overflow: auto;
  font-family: 'Courier New', 'Consolas', monospace;
  font-size: 13px;
  line-height: 1.6;
  color: #1e293b;
  background: linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%);
  border-radius: 8px;
}
</style>


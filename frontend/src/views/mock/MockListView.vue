<template>
  <div class="common-list-container">
    <div class="common-header-bar">
      <div class="common-search-bar">
        <el-form :inline="true" :model="searchForm" class="demo-form-inline">
          <el-form-item label="接口名称">
            <el-input v-model="searchForm.name" placeholder="请输入接口名称" clearable @input="handleInputSearch"/>
          </el-form-item>
          <el-form-item label="接口路径">
            <el-input v-model="searchForm.path" placeholder="请输入接口路径" clearable @input="handleInputSearch"/>
          </el-form-item>
          <el-form-item label="接口方法">
            <el-select v-model="searchForm.method" placeholder="请选择接口方法" clearable @change="handleInputSearch">
              <el-option label="GET" value="GET" />
              <el-option label="POST" value="POST" />
              <el-option label="PUT" value="PUT" />
              <el-option label="DELETE" value="DELETE" />
            </el-select>
          </el-form-item>
          <el-form-item>
            <el-button @click="resetSearch">重置</el-button>
          </el-form-item>
        </el-form>
      </div>

      <div class="common-action-bar">
        <el-button type="primary" @click="handleCreateButtonClick">创建</el-button>
      </div>
    </div>

    <el-table :data="mockStore.mocks" style="width: 100%" v-loading="loading">
      <el-table-column prop="id" label="ID" width="60" />
      <el-table-column prop="name" label="接口名称" width="200" show-overflow-tooltip />
      <el-table-column prop="path" label="接口路径" width="200" show-overflow-tooltip/>
      <el-table-column prop="method" label="接口方法" width="100" />
      <el-table-column prop="response_status" label="状态码" width="100" />
      <el-table-column prop="project_name" label="项目名称" width="100" show-overflow-tooltip/>
      <el-table-column prop="creator_name" label="创建人" width="120" />
      <el-table-column prop="updater_name" label="更新人" width="120" />
      <el-table-column prop="created_at" label="创建时间" width="160" sortable :formatter="formatDate"/>
      <el-table-column prop="updated_at" label="更新时间" width="160" sortable :formatter="formatDate"/>

      <el-table-column label="操作" width="250" fixed="right">
        <template #default="scope">
          <el-tooltip effect="dark" placement="top" :content="getCurlTooltipContent(scope.row)">
            <el-button size="small" type="success" @click="copyCurlCommand(scope.row)">复制CURL</el-button>
          </el-tooltip>
          <el-button size="small" @click="editMock(scope.row.id)">编辑</el-button>
          <el-button size="small" type="danger" @click="confirmDelete(scope.row)">删除</el-button>
        </template>
      </el-table-column>
    </el-table>

    <div class="pagination">
      <el-pagination
        v-model:current-page="currentPage"
        v-model:page-size="pageSize"
        :total="mockStore.pagination.total"
        :page-sizes="[10, 20, 50, 100]"
        :background="true"
        layout="total, sizes, prev, pager, next, jumper"
        @update:current-page="handlePageChange"
        @update:page-size="handleSizeChange"
      />
    </div>

    <el-dialog v-model="showCreateDialog" title="创建">
      <mock-form ref="createFormRef" @submit="handleCreate" @cancel="showCreateDialog = false" />
    </el-dialog>

    <el-dialog v-model="showEditDialog" title="编辑">
      <mock-form ref="editFormRef" :mock="mockStore.currentMock" @submit="handleUpdate" @cancel="showEditDialog = false"/>
    </el-dialog>
  </div>
</template>

<script setup>
import MockForm from '@/components/mock/MockForm.vue'
import { ref, onMounted, nextTick, watch } from 'vue'
import { useClipboard } from '@vueuse/core'
import { ElMessage, ElMessageBox } from 'element-plus'
import { useMockStore } from '@/stores/mock/mockStore'
import { formatDateTime } from '@/utils/date'
import { useRoute } from 'vue-router'

const route = useRoute()
const loading = ref(false)
const showCreateDialog = ref(false)
const showEditDialog = ref(false)
const mockStore = useMockStore()
const { copy, isSupported } = useClipboard()

// 添加表单引用
const createFormRef = ref(null)
const editFormRef = ref(null)

// 搜索表单
const searchForm = ref({
  name: '',
  path: '',
  method: ''
})

// 分页相关状态
const currentPage = ref(1)
const pageSize = ref(10)

// 防抖计时器
let searchTimer = null

// 统一的数据获取方法
const fetchData = async () => {
  loading.value = true
  try {
    const params = {
      page: currentPage.value,
      pageSize: pageSize.value,
      name: searchForm.value.name.trim(),
      path: searchForm.value.path.trim(),
      method: searchForm.value.method
    }
    
    // 如果有项目ID，添加到参数中
    if (route.query.project_id) {
      params.project_id = route.query.project_id
    }
    
    await mockStore.fetchMocks(params)
  } catch (error) {
    console.error('Error fetching data:', error)
    ElMessage.error('获取数据失败: ' + (error.response?.data?.message || error.message))
  } finally {
    loading.value = false
  }
}

// 输入搜索处理
const handleInputSearch = () => {
  clearTimeout(searchTimer)
  searchTimer = setTimeout(() => {
    currentPage.value = 1
    fetchData()
  }, 500) // 500ms防抖延迟
}

const formatDate = (row, column, cellValue) => {
  return cellValue ? formatDateTime(cellValue) : '-'
}

// 监听路由参数变化
watch(
  () => route.query.project_id,
  (newProjectId) => {
    // 重置分页和搜索条件
    currentPage.value = 1
    searchForm.value = { name: '', path: '', method: '' }
    fetchData()
  }
)

// 只在组件挂载时执行一次
onMounted(() => {
  fetchData()
})

// 重置搜索
const resetSearch = () => {
  searchForm.value = {
    name: '',
    path: '',
    method: ''
  }
  currentPage.value = 1
  fetchData()
}

// 分页处理
const handlePageChange = (newPage) => {
  currentPage.value = newPage
  fetchData()
}

const handleSizeChange = (newSize) => {
  pageSize.value = newSize
  currentPage.value = 1
  fetchData()
}

const copyCurlCommand = async (mock) => {
  try {
    loading.value = true;
    
    const apiPath = typeof mock.path === 'string' 
      ? mock.path.replace(/^\/+/, '') 
      : '';

    // 使用URLSearchParams构造正确的查询参数
    const params = new URLSearchParams();
    params.append('method', mock.method);  // 正确格式: method=POST

    // 调用store方法
    const response = await mockStore.generateCurlCommand({
      api_path: apiPath,  // 例如: "api/users"
      method: mock.method || 'GET' // 默认GET方法
    });

    // 复制到剪贴板
    if (isSupported) {
      await copy(response.curl_command);
    } else {
      const textarea = document.createElement('textarea');
      textarea.value = response.curl_command;
      document.body.appendChild(textarea);
      textarea.select();
      document.execCommand('copy');
      document.body.removeChild(textarea);
    }
    
    ElMessage.success('CURL命令已复制');
  } catch (error) {
    ElMessage.error(`复制失败: ${error.message}`);
  } finally {
    loading.value = false;
  }
};

// 添加获取CURL提示内容的方法
const getCurlTooltipContent = (mock) => {
  const baseUrl = window.location.origin; // 获取当前站点基础URL
  const method = mock.method || 'GET';
  const path = mock?.path ? mock.path.replace(/^\/+/, '') : '';
  let curlCommand = `curl -X ${method} "${baseUrl}/api/mock/execute/${path}"`;

  // 如果是POST/PUT请求，添加请求头和请求体
  if (['POST', 'PUT'].includes(method) && mock.response_body) {
    curlCommand += ` \\\n  -H "Content-Type: application/json"`;
    
    try {
      // 尝试解析JSON，确保格式正确
      JSON.parse(mock.response_body);
      curlCommand += ` \\\n  -d '${mock.response_body}'`;
    } catch {
      curlCommand += ` \\\n  -d '${JSON.stringify(mock.response_body)}'`;
    }
  }
  
  // 使用<pre>标签保持格式
  return `${curlCommand}`;
};

// 创建Mock接口
const handleCreate = async (mockData) => {
  try {
    loading.value = true
    await mockStore.createMock(mockData)
    showCreateDialog.value = false
    ElMessage.success('Mock API 创建成功')
    fetchData()
  } catch (error) {
    ElMessage.error('创建 Mock API 失败')
  } finally {
    loading.value = false
  }
}

const editMock = async (id) => {
  try {
    loading.value = true
    await mockStore.fetchMock(id)
    showEditDialog.value = true
  } catch (error) {
    ElMessage.error('获取Mock详情失败')
  } finally {
    loading.value = false
  }
}

const handleUpdate = async (mockData) => {
  try {
    loading.value = true
    await mockStore.updateMock(mockStore.currentMock.id, mockData)
    showEditDialog.value = false
    ElMessage.success('Mock API 更新成功')
    fetchData()
  } catch (error) {
    ElMessage.error('更新 Mock API 失败')
  } finally {
    loading.value = false
  }
}

// 修改创建对话框的显示逻辑
const handleCreateButtonClick = () => {
  showCreateDialog.value = true
  
  // 等待对话框渲染完成后调用子组件的 loadData 方法
  nextTick(() => {
    createFormRef.value?.loadData()
  })
}

const confirmDelete = (mock) => {
  ElMessageBox.confirm(
    `确定要删除 Mock 接口 "${mock.name}" (${mock.method} ${mock.path}) 吗？`,
    '删除确认',
    {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    }
  )
    .then(async () => {
      await deleteMock(mock.id)
    })
    .catch(() => {
      ElMessage.info('已取消删除')
    })
}

const deleteMock = async (id) => {
  try {
    loading.value = true
    await mockStore.deleteMock(id)
    ElMessage.success('Mock API 删除成功')
    fetchData()
  } catch (error) {
    ElMessage.error('Mock API 删除失败')
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
/* 选择框宽度 */
.el-select {
  width: 180px;
}

@media (max-width: 768px) {
  :deep(.el-select) {
    width: 100%;
  }
}
</style>
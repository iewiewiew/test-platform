<template>
  <div class="common-list-container">
    <div class="common-header-bar">
      <div class="common-search-bar">
        <el-form :inline="true" :model="searchForm" class="demo-form-inline">
          <el-form-item label="项目名称">
            <el-input v-model="searchForm.name" placeholder="请输入项目名称" clearable @input="handleInputSearch" />
          </el-form-item>
          <el-form-item>
            <el-button @click="resetSearch">重置</el-button>
          </el-form-item>
        </el-form>
      </div>

      <div class="common-action-bar">
        <el-button type="primary" @click="showCreateDialog = true">创建</el-button>
      </div>
    </div>

    <el-table :data="projectStore.projects" style="width: 100%" v-loading="loading">
      <el-table-column prop="id" label="ID" width="60" />
      <el-table-column prop="name" label="项目名称" width="200" />
      <el-table-column prop="description" label="项目描述" show-overflow-tooltip />
      <el-table-column prop="mock_count" label="接口数量" width="120" align="center">
        <template #default="{ row }">
          <el-tag>{{ row.mock_count || 0 }}</el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="creator_name" label="创建人" width="120" />
      <el-table-column prop="updater_name" label="更新人" width="120" />
      <el-table-column prop="created_at" label="创建时间" width="160" sortable :formatter="formatDate" />
      <el-table-column prop="updated_at" label="更新时间" width="160" sortable :formatter="formatDate" />

      <el-table-column label="操作" width="250" fixed="right">
        <template #default="scope">
          <el-button size="small" @click="goToMockList(scope.row.id)">查看接口</el-button>
          <el-button size="small" @click="editProject(scope.row.id)">编辑</el-button>
          <el-button size="small" type="danger" @click="deleteProject(scope.row)">删除</el-button>
        </template>
      </el-table-column>
    </el-table>

    <div class="pagination">
      <el-pagination v-model:current-page="currentPage" v-model:page-size="pageSize"
        :total="projectStore.pagination.total" :page-sizes="[10, 20, 50, 100]" :background="true"
        layout="total, sizes, prev, pager, next, jumper" @update:current-page="handlePageChange"
        @update:page-size="handleSizeChange" />
    </div>

    <!-- 创建项目对话框 -->
    <el-dialog v-model="showCreateDialog" title="创建">
      <project-form @submit="handleCreate" @cancel="showCreateDialog = false" />
    </el-dialog>

    <!-- 编辑项目对话框 -->
    <el-dialog v-model="showEditDialog" title="编辑">
      <project-form :project="projectStore.currentProject" @submit="handleUpdate" @cancel="showEditDialog = false" />
    </el-dialog>
  </div>
</template>

<script setup>
import ProjectForm from '@/components/project/ProjectForm.vue'
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { formatDateTime } from '@/utils/date'
import { useProjectStore } from '@/stores/project/projectStore'

const router = useRouter()
const loading = ref(false)
const showCreateDialog = ref(false)
const showEditDialog = ref(false)
const projectStore = useProjectStore()

// 搜索表单
const searchForm = ref({
  name: ''
})

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
  searchForm.value = { name: '' }
  currentPage.value = 1
  fetchData()
}

// 获取数据方法
const fetchData = async () => {
  loading.value = true
  try {
    await projectStore.fetchProjects({
      page: currentPage.value,
      pageSize: pageSize.value,
      name: searchForm.value.name.trim()
    })
  } catch (error) {
    ElMessage.error('获取项目列表失败: ' + (error.response?.data?.message || error.message))
  } finally {
    loading.value = false
  }
}

// 格式化日期
const formatDate = (row, column, cellValue) => {
  return cellValue ? formatDateTime(cellValue) : '-'
}

// 跳转到Mock接口列表
const goToMockList = async (projectId) => {
  console.log('项目列表的 project_id:', projectId)

  try {
    // 跳转
    router.push({
      name: 'MockList',
      query: { project_id: projectId }
    })
  } catch (error) {
    console.error('获取 Mock 数据失败:', error)
  }
}

// 创建项目
const handleCreate = async (projectData) => {
  try {
    loading.value = true
    await projectStore.createProject(projectData)
    showCreateDialog.value = false
    ElMessage.success('项目创建成功')
    fetchData()
  } catch (error) {
    ElMessage.error('创建项目失败: ' + (error.response?.data?.error || error.message))
  } finally {
    loading.value = false
  }
}

// 获取项目详情
const editProject = async (id) => {
  try {
    loading.value = true
    await projectStore.fetchProject(id)
    showEditDialog.value = true
  } catch (error) {
    ElMessage.error('获取项目详情失败')
  } finally {
    loading.value = false
  }
}

// 更新项目
const handleUpdate = async (projectData) => {
  try {
    loading.value = true
    await projectStore.updateProject(projectStore.currentProject.id, projectData)
    showEditDialog.value = false
    ElMessage.success('项目更新成功')
    fetchData()
  } catch (error) {
    ElMessage.error('更新项目失败: ' + (error.response?.data?.error || error.message))
  } finally {
    loading.value = false
  }
}

// 删除项目
const deleteProject = async (project) => {
  try {
    await ElMessageBox.confirm(
      `确定要删除项目 "${project.name}" 吗？该项目包含 ${project.mock_api_count || 0} 个接口`,
      '删除确认',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )

    // 用户确认删除
    loading.value = true
    await projectStore.deleteProject(project.id)
    ElMessage.success('项目删除成功')

    // 如果删除的是当前页最后一条，且不是第一页，则返回上一页
    if (projectStore.projects.length === 0 && currentPage.value > 1) {
      currentPage.value -= 1
    }

    fetchData()

  } catch (error) {
    // 用户取消删除或其他错误
    if (error === 'cancel' || error === 'close') {
      ElMessage.info('已取消删除')
    } else {
      ElMessage.error('项目删除失败: ' + (error.response?.data?.error || error.message))
    }
  } finally {
    loading.value = false
  }
}

// 组件挂载时获取项目列表
onMounted(fetchData)

// 分页相关状态
const currentPage = ref(1)
const pageSize = ref(10)

// 分页相关状态
const handlePageChange = (newPage) => {
  currentPage.value = newPage
  fetchData()
}

// 分页相关状态
const handleSizeChange = (newSize) => {
  pageSize.value = newSize
  currentPage.value = 1
  fetchData()
}
</script>

<style scoped>
/* 使用公共样式，无需额外样式 */
</style>
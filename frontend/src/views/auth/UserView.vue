<template>
  <div class="common-list-container">
    <div class="common-header-bar">
      <div class="common-search-bar">
        <el-form :inline="true" :model="searchForm" class="demo-form-inline">
          <el-form-item label="搜索">
            <el-input
              v-model="searchForm.search"
              placeholder="请输入用户名、邮箱或姓名"
              clearable
              @input="handleInputSearch"
              :prefix-icon="Search"
            />
          </el-form-item>
          <el-form-item>
            <el-button @click="resetSearch">重置</el-button>
          </el-form-item>
        </el-form>
      </div>

      <div class="common-action-bar">
        <el-button type="primary" @click="showCreateDialog = true" v-permission="'user:write'">
          创建用户
        </el-button>
      </div>
    </div>

    <el-table :data="userStore.users" style="width: 100%" v-loading="loading">
      <el-table-column prop="id" label="ID" width="60" />
      <el-table-column prop="username" label="用户名" width="150" />
      <el-table-column prop="email" label="邮箱" width="200" show-overflow-tooltip />
      <el-table-column prop="full_name" label="姓名" width="120" />
      <el-table-column prop="role_name" label="角色" width="120" />
      <el-table-column prop="is_active" label="状态" width="100" align="center">
        <template #default="{ row }">
          <el-tag :type="row.is_active ? 'success' : 'danger'">
            {{ row.is_active ? '激活' : '禁用' }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="creator_name" label="创建人" width="120" />
      <el-table-column prop="updater_name" label="更新人" width="120" />
      <el-table-column prop="created_at" label="创建时间" width="160" :formatter="formatDate" />
      <el-table-column prop="updated_at" label="更新时间" width="160" :formatter="formatDate" />

      <el-table-column label="操作" width="200" fixed="right">
        <template #default="scope">
          <el-button size="small" @click="editUser(scope.row.id)" v-permission="'user:write'">
            编辑
          </el-button>
          <el-button
            size="small"
            type="danger"
            @click="deleteUser(scope.row)"
            v-permission="'user:delete'"
          >
            删除
          </el-button>
        </template>
      </el-table-column>
    </el-table>

    <div class="pagination">
      <el-pagination
        v-model:current-page="currentPage"
        v-model:page-size="pageSize"
        :total="userStore.pagination.total"
        :page-sizes="[10, 20, 50, 100]"
        :background="true"
        layout="total, sizes, prev, pager, next, jumper"
        @update:current-page="handlePageChange"
        @update:page-size="handleSizeChange"
      />
    </div>

    <!-- 创建用户对话框 -->
    <el-dialog v-model="showCreateDialog" title="创建">
      <UserForm @submit="handleCreate" @cancel="showCreateDialog = false" />
    </el-dialog>

    <!-- 编辑用户对话框 -->
    <el-dialog v-model="showEditDialog" title="编辑">
      <UserForm
        :user="userStore.currentUser"
        @submit="handleUpdate"
        @cancel="showEditDialog = false"
      />
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Search } from '@element-plus/icons-vue'
import { formatDateTime } from '@/utils/date'
import { useUserStore } from '@/stores/auth/userStore'
import UserForm from '@/components/user/UserForm.vue'

const loading = ref(false)
const showCreateDialog = ref(false)
const showEditDialog = ref(false)
const userStore = useUserStore()

// 搜索表单
const searchForm = ref({
  search: ''
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
  searchForm.value = { search: '' }
  currentPage.value = 1
  fetchData()
}

// 获取数据方法
const fetchData = async () => {
  loading.value = true
  try {
    await userStore.fetchUsers({
      page: currentPage.value,
      per_page: pageSize.value,
      search: searchForm.value.search.trim()
    })
  } catch (error) {
    ElMessage.error('获取用户列表失败: ' + (error.response?.data?.message || error.message))
  } finally {
    loading.value = false
  }
}

// 格式化日期
const formatDate = (row, column, cellValue) => {
  return cellValue ? formatDateTime(cellValue) : '-'
}

// 创建用户
const handleCreate = async (userData) => {
  try {
    loading.value = true
    await userStore.createUser(userData)
    showCreateDialog.value = false
    ElMessage.success('用户创建成功')
    fetchData()
  } catch (error) {
    ElMessage.error('创建用户失败: ' + (error.response?.data?.message || error.message))
  } finally {
    loading.value = false
  }
}

// 获取用户详情
const editUser = async (id) => {
  console.log('用户 ID: ', id)
  try {
    loading.value = true
    await userStore.fetchUserById(id)
    showEditDialog.value = true
  } catch (error) {
    ElMessage.error('获取用户详情失败')
  } finally {
    loading.value = false
  }
}

// 更新用户
const handleUpdate = async (userData) => {
  try {
    loading.value = true
    await userStore.updateUser(userStore.currentUser.id, userData)
    showEditDialog.value = false
    ElMessage.success('用户更新成功')
    fetchData()
  } catch (error) {
    ElMessage.error('更新用户失败: ' + (error.response?.data?.message || error.message))
  } finally {
    loading.value = false
  }
}

// 删除用户
const deleteUser = async (user) => {
  try {
    await ElMessageBox.confirm(
      `确定要删除用户 "${user.username}" 吗？`,
      '删除确认',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )

    loading.value = true
    await userStore.deleteUser(user.id)
    ElMessage.success('用户删除成功')

    // 如果删除的是当前页最后一条，且不是第一页，则返回上一页
    if (userStore.users.length === 0 && currentPage.value > 1) {
      currentPage.value -= 1
    }

    fetchData()

  } catch (error) {
    if (error === 'cancel' || error === 'close') {
      ElMessage.info('已取消删除')
    } else {
      ElMessage.error('用户删除失败: ' + (error.response?.data?.message || error.message))
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

// 组件挂载时获取用户列表
onMounted(fetchData)
</script>

<style scoped>
/* 使用公共样式，无需额外样式 */
</style>
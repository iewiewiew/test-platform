<template>
  <div class="common-list-container">
    <div class="common-header-bar">
      <div class="common-search-bar">
        <el-form :inline="true" :model="searchForm" class="demo-form-inline">
          <el-form-item label="角色名称">
            <el-input 
              v-model="searchForm.name" 
              placeholder="请输入角色名称" 
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
        <el-button type="primary" @click="showCreateDialog = true" v-permission="'role:write'">
          创建角色
        </el-button>
      </div>
    </div>

    <el-table :data="roleStore.roles" style="width: 100%" v-loading="loading">
      <el-table-column prop="id" label="ID" width="60" />
      <el-table-column prop="name" label="角色名称" width="150" />
      <el-table-column prop="description" label="角色描述" width="150" show-overflow-tooltip />
      <el-table-column prop="user_count" label="用户数量" width="120" align="center">
        <template #default="{ row }">
          <el-tag>{{ row.user_count || 0 }}</el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="permissions" label="权限数量" width="120" align="center">
        <template #default="{ row }">
          <el-tag type="info">{{ getPermissionCount(row) }}</el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="creator_name" label="创建人" width="120" />
      <el-table-column prop="updater_name" label="更新人" width="120" />
      <el-table-column prop="created_at" label="创建时间" width="160" :formatter="formatDate" />
      <el-table-column prop="updated_at" label="更新时间" width="160" :formatter="formatDate" />

      <el-table-column label="操作" width="200" fixed="right">
        <template #default="scope">
          <el-button size="small" @click="editRole(scope.row.id)" v-permission="'role:write'">
            编辑
          </el-button>
          <el-button 
            size="small" 
            type="danger" 
            @click="deleteRole(scope.row)"
            v-permission="'role:write'"
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
        :total="roleStore.pagination?.total || 0" 
        :page-sizes="[10, 20, 50, 100]" 
        :background="true"
        layout="total, sizes, prev, pager, next, jumper" 
        @update:current-page="handlePageChange"
        @update:page-size="handleSizeChange" 
      />
    </div>

    <!-- 创建角色对话框 -->
    <el-dialog v-model="showCreateDialog" title="创建" width="600px">
      <RoleForm @submit="handleCreate" @cancel="showCreateDialog = false" />
    </el-dialog>

    <!-- 编辑角色对话框 -->
    <el-dialog v-model="showEditDialog" title="编辑" width="600px">
      <RoleForm 
        :role="roleStore.currentRole" 
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
import { useRoleStore } from '@/stores/auth/roleStore'
import RoleForm from '@/components/user/RoleForm.vue'

const loading = ref(false)
const showCreateDialog = ref(false)
const showEditDialog = ref(false)
const roleStore = useRoleStore()

// 搜索表单
const searchForm = ref({
  name: ''
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
  searchForm.value = { name: '' }
  currentPage.value = 1
  fetchData()
}

// 获取数据方法
const fetchData = async () => {
  loading.value = true
  try {
    await roleStore.fetchRoles({
      page: currentPage.value,
      per_page: pageSize.value,
      name: searchForm.value.name.trim()
    })
  } catch (error) {
    ElMessage.error('获取角色列表失败: ' + (error.response?.data?.message || error.message))
  } finally {
    loading.value = false
  }
}

// 格式化日期
const formatDate = (row, column, cellValue) => {
  return cellValue ? formatDateTime(cellValue) : '-'
}

// 获取权限数量
const getPermissionCount = (role) => {
  if (!role || role.permissions == null) return 0
  // 后端可能返回数组或字符串，均需兼容
  if (Array.isArray(role.permissions)) {
    return role.permissions.length
  }
  if (typeof role.permissions === 'string') {
    try {
      const parsed = JSON.parse(role.permissions)
      return Array.isArray(parsed) ? parsed.length : 0
    } catch {
      return 0
    }
  }
  return 0
}

// 创建角色
const handleCreate = async (roleData) => {
  try {
    loading.value = true
    await roleStore.createRole(roleData)
    showCreateDialog.value = false
    ElMessage.success('角色创建成功')
    fetchData()
  } catch (error) {
    ElMessage.error('创建角色失败: ' + (error.response?.data?.message || error.message))
  } finally {
    loading.value = false
  }
}

// 获取角色详情
const editRole = async (id) => {
  try {
    loading.value = true
    await roleStore.fetchRoleById(id)
    showEditDialog.value = true
  } catch (error) {
    ElMessage.error('获取角色详情失败')
  } finally {
    loading.value = false
  }
}

// 更新角色
const handleUpdate = async (roleData) => {
  try {
    loading.value = true
    await roleStore.updateRole(roleStore.currentRole.id, roleData)
    showEditDialog.value = false
    ElMessage.success('角色更新成功')
    fetchData()
  } catch (error) {
    ElMessage.error('更新角色失败: ' + (error.response?.data?.message || error.message))
  } finally {
    loading.value = false
  }
}

// 删除角色
const deleteRole = async (role) => {
  try {
    await ElMessageBox.confirm(
      `确定要删除角色 "${role.name}" 吗？该角色下有 ${role.user_count || 0} 个用户`,
      '删除确认',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )

    loading.value = true
    await roleStore.deleteRole(role.id)
    ElMessage.success('角色删除成功')

    // 如果删除的是当前页最后一条，且不是第一页，则返回上一页
    if (roleStore.roles.length === 0 && currentPage.value > 1) {
      currentPage.value -= 1
    }

    fetchData()

  } catch (error) {
    if (error === 'cancel' || error === 'close') {
      ElMessage.info('已取消删除')
    } else {
      ElMessage.error('角色删除失败: ' + (error.response?.data?.message || error.message))
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

// 组件挂载时获取角色列表
onMounted(fetchData)
</script>

<style scoped>
/* 使用公共样式，无需额外样式 */
</style>
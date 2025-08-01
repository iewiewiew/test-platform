<template>
  <div class="common-list-container">
    <div class="common-header-bar">
      <div class="common-search-bar">
        <el-form :inline="true" :model="searchForm" class="demo-form-inline">
          <el-form-item label="搜索">
            <el-input v-model="searchForm.name" placeholder="请输入通知名称" clearable @input="handleInputSearch" :prefix-icon="Search" />
          </el-form-item>
          <el-form-item label="类型">
            <el-select v-model="searchForm.notification_type" placeholder="请选择类型" clearable @change="handleInputSearch" style="width: 150px">
              <el-option label="飞书" value="feishu" />
              <el-option label="钉钉" value="dingtalk" />
              <el-option label="企业微信" value="wechat_work" />
              <el-option label="自定义" value="custom" />
            </el-select>
          </el-form-item>
          <el-form-item>
            <el-button @click="resetSearch">重置</el-button>
          </el-form-item>
        </el-form>
      </div>

      <div class="common-action-bar">
        <el-button type="primary" @click="showCreateDialog = true" v-permission="'user:write'">创建通知</el-button>
      </div>
    </div>

    <el-table :data="notificationStore.notifications" style="width: 100%" v-loading="loading">
      <el-table-column prop="id" label="ID" width="60" />
      <el-table-column prop="name" label="通知名称" width="150" />
      <el-table-column prop="notification_type" label="通知类型" width="120">
        <template #default="{ row }">
          <el-tag :type="getTypeTagType(row.notification_type)">
            {{ getTypeLabel(row.notification_type) }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="webhook_url" label="Webhook URL" width="300" show-overflow-tooltip />
      <el-table-column prop="is_enabled" label="状态" width="100" align="center">
        <template #default="{ row }">
          <el-tag :type="row.is_enabled ? 'success' : 'danger'">
            {{ row.is_enabled ? '启用' : '禁用' }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="description" label="描述" width="200" show-overflow-tooltip />
      <el-table-column prop="creator_name" label="创建人" width="120" />
      <el-table-column prop="updater_name" label="更新人" width="120" />
      <el-table-column prop="created_at" label="创建时间" width="160" :formatter="formatDate" />
      <el-table-column prop="updated_at" label="更新时间" width="160" :formatter="formatDate" />

      <el-table-column label="操作" width="250" fixed="right">
        <template #default="scope">
          <el-button size="small" @click="testNotification(scope.row)" v-permission="'user:write'">测试</el-button>
          <el-button size="small" @click="editNotification(scope.row.id)" v-permission="'user:write'">编辑</el-button>
          <el-button size="small" type="danger" @click="deleteNotification(scope.row)" v-permission="'user:delete'">删除</el-button>
        </template>
      </el-table-column>
    </el-table>

    <div class="pagination">
      <el-pagination
        v-model:current-page="currentPage"
        v-model:page-size="pageSize"
        :total="notificationStore.pagination.total"
        :page-sizes="[10, 20, 50, 100]"
        :background="true"
        layout="total, sizes, prev, pager, next, jumper"
        @update:current-page="handlePageChange"
        @update:page-size="handleSizeChange"
      />
    </div>

    <!-- 创建通知对话框 -->
    <el-dialog v-model="showCreateDialog" title="创建通知" width="600px">
      <NotificationForm @submit="handleCreate" @cancel="showCreateDialog = false" />
    </el-dialog>

    <!-- 编辑通知对话框 -->
    <el-dialog v-model="showEditDialog" title="编辑通知" width="600px">
      <NotificationForm :notification="notificationStore.currentNotification" @submit="handleUpdate" @cancel="showEditDialog = false" />
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Search } from '@element-plus/icons-vue'
import { formatDateTime } from '@/utils/date'
import { useNotificationStore } from '@/stores/notification/notificationStore'
import NotificationForm from '@/components/notification/NotificationForm.vue'

const loading = ref(false)
const showCreateDialog = ref(false)
const showEditDialog = ref(false)
const notificationStore = useNotificationStore()

// 搜索表单
const searchForm = ref({
  name: '',
  notification_type: ''
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
  searchForm.value = { name: '', notification_type: '' }
  currentPage.value = 1
  fetchData()
}

// 获取数据方法
const fetchData = async () => {
  loading.value = true
  try {
    await notificationStore.fetchNotifications({
      page: currentPage.value,
      per_page: pageSize.value,
      name: searchForm.value.name.trim() || undefined,
      notification_type: searchForm.value.notification_type || undefined
    })
  } catch (error) {
    ElMessage.error('获取通知列表失败: ' + (error.response?.data?.message || error.message))
  } finally {
    loading.value = false
  }
}

// 格式化日期
const formatDate = (row, column, cellValue) => {
  return cellValue ? formatDateTime(cellValue) : '-'
}

// 获取类型标签
const getTypeLabel = (type) => {
  const typeMap = {
    feishu: '飞书',
    dingtalk: '钉钉',
    wechat_work: '企业微信',
    custom: '自定义'
  }
  return typeMap[type] || type
}

// 获取类型标签颜色
const getTypeTagType = (type) => {
  const typeMap = {
    feishu: 'primary',
    dingtalk: 'success',
    wechat_work: 'warning',
    custom: 'info'
  }
  return typeMap[type] || ''
}

// 创建通知
const handleCreate = async (notificationData) => {
  try {
    loading.value = true
    const result = await notificationStore.createNotification(notificationData)
    if (result.success) {
      showCreateDialog.value = false
      ElMessage.success('通知创建成功')
      fetchData()
    } else {
      ElMessage.error(result.message || '创建通知失败')
    }
  } catch (error) {
    ElMessage.error('创建通知失败: ' + (error.response?.data?.message || error.message))
  } finally {
    loading.value = false
  }
}

// 获取通知详情
const editNotification = async (id) => {
  try {
    loading.value = true
    await notificationStore.fetchNotificationById(id)
    showEditDialog.value = true
  } catch (error) {
    ElMessage.error('获取通知详情失败')
  } finally {
    loading.value = false
  }
}

// 更新通知
const handleUpdate = async (notificationData) => {
  try {
    loading.value = true
    const result = await notificationStore.updateNotification(notificationStore.currentNotification.id, notificationData)
    if (result.success) {
      showEditDialog.value = false
      ElMessage.success('通知更新成功')
      fetchData()
    } else {
      ElMessage.error(result.message || '更新通知失败')
    }
  } catch (error) {
    ElMessage.error('更新通知失败: ' + (error.response?.data?.message || error.message))
  } finally {
    loading.value = false
  }
}

// 删除通知
const deleteNotification = async (notification) => {
  try {
    await ElMessageBox.confirm(`确定要删除通知 "${notification.name}" 吗？`, '删除确认', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })

    loading.value = true
    const result = await notificationStore.deleteNotification(notification.id)
    if (result.success) {
      ElMessage.success('通知删除成功')

      // 如果删除的是当前页最后一条，且不是第一页，则返回上一页
      if (notificationStore.notifications.length === 0 && currentPage.value > 1) {
        currentPage.value -= 1
      }

      fetchData()
    } else {
      ElMessage.error(result.message || '删除通知失败')
    }
  } catch (error) {
    if (error === 'cancel' || error === 'close') {
      ElMessage.info('已取消删除')
    } else {
      ElMessage.error('删除通知失败: ' + (error.response?.data?.message || error.message))
    }
  } finally {
    loading.value = false
  }
}

// 测试通知
const testNotification = async (notification) => {
  try {
    loading.value = true
    const result = await notificationStore.testNotification(notification.id, '这是一条测试消息')
    if (result.success) {
      ElMessage.success(result.message || '测试通知发送成功')
    } else {
      ElMessage.error(result.message || '测试通知发送失败')
    }
  } catch (error) {
    ElMessage.error('测试通知失败: ' + (error.message || '未知错误'))
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

// 组件挂载时获取通知列表
onMounted(fetchData)
</script>

<style scoped>
/* 使用公共样式，无需额外样式 */
</style>

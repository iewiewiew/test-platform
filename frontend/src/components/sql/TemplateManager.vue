<template>
  <div class="template-manager">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>SQL模板管理</span>
          <div>
            <el-button 
              type="primary" 
              link 
              :loading="loading"
              @click="refreshData"
            >
              <el-icon><Refresh /></el-icon>
              刷新
            </el-button>
            <el-button type="primary" @click="handleCreateTemplate">
              <el-icon><Plus /></el-icon>
              创建模板
            </el-button>
          </div>
        </div>
      </template>

      <!-- 搜索和筛选 -->
      <div class="filter-bar">
        <el-input
          v-model="searchKeyword"
          placeholder="搜索模板名称或描述"
          clearable
          style="width: 300px; margin-right: 16px;"
          @clear="handleSearch"
          @keyup.enter="handleSearch"
        >
          <template #prefix>
            <el-icon><Search /></el-icon>
          </template>
        </el-input>

        <el-select
          v-model="filterCategory"
          placeholder="选择分类"
          clearable
          @change="handleSearch"
          style="width: 200px; margin-right: 16px;"
        >
          <el-option
            v-for="category in categories"
            :key="category"
            :label="category"
            :value="category"
          />
        </el-select>

        <el-button type="primary" @click="handleSearch">
          搜索
        </el-button>
        <el-button @click="handleReset">重置</el-button>
      </div>

      <!-- 模板表格 -->
      <el-table
        :data="filteredTemplates"
        v-loading="loading"
        border
        stripe
        style="width: 100%; margin-top: 16px;"
        empty-text="暂无模板数据"
      >
        <el-table-column prop="name" label="模板名称" min-width="150" />
        <el-table-column prop="category" label="分类" width="140">
          <template #default="{ row }">
            <el-tag :type="getCategoryTagType(row.category)">
              {{ row.category }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="sql_content" label="SQL内容" min-width="250" show-overflow-tooltip />
        <el-table-column prop="description" label="描述" min-width="200" show-overflow-tooltip />
        <el-table-column prop="created_at" label="创建时间" width="160">
          <template #default="{ row }">
            {{ formatDateTime(row.created_at) }}
          </template>
        </el-table-column>
        <el-table-column prop="updated_at" label="更新时间" width="160">
          <template #default="{ row }">
            {{ formatDateTime(row.updated_at) }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="180" fixed="right">
          <template #default="{ row }">
            <el-button 
              type="primary" 
              link 
              size="small"
              @click="handleEditTemplate(row)"
            >
              编辑
            </el-button>
            <el-button 
              type="primary" 
              link 
              size="small"
              @click="handleUseTemplate(row)"
            >
              使用
            </el-button>
            <el-button 
              type="danger" 
              link 
              size="small"
              @click="handleDeleteTemplate(row)"
            >
              删除
            </el-button>
          </template>
        </el-table-column>
      </el-table>

      <!-- 空状态 -->
      <el-empty 
        v-if="filteredTemplates.length === 0 && !loading" 
        :description="emptyDescription"
      >
        <el-button type="primary" @click="handleCreateTemplate">
          创建第一个模板
        </el-button>
      </el-empty>
    </el-card>

    <!-- 模板编辑对话框 -->
    <TemplateDialog
      v-model="dialogVisible"
      :template="currentTemplate"
      @success="handleDialogSuccess"
    />
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Search, Plus, Refresh } from '@element-plus/icons-vue'
import { useSQLStore } from '@/stores/database/sqlStore'
import { formatDateTime } from '@/utils/date'
import TemplateDialog from './TemplateDialog.vue'

const sqlStore = useSQLStore()

// 响应式数据
const searchKeyword = ref('')
const filterCategory = ref('')
const dialogVisible = ref(false)
const currentTemplate = ref(null)
const loading = ref(false)

// 计算属性
const categories = computed(() => {
  console.log('当前分类数据:', sqlStore.categoriesOptions)
  return sqlStore.categoriesOptions || []
})

const allTemplates = computed(() => {
  console.log('当前模板数据:', sqlStore.templates)
  return sqlStore.templates || []
})

const filteredTemplates = computed(() => {
  let templates = allTemplates.value

  // 按关键词搜索
  if (searchKeyword.value) {
    const keyword = searchKeyword.value.toLowerCase()
    templates = templates.filter(template => 
      template.name.toLowerCase().includes(keyword) ||
      (template.description && template.description.toLowerCase().includes(keyword)) ||
      (template.sql_content && template.sql_content.toLowerCase().includes(keyword))
    )
  }

  // 按分类筛选
  if (filterCategory.value) {
    templates = templates.filter(template => template.category === filterCategory.value)
  }

  console.log('筛选后的模板:', templates)
  return templates
})

const emptyDescription = computed(() => {
  if (searchKeyword.value || filterCategory.value) {
    return '没有找到匹配的模板'
  }
  return '暂无模板数据'
})

// 方法
const refreshData = async () => {
  loading.value = true
  try {
    await sqlStore.loadTemplates()
    await sqlStore.loadCategories()
    // ElMessage.success('数据刷新成功')
  } catch (error) {
    ElMessage.error('刷新数据失败: ' + (error.message || '未知错误'))
  } finally {
    loading.value = false
  }
}

const handleSearch = () => {
  // 搜索逻辑已在计算属性中实现
  console.log('执行搜索，关键词:', searchKeyword.value, '分类:', filterCategory.value)
}

const handleReset = () => {
  searchKeyword.value = ''
  filterCategory.value = ''
}

const handleCreateTemplate = () => {
  currentTemplate.value = null
  dialogVisible.value = true
}

const handleEditTemplate = (template) => {
  currentTemplate.value = { ...template }
  dialogVisible.value = true
}

const handleUseTemplate = (template) => {
  sqlStore.setCurrentTemplate(template)
  ElMessage.success(`已选择模板: ${template.name}`)
}

const handleDeleteTemplate = async (template) => {
  try {
    await ElMessageBox.confirm(
      `确定要删除模板 "${template.name}" 吗？此操作不可恢复。`,
      '删除确认',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning',
      }
    )

    loading.value = true
    await sqlStore.deleteTemplate(template.id)
    ElMessage.success('模板删除成功')
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('删除模板失败: ' + (error.message || '未知错误'))
    }
  } finally {
    loading.value = false
  }
}

const handleDialogSuccess = () => {
  dialogVisible.value = false
  currentTemplate.value = null
  ElMessage.success('模板操作成功')
}

// 修复：确保返回有效的 tag type
const getCategoryTagType = (category) => {
  const validTypes = ['', 'default', 'primary', 'success', 'warning', 'danger', 'info']
  
  // 根据分类名称生成一致的 type
  const categoryMap = {
    '用户管理': 'primary',
    '订单管理': 'success', 
    '商品管理': 'warning',
    '数据统计': 'info',
    '系统管理': 'danger'
  }
  
  // 如果分类在映射表中，返回对应的类型
  if (categoryMap[category]) {
    return categoryMap[category]
  }
  
  // 否则根据分类名称的哈希值选择一个有效类型
  const hash = category ? category.split('').reduce((a, b) => {
    a = ((a << 5) - a) + b.charCodeAt(0)
    return a & a
  }, 0) : 0
  
  const index = Math.abs(hash) % (validTypes.length - 1) + 1 // 跳过空字符串
  return validTypes[index] || 'default'
}

// 生命周期
onMounted(() => {
  console.log('TemplateManager 组件挂载，开始加载数据...')
  
  // 检查是否已有数据，如果没有则加载
  if (sqlStore.templates.length === 0) {
    console.log('没有模板数据，开始加载...')
    refreshData()
  } else {
    console.log('已有模板数据，数量:', sqlStore.templates.length)
  }
})

// 监听 store 的 loading 状态
watch(() => sqlStore.loading, (newVal) => {
  loading.value = newVal
})
</script>

<style scoped>
.template-manager {
  padding: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.filter-bar {
  display: flex;
  align-items: center;
  margin-bottom: 16px;
}

:deep(.el-table .cell) {
  word-break: break-word;
}

:deep(.el-tag) {
  margin: 2px;
}
</style>
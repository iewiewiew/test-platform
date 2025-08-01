<template>
  <div class="sql-templates">
    <div class="templates-header">
      <h3>SQL模板库</h3>
      <div class="header-actions">
        <el-button-group class="tree-actions">
          <el-tooltip :content="isAllExpanded ? '折叠全部' : '展开全部'" placement="top">
            <el-button @click="toggleAllCategories" size="default" :disabled="categories.length === 0">
              <el-icon>
                <Fold v-if="isAllExpanded" />
                <Expand v-else />
              </el-icon>
            </el-button>
          </el-tooltip>
        </el-button-group>
      </div>
    </div>

    <div class="templates-container">
      <div class="categories">
        <div v-for="category in categories" :key="category" class="category-section">
          <div class="category-header" @click="toggleCategory(category)">
            <div class="category-title">
              <el-icon class="collapse-icon" :class="{ expanded: expandedCategories[category] }">
                <ArrowRight />
              </el-icon>
              <span class="category-name">{{ category }}</span>
              <el-tag size="small" type="info" class="count-tag">
                {{ getTemplateCount(category) }}
              </el-tag>
            </div>
          </div>
          
          <el-collapse-transition>
            <div v-show="expandedCategories[category]" class="template-list">
              <div v-for="template in getTemplatesByCategory(category)" :key="template.id" class="template-item" :class="{ active: isTemplateActive(template) }" @click="handleTemplateSelect(template)">
                <div class="template-info">
                  <div class="template-name-wrapper">
                    <span class="template-name">{{ template.name }}</span>
                    <el-tooltip
                      v-if="template.description"
                      effect="dark"
                      :content="template.description"
                      placement="top"
                    >
                      <el-icon class="description-icon"><QuestionFilled /></el-icon>
                    </el-tooltip>
                  </div>
                </div>
              </div>
            </div>
          </el-collapse-transition>
        </div>
        
        <!-- 空状态 -->
        <div 
          v-if="categories.length === 0"
          class="empty-state"
        >
          <el-empty description="暂无分类数据" />
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch, nextTick } from 'vue'
import { ElMessage } from 'element-plus'
import { QuestionFilled, ArrowRight, Expand, Fold } from '@element-plus/icons-vue'
import { useSQLStore } from '@/stores/database/sqlStore'

const emit = defineEmits(['template-select'])

const sqlStore = useSQLStore()

// 响应式数据
const expandedCategories = ref({})
const isAllExpanded = ref(false) // 默认全部折叠

// 计算属性
const categories = computed(() => {
  return sqlStore.categoriesOptions || []
})

// 使用方法来获取模板数据，避免在计算属性中频繁触发更新
const getTemplatesByCategory = (category) => {
  return sqlStore.templatesByCategory?.[category] || []
}

const getTemplateCount = (category) => {
  return getTemplatesByCategory(category).length
}

const currentTemplate = computed(() => sqlStore.currentTemplate)

// 方法
const handleTemplateSelect = (template) => {
  emit('template-select', template)
}

const toggleCategory = (category) => {
  // 使用 nextTick 确保在下一个 DOM 更新周期执行
  nextTick(() => {
    expandedCategories.value[category] = !expandedCategories.value[category]
    updateAllExpandedStatus()
  })
}

const toggleAllCategories = () => {
  const newState = !isAllExpanded.value
  
  // 使用 nextTick 确保在 DOM 更新后执行
  nextTick(() => {
    // 创建新的对象来避免响应式冲突
    const newExpandedState = { ...expandedCategories.value }
    
    categories.value.forEach(category => {
      newExpandedState[category] = newState
    })
    
    expandedCategories.value = newExpandedState
    isAllExpanded.value = newState
  })
}

const updateAllExpandedStatus = () => {
  const allCategories = categories.value
  if (allCategories.length === 0) {
    isAllExpanded.value = false
    return
  }
  
  const expandedCount = allCategories.filter(category => 
    expandedCategories.value[category]
  ).length
  
  isAllExpanded.value = expandedCount === allCategories.length
}

const isTemplateActive = (template) => {
  return currentTemplate.value && currentTemplate.value.id === template.id
}

// 初始化折叠状态
const initializeExpandedState = () => {
  const newExpandedState = {}
  categories.value.forEach(category => {
    newExpandedState[category] = false // 默认全部折叠
  })
  expandedCategories.value = newExpandedState
  isAllExpanded.value = false
}

// 监听分类数据变化
watch(categories, (newCategories) => {
  if (newCategories.length > 0) {
    // 使用 nextTick 确保在 DOM 更新后初始化状态
    nextTick(() => {
      initializeExpandedState()
    })
  }
}, { immediate: true })

// 生命周期
onMounted(() => {
  console.log('SQLTemplates 组件挂载')
  // 确保数据已加载
  if (sqlStore.templates.length === 0) {
    sqlStore.loadTemplates().then(() => {
      console.log('模板数据加载完成')
    })
  }
  if (sqlStore.categories.length === 0) {
    sqlStore.loadCategories().then(() => {
      console.log('分类数据加载完成')
    })
  }
})
</script>

<style scoped>
.sql-templates {
  height: 100%;
  max-height: 100%;
  display: flex;
  flex-direction: column;
  background: #fff;
  overflow: hidden; /* 防止整体溢出，让内部容器负责滚动 */
}

.templates-header {
  padding: 12px 16px;
  border-bottom: 1px solid #e4e7ed;
  display: flex;
  justify-content: space-between;
  align-items: center;
  background: #f8f9fa;
  flex-shrink: 0;
}

.templates-header h3 {
  margin: 0;
  color: #303133;
  font-size: 16px;
  font-weight: 600;
}

.header-actions {
  display: flex;
  align-items: center;
  gap: 8px;
}

.tree-actions {
  display: flex;
  gap: 4px;
}

.templates-container {
  flex: 1;
  overflow-y: auto;
  overflow-x: auto; /* 支持左右滚动 */
  padding: 8px 0;
  min-height: 0; /* 确保flex子元素可以正确收缩 */
  min-width: 0; /* 允许横向收缩，确保滚动条正常显示 */
  max-height: 100%; /* 限制最大高度为父容器的100% */
  position: relative; /* 为滚动条定位提供上下文 */
  /* 平滑滚动 */
  scroll-behavior: smooth;
  -webkit-overflow-scrolling: touch; /* iOS 平滑滚动 */
  /* Firefox 滚动条样式 */
  scrollbar-width: thin;
  scrollbar-color: #c1c8d1 #f8f9fa;
}

.categories {
  padding: 16px;
}

.category-section {
  margin-bottom: 16px;
}

.category-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 8px;
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.3s;
  user-select: none;
}

.category-header:hover {
  background: #f5f7fa;
}

.category-title {
  display: flex;
  align-items: center;
  gap: 8px;
  flex: 1;
}

.collapse-icon {
  transition: transform 0.3s;
  color: #909399;
  font-size: 12px;
}

.collapse-icon.expanded {
  transform: rotate(90deg);
}

.category-name {
  font-weight: 600;
  color: #303133;
  font-size: 14px;
}

.count-tag {
  font-size: 12px;
  height: 20px;
  line-height: 18px;
}

.template-list {
  margin-top: 8px;
  margin-left: 20px;
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.template-item {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  padding: 12px;
  border: 1px solid #e4e7ed;
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.3s;
  background: white;
}

.template-item:hover {
  border-color: #409eff;
  background: #f5f7fa;
  transform: translateY(-1px);
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.template-item.active {
  border-color: #409eff;
  background: #ecf5ff;
}

.template-info {
  flex: 1;
  min-width: 0;
}

.template-name-wrapper {
  display: flex;
  align-items: center;
  gap: 6px;
}

.template-name {
  font-weight: 500;
  color: #303133;
  font-size: 14px;
  line-height: 1.4;
}

.description-icon {
  color: #909399;
  font-size: 12px;
  cursor: help;
  transition: color 0.3s;
}

.description-icon:hover {
  color: #409eff;
}

.empty-category {
  padding: 20px;
  text-align: center;
  border: 1px dashed #e4e7ed;
  border-radius: 6px;
  background: #fafafa;
}

.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 200px;
  gap: 16px;
  color: #909399;
  padding: 0 20px;
}

/* 滚动条样式优化 - Webkit浏览器 */
.templates-container::-webkit-scrollbar {
  width: 8px;
  height: 8px;
}

.templates-container::-webkit-scrollbar-track {
  background: #f8f9fa;
  border-radius: 4px;
}

.templates-container::-webkit-scrollbar-thumb {
  background: #c1c8d1;
  border-radius: 4px;
  transition: background 0.3s ease;
}

.templates-container::-webkit-scrollbar-thumb:hover {
  background: #a8b2bd;
}
</style>
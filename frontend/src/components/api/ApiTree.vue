<template>
  <div class="api-tree">
    <div class="tree-header">
      <el-input v-model="searchKeyword" placeholder="搜索接口..." clearable size="default" @clear="handleSearchClear"
        @input="handleSearchInput">
        <template #prefix>
          <el-icon>
            <Search />
          </el-icon>
        </template>
      </el-input>
      <el-button-group class="tree-actions">
        <el-tooltip :content="isAllExpanded ? '折叠全部' : '展开全部'" placement="top">
          <el-button @click="toggleExpandAll" size="default" :disabled="treeData.length === 0">
            <el-icon>
              <Fold v-if="isAllExpanded" />
              <Expand v-else />
            </el-icon>
          </el-button>
        </el-tooltip>
        <el-tooltip content="刷新文档" placement="top">
          <el-button @click="handleRefresh" :loading="loading" size="default">
            <el-icon>
              <Refresh />
            </el-icon>
          </el-button>
        </el-tooltip>
      </el-button-group>
    </div>

    <el-alert v-if="error" :title="error" type="error" show-icon closable @close="clearError" class="error-alert" />

    <div class="tree-container" v-loading="loading">
      <div v-if="!loading && treeData.length === 0" class="empty-state">
        <el-empty description="暂无接口数据" :image-size="80" />
        <el-button @click="handleRefresh" type="primary" size="small">刷新数据</el-button>
      </div>

      <el-tree v-else ref="treeRef" :data="filteredTreeData" :props="defaultProps" node-key="id"
        :default-expanded-keys="defaultExpandedKeys" :highlight-current="true" :expand-on-click-node="false"
        @node-click="handleNodeClick" @node-expand="updateExpandState" @node-collapse="updateExpandState" class="api-tree-content">
        <template #default="{ node, data }">
          <span class="tree-node">
            <span v-if="data.type === 'category'" class="category-node">
              <el-icon>
                <component :is="node.expanded ? 'FolderOpened' : 'Folder'" />
              </el-icon>
              <span class="category-label">{{ data.label }}</span>
              <el-tag size="small" type="info" class="count-tag">
                {{ data.children?.length || 0 }}
              </el-tag>
            </span>
            <span v-else class="api-item">
              <el-tag :type="getMethodType(data.method)" size="small" class="method-tag" effect="dark">
                {{ data.method }}
              </el-tag>
              <div class="api-info">
                <div class="api-name">{{ getApiName(data) }}</div>
              </div>
            </span>
          </span>
        </template>
      </el-tree>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, nextTick } from 'vue'
import { storeToRefs } from 'pinia'
import { useEndpointStore } from '@/stores/project/endpointStore'
import {
  ElTree,
  ElInput,
  ElButton,
  ElButtonGroup,
  ElTag,
  ElAlert,
  ElIcon,
  ElTooltip,
  ElMessage,
  ElEmpty
} from 'element-plus'
import {
  Refresh,
  Search,
  Folder,
  FolderOpened,
  Expand,
  Fold
} from '@element-plus/icons-vue'

// 使用 store
const endpointStore = useEndpointStore()
const {
  treeData,
  filteredTreeData,
  loading,
  error,
  searchKeyword
} = storeToRefs(endpointStore)

// 定义 emits
const emit = defineEmits(['endpoint-selected'])

// 响应式数据
const treeRef = ref()
const defaultExpandedKeys = ref([])
const isAllExpanded = ref(false)

// 计算属性
const defaultProps = computed(() => ({
  children: 'children',
  label: 'label'
}))

// 方法
const getMethodType = (method) => {
  const types = {
    'GET': 'success',
    'POST': 'warning',
    'PUT': 'primary',
    'DELETE': 'danger',
    'PATCH': 'info',
    'HEAD': 'info',
    'OPTIONS': 'info'
  }
  return types[method?.toUpperCase()] || 'info'
}

// 在 ApiTree.vue 的 getApiName 方法中，使用相同的逻辑
const getApiName = (data) => {
  if (!data) return '未知接口'

  // 1. 检查 operation 对象
  if (data.operation) {
    if (data.operation.summary) return data.operation.summary
    if (data.operation.operationId) return data.operation.operationId
    if (data.operation.description) return data.operation.description
  }

  // 2. 检查直接字段
  if (data.summary) return data.summary
  if (data.name) return data.name
  if (data.label) return data.label
  if (data.operationId) return data.operationId
  if (data.description) return data.description
  if (data.title) return data.title

  // 3. 使用路径生成名称
  if (data.path) {
    const pathParts = data.path.split('/').filter(part => part && !part.includes('{'))
    return pathParts[pathParts.length - 1] || data.path
  }

  return '未命名接口'
}

const handleNodeClick = async (data, node) => {
  if (data.type === 'endpoint') {
    try {
      // 直接传递整个接口数据
      emit('endpoint-selected', data)
    } catch (error) {
      ElMessage.error('选择接口失败: ' + error.message)
    }
  } else if (data.type === 'category') {
    node.expanded ? node.collapse() : node.expand()
  }
}

const handleRefresh = async () => {
  try {
    await endpointStore.refreshApiDocs()
    ElMessage.success('文档刷新成功')
    collapseAll()
  } catch (error) {
    ElMessage.error('刷新文档失败: ' + error.message)
  }
}

const handleSearchClear = () => {
  endpointStore.setSearchKeyword('')
}

const handleSearchInput = (value) => {
  endpointStore.setSearchKeyword(value)

  if (value.trim()) {
    nextTick(() => {
      expandAll()
    })
  } else {
    collapseAll()
  }
}

const clearError = () => {
  endpointStore.clearError()
}

// 展开所有节点
const expandAll = () => {
  if (treeRef.value) {
    const nodes = treeRef.value.store._getAllNodes()
    nodes.forEach(node => {
      node.expanded = true
    })
    isAllExpanded.value = true
  }
}

// 折叠所有节点
const collapseAll = () => {
  if (treeRef.value) {
    const nodes = treeRef.value.store._getAllNodes()
    nodes.forEach(node => {
      node.expanded = false
    })
    isAllExpanded.value = false
  }
}

// 切换展开/折叠全部
const toggleExpandAll = () => {
  if (isAllExpanded.value) {
    collapseAll()
  } else {
    expandAll()
  }
}

// 更新展开状态（当手动点击节点展开/折叠时调用）
const updateExpandState = () => {
  if (treeRef.value) {
    const nodes = treeRef.value.store._getAllNodes()
    const categoryNodes = nodes.filter(node => node.data?.type === 'category')
    if (categoryNodes.length === 0) {
      isAllExpanded.value = false
      return
    }
    // 检查所有分类节点是否都展开
    const allExpanded = categoryNodes.every(node => node.expanded)
    isAllExpanded.value = allExpanded
  }
}

// 生命周期
onMounted(() => {
  endpointStore.fetchEndpointsByCategories().catch(error => {
    ElMessage.error('加载接口数据失败: ' + error.message)
  })
})
</script>

<style scoped>
.api-tree {
  height: 100%;
  max-height: 100%;
  display: flex;
  flex-direction: column;
  background: #fff;
  overflow: hidden; /* 防止整体溢出，让内部容器负责滚动 */
}

.tree-header {
  padding: 12px 16px;
  border-bottom: 1px solid #e4e7ed;
  display: flex;
  gap: 8px;
  align-items: center;
  background: #f8f9fa;
  flex-shrink: 0;
}

.tree-header .el-input {
  flex: 1;
}

.tree-actions {
  display: flex;
  gap: 4px;
}

.error-alert {
  margin: 8px 16px 0;
  flex-shrink: 0;
}

.tree-container {
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

:deep(.api-tree-content) {
  padding: 0 8px 0 8px; /* 左右padding，确保内容有足够空间 */
  min-height: 100%; /* 确保树内容至少占满容器高度 */
  width: max-content; /* 允许内容决定宽度，可以超出容器 */
  min-width: 100%; /* 至少占满容器宽度 */
  box-sizing: border-box; /* 确保padding计算正确 */
}

/* 确保树节点不会被截断 */
:deep(.api-tree-content .el-tree) {
  min-height: 100%;
  width: max-content; /* 允许树根据内容决定宽度，可以超出容器 */
  min-width: 100%; /* 至少占满容器宽度 */
}

:deep(.api-tree-content .el-tree-node__content) {
  height: auto;
  min-height: 36px;
  margin: 2px 0;
  border-radius: 6px;
  transition: all 0.2s ease;
  padding: 4px 8px;
  width: max-content; /* 允许内容决定宽度，可以超出容器 */
  box-sizing: border-box; /* 确保padding不会导致溢出 */
}

:deep(.api-tree-content .el-tree-node__content:hover) {
  background-color: #f5f7fa;
}

:deep(.api-tree-content .el-tree-node.is-current > .el-tree-node__content) {
  background-color: #f0f7ff;
  border: 1px solid #409eff;
}

:deep(.api-tree-content .el-tree-node__expand-icon) {
  color: #909399;
  transition: transform 0.2s ease;
}

:deep(.api-tree-content .el-tree-node__expand-icon.is-leaf) {
  color: transparent;
  cursor: default;
}

.tree-node {
  display: flex;
  align-items: center;
  width: max-content; /* 允许内容决定宽度，支持超出容器 */
  font-size: 14px;
  flex-shrink: 0; /* 不允许收缩 */
}

.category-node {
  display: flex;
  align-items: center;
  gap: 6px;
  font-weight: 600;
  color: #409eff;
  flex-shrink: 0;
}

.category-node .el-icon {
  color: #e6a23c;
  font-size: 16px;
}

.category-label {
  flex-shrink: 0; /* 不允许收缩，保持完整显示 */
  overflow: visible; /* 允许内容超出，通过滚动查看 */
  text-overflow: clip; /* 不截断文本 */
  white-space: nowrap; /* 保持单行 */
  font-size: 13px;
  min-width: fit-content; /* 至少与内容同宽 */
}

.count-tag {
  min-width: 20px;
  height: 18px;
  justify-content: center;
  flex-shrink: 0;
  font-size: 11px;
}

.api-item {
  display: flex;
  align-items: flex-start;
  gap: 8px;
  width: max-content; /* 允许内容决定宽度 */
  padding: 6px 0;
  flex-shrink: 0; /* 不允许收缩 */
}

.method-tag {
  min-width: 48px;
  text-align: center;
  font-weight: 600;
  font-size: 10px;
  flex-shrink: 0;
  margin-top: 1px;
}

.api-info {
  display: flex;
  flex-direction: column;
  gap: 2px;
  min-width: fit-content; /* 至少与内容同宽 */
  flex-shrink: 0; /* 不允许收缩，保持完整显示 */
}

.api-name {
  font-size: 13px;
  font-weight: 500;
  color: #303133;
  line-height: 1.3;
  overflow: visible; /* 允许内容超出，通过滚动查看 */
  text-overflow: clip; /* 不截断文本 */
  white-space: nowrap; /* 保持单行 */
  min-width: fit-content; /* 允许内容决定宽度 */
  flex-shrink: 0; /* 不允许收缩 */
}

.api-path {
  font-family: 'Monaco', 'Consolas', 'Courier New', monospace;
  font-size: 11px;
  color: #909399;
  line-height: 1.3;
  overflow: visible; /* 允许内容超出，通过滚动查看 */
  text-overflow: clip; /* 不截断文本 */
  white-space: nowrap; /* 保持单行 */
  min-width: fit-content; /* 允许内容决定宽度 */
  flex-shrink: 0; /* 不允许收缩 */
}

.tree-container::-webkit-scrollbar {
  width: 8px;
  height: 8px;
}

.tree-container::-webkit-scrollbar-track {
  background: #f8f9fa;
  border-radius: 4px;
}

.tree-container::-webkit-scrollbar-thumb {
  background: #c1c8d1;
  border-radius: 4px;
  transition: background 0.3s ease;
}

.tree-container::-webkit-scrollbar-thumb:hover {
  background: #a8b2bd;
}
</style>
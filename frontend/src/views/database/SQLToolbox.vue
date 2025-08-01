<template>
    <div class="sql-toolbox">
      <div class="layout-container">
        <!-- 左侧模板列表 -->
        <div class="templates-panel">
          <SQLTemplates 
            @template-select="handleTemplateSelect"
            @template-edit="handleTemplateEdit"
          />
        </div>
  
        <!-- 右侧内容区 -->
        <div class="content-panel">
          <el-tabs v-model="activeTab" type="border-card" class="content-tabs">
            <!-- SQL执行标签页 -->
            <el-tab-pane label="SQL执行" name="execute">
              <SQLExecutor />
            </el-tab-pane>
  
            <!-- 模板管理标签页 -->
            <el-tab-pane label="模板管理" name="templates">
              <TemplateManager />
            </el-tab-pane>
  
            <!-- 查询历史标签页 -->
            <el-tab-pane label="查询历史" name="history">
              <QueryHistory />
            </el-tab-pane>
          </el-tabs>
        </div>
      </div>
  
      <!-- 模板编辑对话框 -->
      <TemplateDialog 
        v-model="templateDialogVisible"
        :template="editingTemplate"
        @success="handleTemplateSuccess"
      />
    </div>
  </template>
  
  <script setup>
  import { ref, onMounted } from 'vue'
  import { useSQLStore } from '@/stores/database/sqlStore'
  
  // 组件导入
  import SQLTemplates from '@/components/sql/SQLTemplates.vue'
  import SQLExecutor from '@/components/sql/SQLExecutor.vue'
  import TemplateManager from '@/components/sql/TemplateManager.vue'
  import QueryHistory from '@/components/sql/QueryHistory.vue'
  import TemplateDialog from '@/components/sql/TemplateDialog.vue'
  
  const sqlStore = useSQLStore()
  
  // 响应式数据
  const activeTab = ref('execute')
  const templateDialogVisible = ref(false)
  const editingTemplate = ref(null)
  
  // 方法
  const handleTemplateSelect = (template) => {
    sqlStore.setCurrentTemplate(template)
    activeTab.value = 'execute'
  }
  
  const handleTemplateEdit = (template) => {
    editingTemplate.value = template
    templateDialogVisible.value = true
  }
  
  const handleTemplateSuccess = () => {
    templateDialogVisible.value = false
    editingTemplate.value = null
    sqlStore.loadTemplates()
  }
  
  // 生命周期
  onMounted(() => {
    sqlStore.loadTemplates()
    sqlStore.loadHistory()
  })
  </script>
  
  <style scoped>
  .sql-toolbox {
    height: 100%;
    max-height: 100%;
    background: #f5f7fa;
    padding: 16px;
    overflow: hidden;
  }
  
  .layout-container {
    display: flex;
    height: 100%;
    max-height: 100%;
    background: #fff;
    border-radius: 8px;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
    overflow: hidden; /* 确保布局容器本身不滚动 */
    min-height: 0; /* 确保flex容器可以正确收缩 */
    align-items: stretch; /* 确保左右面板等高 */
  }
  
  .templates-panel {
    width: 300px;
    min-width: 280px;
    max-width: 300px;
    border-right: 1px solid #e4e7ed;
    background: #fff;
    height: 100%;
    /* 限制模板面板高度为视口内高度（扣除顶部导航60px与内容内边距约48px）*/
    max-height: calc(100vh - 60px - 48px);
    display: flex;
    flex-direction: column;
    overflow: hidden; /* 让内部的模板组件负责滚动 */
    min-height: 0; /* 确保flex子元素可以正确收缩 */
  }
  
  .content-panel {
    flex: 1;
    min-width: 0;
    min-height: 0; /* 确保flex子元素可以正确收缩 */
    background: #fff;
    height: 100%;
    /* 固定右侧内容面板在内容区域内的高度，与左侧保持一致 */
    max-height: calc(100vh - 60px - 48px);
    overflow: hidden; /* 防止面板本身滚动，让内部组件负责滚动 */
    display: flex;
    flex-direction: column;
    position: relative; /* 确保定位上下文 */
  }
  
  .content-tabs {
    height: 100%;
    display: flex;
    flex-direction: column;
    overflow: hidden;
  }
  
  :deep(.content-tabs .el-tabs__header) {
    margin: 0;
    flex-shrink: 0;
  }
  
  :deep(.content-tabs .el-tabs__content) {
    flex: 1;
    overflow: hidden;
    padding: 0;
    min-height: 0;
  }
  
  :deep(.content-tabs .el-tab-pane) {
    height: 100%;
    overflow: hidden;
  }
  
  @media (max-width: 768px) {
    .sql-toolbox {
      padding: 8px;
    }

    .layout-container {
      flex-direction: column;
      align-items: stretch; /* 确保移动端也等高 */
    }

    .templates-panel {
      width: 100%;
      height: 40%;
      max-height: 40%; /* 限制最大高度 */
      border-right: none;
      border-bottom: 1px solid #e4e7ed;
      flex-shrink: 0; /* 防止被压缩 */
    }

    .content-panel {
      height: 60%;
      max-height: 60%; /* 限制最大高度 */
      flex-shrink: 0; /* 防止被压缩 */
    }
  }
  </style>
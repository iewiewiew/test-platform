<template>
  <div class="docs-view-container">
    <!-- 左侧目录树 -->
    <div class="docs-sidebar">
      <div class="sidebar-header">
        <h3>文档列表</h3>
        <el-button type="primary" size="default" :icon="Plus" @click="handleCreateDoc()">新建文档</el-button>
      </div>
      <div class="sidebar-content">
        <el-tree ref="treeRef" :data="treeData" :props="{ label: 'name', children: 'children' }" node-key="path" :default-expand-all="false" :highlight-current="true" @node-click="handleNodeClick">
          <template #default="{ node, data }">
            <div class="tree-node">
              <el-icon v-if="data.type === 'directory'"><Folder /></el-icon>
              <el-icon v-else><Document /></el-icon>
              <span class="node-label">{{ node.label }}</span>
              <div v-if="data.type === 'file'" class="node-actions" @click.stop>
                <el-button link type="danger" size="small" :icon="Delete" @click="handleDeleteDoc(data.path)" />
              </div>
            </div>
          </template>
        </el-tree>
      </div>
    </div>

    <!-- 右侧内容区域 -->
    <div class="docs-content">
      <div v-if="!currentDocPath" class="empty-state">
        <el-empty description="请从左侧选择文档或创建新文档" />
      </div>
      <div v-else class="content-wrapper">
        <div class="content-header">
          <h2>{{ currentDocName }}</h2>
          <div class="header-actions">
            <el-button v-if="!isEditing" type="primary" size="default" :icon="Edit" @click="handleEdit">编辑</el-button>
            <template v-else>
              <el-button size="small" :icon="Close" @click="handleCancelEdit">取消</el-button>
              <el-button type="primary" size="small" :icon="Check" @click="handleSave" :loading="saving">保存</el-button>
            </template>
          </div>
        </div>
        <div class="content-body">
          <div v-if="loading" class="loading-container">
            <el-skeleton :rows="10" animated />
          </div>
          <div v-else-if="error" class="error-container">
            <el-alert :title="error" type="error" :closable="false" show-icon />
          </div>
          <div v-else-if="isEditing" class="edit-container">
            <el-input v-model="editContent" type="textarea" :rows="30" placeholder="请输入 Markdown 内容..." class="markdown-editor" />
          </div>
          <div v-else class="markdown-content" v-html="htmlContent"></div>
        </div>
      </div>
    </div>

    <!-- 新建文档对话框 -->
    <el-dialog v-model="createDialogVisible" title="新建文档" width="500px" @close="handleCreateDialogClose">
      <el-form :model="createForm" label-width="80px">
        <el-form-item label="文档名称" required>
          <el-input
            v-model="createForm.name"
            :placeholder="createForm.parentPath ? `将在 ${createForm.parentPath} 目录下创建` : '请输入文档名称（不含 .md 后缀）'"
            @keyup.enter="handleConfirmCreate"
          />
          <div class="form-tip">
            文档名称只能包含字母、数字、下划线、中划线和中文
            <span v-if="createForm.parentPath">，将在目录 "{{ createForm.parentPath }}" 下创建</span>
          </div>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="createDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleConfirmCreate" :loading="creating">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted, watch, nextTick } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { marked } from 'marked'
import { docsService } from '@/services/tool/docsService'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus, Edit, Delete, Check, Close, Document, Folder } from '@element-plus/icons-vue'

const route = useRoute()
const router = useRouter()

const treeRef = ref(null)
const treeData = ref([])
const currentDocPath = ref('')
const currentDocName = ref('')
const markdownContent = ref('')
const htmlContent = ref('')
const editContent = ref('')
const loading = ref(false)
const error = ref('')
const isEditing = ref(false)
const saving = ref(false)
const createDialogVisible = ref(false)
const creating = ref(false)
const createForm = ref({
  name: '',
  parentPath: ''
})

// 配置 marked 选项
marked.setOptions({
  breaks: true, // 支持 GitHub 风格的换行
  gfm: true // 支持 GitHub 风格的 Markdown
})

// 递归查找文件节点
const findFileNode = (nodes, path) => {
  for (const node of nodes) {
    if (node.path === path && node.type === 'file') {
      return node
    }
    if (node.children) {
      const found = findFileNode(node.children, path)
      if (found) return found
    }
  }
  return null
}

// 加载文档列表
const loadDocsList = async () => {
  try {
    const response = await docsService.getDocsList()
    if (response.data.code === 0) {
      treeData.value = response.data.data || []

      // 如果有路由参数，加载对应文档
      const docPath = route.params.name ? decodeURIComponent(route.params.name) : ''
      if (docPath) {
        const fileNode = findFileNode(treeData.value, docPath)
        if (fileNode) {
          currentDocPath.value = docPath
          currentDocName.value = fileNode.name
          loadDoc(docPath)
          // 选中树节点
          nextTick(() => {
            if (treeRef.value) {
              treeRef.value.setCurrentKey(docPath)
            }
          })
        }
      } else {
        // 查找第一个文件节点
        const firstFile = findFirstFile(treeData.value)
        if (firstFile) {
          currentDocPath.value = firstFile.path
          currentDocName.value = firstFile.name
          router.replace(`/docs/${encodeURIComponent(firstFile.path)}`)
          loadDoc(firstFile.path)
        }
      }
    } else {
      ElMessage.error(response.data.message || '加载文档列表失败')
    }
  } catch (err) {
    ElMessage.error('加载文档列表失败')
    console.error('加载文档列表异常:', err)
  }
}

// 查找第一个文件节点
const findFirstFile = (nodes) => {
  for (const node of nodes) {
    if (node.type === 'file') {
      return node
    }
    if (node.children) {
      const found = findFirstFile(node.children)
      if (found) return found
    }
  }
  return null
}

// 加载文档内容
const loadDoc = async (docPath) => {
  if (!docPath) return

  loading.value = true
  error.value = ''
  isEditing.value = false

  try {
    const response = await docsService.getDoc(docPath)
    if (response.data.code === 0) {
      markdownContent.value = response.data.data.content
      htmlContent.value = marked.parse(markdownContent.value)
      editContent.value = markdownContent.value
      currentDocName.value = response.data.data.name || currentDocName.value
    } else {
      error.value = response.data.message || '加载文档失败'
    }
  } catch (err) {
    error.value = err.message || '加载文档失败'
    ElMessage.error('加载文档失败')
  } finally {
    loading.value = false
  }
}

// 处理节点点击
const handleNodeClick = (data) => {
  // 只处理文件节点，目录节点用于展开/折叠
  if (data.type !== 'file') return
  if (data.path === currentDocPath.value) return

  currentDocPath.value = data.path
  currentDocName.value = data.name
  router.push(`/docs/${encodeURIComponent(data.path)}`)
  loadDoc(data.path)
}

// 处理编辑
const handleEdit = () => {
  isEditing.value = true
  editContent.value = markdownContent.value
}

// 处理取消编辑
const handleCancelEdit = () => {
  isEditing.value = false
  editContent.value = markdownContent.value
}

// 处理保存
const handleSave = async () => {
  if (!currentDocPath.value) return

  saving.value = true
  try {
    const response = await docsService.updateDoc(currentDocPath.value, editContent.value)
    if (response.data.code === 0) {
      ElMessage.success('保存成功')
      markdownContent.value = editContent.value
      htmlContent.value = marked.parse(editContent.value)
      isEditing.value = false
    } else {
      ElMessage.error(response.data.message || '保存失败')
    }
  } catch (err) {
    ElMessage.error('保存失败')
    console.error(err)
  } finally {
    saving.value = false
  }
}

// 处理新建文档
const handleCreateDoc = (parentPath = '') => {
  createForm.value.name = ''
  createForm.value.parentPath = parentPath
  createDialogVisible.value = true
}

// 处理确认新建
const handleConfirmCreate = async () => {
  const name = createForm.value.name?.trim()
  if (!name) {
    ElMessage.warning('请输入文档名称')
    return
  }

  // 验证文档名称
  if (!/^[\w\-\u4e00-\u9fa5]+$/.test(name)) {
    ElMessage.warning('文档名称只能包含字母、数字、下划线、中划线和中文')
    return
  }

  // 构建文档路径
  const parentPath = createForm.value.parentPath?.trim()
  const docPath = parentPath ? `${parentPath}/${name}.md` : `${name}.md`

  creating.value = true
  try {
    const response = await docsService.createDoc(docPath, '')
    if (response.data.code === 0) {
      ElMessage.success('创建成功')
      createDialogVisible.value = false
      // 重新加载列表
      await loadDocsList()
      // 选中新创建的文档
      currentDocPath.value = docPath
      currentDocName.value = response.data.data.name || name
      router.push(`/docs/${encodeURIComponent(docPath)}`)
      await loadDoc(docPath)
      // 选中树节点
      nextTick(() => {
        if (treeRef.value) {
          treeRef.value.setCurrentKey(docPath)
        }
      })
      // 自动进入编辑模式
      setTimeout(() => {
        handleEdit()
      }, 100)
    } else {
      ElMessage.error(response.data.message || '创建失败')
    }
  } catch (err) {
    ElMessage.error('创建失败')
    console.error(err)
  } finally {
    creating.value = false
  }
}

// 处理新建对话框关闭
const handleCreateDialogClose = () => {
  createForm.value.name = ''
}

// 处理删除文档
const handleDeleteDoc = async (docPath) => {
  try {
    await ElMessageBox.confirm(`确定要删除文档吗？此操作不可恢复。`, '确认删除', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })

    const response = await docsService.deleteDoc(docPath)
    if (response.data.code === 0) {
      ElMessage.success('删除成功')
      // 如果删除的是当前文档，清空内容
      if (docPath === currentDocPath.value) {
        currentDocPath.value = ''
        currentDocName.value = ''
        markdownContent.value = ''
        htmlContent.value = ''
        router.push('/docs')
      }
      // 重新加载列表
      await loadDocsList()
    } else {
      ElMessage.error(response.data.message || '删除失败')
    }
  } catch (err) {
    if (err !== 'cancel') {
      ElMessage.error('删除失败')
      console.error(err)
    }
  }
}

// 监听路由变化
watch(
  () => route.params.name,
  (newPath) => {
    if (newPath) {
      const docPath = decodeURIComponent(newPath)
      if (docPath !== currentDocPath.value) {
        currentDocPath.value = docPath
        const fileNode = findFileNode(treeData.value, docPath)
        if (fileNode) {
          currentDocName.value = fileNode.name
        }
        loadDoc(docPath)
        // 选中树节点
        nextTick(() => {
          if (treeRef.value) {
            treeRef.value.setCurrentKey(docPath)
          }
        })
      }
    }
  }
)

onMounted(() => {
  loadDocsList()
})
</script>

<style scoped>
.docs-view-container {
  position: relative !important;
  height: 100% !important;
  width: 100% !important;
  display: flex !important;
  flex-direction: row !important;
  background-color: #f0f2f5;
  overflow: hidden !important;
  /* 确保容器占满父元素高度，不跟随页面滚动 */
  min-height: 0;
}

/* 左侧目录树 - 固定宽度，独立布局，固定定位 */
.docs-sidebar {
  width: 280px;
  min-width: 280px;
  max-width: 280px;
  background: #fff;
  border-right: 1px solid #e4e7ed;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  box-shadow: 2px 0 4px rgba(0, 0, 0, 0.05);
  position: relative;
  height: 100%;
  flex-shrink: 0;
  z-index: 10;
  /* 确保左侧目录树固定，不跟随右侧内容滚动，且不被遮挡 */
}

.sidebar-header {
  padding: 16px 24px;
  border-bottom: 1px solid #e4e7ed;
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-shrink: 0;
  z-index: 1;
  height: 65px;
  min-height: 65px;
  box-sizing: border-box;
}

.sidebar-header h3 {
  margin: 0;
  font-size: 16px;
  font-weight: 600;
  color: #303133;
}

.sidebar-content {
  flex: 1;
  overflow-y: auto;
  overflow-x: hidden;
  padding: 8px;
  position: relative;
  min-height: 0;
}

/* 自定义滚动条样式 */
.sidebar-content::-webkit-scrollbar {
  width: 6px;
}

.sidebar-content::-webkit-scrollbar-track {
  background: #f1f1f1;
}

.sidebar-content::-webkit-scrollbar-thumb {
  background: #c1c1c1;
  border-radius: 3px;
}

.sidebar-content::-webkit-scrollbar-thumb:hover {
  background: #a8a8a8;
}

.tree-node {
  display: flex;
  align-items: center;
  flex: 1;
  padding-right: 8px;
  cursor: pointer;
  transition: background-color 0.2s;
}

.tree-node:hover {
  background-color: #f5f7fa;
}

.tree-node .el-icon {
  margin-right: 6px;
  color: #909399;
  flex-shrink: 0;
}

.node-label {
  flex: 1;
  font-size: 14px;
}

.node-actions {
  display: none;
  margin-left: auto;
}

.tree-node:hover .node-actions {
  display: block;
}

.docs-content {
  flex: 1;
  min-width: 0;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  background: #fff;
  height: 100%;
  position: relative;
  flex-shrink: 1;
  /* 确保右侧内容区域独立滚动 */
}

.empty-state {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #fff;
  min-height: 0;
}

.content-wrapper {
  flex: 1;
  display: flex;
  flex-direction: column;
  background: #fff;
  overflow: hidden;
  min-height: 0;
}

.content-header {
  padding: 16px 24px;
  border-bottom: 1px solid #e4e7ed;
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-shrink: 0;
  z-index: 1;
  background: #fff;
  height: 65px;
  min-height: 65px;
  box-sizing: border-box;
}

.content-header h2 {
  margin: 0;
  font-size: 20px;
  font-weight: 600;
  color: #303133;
}

.header-actions {
  display: flex;
  gap: 8px;
}

.content-body {
  flex: 1;
  padding: 24px;
  overflow-y: auto;
  overflow-x: hidden;
  min-height: 0;
  position: relative;
}

/* 自定义滚动条样式 */
.content-body::-webkit-scrollbar {
  width: 8px;
}

.content-body::-webkit-scrollbar-track {
  background: #f1f1f1;
}

.content-body::-webkit-scrollbar-thumb {
  background: #c1c1c1;
  border-radius: 4px;
}

.content-body::-webkit-scrollbar-thumb:hover {
  background: #a8a8a8;
}

.loading-container {
  padding: 20px;
}

.error-container {
  padding: 20px;
}

.edit-container {
  flex: 1;
  min-height: 0;
  display: flex;
  flex-direction: column;
}

.markdown-editor {
  flex: 1;
  min-height: 0;
  display: flex;
  flex-direction: column;
}

.markdown-editor :deep(.el-textarea) {
  flex: 1;
  min-height: 0;
  display: flex;
  flex-direction: column;
}

.markdown-editor :deep(.el-textarea__inner) {
  flex: 1;
  min-height: 0;
  font-family: 'Monaco', 'Menlo', 'Ubuntu Mono', monospace;
  font-size: 14px;
  line-height: 1.6;
  resize: none;
}

.markdown-content {
  line-height: 1.8;
  color: #333;
}

.markdown-content :deep(h1) {
  font-size: 28px;
  font-weight: 600;
  margin-top: 24px;
  margin-bottom: 16px;
  padding-bottom: 8px;
  border-bottom: 2px solid #eaecef;
  color: #24292e;
}

.markdown-content :deep(h2) {
  font-size: 24px;
  font-weight: 600;
  margin-top: 24px;
  margin-bottom: 16px;
  padding-bottom: 8px;
  border-bottom: 1px solid #eaecef;
  color: #24292e;
}

.markdown-content :deep(h3) {
  font-size: 20px;
  font-weight: 600;
  margin-top: 20px;
  margin-bottom: 12px;
  color: #24292e;
}

.markdown-content :deep(h4) {
  font-size: 16px;
  font-weight: 600;
  margin-top: 16px;
  margin-bottom: 10px;
  color: #24292e;
}

.markdown-content :deep(p) {
  margin-bottom: 16px;
  color: #24292e;
}

.markdown-content :deep(ul),
.markdown-content :deep(ol) {
  margin-bottom: 16px;
  padding-left: 30px;
}

.markdown-content :deep(li) {
  margin-bottom: 8px;
  line-height: 1.6;
}

.markdown-content :deep(code) {
  padding: 2px 6px;
  background-color: #f6f8fa;
  border-radius: 3px;
  font-family: 'Monaco', 'Menlo', 'Ubuntu Mono', monospace;
  font-size: 85%;
  color: #e83e8c;
}

.markdown-content :deep(pre) {
  background-color: #f6f8fa;
  border-radius: 6px;
  padding: 16px;
  overflow-x: auto;
  margin-bottom: 16px;
  line-height: 1.45;
}

.markdown-content :deep(pre code) {
  display: block;
  padding: 0;
  background-color: transparent;
  color: #24292e;
  font-size: 85%;
  white-space: pre;
  overflow-x: auto;
}

.markdown-content :deep(blockquote) {
  padding: 0 16px;
  color: #6a737d;
  border-left: 4px solid #dfe2e5;
  margin-bottom: 16px;
}

.markdown-content :deep(table) {
  border-collapse: collapse;
  width: 100%;
  margin-bottom: 16px;
}

.markdown-content :deep(table th),
.markdown-content :deep(table td) {
  border: 1px solid #dfe2e5;
  padding: 8px 12px;
  text-align: left;
}

.markdown-content :deep(table th) {
  background-color: #f6f8fa;
  font-weight: 600;
}

.markdown-content :deep(table tr:nth-child(even)) {
  background-color: #f6f8fa;
}

.markdown-content :deep(a) {
  color: #0366d6;
  text-decoration: none;
}

.markdown-content :deep(a:hover) {
  text-decoration: underline;
}

.markdown-content :deep(img) {
  max-width: 100%;
  height: auto;
  border-radius: 4px;
  margin-bottom: 16px;
}

.markdown-content :deep(hr) {
  height: 1px;
  background-color: #eaecef;
  border: none;
  margin: 24px 0;
}

.form-tip {
  font-size: 12px;
  color: #909399;
  margin-top: 4px;
}
</style>

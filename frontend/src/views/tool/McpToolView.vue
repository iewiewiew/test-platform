<template>
  <div class="common-list-container">
    <el-tabs v-model="activeTab" type="border-card" class="mcp-tabs">
      <!-- 资源管理 -->
      <el-tab-pane label="资源管理" name="resources">
        <div class="mcp-section">
          <div class="common-header-bar">
            <div class="common-search-bar">
              <span style="font-size: 14px; color: #606266; font-weight: 500">MCP 资源列表</span>
            </div>
            <div class="common-action-bar">
              <el-button type="primary" @click="loadResources" :loading="resourcesLoading">
                <el-icon><Refresh /></el-icon>
                刷新资源
              </el-button>
            </div>
          </div>

          <el-table :data="resources" stripe style="width: 100%" v-loading="resourcesLoading" empty-text="暂无数据">
            <el-table-column prop="name" label="名称" width="150" />
            <el-table-column prop="uri" label="URI" show-overflow-tooltip />
            <el-table-column prop="description" label="描述" />
            <el-table-column prop="mimeType" label="MIME 类型" width="150" />
            <el-table-column label="操作" width="120">
              <template #default="scope">
                <el-button type="primary" size="small" @click="readResource(scope.row.uri)">读取</el-button>
              </template>
            </el-table-column>
          </el-table>

          <el-card v-if="resourceContent" class="mcp-resource-content" style="margin-top: 20px">
            <template #header>
              <div style="display: flex; align-items: center; justify-content: space-between">
                <span style="font-weight: 500">资源内容</span>
                <el-button type="text" @click="resourceContent = null">
                  <el-icon><Close /></el-icon>
                </el-button>
              </div>
            </template>
            <pre>{{ resourceContent }}</pre>
          </el-card>
        </div>
      </el-tab-pane>

      <!-- 工具调用 -->
      <el-tab-pane label="工具调用" name="tools">
        <div class="mcp-section">
          <div class="common-header-bar">
            <div class="common-search-bar">
              <span style="font-size: 14px; color: #606266; font-weight: 500">MCP 工具列表</span>
            </div>
            <div class="common-action-bar">
              <el-button type="primary" @click="loadTools" :loading="toolsLoading">
                <el-icon><Refresh /></el-icon>
                刷新工具
              </el-button>
            </div>
          </div>

          <el-table :data="tools" stripe style="width: 100%" v-loading="toolsLoading" empty-text="暂无数据">
            <el-table-column prop="name" label="工具名称" width="200" />
            <el-table-column prop="description" label="描述" />
            <el-table-column label="操作" width="120">
              <template #default="scope">
                <el-button type="primary" size="small" @click="openToolDialog(scope.row)">调用</el-button>
              </template>
            </el-table-column>
          </el-table>

          <!-- 工具调用对话框 -->
          <el-dialog v-model="toolDialogVisible" :title="`调用工具: ${selectedTool?.name || ''}`" width="600px">
            <el-form :model="toolForm" label-width="100px">
              <el-form-item v-for="(prop, key) in toolFormSchema" :key="key" :label="prop.description || key" :required="selectedTool?.inputSchema?.required?.includes(key)">
                <el-input v-if="prop.type === 'string'" v-model="toolForm[key]" :placeholder="`请输入 ${prop.description || key}`" />
                <el-input-number v-else-if="prop.type === 'integer'" v-model="toolForm[key]" :placeholder="`请输入 ${prop.description || key}`" style="width: 100%" />
              </el-form-item>
            </el-form>
            <template #footer>
              <el-button @click="toolDialogVisible = false">取消</el-button>
              <el-button type="primary" @click="callTool" :loading="toolCalling">执行</el-button>
            </template>
          </el-dialog>

          <!-- 工具执行结果 -->
          <el-card v-if="toolResult" class="mcp-tool-result" style="margin-top: 20px">
            <template #header>
              <div style="display: flex; align-items: center; justify-content: space-between">
                <span style="font-weight: 500">执行结果</span>
                <el-button type="text" @click="toolResult = null">
                  <el-icon><Close /></el-icon>
                </el-button>
              </div>
            </template>
            <pre>{{ toolResult }}</pre>
          </el-card>
        </div>
      </el-tab-pane>

      <!-- 提示模板 -->
      <el-tab-pane label="提示模板" name="prompts">
        <div class="mcp-section">
          <div class="common-header-bar">
            <div class="common-search-bar">
              <span style="font-size: 14px; color: #606266; font-weight: 500">MCP 提示模板列表</span>
            </div>
            <div class="common-action-bar">
              <el-button type="primary" @click="loadPrompts" :loading="promptsLoading">
                <el-icon><Refresh /></el-icon>
                刷新模板
              </el-button>
            </div>
          </div>

          <el-table :data="prompts" stripe style="width: 100%" v-loading="promptsLoading" empty-text="暂无数据">
            <el-table-column prop="name" label="模板名称" width="200" />
            <el-table-column prop="description" label="描述" />
            <el-table-column label="参数" width="200">
              <template #default="scope">
                <el-tag v-for="arg in scope.row.arguments" :key="arg.name" :type="arg.required ? 'danger' : 'info'" size="small" style="margin-right: 4px">
                  {{ arg.name }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column label="操作" width="120">
              <template #default="scope">
                <el-button type="primary" size="small" @click="openPromptDialog(scope.row)">使用</el-button>
              </template>
            </el-table-column>
          </el-table>

          <!-- 提示模板对话框 -->
          <el-dialog v-model="promptDialogVisible" :title="`使用提示模板: ${selectedPrompt?.name || ''}`" width="700px">
            <el-form :model="promptForm" label-width="100px">
              <el-form-item v-for="arg in selectedPrompt?.arguments || []" :key="arg.name" :label="arg.description || arg.name" :required="arg.required">
                <el-input v-model="promptForm[arg.name]" type="textarea" :rows="arg.name === 'code' ? 8 : 3" :placeholder="`请输入 ${arg.description || arg.name}`" />
              </el-form-item>
            </el-form>
            <template #footer>
              <el-button @click="promptDialogVisible = false">取消</el-button>
              <el-button type="primary" @click="getPrompt" :loading="promptLoading">生成提示</el-button>
            </template>
          </el-dialog>

          <!-- 提示内容 -->
          <el-card v-if="promptContent" class="mcp-prompt-content" style="margin-top: 20px">
            <template #header>
              <div style="display: flex; align-items: center; justify-content: space-between">
                <span style="font-weight: 500">生成的提示内容</span>
                <el-button type="text" @click="promptContent = null">
                  <el-icon><Close /></el-icon>
                </el-button>
              </div>
            </template>
            <pre>{{ promptContent }}</pre>
          </el-card>
        </div>
      </el-tab-pane>
    </el-tabs>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { Refresh, Close } from '@element-plus/icons-vue'
import mcpService from '@/services/tool/mcpService'

const activeTab = ref('resources')

// 资源管理
const resources = ref([])
const resourcesLoading = ref(false)
const resourceContent = ref(null)

// 工具调用
const tools = ref([])
const toolsLoading = ref(false)
const selectedTool = ref(null)
const toolDialogVisible = ref(false)
const toolForm = ref({})
const toolFormSchema = ref({})
const toolCalling = ref(false)
const toolResult = ref(null)

// 提示模板
const prompts = ref([])
const promptsLoading = ref(false)
const selectedPrompt = ref(null)
const promptDialogVisible = ref(false)
const promptForm = ref({})
const promptLoading = ref(false)
const promptContent = ref(null)

// 加载资源列表
const loadResources = async () => {
  resourcesLoading.value = true
  try {
    const response = await mcpService.listResources()
    if (response.data.success) {
      resources.value = response.data.resources || []
      // ElMessage.success(`成功加载 ${response.data.count} 个资源`)
    } else {
      ElMessage.error(response.data.error || '加载资源失败')
    }
  } catch (error) {
    ElMessage.error('加载资源失败：' + (error.message || '未知错误'))
  } finally {
    resourcesLoading.value = false
  }
}

// 读取资源
const readResource = async (uri) => {
  try {
    const response = await mcpService.readResource(uri)
    if (response.data.success && response.data.contents && response.data.contents.length > 0) {
      resourceContent.value = response.data.contents[0].text
      ElMessage.success('资源读取成功')
    } else {
      ElMessage.error(response.data.error || '读取资源失败')
    }
  } catch (error) {
    ElMessage.error('读取资源失败：' + (error.message || '未知错误'))
  }
}

// 加载工具列表
const loadTools = async () => {
  toolsLoading.value = true
  try {
    const response = await mcpService.listTools()
    if (response.data.success) {
      tools.value = response.data.tools || []
      // ElMessage.success(`成功加载 ${response.data.count} 个工具`)
    } else {
      ElMessage.error(response.data.error || '加载工具失败')
    }
  } catch (error) {
    ElMessage.error('加载工具失败：' + (error.message || '未知错误'))
  } finally {
    toolsLoading.value = false
  }
}

// 打开工具调用对话框
const openToolDialog = (tool) => {
  selectedTool.value = tool
  toolForm.value = {}
  toolFormSchema.value = tool.inputSchema?.properties || {}
  toolDialogVisible.value = true
  toolResult.value = null
}

// 调用工具
const callTool = async () => {
  toolCalling.value = true
  try {
    const response = await mcpService.callTool(selectedTool.value.name, toolForm.value)
    if (response.data.success && response.data.content && response.data.content.length > 0) {
      toolResult.value = response.data.content[0].text
      ElMessage.success('工具执行成功')
      toolDialogVisible.value = false
    } else {
      ElMessage.error(response.data.error || '工具执行失败')
    }
  } catch (error) {
    ElMessage.error('工具执行失败：' + (error.message || '未知错误'))
  } finally {
    toolCalling.value = false
  }
}

// 加载提示模板列表
const loadPrompts = async () => {
  promptsLoading.value = true
  try {
    const response = await mcpService.listPrompts()
    if (response.data.success) {
      prompts.value = response.data.prompts || []
      // ElMessage.success(`成功加载 ${response.data.count} 个提示模板`)
    } else {
      ElMessage.error(response.data.error || '加载提示模板失败')
    }
  } catch (error) {
    ElMessage.error('加载提示模板失败：' + (error.message || '未知错误'))
  } finally {
    promptsLoading.value = false
  }
}

// 打开提示模板对话框
const openPromptDialog = (prompt) => {
  selectedPrompt.value = prompt
  promptForm.value = {}
  promptDialogVisible.value = true
  promptContent.value = null
}

// 获取提示内容
const getPrompt = async () => {
  promptLoading.value = true
  try {
    const response = await mcpService.getPrompt(selectedPrompt.value.name, promptForm.value)
    if (response.data.success && response.data.messages && response.data.messages.length > 0) {
      promptContent.value = response.data.messages[0].content.text
      ElMessage.success('提示生成成功')
      promptDialogVisible.value = false
    } else {
      ElMessage.error(response.data.error || '生成提示失败')
    }
  } catch (error) {
    ElMessage.error('生成提示失败：' + (error.message || '未知错误'))
  } finally {
    promptLoading.value = false
  }
}

// 初始化
onMounted(() => {
  loadResources()
  loadTools()
  loadPrompts()
})
</script>

<style scoped>
.mcp-tabs {
  background-color: transparent;
  box-shadow: none;
  height: 100%;
  display: flex;
  flex-direction: column;
}

.mcp-tabs :deep(.el-tabs__content) {
  flex: 1;
  overflow: auto;
  padding: 20px 0;
}

.mcp-section {
  height: 100%;
  display: flex;
  flex-direction: column;
}

.mcp-resource-content,
.mcp-tool-result,
.mcp-prompt-content {
  flex-shrink: 0;
}

:deep(.el-card__header) {
  font-weight: 500;
  background-color: #f8f9fa;
  border-bottom: 1px solid #ebeef5;
  padding: 12px 16px;
  font-size: 14px;
}

:deep(.el-card__body) {
  padding: 16px;
}

:deep(pre) {
  margin: 0;
  font-family: 'Monaco', 'Menlo', 'Ubuntu Mono', monospace;
  font-size: 13px;
}
</style>

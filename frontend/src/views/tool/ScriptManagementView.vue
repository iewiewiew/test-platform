<template>
  <div class="common-list-container">
    <!-- 顶部操作栏 -->
    <div class="common-header-bar">
      <div class="common-search-bar">
        <el-form :inline="true" :model="searchForm" class="demo-form-inline">
          <el-form-item label="脚本名称">
            <el-input
              v-model="searchForm.name"
              placeholder="请输入脚本名称"
              clearable
              style="width: 200px"
              @input="handleInputSearch"
            />
          </el-form-item>
          <el-form-item label="脚本类型">
            <el-select
              v-model="searchForm.script_type"
              placeholder="请选择"
              clearable
              style="width: 150px"
              @change="handleSearch"
            >
              <el-option label="Python" value="python" />
              <el-option label="Shell" value="shell" />
              <el-option label="Bash" value="bash" />
            </el-select>
          </el-form-item>
          <el-form-item>
            <el-button @click="resetSearch">重置</el-button>
          </el-form-item>
        </el-form>
      </div>
      <div class="common-action-bar">
        <el-button type="primary" @click="createScript">创建</el-button>
      </div>
    </div>

    <el-table :data="store.scripts" v-loading="store.loading" style="width: 100%" empty-text="暂无数据">
      <el-table-column prop="id" label="ID" width="60" />
      <el-table-column prop="name" label="脚本名称" width="150" />
      <el-table-column prop="description" label="描述" show-overflow-tooltip min-width="100" />
      <el-table-column prop="script_type" label="类型" width="100" align="center">
        <template #default="{ row }">
          <el-tag :type="getScriptTypeTag(row.script_type)">{{ row.script_type }}</el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="is_enabled" label="状态" width="100" align="center">
        <template #default="{ row }">
          <el-tag :type="row.is_enabled ? 'success' : 'info'">
            {{ row.is_enabled ? '启用' : '禁用' }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="is_scheduled" label="定时任务" width="100" align="center">
        <template #default="{ row }">
          <el-tag v-if="row.is_scheduled" type="warning">已启用</el-tag>
          <span v-else>-</span>
        </template>
      </el-table-column>
      <el-table-column prop="total_executions" label="执行次数" width="100" align="center" />
      <el-table-column prop="success_count" label="成功" width="80" align="center">
        <template #default="{ row }">
          <span style="color: #67c23a">{{ row.success_count || 0 }}</span>
        </template>
      </el-table-column>
      <el-table-column prop="failure_count" label="失败" width="80" align="center">
        <template #default="{ row }">
          <span style="color: #f56c6c">{{ row.failure_count || 0 }}</span>
        </template>
      </el-table-column>
      <el-table-column prop="creator_name" label="创建人" width="120" />
      <el-table-column prop="updater_name" label="更新人" width="120" />
      <el-table-column prop="created_at" label="创建时间" width="160" sortable :formatter="formatDate" />
      <el-table-column prop="updated_at" label="更新时间" width="160" sortable :formatter="formatDate" />
      <el-table-column label="操作" width="300" fixed="right">
        <template #default="{ row }">
          <el-button size="small" @click="viewScript(row.id)">查看</el-button>
          <el-button 
            size="small" 
            type="primary" 
            @click="executeScript(row.id)" 
            :loading="executingIds.includes(row.id)"
            :disabled="executingIds.includes(row.id)"
          >
            {{ executingIds.includes(row.id) ? '执行' : '执行' }}
          </el-button>
          <el-button size="small" @click="editScript(row.id)">编辑</el-button>
          <el-button size="small" type="danger" @click="deleteScript(row)">删除</el-button>
        </template>
      </el-table-column>
    </el-table>

    <!-- 分页 -->
    <div class="pagination">
      <el-pagination
        v-model:current-page="currentPage"
        v-model:page-size="pageSize"
        :total="store.pagination.total"
        :page-sizes="[10, 20, 50, 100]"
        :background="true"
        layout="total, sizes, prev, pager, next, jumper"
        @update:current-page="handlePageChange"
        @update:page-size="handleSizeChange"
      />
    </div>

    <!-- 创建/编辑脚本对话框 -->
    <el-dialog
      v-model="showScriptDialog"
      :title="dialogTitle"
      width="800px"
      :close-on-click-modal="false"
    >
      <el-form :model="scriptForm" label-width="100px" ref="scriptFormRef">
        <el-form-item label="脚本名称" prop="name" :rules="[{ required: true, message: '请输入脚本名称', trigger: 'blur' }]">
          <el-input v-model="scriptForm.name" placeholder="请输入脚本名称" />
        </el-form-item>
        <el-form-item label="脚本描述">
          <el-input
            v-model="scriptForm.description"
            type="textarea"
            :rows="2"
            placeholder="请输入脚本描述"
          />
        </el-form-item>
        <el-form-item label="脚本类型" prop="script_type" :rules="[{ required: true, message: '请选择脚本类型', trigger: 'change' }]">
          <el-select v-model="scriptForm.script_type" placeholder="请选择脚本类型">
            <el-option label="Python" value="python" />
            <el-option label="Shell" value="shell" />
            <el-option label="Bash" value="bash" />
          </el-select>
        </el-form-item>
        <el-form-item label="脚本内容" prop="script_content" :rules="[{ required: true, message: '请输入脚本内容', trigger: 'blur' }]">
          <el-input
            v-model="scriptForm.script_content"
            type="textarea"
            :rows="12"
            placeholder="请输入脚本内容，例如：&#10;#!/usr/bin/env python3&#10;print('Hello World')"
          />
        </el-form-item>
        <el-form-item label="是否启用">
          <el-switch v-model="scriptForm.is_enabled" />
        </el-form-item>
        <el-form-item label="超时时间(秒)">
          <el-input-number v-model="scriptForm.timeout_seconds" :min="1" :max="3600" style="width: 200px" />
        </el-form-item>
        <el-form-item label="定时任务">
          <el-switch v-model="scriptForm.is_scheduled" />
        </el-form-item>
        <el-form-item v-if="scriptForm.is_scheduled" label="Cron表达式">
          <el-input
            v-model="scriptForm.cron_expression"
            placeholder="例如：0 0 * * * (每天凌晨执行)"
            style="width: 300px"
            @input="calculateNextExecutionTime"
          />
          <el-link type="primary" href="https://crontab.guru/" target="_blank" style="margin-left: 10px">
            Cron表达式生成器
          </el-link>
        </el-form-item>
        <el-form-item v-if="scriptForm.is_scheduled && nextExecutionTime && scriptForm.cron_expression" label="下一次执行">
          <div style="color: #409eff; font-size: 13px; display: flex; align-items: center;">
            <el-icon style="margin-right: 4px;"><Clock /></el-icon>
            <span>{{ nextExecutionTime }}</span>
          </div>
        </el-form-item>
        <el-form-item v-if="scriptForm.is_scheduled && scriptForm.cron_expression && !nextExecutionTime && cronError" label=" ">
          <div style="color: #f56c6c; font-size: 13px; display: flex; align-items: center;">
            <el-icon style="margin-right: 4px;"><WarningFilled /></el-icon>
            <span>{{ cronError }}</span>
          </div>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showScriptDialog = false">取消</el-button>
        <el-button type="primary" @click="handleSubmitScript" :loading="submitting">
          {{ isEditMode ? '更新' : '创建' }}
        </el-button>
      </template>
    </el-dialog>

    <!-- 查看脚本执行结果对话框 -->
    <el-dialog
      v-model="showViewDialog"
      title="执行结果"
      width="900px"
    >
      <div v-if="latestExecution" style="margin-bottom: 16px;">
        <el-alert
          :title="`最近执行时间: ${formatDateTime(latestExecution.start_time)}`"
          :type="latestExecution.status === 'success' ? 'success' : latestExecution.status === 'failed' ? 'error' : 'info'"
          :description="`状态: ${getStatusText(latestExecution.status)} | 耗时: ${latestExecution.duration_seconds ? latestExecution.duration_seconds.toFixed(2) : '-'}秒 | 退出码: ${latestExecution.exit_code !== null ? latestExecution.exit_code : '-'}`"
          show-icon
          :closable="false"
        />
      </div>
      <div v-else style="margin-bottom: 16px;">
        <el-alert
          title="暂无执行记录"
          type="info"
          description="该脚本尚未执行过"
          show-icon
          :closable="false"
        />
      </div>
      <div v-if="latestExecution">
        <div style="margin-bottom: 16px;">
          <h4 style="margin: 0 0 8px 0; font-size: 14px; font-weight: 600;">标准输出 (stdout)</h4>
          <pre style="background: #f5f5f5; padding: 12px; border-radius: 4px; max-height: 400px; overflow: auto; margin: 0; font-family: 'Monaco', 'Menlo', 'Ubuntu Mono', monospace; font-size: 12px; line-height: 1.5; white-space: pre-wrap; word-wrap: break-word;">{{ latestExecution.output || '(无输出)' }}</pre>
        </div>
        <div v-if="latestExecution.error_output">
          <h4 style="margin: 0 0 8px 0; font-size: 14px; font-weight: 600; color: #f56c6c;">错误输出 (stderr)</h4>
          <pre style="background: #fee; padding: 12px; border-radius: 4px; max-height: 400px; overflow: auto; margin: 0; font-family: 'Monaco', 'Menlo', 'Ubuntu Mono', monospace; font-size: 12px; line-height: 1.5; white-space: pre-wrap; word-wrap: break-word;">{{ latestExecution.error_output }}</pre>
        </div>
      </div>
      <template #footer>
        <el-button @click="showViewDialog = false">关闭</el-button>
      </template>
    </el-dialog>

    <!-- 执行详情对话框 -->
    <el-dialog
      v-model="showExecutionDetailDialog"
      title="执行详情"
      width="900px"
    >
      <el-descriptions :column="2" border v-if="store.currentExecution">
        <el-descriptions-item label="执行类型">
          <el-tag :type="store.currentExecution.execution_type === 'manual' ? 'primary' : 'warning'">
            {{ store.currentExecution.execution_type === 'manual' ? '手动' : '定时' }}
          </el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="状态">
          <el-tag :type="getStatusTag(store.currentExecution.status)">
            {{ getStatusText(store.currentExecution.status) }}
          </el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="开始时间" :span="2">
          {{ formatDateTime(store.currentExecution.start_time) }}
        </el-descriptions-item>
        <el-descriptions-item label="结束时间" v-if="store.currentExecution.end_time" :span="2">
          {{ formatDateTime(store.currentExecution.end_time) }}
        </el-descriptions-item>
        <el-descriptions-item label="耗时" v-if="store.currentExecution.duration_seconds">
          {{ store.currentExecution.duration_seconds.toFixed(2) }}秒
        </el-descriptions-item>
        <el-descriptions-item label="退出码" v-if="store.currentExecution.exit_code !== null">
          {{ store.currentExecution.exit_code }}
        </el-descriptions-item>
        <el-descriptions-item label="输出内容" :span="2">
          <pre style="background: #f5f5f5; padding: 10px; border-radius: 4px; max-height: 200px; overflow: auto">{{ store.currentExecution.output || '(无输出)' }}</pre>
        </el-descriptions-item>
        <el-descriptions-item label="错误输出" v-if="store.currentExecution.error_output" :span="2">
          <pre style="background: #fee; padding: 10px; border-radius: 4px; max-height: 200px; overflow: auto">{{ store.currentExecution.error_output }}</pre>
        </el-descriptions-item>
      </el-descriptions>
      <template #footer>
        <el-button @click="showExecutionDetailDialog = false">关闭</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onBeforeUnmount, watch } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Clock, WarningFilled } from '@element-plus/icons-vue'
import { useScriptManagementStore } from '@/stores/tool/scriptManagementStore'
import { formatDateTime } from '@/utils/date'
import { CronExpressionParser } from 'cron-parser'

const store = useScriptManagementStore()

// 搜索表单
const searchForm = ref({
  name: '',
  script_type: ''
})

// 分页
const currentPage = ref(1)
const pageSize = ref(20)

// 对话框
const showScriptDialog = ref(false)
const showViewDialog = ref(false)
const showExecutionDetailDialog = ref(false)
const isEditMode = ref(false)
const submitting = ref(false)
const executingIds = ref([])
const latestExecution = ref(null)
// 存储每个执行ID的轮询定时器，避免重复轮询
const pollingTimers = ref(new Map())

// 脚本表单
const scriptForm = ref({
  name: '',
  description: '',
  script_type: 'python',
  script_content: '',
  is_enabled: true,
  is_scheduled: false,
  cron_expression: '',
  timeout_seconds: 300
})

const scriptFormRef = ref(null)

// 下一次执行时间相关
const nextExecutionTime = ref('')
const cronError = ref('')

// 搜索防抖
let searchTimer = null

// 计算属性
const dialogTitle = computed(() => isEditMode.value ? '编辑' : '创建')

// 计算下一次执行时间
const calculateNextExecutionTime = () => {
  const cronExpr = scriptForm.value.cron_expression?.trim()
  nextExecutionTime.value = ''
  cronError.value = ''
  
  if (!cronExpr) {
    return
  }
  
  try {
    // 验证 cron 表达式格式（5个字段）
    const parts = cronExpr.split(/\s+/)
    if (parts.length !== 5) {
      cronError.value = 'Cron表达式格式错误：应为5个字段（分钟 小时 日 月 星期）'
      return
    }
    
    // 使用 cron-parser 解析并计算下一次执行时间
    const interval = CronExpressionParser.parse(cronExpr)
    const nextDate = interval.next()
    // formatDateTime 可以处理 Date 对象或 ISO 字符串
    nextExecutionTime.value = formatDateTime(nextDate.toDate())
  } catch (error) {
    cronError.value = `Cron表达式错误：${error.message}`
  }
}

// 监听 cron 表达式变化
watch(() => scriptForm.value.cron_expression, () => {
  if (scriptForm.value.is_scheduled) {
    calculateNextExecutionTime()
  }
})

// 监听定时任务开关变化
watch(() => scriptForm.value.is_scheduled, (newVal) => {
  if (newVal && scriptForm.value.cron_expression) {
    calculateNextExecutionTime()
  } else {
    nextExecutionTime.value = ''
    cronError.value = ''
  }
})

// 方法
const handleInputSearch = () => {
  clearTimeout(searchTimer)
  searchTimer = setTimeout(() => {
    currentPage.value = 1
    fetchScripts()
  }, 500)
}

const handleSearch = () => {
  currentPage.value = 1
  fetchScripts()
}

const resetSearch = () => {
  searchForm.value = { name: '', script_type: '' }
  currentPage.value = 1
  fetchScripts()
}

const fetchScripts = async () => {
  try {
    await store.fetchScripts({
      page: currentPage.value,
      per_page: pageSize.value,
      name: searchForm.value.name,
      script_type: searchForm.value.script_type
    })
  } catch (error) {
    ElMessage.error(store.error || '获取脚本列表失败')
  }
}

const handlePageChange = () => {
  fetchScripts()
}

const handleSizeChange = () => {
  currentPage.value = 1
  fetchScripts()
}

const formatDate = (row, column, cellValue) => {
  return cellValue ? formatDateTime(cellValue) : '-'
}

const getScriptTypeTag = (type) => {
  const map = { python: 'success', shell: 'warning', bash: 'warning' }
  return map[type] || ''
}

const getStatusTag = (status) => {
  const map = {
    running: 'warning',
    success: 'success',
    failed: 'danger',
    cancelled: 'info'
  }
  return map[status] || ''
}

const getStatusText = (status) => {
  const map = {
    running: '执行中',
    success: '成功',
    failed: '失败',
    cancelled: '已取消'
  }
  return map[status] || status
}

// 获取脚本类型的默认内容
const getDefaultScriptContent = (scriptType) => {
  const type = scriptType?.toLowerCase() || 'python'
  
  if (type === 'python' || type === 'py') {
    return `#!/usr/bin/env python3
# -*- coding:utf-8 -*-

"""
脚本描述：请在这里填写脚本的功能说明
"""

import os
import sys

def main():
    print('Hello World')
    # 在这里编写你的脚本逻辑

if __name__ == '__main__':
    main()
`
  } else if (type === 'shell' || type === 'bash' || type === 'sh') {
    return `#!/bin/bash

# 脚本描述：请在这里填写脚本的功能说明

# 示例：执行远程命令
# sshpass -p 'password' ssh root@host -o StrictHostKeyChecking=no -o BatchMode=yes 'ls -al'

echo "Hello World"
# 在这里编写你的脚本逻辑
`
  } else {
    return `# 脚本内容
# 请在这里填写你的脚本内容
`
  }
}

const resetScriptForm = () => {
  scriptForm.value = {
    name: '',
    description: '',
    script_type: 'python',
    script_content: getDefaultScriptContent('python'),
    is_enabled: true,
    is_scheduled: false,
    cron_expression: '',
    timeout_seconds: 300
  }
  isEditMode.value = false
}

const createScript = () => {
  resetScriptForm()
  showScriptDialog.value = true
}

const editScript = async (id) => {
  try {
    await store.fetchScriptById(id)
    if (store.currentScript) {
      scriptForm.value = {
        name: store.currentScript.name,
        description: store.currentScript.description || '',
        script_type: store.currentScript.script_type,
        script_content: store.currentScript.script_content,
        is_enabled: store.currentScript.is_enabled,
        is_scheduled: store.currentScript.is_scheduled || false,
        cron_expression: store.currentScript.cron_expression || '',
        timeout_seconds: store.currentScript.timeout_seconds || 300
      }
      isEditMode.value = true
      showScriptDialog.value = true
      // 如果是定时任务且有 cron 表达式，计算下一次执行时间
      if (scriptForm.value.is_scheduled && scriptForm.value.cron_expression) {
        calculateNextExecutionTime()
      }
    }
  } catch (error) {
    ElMessage.error(store.error || '获取脚本详情失败')
  }
}

const handleSubmitScript = async () => {
  if (!scriptFormRef.value) return
  
  try {
    await scriptFormRef.value.validate()
    submitting.value = true
    
    if (isEditMode.value) {
      const scriptId = store.currentScript.id
      await store.updateScript(scriptId, scriptForm.value)
      ElMessage.success('脚本更新成功')
    } else {
      await store.createScript(scriptForm.value)
      ElMessage.success('脚本创建成功')
    }
    
    showScriptDialog.value = false
    resetScriptForm()
    fetchScripts()
  } catch (error) {
    if (error !== false) { // 表单验证失败会返回false
      ElMessage.error(store.error || '操作失败')
    }
  } finally {
    submitting.value = false
  }
}

const viewScript = async (id) => {
  try {
    // 获取最近的执行记录
    await store.fetchExecutionHistory({
      page: 1,
      per_page: 1,
      script_id: id
    })
    // 从 store 中获取最新的执行记录
    latestExecution.value = store.executionHistory && store.executionHistory.length > 0 ? store.executionHistory[0] : null
    showViewDialog.value = true
  } catch (error) {
    latestExecution.value = null
    ElMessage.error(store.error || '获取执行记录失败')
  }
}

const deleteScript = async (row) => {
  try {
    await ElMessageBox.confirm(`确定要删除脚本 "${row.name}" 吗？`, '确认删除', {
      type: 'warning',
      confirmButtonText: '删除',
      cancelButtonText: '取消'
    })
    
    await store.deleteScript(row.id)
    ElMessage.success('删除成功')
    fetchScripts()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error(store.error || '删除失败')
    }
  }
}

const executeScript = async (id) => {
  try {
    // 将脚本ID添加到执行中列表，按钮将显示为"执行中"并禁用
    executingIds.value.push(id)
    const result = await store.executeScriptWithoutHistory(id, 'manual')
    ElMessage.success(`脚本执行已启动，执行ID: ${result.execution_id}`)
    // 开始轮询执行状态，直到执行完成
    if (result.execution_id) {
      pollExecutionStatus(result.execution_id, id)
    } else {
      // 如果没有返回 execution_id，立即恢复按钮状态
      const index = executingIds.value.indexOf(id)
      if (index > -1) executingIds.value.splice(index, 1)
    }
    // 只刷新脚本列表
    fetchScripts()
  } catch (error) {
    ElMessage.error(store.error || '执行脚本失败')
    // 执行失败时也要恢复按钮状态
    const index = executingIds.value.indexOf(id)
    if (index > -1) executingIds.value.splice(index, 1)
  }
}

const pollExecutionStatus = (executionId, scriptId) => {
  // 如果该执行ID已经在轮询中，先清除之前的轮询
  if (pollingTimers.value.has(executionId)) {
    clearTimeout(pollingTimers.value.get(executionId))
    pollingTimers.value.delete(executionId)
  }
  
  const maxAttempts = 60 // 最多轮询60次
  let attempts = 0
  
  const poll = async () => {
    // 清除定时器引用，因为这次轮询已经执行
    pollingTimers.value.delete(executionId)
    
    if (attempts >= maxAttempts) {
      ElMessage.warning('轮询超时，请手动查看执行结果')
      // 超时后也要恢复按钮状态
      if (scriptId) {
        const index = executingIds.value.indexOf(scriptId)
        if (index > -1) executingIds.value.splice(index, 1)
      }
      return
    }
    
    try {
      await store.fetchExecutionById(executionId)
      const status = store.currentExecution?.status
      
      if (status === 'running') {
        attempts++
        // 设置下一次轮询的定时器，并记录到 Map 中
        const timerId = setTimeout(poll, 2000)
        pollingTimers.value.set(executionId, timerId)
      } else {
        // 执行完成，清除轮询
        pollingTimers.value.delete(executionId)
        ElMessage.info(`脚本执行${status === 'success' ? '成功' : '失败'}`)
        // 恢复按钮状态，允许再次点击
        if (scriptId) {
          const index = executingIds.value.indexOf(scriptId)
          if (index > -1) executingIds.value.splice(index, 1)
        }
        // 刷新脚本列表以更新统计数据
        fetchScripts()
      }
    } catch (error) {
      // 请求失败时也清除轮询
      pollingTimers.value.delete(executionId)
      // 请求失败时也要恢复按钮状态
      if (scriptId) {
        const index = executingIds.value.indexOf(scriptId)
        if (index > -1) executingIds.value.splice(index, 1)
      }
      console.error('轮询执行状态失败:', error)
    }
  }
  
  // 立即执行第一次轮询
  poll()
}

// 清除所有轮询定时器
const clearAllPolling = () => {
  pollingTimers.value.forEach((timerId) => {
    clearTimeout(timerId)
  })
  pollingTimers.value.clear()
}

const viewExecutionDetail = async (id) => {
  try {
    await store.fetchExecutionById(id)
    showExecutionDetailDialog.value = true
  } catch (error) {
    ElMessage.error(store.error || '获取执行详情失败')
  }
}

const cancelExecution = async (id) => {
  try {
    await ElMessageBox.confirm('确定要取消正在执行的脚本吗？', '确认取消', {
      type: 'warning'
    })
    
    await store.cancelExecution(id)
    ElMessage.success('任务已取消')
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error(store.error || '取消执行失败')
    }
  }
}

// 生命周期
onMounted(() => {
  fetchScripts()
})

// 组件卸载前清除所有轮询定时器
onBeforeUnmount(() => {
  clearAllPolling()
})
</script>

<style scoped>
/* 代码块样式 */
pre {
  margin: 0;
  font-family: 'Monaco', 'Menlo', 'Ubuntu Mono', monospace;
  font-size: 12px;
  line-height: 1.5;
}
</style>

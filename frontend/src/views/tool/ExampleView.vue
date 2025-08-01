<template>
  <div class="common-list-container">
    <div class="common-header-bar">
      <div class="common-search-bar">
        <el-form :inline="true" :model="searchForm" class="demo-form-inline">
          <el-form-item label="名称">
            <el-input v-model="searchForm.name" placeholder="请输入名称" clearable @input="handleInputSearch" />
          </el-form-item>
          <el-form-item label="状态">
            <el-select v-model="searchForm.status" placeholder="请选择状态" clearable @change="handleSearch">
              <el-option label="激活" value="active" />
              <el-option label="禁用" value="inactive" />
            </el-select>
          </el-form-item>
          <el-form-item>
            <el-button @click="resetSearch">重置</el-button>
          </el-form-item>
        </el-form>
      </div>

      <div class="common-action-bar">
        <el-button type="danger" :disabled="selectedIds.size === 0" @click="handleBatchDelete" :loading="batchDeleteLoading">批量删除({{ selectedIds.size }})</el-button>
        <el-button type="primary" @click="showCreateDialog = true">创建</el-button>
      </div>
    </div>

    <!-- 表格操作栏 -->
    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px; padding: 0 4px">
      <div style="display: flex; align-items: center; gap: 12px">
        <span style="color: #606266; font-size: 14px">
          已选择
          <span style="color: #409eff; font-weight: 500">{{ selectedIds.size }}</span>
          项
        </span>
        <el-button text type="primary" size="small" @click="selectAll" :loading="selectAllLoading">全选所有页</el-button>
      </div>
    </div>

    <!-- 关键修复：使用计算属性确保数据是数组 -->
    <el-table ref="tableRef" :data="tableData" style="width: 100%" v-loading="store.loading" empty-text="暂无数据" :key="tableKey" @selection-change="handleSelectionChange" row-key="id">
      <el-table-column type="selection" width="55" :reserve-selection="true" />
      <el-table-column prop="id" label="ID" width="60" />
      <el-table-column prop="name" label="名称" width="200" show-overflow-tooltip />
      <el-table-column prop="description" label="描述" show-overflow-tooltip />
      <el-table-column prop="status" label="状态" width="100">
        <template #default="{ row }">
          <el-tag :type="row.status === 'active' ? 'success' : 'danger'">
            {{ getStatusText(row.status) }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="creator_name" label="创建人" width="120" />
      <el-table-column prop="updater_name" label="更新人" width="120" />
      <el-table-column prop="created_at" label="创建时间" width="160" sortable :formatter="formatDate" />
      <el-table-column prop="updated_at" label="更新时间" width="160" sortable :formatter="formatDate" />

      <el-table-column label="操作" width="200">
        <template #default="scope">
          <el-button size="small" @click="editExample(scope.row.id)">编辑</el-button>
          <el-button size="small" type="danger" @click="confirmDelete(scope.row)">删除</el-button>
        </template>
      </el-table-column>
    </el-table>

    <div class="pagination">
      <el-pagination
        v-model:current-page="store.pagination.currentPage"
        v-model:page-size="store.pagination.pageSize"
        :total="store.pagination.total"
        :page-sizes="[10, 20, 50, 100]"
        :background="true"
        layout="total, sizes, prev, pager, next, jumper"
        @update:current-page="handlePageChange"
        @update:page-size="handleSizeChange"
      />
    </div>

    <el-dialog v-model="showCreateDialog" title="创建" :before-close="handleDialogClose">
      <ExampleDialog :editing-item="null" :loading="dialogLoading" @submit="handleCreate" @cancel="showCreateDialog = false" />
    </el-dialog>

    <el-dialog v-model="showEditDialog" title="编辑" :before-close="handleDialogClose">
      <ExampleDialog :editing-item="store.currentExample" :loading="dialogLoading" @submit="handleUpdate" @cancel="showEditDialog = false" />
    </el-dialog>
  </div>
</template>

<script setup>
// ==================== 导入语句 ====================
// Vue相关
import { ref, onMounted, computed, nextTick, watch } from 'vue'
// Element Plus
import { ElMessage, ElMessageBox } from 'element-plus'
// Store
import { useExampleStore } from '@/stores/tool/exampleStore'
// 组件
import ExampleDialog from '@/components/example/ExampleDialog.vue'
// 工具函数
import { formatDateTime } from '@/utils/date'
// 服务（仅用于批量删除，其他操作通过store）
import { exampleService } from '@/services/tool/exampleService'

// ==================== Store ====================
const store = useExampleStore()

// ==================== 响应式数据 ====================
// 对话框状态
const dialogLoading = ref(false)
const showCreateDialog = ref(false)
const showEditDialog = ref(false)

// 表格相关
const tableKey = ref(0) // 用于强制表格重新渲染
const tableRef = ref(null) // 表格引用

// 加载状态
const batchDeleteLoading = ref(false)
const selectAllLoading = ref(false)

// 选中状态：使用Set存储所有选中的ID（支持跨页）
const selectedIds = ref(new Set())
const selectAllMode = ref(false) // 是否处于全选所有页模式

// 搜索表单
const searchForm = ref({
  name: '',
  status: ''
})

// 防抖计时器
let searchTimer = null

// ==================== 计算属性 ====================
// 计算属性确保表格数据是数组
const tableData = computed(() => {
  return Array.isArray(store.examples) ? store.examples : []
})

// ==================== 常量/配置 ====================
// 状态文本映射
const statusMap = {
  active: '激活',
  inactive: '禁用'
}

// ==================== 工具函数 ====================
// 获取状态文本
const getStatusText = (status) => {
  return statusMap[status] || status
}

// 格式化日期
const formatDate = (row, column, cellValue) => {
  return cellValue ? formatDateTime(cellValue) : '-'
}

// 强制刷新表格
const refreshTable = () => {
  tableKey.value += 1
}

// ==================== 数据获取/刷新 ====================
// 更新表格选中状态
const updateTableSelection = async () => {
  if (!tableRef.value) {
    console.log('updateTableSelection - tableRef不存在')
    return
  }

  // 等待DOM更新
  await nextTick()

  // 根据selectedIds设置当前页的选中状态
  if (!tableData.value || tableData.value.length === 0) {
    console.log('updateTableSelection - tableData为空')
    tableRef.value.clearSelection()
    return
  }

  if (selectedIds.value.size === 0) {
    console.log('updateTableSelection - selectedIds为空，清除所有选择')
    tableRef.value.clearSelection()
    return
  }

  // 收集需要选中的行ID
  const idsToSelect = tableData.value.filter((row) => row && row.id !== undefined && selectedIds.value.has(row.id)).map((row) => row.id)

  console.log(
    'updateTableSelection - 需要选中的行数:',
    idsToSelect.length,
    '当前页数据:',
    tableData.value.length,
    'selectedIds数量:',
    selectedIds.value.size,
    '当前页的ID列表:',
    tableData.value.map((r) => r.id),
    '应该选中的ID:',
    idsToSelect
  )

  // 清除所有选择
  tableRef.value.clearSelection()

  // 等待一下确保clearSelection完成
  await nextTick()

  // 批量设置选中状态 - 使用表格数据中的实际行对象
  if (idsToSelect.length > 0) {
    idsToSelect.forEach((id) => {
      const actualRow = tableData.value.find((r) => r && r.id === id)
      if (actualRow) {
        try {
          tableRef.value.toggleRowSelection(actualRow, true)
        } catch (error) {
          console.error('toggleRowSelection失败 - ID:', id, error)
        }
      } else {
        console.warn('找不到ID为', id, '的行')
      }
    })
  }

  // 等待一下确保所有选择都已应用
  await nextTick()

  // 验证选中状态
  try {
    if (tableRef.value && typeof tableRef.value.getSelectionRows === 'function') {
      const selectedRows = tableRef.value.getSelectionRows()
      console.log('updateTableSelection - 实际选中的行数:', selectedRows?.length || 0, '选中的ID:', selectedRows?.map((r) => r.id) || [])
    }
  } catch (error) {
    console.error('获取选中行失败:', error)
  }
}

// ==================== 搜索/筛选 ====================
// 输入搜索处理（防抖）
const handleInputSearch = () => {
  clearTimeout(searchTimer)
  searchTimer = setTimeout(() => {
    handleSearch()
  }, 500)
}

// 搜索处理
const handleSearch = async () => {
  try {
    // 搜索时清空选择
    selectedIds.value.clear()
    selectAllMode.value = false

    await store.fetchExamples({
      page: 1,
      name: searchForm.value.name.trim(),
      status: searchForm.value.status
    })
    // 数据更新后刷新表格
    nextTick(async () => {
      refreshTable()
      await updateTableSelection()
    })
  } catch (error) {
    if (store.error) {
      ElMessage.error(store.error)
    }
  }
}

// 重置搜索
const resetSearch = async () => {
  // 重置时清空选择
  selectedIds.value.clear()
  selectAllMode.value = false

  searchForm.value = {
    name: '',
    status: ''
  }
  try {
    await store.fetchExamples({ page: 1 })
    nextTick(async () => {
      refreshTable()
      await updateTableSelection()
    })
  } catch (error) {
    if (store.error) {
      ElMessage.error(store.error)
    }
  }
}

// ==================== CRUD操作 ====================
// 创建示例
const handleCreate = async (exampleData) => {
  try {
    dialogLoading.value = true
    await store.createExample(exampleData)
    showCreateDialog.value = false
    ElMessage.success('示例创建成功')
    // 创建成功后刷新表格
    nextTick(() => {
      refreshTable()
    })
  } catch (error) {
    if (store.error) {
      ElMessage.error(store.error)
    }
  } finally {
    dialogLoading.value = false
  }
}

// 获取示例详情
const editExample = async (id) => {
  try {
    await store.fetchExample(id)
    showEditDialog.value = true
  } catch (error) {
    if (store.error) {
      ElMessage.error(store.error)
    }
  }
}

// 更新示例
const handleUpdate = async (exampleData) => {
  try {
    dialogLoading.value = true
    await store.updateExample(store.currentExample.id, exampleData)
    showEditDialog.value = false
    ElMessage.success('示例更新成功')
    // 更新成功后刷新表格
    nextTick(() => {
      refreshTable()
    })
  } catch (error) {
    if (store.error) {
      ElMessage.error(store.error)
    }
  } finally {
    dialogLoading.value = false
  }
}

// 确认删除
const confirmDelete = (example) => {
  ElMessageBox.confirm(`确定要删除示例 "${example.name}" 吗？`, '删除确认', {
    confirmButtonText: '确定',
    cancelButtonText: '取消',
    type: 'warning'
  })
    .then(async () => {
      await deleteExample(example)
    })
    .catch(() => {
      ElMessage.info('已取消删除')
    })
}

// 删除示例
const deleteExample = async (example) => {
  try {
    await store.deleteExample(example.id)
    ElMessage.success('示例删除成功')
    // 删除成功后刷新表格
    nextTick(() => {
      refreshTable()
    })
  } catch (error) {
    if (store.error) {
      ElMessage.error(store.error)
    }
  }
}

// ==================== 选择相关 ====================
// 处理表格选择变化
const handleSelectionChange = (selection) => {
  // 获取当前页的ID列表
  const currentPageIds = tableData.value.map((item) => item.id)

  // 移除当前页的所有ID（因为可能从选中变为未选中）
  currentPageIds.forEach((id) => selectedIds.value.delete(id))

  // 添加新选中的ID
  selection.forEach((row) => {
    selectedIds.value.add(row.id)
  })

  // 如果当前页全选且在跨页全选模式，保持跨页全选状态
  // 如果当前页未全选，取消跨页全选模式
  if (selection.length === tableData.value.length && tableData.value.length > 0) {
    // 当前页全选，保持全选模式（如果已开启）
  } else {
    // 当前页未全选，如果处于全选模式，则退出全选模式
    if (selectAllMode.value && selection.length < tableData.value.length) {
      selectAllMode.value = false
    }
  }
}

// 全选所有页
const selectAll = async () => {
  try {
    // 获取所有数据的总数
    const total = store.pagination.total

    if (total === 0) {
      ElMessage.warning('没有数据可全选')
      return
    }

    selectAllLoading.value = true

    // 设置为全选模式
    selectAllMode.value = true

    // 先加载所有页的数据获取所有ID（分批获取）
    const allIds = new Set()
    const pageSize = store.pagination.pageSize
    const totalPages = Math.ceil(total / pageSize)

    // 分批获取所有页的ID（使用store的静默方法，避免更新状态和触发loading）
    for (let page = 1; page <= totalPages; page++) {
      try {
        const dataList = await store.fetchExamplesSilently({
          page: page,
          pageSize: pageSize,
          name: searchForm.value.name.trim() || undefined,
          status: searchForm.value.status || undefined
        })

        if (Array.isArray(dataList) && dataList.length > 0) {
          dataList.forEach((item) => {
            if (item && item.id !== undefined && item.id !== null) {
              allIds.add(item.id)
            }
          })
        }
      } catch (error) {
        console.error(`加载第${page}页失败:`, error)
        ElMessage.error(`加载第${page}页失败: ${error.message || '未知错误'}`)
      }
    }

    console.log('全选加载完成，共获取', allIds.size, '个ID:', Array.from(allIds).slice(0, 10))

    if (allIds.size === 0) {
      ElMessage.warning('没有找到可全选的数据')
      selectAllMode.value = false
      return
    }

    // 更新选中状态：创建新的Set确保响应式更新
    const newSelectedIds = new Set(allIds)
    selectedIds.value = newSelectedIds

    // 强制触发响应式更新
    await nextTick()

    // 重新加载当前页以更新表格的选择状态
    await store.fetchExamples({
      page: store.pagination.currentPage,
      name: searchForm.value.name.trim(),
      status: searchForm.value.status
    })

    // 等待DOM更新后再更新表格选中状态
    await nextTick()
    refreshTable()

    // 等待表格完全渲染（多等几次确保DOM完全更新）
    await nextTick()
    await new Promise((resolve) => setTimeout(resolve, 50)) // 额外等待50ms确保表格渲染完成
    await nextTick()

    // 更新表格选中状态
    await updateTableSelection()

    // 再次验证选中状态
    await nextTick()
    const currentPageSelected = tableData.value.filter((row) => selectedIds.value.has(row.id)).length
    console.log('全选完成 - 当前页应选中:', currentPageSelected, '条，实际数据:', tableData.value.length, 'selectedIds数量:', selectedIds.value.size)

    // 如果当前页应该选中的数量和实际不匹配，尝试再次更新
    if (currentPageSelected > 0) {
      const actualSelected = tableRef.value?.getSelectionRows?.()?.length || 0
      if (actualSelected !== currentPageSelected) {
        console.warn('选中数量不匹配，尝试重新设置...')
        await updateTableSelection()
      }
    }

    ElMessage.success(`已全选所有 ${allIds.size} 条数据`)
  } catch (error) {
    ElMessage.error('全选失败: ' + (error.message || '未知错误'))
    selectAllMode.value = false
  } finally {
    selectAllLoading.value = false
  }
}

// 批量删除
const handleBatchDelete = () => {
  if (selectedIds.value.size === 0) {
    ElMessage.warning('请先选择要删除的数据')
    return
  }

  const count = selectedIds.value.size
  ElMessageBox.confirm(`确定要删除选中的 ${count} 条示例吗？`, '批量删除确认', {
    confirmButtonText: '确定',
    cancelButtonText: '取消',
    type: 'warning'
  })
    .then(async () => {
      await batchDeleteExamples()
    })
    .catch(() => {
      ElMessage.info('已取消删除')
    })
}

// 执行批量删除
const batchDeleteExamples = async () => {
  if (selectedIds.value.size === 0) {
    return
  }

  try {
    batchDeleteLoading.value = true

    const ids = Array.from(selectedIds.value)
    const response = await exampleService.batchDeleteExamples(ids)

    if (response.data.success) {
      const result = response.data.data
      if (result.failed_count > 0) {
        ElMessage.warning(`成功删除 ${result.success_count} 条，失败 ${result.failed_count} 条`)
      } else {
        ElMessage.success(`成功删除 ${result.success_count} 条数据`)
      }

      // 清空选择
      selectedIds.value.clear()
      selectAllMode.value = false

      // 刷新列表
      await store.fetchExamples({
        page: store.pagination.currentPage,
        name: searchForm.value.name.trim(),
        status: searchForm.value.status
      })

      nextTick(() => {
        refreshTable()
      })
    } else {
      ElMessage.error(response.data.message || '批量删除失败')
    }
  } catch (error) {
    ElMessage.error('批量删除失败: ' + (error.response?.data?.message || error.message || '未知错误'))
  } finally {
    batchDeleteLoading.value = false
  }
}

// ==================== 分页处理 ====================
// 分页变化处理
const handlePageChange = async (newPage) => {
  try {
    await store.fetchExamples({
      page: newPage,
      name: searchForm.value.name.trim(),
      status: searchForm.value.status
    })
    nextTick(async () => {
      refreshTable()
      // 更新表格选中状态
      await updateTableSelection()
    })
  } catch (error) {
    if (store.error) {
      ElMessage.error(store.error)
    }
  }
}

// 分页大小变化处理
const handleSizeChange = async (newSize) => {
  try {
    await store.fetchExamples({
      page: 1,
      pageSize: newSize,
      name: searchForm.value.name.trim(),
      status: searchForm.value.status
    })
    nextTick(() => {
      refreshTable()
    })
  } catch (error) {
    if (store.error) {
      ElMessage.error(store.error)
    }
  }
}

// ==================== 对话框处理 ====================
// 对话框关闭处理
const handleDialogClose = (done) => {
  if (!dialogLoading.value) {
    done()
  }
}

// ==================== 监听器 ====================
// 监听表格数据变化，更新选中状态
watch(
  () => tableData.value,
  async () => {
    await updateTableSelection()
  },
  { deep: true }
)

// ==================== 生命周期 ====================
// 组件挂载时获取数据
onMounted(() => {
  store
    .fetchExamples()
    .then(() => {
      // 数据加载完成后刷新表格
      nextTick(async () => {
        refreshTable()
        await updateTableSelection()
      })
    })
    .catch((error) => {
      if (store.error) {
        ElMessage.error(store.error)
      }
    })
})
</script>

<style scoped>
/* 选择框宽度 */
:deep(.el-select) {
  width: 180px;
}

@media (max-width: 768px) {
  :deep(.el-select) {
    width: 100%;
  }
}
</style>

<template>
  <div class="database-info-view">
    <!-- 顶部：数据库连接选择 -->
    <div class="header-bar">
      <el-select v-model="selectedConnectionId" placeholder="请选择数据库连接" filterable @change="handleConnectionChange" style="width: 300px" clearable>
        <el-option v-for="conn in connectionOptions" :key="conn.value" :label="`${conn.label} (${conn.host})`" :value="conn.value" />
      </el-select>
      <el-button v-if="selectedConnectionId" @click="loadDatabases" :loading="store.loading">刷新</el-button>
      <el-button v-if="selectedConnectionId" type="primary" @click="handleExportDatabasesSql" :loading="exportDatabasesLoading">
        <el-icon><Download /></el-icon>
        导出SQL
      </el-button>
    </div>

    <!-- 主体：分为左右两部分 -->
    <div class="main-content" v-if="selectedConnectionId">
      <!-- 左侧：数据库树 -->
      <div class="left-panel">
        <div style="display: flex; gap: 8px; margin-bottom: 12px">
          <el-input v-model="tableKeyword" placeholder="搜索当前库的表名" size="small" clearable :disabled="!store.currentDatabase" @keyup.enter="searchTables" @clear="searchTables" />
          <el-button size="small" type="primary" :disabled="!store.currentDatabase" @click="searchTables">搜索</el-button>
        </div>
        <el-tree ref="treeRef" :data="treeData" :props="treeProps" default-expand-all highlight-current @node-click="handleNodeClick" node-key="id">
          <template #default="{ node, data }">
            <div class="tree-node">
              <el-icon v-if="data.type === 'database'"><Document /></el-icon>
              <el-icon v-else><Menu /></el-icon>
              <span class="node-label">{{ node.label }}</span>
            </div>
          </template>
        </el-tree>
      </div>

      <!-- 右侧：数据展示区 -->
      <div class="right-panel">
        <el-tabs v-model="activeTab" type="border-card">
          <!-- 数据表数据 -->
          <el-tab-pane label="表数据" name="data">
            <div v-if="store.currentTable">
              <div class="table-header">
                <span class="table-name">数据库: {{ store.currentDatabase }} / 表: {{ store.currentTable }}</span>
                <div style="display: flex; align-items: center; gap: 12px">
                  <span style="color: #606266; font-size: 12px">
                    共 {{ store.pagination.total }} 条
                    <span v-if="selectedRows.length > 0" style="color: #409eff; margin-left: 8px">(已选中 {{ selectedRows.length }} 条)</span>
                  </span>
                  <el-button size="small" type="primary" :disabled="selectedRows.length === 0" @click="handleExportSql">
                    <el-icon><Download /></el-icon>
                    导出SQL
                  </el-button>
                  <el-button size="small" @click="refreshTableData">刷新</el-button>
                </div>
              </div>

              <div class="table-container" v-loading="store.dataLoading">
                <el-table ref="tableRef" :data="tableDataArray" border stripe style="width: 100%" max-height="460" @selection-change="handleSelectionChange">
                  <el-table-column v-if="tableDataArray.length > 0" type="selection" width="55" />
                  <el-table-column v-for="column in tableColumns" :key="column" :prop="column" min-width="150" show-overflow-tooltip>
                    <template #header>
                      <div style="display: flex; align-items: center; gap: 8px; position: relative">
                        <span style="font-weight: 500; font-size: 14px; flex: 1">{{ column }}</span>
                        <el-icon
                          class="filter-icon"
                          :class="{ 'filter-active': columnMultiSelectFilters[column]?.length > 0 }"
                          @click.stop="() => handleFilterIconClick(column)"
                          style="cursor: pointer; color: #909399; font-size: 16px; transition: color 0.2s"
                          :style="{ color: columnMultiSelectFilters[column]?.length > 0 ? '#409eff' : '#909399' }"
                        >
                          <Filter />
                        </el-icon>
                        <!-- 筛选下拉面板 -->
                        <teleport to="body">
                          <div v-if="columnFilterVisible[column]" class="filter-panel" :style="getFilterPanelStyle(column)" @click.stop>
                            <div class="filter-panel-header" @mousedown.prevent>
                              <span class="filter-panel-title">筛选: {{ column }}</span>
                              <el-icon class="filter-close-icon" @click="() => handleCloseFilter(column)" style="cursor: pointer">
                                <Close />
                              </el-icon>
                            </div>
                            <div class="filter-panel-search">
                              <el-input
                                v-model="columnMultiSelectSearchKeywords[column]"
                                :placeholder="`搜索 ${column}`"
                                size="small"
                                clearable
                                @input="() => handleSearchInput(column)"
                                @clear="() => handleClearSearch(column)"
                              >
                                <template #prefix>
                                  <el-icon><Search /></el-icon>
                                </template>
                              </el-input>
                            </div>
                            <div class="filter-panel-actions" @mousedown.prevent>
                              <el-button text type="primary" size="small" @click="() => handleSelectAll(column)">全选</el-button>
                              <el-button text size="small" @click="() => handleClearAll(column)">清空</el-button>
                            </div>
                            <div class="filter-panel-content" @mousedown.prevent @scroll="(event) => handleFilterPanelScroll(event, column)" v-loading="columnUniqueValuesLoading[column]">
                              <el-checkbox-group v-model="columnMultiSelectFilters[column]" @change="(val) => handleMultiSelectFilterChange(val, column)">
                                <div v-for="option in getFilteredColumnUniqueValues(column)" :key="option" class="filter-option-item">
                                  <el-checkbox :label="option">
                                    <span class="filter-option-text">{{ option }}</span>
                                  </el-checkbox>
                                </div>
                              </el-checkbox-group>
                              <div v-if="!columnUniqueValuesLoading[column] && getFilteredColumnUniqueValues(column).length === 0" class="filter-empty">无匹配项</div>
                              <div v-if="hasMoreFilterData(column)" class="filter-loading-more">
                                <el-icon class="is-loading"><Loading /></el-icon>
                                <span>滚动加载更多...</span>
                              </div>
                            </div>
                            <div v-if="columnMultiSelectFilters[column]?.length > 0" class="filter-panel-footer" @mousedown.prevent>已选择 {{ columnMultiSelectFilters[column].length }} 项</div>
                          </div>
                        </teleport>
                      </div>
                    </template>
                    <template #default="{ row }">
                      {{ formatCell(column, row[column]) }}
                    </template>
                  </el-table-column>
                </el-table>
              </div>

              <div class="pagination" v-show="store.pagination.total >= 0">
                <el-pagination
                  v-model:current-page="currentPage"
                  v-model:page-size="pageSize"
                  :page-sizes="[20, 50, 100, 200]"
                  :total="store.pagination.total"
                  :background="true"
                  layout="total, sizes, prev, pager, next, jumper"
                  @update:current-page="handlePageChange"
                  @update:page-size="handleSizeChange"
                />
              </div>
            </div>
            <el-empty v-else description="请先选择数据库和数据表" />
          </el-tab-pane>

          <!-- SQL查询控制台 -->
          <el-tab-pane label="SQL控制台" name="console">
            <div class="console-container">
              <div class="console-toolbar">
                <el-button size="small" type="primary" @click="executeQuery" :loading="store.loading">执行查询</el-button>
                <el-button size="small" @click="clearConsole">清空</el-button>
              </div>
              <div class="editor-area">
                <el-input v-model="sqlQuery" type="textarea" :rows="8" placeholder="请输入SQL查询语句，例如：SELECT * FROM users LIMIT 10" />
              </div>

              <!-- 查询结果 -->
              <div v-if="queryResult && queryResult.data !== undefined" class="result-area">
                <el-divider>
                  <span>查询结果</span>
                  <span style="margin-left: 10px; color: #409eff; font-weight: normal">
                    (共 {{ queryResult.row_count !== undefined ? queryResult.row_count : Array.isArray(queryResult.data) ? queryResult.data.length : 0 }} 条)
                  </span>
                </el-divider>
                <el-table v-if="Array.isArray(queryResult.data) && queryResult.data.length > 0" :data="queryResult.data" border stripe style="width: 100%" max-height="400">
                  <el-table-column v-for="column in queryColumns" :key="column" :prop="column" :label="column" min-width="150" show-overflow-tooltip>
                    <template #default="{ row }">
                      {{ formatCell(column, row[column]) }}
                    </template>
                  </el-table-column>
                </el-table>
                <el-empty v-else description="查询结果为空" :image-size="100" />
              </div>
            </div>
          </el-tab-pane>
        </el-tabs>
      </div>
    </div>

    <!-- 未选择连接时的提示 -->
    <el-empty v-else description="请先选择数据库连接" />

    <!-- 导出SQL类型选择对话框 -->
    <el-dialog v-model="exportDialogVisible" title="选择SQL类型" width="400px">
      <div style="margin-bottom: 20px">
        <p style="color: #606266; margin-bottom: 12px">请选择要生成的SQL类型（可多选）：</p>
        <el-checkbox-group v-model="selectedSqlTypes">
          <el-checkbox label="INSERT">INSERT（插入语句）</el-checkbox>
          <el-checkbox label="UPDATE">UPDATE（更新语句）</el-checkbox>
          <el-checkbox label="DELETE">DELETE（删除语句）</el-checkbox>
          <el-checkbox label="SELECT">SELECT（查询语句）</el-checkbox>
        </el-checkbox-group>
      </div>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="exportDialogVisible = false">取消</el-button>
          <el-button type="primary" @click="confirmExportSql" :loading="exportLoading">导出</el-button>
        </span>
      </template>
    </el-dialog>

    <!-- 导出数据库SQL对话框 -->
    <el-dialog v-model="exportDatabasesDialogVisible" title="导出数据库SQL" width="600px">
      <div style="margin-bottom: 20px; max-height: 400px; overflow-y: auto; border: 1px solid #e4e7ed; padding: 12px; border-radius: 4px">
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px">
          <p style="color: #606266; margin: 0; font-weight: 500">请选择要导出的数据库和表：</p>
          <div style="display: flex; gap: 8px">
            <el-button size="small" text type="primary" @click="selectAllDatabasesTables" :loading="selectAllLoading">全选</el-button>
            <el-button size="small" text @click="clearAllDatabasesTables" :disabled="selectAllLoading">取消全选</el-button>
          </div>
        </div>
        <div v-for="db in databaseTablesForExport" :key="db.name" style="margin-bottom: 16px">
          <div style="display: flex; align-items: center; gap: 8px; margin-bottom: 8px">
            <el-checkbox :model-value="db.selected" @change="(val) => handleDatabaseSelectChange(db.name, val)" :indeterminate="db.indeterminate">
              <span style="font-weight: 500">{{ db.name }}</span>
            </el-checkbox>
            <el-button text size="small" @click="handleExpandDatabase(db)" style="margin-left: auto">
              {{ db.expanded ? '收起' : '展开' }}
            </el-button>
          </div>
          <div v-if="db.expanded" style="margin-left: 24px; padding-left: 16px; border-left: 2px solid #e4e7ed">
            <div v-if="db.loading" style="padding: 8px; color: #909399">
              <el-icon class="is-loading"><Loading /></el-icon>
              加载表列表中...
            </div>
            <div v-else-if="db.tables.length === 0" style="padding: 8px; color: #909399">该数据库暂无表</div>
            <div v-else style="display: flex; flex-direction: column; gap: 6px">
              <el-checkbox v-for="table in db.tables" :key="table" :model-value="db.selectedTables.includes(table)" @change="(val) => handleTableSelectChange(db.name, table, val)">
                {{ table }}
              </el-checkbox>
            </div>
          </div>
        </div>
      </div>
      <div style="margin-bottom: 20px">
        <p style="color: #606266; margin-bottom: 12px; font-weight: 500">请选择要生成的SQL类型（可多选）：</p>
        <el-checkbox-group v-model="selectedDatabasesSqlTypes">
          <el-checkbox label="CREATE">CREATE（表结构）</el-checkbox>
          <el-checkbox label="INSERT">INSERT（插入语句）</el-checkbox>
          <el-checkbox label="UPDATE">UPDATE（更新语句）</el-checkbox>
          <el-checkbox label="DELETE">DELETE（删除语句）</el-checkbox>
          <el-checkbox label="SELECT">SELECT（查询语句）</el-checkbox>
        </el-checkbox-group>
      </div>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="exportDatabasesDialogVisible = false">取消</el-button>
          <el-button type="primary" @click="confirmExportDatabasesSql" :loading="exportDatabasesLoading">导出</el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, computed, watch, onMounted, onUnmounted, nextTick } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Document, Menu, Download, Loading, Search, Filter, Close } from '@element-plus/icons-vue'
import { useDatabaseInfoStore } from '@/stores/database/databaseInfoStore'
import { useDatabaseConnStore } from '@/stores/database/databaseConnStore'
import { formatDateTime } from '@/utils/date'
import { databaseInfoService } from '@/services/database/databaseInfoService'

const databaseConnStore = useDatabaseConnStore()
const store = useDatabaseInfoStore()

// 表格引用
const tableRef = ref(null)

// 连接选择
const selectedConnectionId = ref(null)
const connectionOptions = ref([])

// 数据库树
const treeRef = ref(null)
const treeData = ref([])
const treeProps = {
  label: 'name',
  children: 'children'
}
const tableKeyword = ref('')
const lastDatabaseNode = ref(null)
const searchDebounceTimer = ref(null)

// 分页
const currentPage = ref(1)
const pageSize = ref(20)

// Tab
const activeTab = ref('data')

// SQL查询
const sqlQuery = ref('')
const queryResult = ref(null)
const queryColumns = ref([])
// 标记当前 SQL 对应的表名，用于判断是否需要更新
const currentSQLTableName = ref('')

// 选中的行数据
const selectedRows = ref([])

// 列多选筛选值
const columnMultiSelectFilters = ref({})
// 列多选筛选的搜索关键词
const columnMultiSelectSearchKeywords = ref({})
// 列筛选下拉框显示状态
const columnFilterVisible = ref({})
// 列筛选列表加载状态（每个列的已加载数量）
const columnFilterLoadedCount = ref({})
// 每次加载的数量
const FILTER_LOAD_STEP = 50
// 列的唯一值缓存（从后端获取的全部数据）
const columnUniqueValuesCache = ref({})
// 列的唯一值加载状态
const columnUniqueValuesLoading = ref({})

// 导出相关
const exportDialogVisible = ref(false)
const selectedSqlTypes = ref([])
const exportLoading = ref(false)

// 导出数据库相关
const exportDatabasesDialogVisible = ref(false)
const databaseTablesForExport = ref([]) // {name, selected, tables, selectedTables, expanded, loading, indeterminate}
const selectedDatabasesSqlTypes = ref([])
const exportDatabasesLoading = ref(false)
const selectAllLoading = ref(false)

// 计算属性
// 先获取原始数据和列名
const rawTableData = computed(() => {
  return store.tableData?.data || []
})

const tableColumns = computed(() => {
  if (!rawTableData.value || rawTableData.value.length === 0) return []
  const keys = Object.keys(rawTableData.value[0])
  // 将 id 放到最前面，created_at 和 updated_at 放到最后
  const sortedKeys = [...keys.filter((k) => k === 'id'), ...keys.filter((k) => !['id', 'created_at', 'updated_at'].includes(k)), ...keys.filter((k) => ['created_at', 'updated_at'].includes(k))]
  return sortedKeys
})

// 应用筛选后的数据（筛选已在后端完成，这里直接返回原始数据）
const tableDataArray = computed(() => {
  return rawTableData.value
})

// 方法
const loadConnectionOptions = async () => {
  try {
    await databaseConnStore.fetchConnectionsForSelect()
    connectionOptions.value = databaseConnStore.connectionOptions
    // 优先默认选中主机为 127.0.0.1 的连接；否则选中第一个
    if (!selectedConnectionId.value && connectionOptions.value.length > 0) {
      const localOption = connectionOptions.value.find((opt) => opt.host === '127.0.0.1')
      selectedConnectionId.value = (localOption || connectionOptions.value[0]).value
      await handleConnectionChange(selectedConnectionId.value)
    }
  } catch (error) {
    ElMessage.error('加载连接列表失败')
  }
}

const handleConnectionChange = async (connectionId) => {
  if (!connectionId) {
    store.reset()
    treeData.value = []
    return
  }

  const connection = databaseConnStore.connections.find((c) => c.id === connectionId)
  if (connection) {
    store.setCurrentConnection(connection)
    await loadDatabases()
  }
}

const loadDatabases = async () => {
  if (!selectedConnectionId.value) return

  try {
    await store.fetchDatabases()
    buildTreeData()
  } catch (error) {
    // 错误消息已由响应拦截器统一显示，这里不需要重复显示
    // 响应拦截器会优先显示后端返回的错误消息（如"获取数据库列表失败"）
  }
}

const buildTreeData = () => {
  const databases = store.databases.map((db) => ({
    id: `db_${db}`,
    name: db,
    type: 'database',
    database: db,
    children: []
  }))

  treeData.value = databases
}

const handleNodeClick = async (data) => {
  if (data.type === 'database') {
    // 点击数据库，加载表列表
    try {
      await store.fetchTables(data.database, tableKeyword.value)
      lastDatabaseNode.value = data
      loadTableNodes(data)
    } catch (error) {
      ElMessage.error(store.error || '加载表列表失败')
    }
  } else if (data.type === 'table') {
    // 点击表，加载表数据
    store.currentTable = data.table
    store.currentDatabase = data.database
    await loadTableData()

    // 如果在控制台 tab，更新 SQL 为当前表的默认 SQL
    if (activeTab.value === 'console' && data.table) {
      updateConsoleSQLForTable(data.table, data.database)
    }
  }
}

const loadTableNodes = (databaseNode) => {
  const tables = store.currentTables.map((table) => ({
    id: `table_${databaseNode.database}_${table}`,
    name: table,
    type: 'table',
    database: databaseNode.database,
    table: table
  }))

  databaseNode.children = tables
  treeRef.value?.updateKeyChildren(databaseNode.id, tables)
}

const searchTables = async () => {
  if (!store.currentDatabase) return
  try {
    await store.fetchTables(store.currentDatabase, tableKeyword.value)
    if (lastDatabaseNode.value) {
      loadTableNodes(lastDatabaseNode.value)
    }
  } catch (error) {
    ElMessage.error(store.error || '搜索表失败')
  }
}

// 实时搜索（防抖）
watch(
  () => tableKeyword.value,
  (val) => {
    if (!store.currentDatabase) return
    if (searchDebounceTimer.value) {
      clearTimeout(searchDebounceTimer.value)
    }
    searchDebounceTimer.value = setTimeout(() => {
      searchTables()
    }, 300)
  }
)

const loadTableData = async () => {
  if (!store.currentDatabase || !store.currentTable) return

  try {
    // 清空表格筛选状态
    if (tableRef.value) {
      tableRef.value.clearFilter()
    }

    // 构建筛选条件（只包含有值的筛选）
    const filters = {}
    Object.keys(columnMultiSelectFilters.value).forEach((column) => {
      const filterValues = columnMultiSelectFilters.value[column]
      if (filterValues && Array.isArray(filterValues) && filterValues.length > 0) {
        filters[column] = filterValues
      }
    })

    await store.fetchTableData(store.currentDatabase, store.currentTable, currentPage.value, pageSize.value, Object.keys(filters).length > 0 ? filters : null)
  } catch (error) {
    ElMessage.error(store.error || '加载表数据失败')
  }
}

const refreshTableData = () => {
  // 刷新数据时清空选择，但保留筛选条件
  selectedRows.value = []
  loadTableData()
}

const handlePageChange = (page) => {
  currentPage.value = page
  loadTableData()
}

const handleSizeChange = (size) => {
  pageSize.value = size
  currentPage.value = 1
  loadTableData()
}

// 取消滚动触底逻辑，使用分页器

// 过滤 SQL 注释：移除以 -- 开头的行和行内的 -- 注释
const filterSQLComments = (sql) => {
  if (!sql) return ''

  return sql
    .split('\n')
    .map((line) => {
      // 找到 -- 的位置
      const commentIndex = line.indexOf('--')
      if (commentIndex === -1) {
        return line
      }
      // 返回 -- 之前的部分
      return line.substring(0, commentIndex)
    })
    .filter((line) => line.trim() !== '') // 过滤空行
    .join('\n')
    .trim()
}

const executeQuery = async () => {
  if (!sqlQuery.value.trim()) {
    ElMessage.warning('请输入SQL查询语句')
    return
  }

  try {
    // 过滤掉注释后执行
    const filteredSQL = filterSQLComments(sqlQuery.value)

    if (!filteredSQL) {
      ElMessage.warning('请编写可执行的SQL语句，当前SQL均为注释')
      return
    }

    const result = await store.executeQuery(filteredSQL, store.currentDatabase)

    if (result.success && result.data !== undefined) {
      // result 的结构是 {success: True, data: [...], columns: [...], row_count: 10}
      // 其中 data 是数据数组，columns 是列名数组
      queryResult.value = result
      // 设置列信息
      if (result.columns && result.columns.length > 0) {
        queryColumns.value = result.columns
      } else if (Array.isArray(result.data) && result.data.length > 0) {
        // 如果没有 columns，从数据的第一行获取列名
        queryColumns.value = Object.keys(result.data[0])
      } else {
        queryColumns.value = []
      }
    } else {
      queryResult.value = null
      queryColumns.value = []
      ElMessage.success(result.message || '查询执行成功')
    }
  } catch (error) {
    queryResult.value = null
    queryColumns.value = []
    ElMessage.error(store.error || '执行查询失败')
  }
}

const clearConsole = () => {
  sqlQuery.value = ''
  queryResult.value = null
  queryColumns.value = []
  currentSQLTableName.value = ''
}

// 更新控制台 SQL 为指定表的默认 SQL
const updateConsoleSQLForTable = (tableName, databaseName) => {
  // 只在以下情况更新：
  // 1. SQL 为空
  // 2. 或者是默认模板 SQL（包含 "常用 SQL 查询语句模板" 标记）
  const isDefaultTemplate = sqlQuery.value.includes('常用 SQL 查询语句模板')

  if (!sqlQuery.value.trim() || isDefaultTemplate) {
    const defaultSQL = generateDefaultSQL(tableName, databaseName)
    sqlQuery.value = defaultSQL
    currentSQLTableName.value = tableName
  }
}

// 单元格格式化：针对时间/日期字段自动格式化（仅格式化当前数据表的 created_at 和 updated_at）
const formatCell = (key, value) => {
  try {
    // 只格式化 created_at 和 updated_at 字段（数据库连接管理的表）
    if (key === 'created_at' || key === 'updated_at' || key === 'create_time') {
      if (value == null || value === '') return ''
      return formatDateTime(value)
    }
    return value
  } catch (e) {
    return value
  }
}

// 获取列的所有唯一值（从后端获取全部数据）
const getAllColumnUniqueValues = async (column) => {
  // 如果缓存中有数据，直接返回
  if (columnUniqueValuesCache.value[column]) {
    return columnUniqueValuesCache.value[column]
  }

  // 如果正在加载，返回空数组
  if (columnUniqueValuesLoading.value[column]) {
    return []
  }

  // 如果没有当前连接、数据库或表，返回空数组
  if (!selectedConnectionId.value || !store.currentDatabase || !store.currentTable) {
    return []
  }

  // 从后端获取该列的所有唯一值
  try {
    columnUniqueValuesLoading.value[column] = true
    const response = await databaseInfoService.getColumnUniqueValues(
      selectedConnectionId.value,
      store.currentDatabase,
      store.currentTable,
      column,
      1000 // 限制最多1000个唯一值
    )

    const values = response.data.data || []
    columnUniqueValuesCache.value[column] = values
    return values
  } catch (error) {
    console.error('获取列唯一值失败:', error)
    ElMessage.error(`获取列 ${column} 的唯一值失败`)
    return []
  } finally {
    columnUniqueValuesLoading.value[column] = false
  }
}

// 获取筛选后的列唯一值（根据搜索关键词过滤，支持滚动加载）
const getFilteredColumnUniqueValues = (column) => {
  // 从缓存中获取所有唯一值
  const allValues = columnUniqueValuesCache.value[column] || []
  const searchKeyword = columnMultiSelectSearchKeywords.value[column] || ''

  // 先根据搜索关键词过滤
  let filteredValues = allValues
  if (searchKeyword) {
    const keyword = searchKeyword.toLowerCase()
    filteredValues = allValues.filter((value) => String(value).toLowerCase().includes(keyword))
  }

  // 获取当前已加载的数量，如果没有则初始化为加载步长
  const loadedCount = columnFilterLoadedCount.value[column] || FILTER_LOAD_STEP

  // 返回已加载的部分
  return filteredValues.slice(0, loadedCount)
}

// 检查是否还有更多数据可加载
const hasMoreFilterData = (column) => {
  const allValues = columnUniqueValuesCache.value[column] || []
  const searchKeyword = columnMultiSelectSearchKeywords.value[column] || ''

  let filteredValues = allValues
  if (searchKeyword) {
    const keyword = searchKeyword.toLowerCase()
    filteredValues = allValues.filter((value) => String(value).toLowerCase().includes(keyword))
  }

  const loadedCount = columnFilterLoadedCount.value[column] || FILTER_LOAD_STEP
  return filteredValues.length > loadedCount
}

// 加载更多筛选数据
const loadMoreFilterData = (column) => {
  const currentCount = columnFilterLoadedCount.value[column] || FILTER_LOAD_STEP
  columnFilterLoadedCount.value[column] = currentCount + FILTER_LOAD_STEP
}

// 处理筛选面板滚动
const handleFilterPanelScroll = (event, column) => {
  const target = event.target
  const scrollTop = target.scrollTop
  const scrollHeight = target.scrollHeight
  const clientHeight = target.clientHeight

  // 当滚动到底部附近（距离底部20px）时加载更多
  if (scrollHeight - scrollTop - clientHeight < 20) {
    if (hasMoreFilterData(column)) {
      loadMoreFilterData(column)
    }
  }
}

// 重置列的加载数量（当搜索关键词变化时）
const resetFilterLoadedCount = (column) => {
  columnFilterLoadedCount.value[column] = FILTER_LOAD_STEP
}

// 清空搜索
const handleClearSearch = (column) => {
  columnMultiSelectSearchKeywords.value[column] = ''
  // 清空搜索时，重置加载数量
  resetFilterLoadedCount(column)
  // 清空搜索时，可以选择是否也清空已选择的值
  // columnMultiSelectFilters.value[column] = []
}

// 多选筛选变化处理
const handleMultiSelectFilterChange = (value, column) => {
  columnMultiSelectFilters.value[column] = value || []
  // 筛选条件变化时，重新加载数据（从后端获取筛选后的数据）
  // 重置到第一页
  currentPage.value = 1
  loadTableData()
  // 保持下拉框显示以便继续选择
  columnFilterVisible.value[column] = true
}

// 输入框输入时保持下拉框显示
const handleSearchInput = (column) => {
  // 搜索时保持下拉框显示
  if (!columnFilterVisible.value[column]) {
    columnFilterVisible.value[column] = true
  }
  // 搜索关键词变化时，重置加载数量
  resetFilterLoadedCount(column)
}

// 筛选面板位置信息
const filterPanelPositions = ref({})

// 获取筛选面板样式
const getFilterPanelStyle = (column) => {
  const position = filterPanelPositions.value[column]
  if (!position) {
    return {}
  }
  // 根据视口高度动态调整面板最大高度
  const viewportHeight = window.innerHeight
  const maxHeight = Math.min(300, viewportHeight * 0.5) // 最大高度为视口高度的50%，但不超过300px

  return {
    position: 'fixed',
    top: `${position.top}px`,
    left: `${position.left}px`,
    width: '320px',
    maxHeight: `${maxHeight}px`
  }
}

// 点击筛选图标
const handleFilterIconClick = async (column) => {
  // 切换下拉框显示状态
  const isVisible = columnFilterVisible.value[column]

  // 先关闭所有其他列的下拉框
  Object.keys(columnFilterVisible.value).forEach((key) => {
    if (key !== column) {
      columnFilterVisible.value[key] = false
    }
  })

  // 如果即将打开面板，初始化加载数量并计算位置
  if (!isVisible) {
    // 初始化该列的加载数量
    if (!columnFilterLoadedCount.value[column]) {
      columnFilterLoadedCount.value[column] = FILTER_LOAD_STEP
    }

    // 如果缓存中没有该列的唯一值，从后端加载
    if (!columnUniqueValuesCache.value[column] && !columnUniqueValuesLoading.value[column]) {
      await getAllColumnUniqueValues(column)
    }

    await nextTick()
    // 查找对应的表头元素
    const headerCells = document.querySelectorAll('.el-table__header-wrapper th')
    let targetCell = null
    headerCells.forEach((cell) => {
      const columnNameSpan = cell.querySelector('span[style*="font-weight"]')
      if (columnNameSpan) {
        const columnName = columnNameSpan.textContent?.trim()
        if (columnName === column) {
          targetCell = cell
        }
      }
    })

    if (targetCell) {
      const rect = targetCell.getBoundingClientRect()
      const panelWidth = 320
      const viewportWidth = window.innerWidth
      const viewportHeight = window.innerHeight
      let left = rect.right - panelWidth

      // 确保面板不会超出视口左侧
      if (left < 0) {
        left = rect.left
      }

      // 确保面板不会超出视口右侧
      if (left + panelWidth > viewportWidth) {
        left = viewportWidth - panelWidth - 10
      }

      // 计算面板高度，确保不会超出视口底部
      const maxPanelHeight = Math.min(300, viewportHeight * 0.5)
      let top = rect.bottom + 4
      // 如果面板会超出视口底部，则向上调整
      if (top + maxPanelHeight > viewportHeight) {
        top = Math.max(10, viewportHeight - maxPanelHeight - 10)
      }

      filterPanelPositions.value[column] = {
        top: top,
        left: Math.max(10, left)
      }
    }
  }

  // 切换当前列的下拉框
  columnFilterVisible.value[column] = !isVisible
}

// 关闭筛选面板
const handleCloseFilter = (column) => {
  columnFilterVisible.value[column] = false
}

// 全选当前列的所有值（根据搜索关键词）
const handleSelectAll = (column) => {
  const filteredValues = getFilteredColumnUniqueValues(column)
  const currentSelected = columnMultiSelectFilters.value[column] || []
  // 合并当前已选中的值和筛选后的值（去重）
  const merged = new Set([...currentSelected, ...filteredValues])
  columnMultiSelectFilters.value[column] = Array.from(merged)
}

// 清空当前列的所有选择
const handleClearAll = (column) => {
  columnMultiSelectFilters.value[column] = []
}

// 监听当前表变化，切换到数据tab
watch(
  () => store.currentTable,
  (newTable) => {
    if (newTable && activeTab.value !== 'data') {
      activeTab.value = 'data'
    }
  }
)

// 监听 tab 切换，当切换到控制台时填充默认 SQL
watch(
  () => activeTab.value,
  (newTab, oldTab) => {
    if (newTab === 'console' && store.currentTable && store.currentDatabase) {
      // 调用更新函数，会智能判断是否需要更新
      updateConsoleSQLForTable(store.currentTable, store.currentDatabase)
    }
  }
)

// 生成默认的常用 SQL 语句
const generateDefaultSQL = (tableName, databaseName) => {
  return `-- 常用 SQL 查询语句模板（可复制取消注释后使用）提示：执行时系统会自动过滤 -- 注释，请确保至少有一行可执行的 SQL 语句

-- 1. 查询表的前10条数据
-- SELECT * FROM ${tableName} ORDER BY id DESC LIMIT 10;

-- 2. 查询表的记录总数
-- SELECT COUNT(*) as total FROM ${tableName};

-- 3. 查看表结构
-- DESCRIBE ${tableName};
-- 或者使用: SHOW COLUMNS FROM ${tableName};

-- 4. 带条件查询
-- SELECT * FROM ${tableName} WHERE id in (1,2,3);

-- 5. 查看表的创建语句
-- SHOW CREATE TABLE ${tableName};`
}

// 处理表格选择变化
const handleSelectionChange = (selection) => {
  selectedRows.value = selection
}

// 导出SQL文件 - 打开对话框
const handleExportSql = () => {
  if (selectedRows.value.length === 0) {
    ElMessage.warning('请先选择要导出的数据')
    return
  }
  exportDialogVisible.value = true
}

// 确认导出SQL
const confirmExportSql = async () => {
  if (selectedSqlTypes.value.length === 0) {
    ElMessage.warning('请至少选择一种SQL类型')
    return
  }

  try {
    exportLoading.value = true

    const response = await databaseInfoService.exportDataToSql(selectedConnectionId.value, {
      database_name: store.currentDatabase,
      table_name: store.currentTable,
      selected_data: selectedRows.value,
      sql_types: selectedSqlTypes.value
    })

    // 创建下载链接
    const blob = new Blob([response.data], { type: 'application/sql;charset=utf-8' })
    const url = window.URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url

    // 从响应头获取文件名，如果没有则生成默认文件名
    const contentDisposition = response.headers['content-disposition']
    let filename = `${store.currentDatabase}_${store.currentTable}_${formatDateTime(new Date())}.sql`
    if (contentDisposition) {
      const filenameMatch = contentDisposition.match(/filename[^;=\n]*=((['"]).*?\2|[^;\n]*)/)
      if (filenameMatch && filenameMatch[1]) {
        filename = filenameMatch[1].replace(/['"]/g, '')
        // 处理URL编码的文件名
        try {
          filename = decodeURIComponent(filename)
        } catch (e) {
          // 如果解码失败，使用原始文件名
        }
      }
    }

    link.download = filename
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
    window.URL.revokeObjectURL(url)

    ElMessage.success(`成功导出 ${selectedRows.value.length} 条数据的SQL文件`)
    exportDialogVisible.value = false
  } catch (error) {
    console.error('导出失败:', error)
    // 如果是blob响应但解析失败，尝试读取错误信息
    if (error.response?.data instanceof Blob) {
      const reader = new FileReader()
      reader.onload = () => {
        try {
          const text = reader.result
          const errorData = JSON.parse(text)
          ElMessage.error('导出失败: ' + (errorData.message || '未知错误'))
        } catch (e) {
          ElMessage.error('导出失败，请检查网络连接')
        }
      }
      reader.readAsText(error.response.data)
    } else {
      ElMessage.error('导出失败: ' + (error.response?.data?.message || error.message || '未知错误'))
    }
  } finally {
    exportLoading.value = false
  }
}

// 导出数据库SQL - 打开对话框
const handleExportDatabasesSql = async () => {
  if (!store.databases || store.databases.length === 0) {
    ElMessage.warning('请先加载数据库列表')
    return
  }

  // 初始化数据库和表的数据结构
  databaseTablesForExport.value = store.databases.map((db) => ({
    name: db,
    selected: false,
    tables: [],
    selectedTables: [],
    expanded: false,
    loading: false,
    indeterminate: false
  }))

  exportDatabasesDialogVisible.value = true
}

// 计算数据库的选中状态
const updateDatabaseState = (db) => {
  if (db.tables.length === 0) {
    db.selected = false
    db.indeterminate = false
    return
  }

  const selectedCount = db.selectedTables.length
  if (selectedCount === 0) {
    db.selected = false
    db.indeterminate = false
  } else if (selectedCount === db.tables.length) {
    db.selected = true
    db.indeterminate = false
  } else {
    db.selected = false
    db.indeterminate = true
  }
}

// 数据库选择变化
const handleDatabaseSelectChange = async (dbName, selected) => {
  const db = databaseTablesForExport.value.find((d) => d.name === dbName)
  if (!db) return

  // 如果表列表未加载，先加载
  if (db.tables.length === 0 && !db.loading) {
    await loadDatabaseTables(db)
  }

  if (selected) {
    // 全选所有表
    db.selectedTables = [...db.tables]
  } else {
    // 取消选择所有表
    db.selectedTables = []
  }
  updateDatabaseState(db)
}

// 表选择变化
const handleTableSelectChange = (dbName, tableName, selected) => {
  const db = databaseTablesForExport.value.find((d) => d.name === dbName)
  if (!db) return

  if (selected) {
    if (!db.selectedTables.includes(tableName)) {
      db.selectedTables.push(tableName)
    }
  } else {
    const index = db.selectedTables.indexOf(tableName)
    if (index > -1) {
      db.selectedTables.splice(index, 1)
    }
  }
  updateDatabaseState(db)
}

// 加载数据库的表列表
const loadDatabaseTables = async (db) => {
  if (db.loading) return

  db.loading = true
  try {
    const response = await databaseInfoService.getTables(
      selectedConnectionId.value,
      db.name,
      null // 不设置关键字，获取所有表
    )
    db.tables = response.data.data || []
    // 如果有表，默认全部选中
    if (db.tables.length > 0 && db.selectedTables.length === 0) {
      db.selectedTables = [...db.tables]
      updateDatabaseState(db)
    }
  } catch (error) {
    ElMessage.error(`加载数据库 ${db.name} 的表列表失败`)
    db.tables = []
  } finally {
    db.loading = false
  }
}

// 展开/收起数据库
const handleExpandDatabase = (db) => {
  db.expanded = !db.expanded
  // 展开时自动加载表列表
  if (db.expanded && db.tables.length === 0 && !db.loading) {
    loadDatabaseTables(db)
  }
}

// 全选所有数据库的所有表
const selectAllDatabasesTables = async () => {
  try {
    selectAllLoading.value = true

    // 先加载所有数据库的表列表（如果还没加载）
    const loadPromises = databaseTablesForExport.value.map(async (db) => {
      if (db.tables.length === 0 && !db.loading) {
        await loadDatabaseTables(db)
      }
    })
    await Promise.all(loadPromises)

    // 全选所有表
    databaseTablesForExport.value.forEach((db) => {
      if (db.tables.length > 0) {
        db.selectedTables = [...db.tables]
        updateDatabaseState(db)
      }
    })

    const totalDbs = databaseTablesForExport.value.filter((db) => db.tables.length > 0).length
    const totalTables = databaseTablesForExport.value.reduce((sum, db) => sum + db.tables.length, 0)
    ElMessage.success(`已全选 ${totalDbs} 个数据库，共 ${totalTables} 个表`)
  } catch (error) {
    ElMessage.error('全选失败: ' + (error.message || '未知错误'))
  } finally {
    selectAllLoading.value = false
  }
}

// 取消全选所有数据库的所有表
const clearAllDatabasesTables = () => {
  databaseTablesForExport.value.forEach((db) => {
    db.selectedTables = []
    updateDatabaseState(db)
  })
  ElMessage.success('已取消全选')
}

// 确认导出数据库SQL
const confirmExportDatabasesSql = async () => {
  // 构建数据库和表的映射关系
  const databaseTables = {}
  let hasSelection = false

  databaseTablesForExport.value.forEach((db) => {
    if (db.selectedTables.length > 0) {
      databaseTables[db.name] = db.selectedTables
      hasSelection = true
    }
  })

  if (!hasSelection) {
    ElMessage.warning('请至少选择一个数据库下的表')
    return
  }

  if (selectedDatabasesSqlTypes.value.length === 0) {
    ElMessage.warning('请至少选择一种SQL类型')
    return
  }

  try {
    exportDatabasesLoading.value = true

    const response = await databaseInfoService.exportDatabasesToSql(selectedConnectionId.value, {
      database_tables: databaseTables,
      sql_types: selectedDatabasesSqlTypes.value
    })

    // 创建下载链接
    const blob = new Blob([response.data], { type: 'application/sql;charset=utf-8' })
    const url = window.URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url

    // 从响应头获取文件名，如果没有则生成默认文件名
    const contentDisposition = response.headers['content-disposition']
    let filename = `databases_${formatDateTime(new Date())}.sql`
    if (contentDisposition) {
      const filenameMatch = contentDisposition.match(/filename[^;=\n]*=((['"]).*?\2|[^;\n]*)/)
      if (filenameMatch && filenameMatch[1]) {
        filename = filenameMatch[1].replace(/['"]/g, '')
        // 处理URL编码的文件名
        try {
          filename = decodeURIComponent(filename)
        } catch (e) {
          // 如果解码失败，使用原始文件名
        }
      }
    }

    link.download = filename
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
    window.URL.revokeObjectURL(url)

    const dbCount = Object.keys(databaseTables).length
    const totalTables = Object.values(databaseTables).reduce((sum, tables) => sum + tables.length, 0)
    ElMessage.success(`成功导出 ${dbCount} 个数据库，共 ${totalTables} 个表的SQL文件`)
    exportDatabasesDialogVisible.value = false
  } catch (error) {
    console.error('导出失败:', error)
    // 如果是blob响应但解析失败，尝试读取错误信息
    if (error.response?.data instanceof Blob) {
      const reader = new FileReader()
      reader.onload = () => {
        try {
          const text = reader.result
          const errorData = JSON.parse(text)
          ElMessage.error('导出失败: ' + (errorData.message || '未知错误'))
        } catch (e) {
          ElMessage.error('导出失败，请检查网络连接')
        }
      }
      reader.readAsText(error.response.data)
    } else {
      ElMessage.error('导出失败: ' + (error.response?.data?.message || error.message || '未知错误'))
    }
  } finally {
    exportDatabasesLoading.value = false
  }
}

// 点击外部关闭筛选面板
const handleClickOutside = (event) => {
  // 检查点击是否在筛选面板外部
  const filterPanels = document.querySelectorAll('.filter-panel')
  const filterIcons = document.querySelectorAll('.filter-icon')

  let isClickInsidePanel = false
  let isClickOnIcon = false

  filterPanels.forEach((panel) => {
    if (panel.contains(event.target)) {
      isClickInsidePanel = true
    }
  })

  filterIcons.forEach((icon) => {
    if (icon.contains(event.target)) {
      isClickOnIcon = true
    }
  })

  // 如果点击在面板外部且不是点击图标，则关闭所有面板
  if (!isClickInsidePanel && !isClickOnIcon) {
    Object.keys(columnFilterVisible.value).forEach((key) => {
      columnFilterVisible.value[key] = false
    })
  }
}

// 生命周期
onMounted(() => {
  // 添加全局点击事件监听
  document.addEventListener('click', handleClickOutside)
})

onUnmounted(() => {
  // 移除全局点击事件监听
  document.removeEventListener('click', handleClickOutside)
  // 页面卸载时关闭连接
  store.closeConnection()
})

// 初始化
loadConnectionOptions()
</script>

<style scoped>
.database-info-view {
  height: 100vh;
  display: flex;
  flex-direction: column;
  background: #f5f7fa;
}

.header-bar {
  padding: 16px 20px;
  background: white;
  border-bottom: 1px solid #ebeef5;
  display: flex;
  gap: 12px;
  align-items: center;
}

.main-content {
  flex: 1;
  display: flex;
  overflow: hidden;
}

.left-panel {
  width: 250px;
  background: white;
  border-right: 1px solid #ebeef5;
  overflow-y: auto;
  padding: 16px;
}

.tree-node {
  display: flex;
  align-items: center;
  gap: 8px;
}

.node-label {
  font-size: 14px;
}

.right-panel {
  flex: 1;
  background: white;
  overflow: hidden;
  display: flex;
  flex-direction: column;
}

.right-panel :deep(.el-tabs__content) {
  flex: 1;
  overflow: hidden;
  display: flex;
  flex-direction: column;
  min-height: 0; /* 允许在小屏幕下正常收缩 */
}

.right-panel :deep(.el-tab-pane) {
  height: 100%;
  overflow: hidden;
  display: flex;
  flex-direction: column;
  min-height: 0; /* 允许内部子容器正确分配空间 */
}

.table-header {
  padding: 16px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  border-bottom: 1px solid #ebeef5;
  flex-shrink: 0; /* 防止在小屏幕下被压缩隐藏 */
}

.table-name {
  font-size: 14px;
  font-weight: 500;
  color: #303133;
}

.table-container {
  padding: 16px;
  flex: 1 1 auto;
  overflow: auto;
  min-height: 0; /* 允许在小屏幕下收缩并启用内部滚动 */
}

.pagination {
  padding: 16px;
  display: flex;
  justify-content: flex-end;
  border-top: 1px solid #ebeef5;
  flex-shrink: 0; /* 保证分页器始终可见 */
  position: sticky; /* 小屏下依旧固定在底部可见 */
  bottom: 0;
  background: white;
  z-index: 1;
}

.console-container {
  height: 100%;
  display: flex;
  flex-direction: column;
  padding: 16px;
}

.console-toolbar {
  margin-bottom: 16px;
}

.editor-area {
  margin-bottom: 16px;
}

.result-area {
  flex: 1;
  overflow: auto;
}

/* 筛选图标样式 */
.filter-icon {
  cursor: pointer;
  transition: color 0.2s, transform 0.2s;
}

.filter-icon:hover {
  color: #409eff !important;
  transform: scale(1.1);
}

.filter-icon.filter-active {
  color: #409eff !important;
}

/* 筛选面板样式 */
.filter-panel {
  background: #fff;
  border: 1px solid #dcdfe6;
  border-radius: 4px;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
  z-index: 2000;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.filter-panel-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 8px 12px;
  border-bottom: 1px solid #e4e7ed;
  background: #f5f7fa;
  flex-shrink: 0;
}

.filter-panel-title {
  font-size: 13px;
  font-weight: 500;
  color: #303133;
}

.filter-close-icon {
  color: #909399;
  font-size: 16px;
  transition: color 0.2s;
}

.filter-close-icon:hover {
  color: #303133;
}

.filter-panel-search {
  padding: 8px 12px;
  border-bottom: 1px solid #e4e7ed;
  flex-shrink: 0;
}

.filter-panel-actions {
  display: flex;
  justify-content: flex-end;
  gap: 8px;
  padding: 6px 12px;
  border-bottom: 1px solid #e4e7ed;
  background: #fafafa;
  flex-shrink: 0;
}

.filter-panel-content {
  flex: 1;
  overflow-y: auto;
  padding: 4px 0;
  min-height: 0;
  /* 移除固定 max-height，由父容器控制 */
}

.filter-option-item {
  padding: 4px 12px;
  transition: background-color 0.2s;
}

.filter-option-item:hover {
  background-color: #f5f7fa;
}

.filter-option-text {
  font-size: 13px;
  color: #606266;
  word-break: break-all;
}

.filter-empty {
  padding: 16px;
  text-align: center;
  color: #909399;
  font-size: 12px;
}

.filter-loading-more {
  padding: 8px;
  text-align: center;
  color: #909399;
  font-size: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 6px;
  border-top: 1px solid #e4e7ed;
  background: #fafafa;
  flex-shrink: 0;
}

.filter-panel-footer {
  padding: 6px 12px;
  border-top: 1px solid #e4e7ed;
  background: #f5f7fa;
  font-size: 12px;
  color: #409eff;
  text-align: center;
  font-weight: 500;
  flex-shrink: 0;
}
</style>

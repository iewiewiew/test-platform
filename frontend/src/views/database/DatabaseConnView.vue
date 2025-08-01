<template>
  <div class="common-list-container">
    <!-- 顶部工具栏 -->
    <div class="common-header-bar">
      <div class="common-search-bar">
        <el-form :inline="true" :model="searchForm" class="demo-form-inline">
          <el-form-item label="名称">
            <el-input v-model="searchForm.name" placeholder="请输入名称" clearable @input="handleInputSearch" />
          </el-form-item>
          <el-form-item label="主机">
            <el-input v-model="searchForm.host" placeholder="请输入主机地址" clearable @input="handleInputSearch" />
          </el-form-item>
          <el-form-item label="数据库">
            <el-input v-model="searchForm.database" placeholder="请输入数据库名" clearable @input="handleInputSearch" />
          </el-form-item>
          <el-form-item>
            <el-button @click="resetSearch">重置</el-button>
          </el-form-item>
        </el-form>
      </div>

      <div class="common-action-bar">
        <el-button type="primary" @click="showEditDialog()">创建</el-button>
      </div>
    </div>

    <!-- 列表 -->
    <el-table :data="store.connections" v-loading="store.loading" style="width: 100%" empty-text="暂无数据" :row-class-name="getRowClassName">
      <el-table-column prop="id" label="ID" min-width="60" />
      <el-table-column prop="name" label="名称" min-width="160" show-overflow-tooltip>
        <template #default="scope">
          <el-popover placement="right" :width="320" trigger="hover" :show-after="300" popper-class="db-conn-info-popover">
            <template #reference>
              <span class="conn-name-cell">{{ scope.row.name }}</span>
            </template>
            <div class="db-conn-info-popover-content">
              <div class="db-conn-info-item">
                <span class="info-label">名称：</span>
                <span class="info-value">{{ scope.row.name }}</span>
              </div>
              <div class="db-conn-info-item">
                <span class="info-label">主机：</span>
                <span class="info-value">{{ scope.row.host }}</span>
              </div>
              <div class="db-conn-info-item">
                <span class="info-label">端口：</span>
                <span class="info-value">{{ scope.row.port || (scope.row.driver === 'redis' ? 6379 : 3306) }}</span>
              </div>
              <div class="db-conn-info-item" v-if="scope.row.driver !== 'redis' || scope.row.database">
                <span class="info-label">{{ scope.row.driver === 'redis' ? '数据库编号：' : '数据库：' }}</span>
                <span class="info-value">{{ scope.row.database || (scope.row.driver === 'redis' ? '0' : '-') }}</span>
              </div>
              <div class="db-conn-info-item" v-if="scope.row.driver !== 'redis' && scope.row.username">
                <span class="info-label">用户名：</span>
                <span class="info-value">{{ scope.row.username }}</span>
              </div>
              <div class="db-conn-info-item" v-if="scope.row.password">
                <span class="info-label">密码：</span>
                <span class="info-value">{{ scope.row.password }}</span>
              </div>
              <div class="db-conn-info-item">
                <span class="info-label">连接命令：</span>
                <span class="info-value">{{ getConnectionCommand(scope.row) }}</span>
              </div>
              <el-button size="small" type="primary" :icon="DocumentCopy" @click="copyAllConnInfo(scope.row)" class="copy-all-btn">复制全部信息</el-button>
            </div>
          </el-popover>
        </template>
      </el-table-column>
      <el-table-column prop="host" label="主机" min-width="140" show-overflow-tooltip />
      <el-table-column prop="port" label="端口" width="90" />
      <el-table-column prop="database" label="数据库" min-width="140" show-overflow-tooltip />
      <el-table-column prop="username" label="用户名" min-width="120" />
      <el-table-column prop="driver" label="驱动" width="100" />
      <el-table-column prop="creator_name" label="创建人" width="120" />
      <el-table-column prop="updater_name" label="更新人" width="120" />
      <el-table-column prop="created_at" label="创建时间" width="170" :formatter="formatDate" />
      <el-table-column prop="updated_at" label="更新时间" width="170" :formatter="formatDate" />
      <el-table-column label="操作" width="240" fixed="right">
        <template #default="scope">
          <el-button size="small" @click="showEditDialog(scope.row)">编辑</el-button>
          <el-button size="small" type="warning" @click="handleTest(scope.row.id)">测试连接</el-button>
          <el-button size="small" type="danger" @click="handleDelete(scope.row.id)">删除</el-button>
        </template>
      </el-table-column>
    </el-table>

    <!-- 分页 -->
    <div class="pagination">
      <el-pagination
        v-model:current-page="currentPage"
        v-model:page-size="pageSize"
        :page-sizes="[10, 20, 50, 100]"
        :total="store.pagination.total"
        :background="true"
        layout="total, sizes, prev, pager, next, jumper"
        @update:current-page="handlePageChange"
        @update:page-size="handleSizeChange"
      />
    </div>

    <!-- 创建/编辑对话框 -->
    <el-dialog v-model="dialog.visible" :title="dialog.isEdit ? '编辑' : '创建'" width="600px">
      <el-form ref="formRef" :model="dialog.form" :rules="rules" label-width="110px">
        <el-form-item label="名称" prop="name">
          <el-input v-model="dialog.form.name" placeholder="请输入连接名称" />
        </el-form-item>
        <el-form-item label="驱动" prop="driver">
          <el-select v-model="dialog.form.driver" style="width: 200px" @change="handleDriverChange">
            <el-option label="MySQL" value="mysql" />
            <el-option label="Redis" value="redis" />
          </el-select>
        </el-form-item>
        <el-form-item label="主机" prop="host">
          <el-input v-model="dialog.form.host" placeholder="例如：127.0.0.1" />
        </el-form-item>
        <el-form-item label="端口" prop="port">
          <el-input-number v-model="dialog.form.port" :min="1" :max="65535" />
        </el-form-item>
        <el-form-item v-if="dialog.form.driver !== 'redis'" label="数据库" prop="database">
          <el-input v-model="dialog.form.database" placeholder="请输入数据库名" />
        </el-form-item>
        <el-form-item v-if="dialog.form.driver === 'redis'" label="数据库编号">
          <el-input-number v-model="dialog.form.database" :min="0" :max="15" placeholder="0-15，默认0" style="width: 100%" />
        </el-form-item>
        <el-form-item v-if="dialog.form.driver !== 'redis'" label="用户名" prop="username">
          <el-input v-model="dialog.form.username" placeholder="请输入用户名" />
        </el-form-item>
        <el-form-item label="密码" :prop="dialog.form.driver === 'redis' ? '' : 'password'">
          <el-input v-model="dialog.form.password" type="password" placeholder="请输入密码（Redis可选）" show-password />
        </el-form-item>
        <el-form-item v-if="dialog.form.driver !== 'redis'" label="字符集" prop="charset">
          <el-input v-model="dialog.form.charset" placeholder="utf8mb4" />
        </el-form-item>
        <el-form-item label="描述">
          <el-input v-model="dialog.form.description" type="textarea" :rows="3" placeholder="备注" />
        </el-form-item>
      </el-form>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="dialog.visible = false">取消</el-button>
          <el-button @click="handleTestTemp" :loading="testLoading">测试连接</el-button>
          <el-button type="primary" @click="handleSubmit">确定</el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { DocumentCopy } from '@element-plus/icons-vue'
import { useDatabaseConnStore } from '@/stores/database/databaseConnStore'
import { formatDateTime } from '@/utils/date'

const store = useDatabaseConnStore()

// 搜索与分页
const searchForm = ref({ name: '', host: '', database: '' })
const currentPage = ref(1)
const pageSize = ref(10)
let searchTimer = null

// 对话框
const dialog = reactive({
  visible: false,
  isEdit: false,
  form: {
    name: '',
    driver: 'mysql',
    host: '',
    port: 3306,
    database: '',
    username: '',
    password: '',
    charset: 'utf8mb4',
    description: ''
  }
})
const formRef = ref()
const testLoading = ref(false)

// 动态验证规则
const getRules = () => {
  const baseRules = {
    name: [{ required: true, message: '请输入名称', trigger: 'blur' }],
    host: [{ required: true, message: '请输入主机', trigger: 'blur' }],
    port: [{ required: true, message: '请输入端口', trigger: 'change' }]
  }

  if (dialog.form.driver === 'redis') {
    // Redis 不需要 database、username、password（可选）
    return baseRules
  } else {
    // MySQL 等需要这些字段
    return {
      ...baseRules,
      database: [{ required: true, message: '请输入数据库名', trigger: 'blur' }],
      username: [{ required: true, message: '请输入用户名', trigger: 'blur' }],
      password: [{ required: true, message: '请输入密码', trigger: 'blur' }]
    }
  }
}

const rules = computed(() => getRules())

const loadList = async () => {
  try {
    await store.fetchConnections({
      page: currentPage.value,
      pageSize: pageSize.value,
      name: searchForm.value.name,
      host: searchForm.value.host,
      database: searchForm.value.database
    })
  } catch (e) {
    ElMessage.error('加载列表失败')
  }
}

const handleInputSearch = () => {
  clearTimeout(searchTimer)
  searchTimer = setTimeout(() => {
    currentPage.value = 1
    loadList()
  }, 500)
}

const resetSearch = () => {
  searchForm.value.name = ''
  searchForm.value.host = ''
  searchForm.value.database = ''
  currentPage.value = 1
  loadList()
}

const handlePageChange = (p) => {
  currentPage.value = p
  loadList()
}

const handleSizeChange = (s) => {
  pageSize.value = s
  currentPage.value = 1
  loadList()
}

const formatDate = (row, column, value) => (value ? formatDateTime(value) : '-')

// 处理驱动类型变化
const handleDriverChange = (driver) => {
  if (driver === 'redis') {
    // Redis 默认端口 6379，database 默认为 0
    dialog.form.port = 6379
    dialog.form.database = dialog.form.database !== undefined && dialog.form.database !== null ? dialog.form.database : 0
    dialog.form.username = ''
    dialog.form.charset = ''
  } else {
    // MySQL 默认端口 3306
    dialog.form.port = 3306
    dialog.form.charset = dialog.form.charset || 'utf8mb4'
  }
}

// CRUD
const showEditDialog = (row = null) => {
  dialog.isEdit = !!row
  dialog.form = row
    ? { ...row, password: '' }
    : {
        name: '',
        driver: 'mysql',
        host: '',
        port: 3306,
        database: '',
        username: '',
        password: '',
        charset: 'utf8mb4',
        description: ''
      }
  dialog.visible = true
}

const handleSubmit = async () => {
  if (!formRef.value) return
  await formRef.value.validate(async (valid) => {
    if (!valid) return
    try {
      if (dialog.isEdit) {
        const payload = { ...dialog.form }
        if (!payload.password) delete payload.password
        await store.updateConnection(dialog.form.id, payload)
        ElMessage.success('更新成功')
      } else {
        await store.createConnection(dialog.form)
        ElMessage.success('创建成功')
      }
      dialog.visible = false
      loadList()
    } catch (e) {
      ElMessage.error(store.error || '操作失败')
    }
  })
}

const handleDelete = async (id) => {
  try {
    await ElMessageBox.confirm('确定要删除此连接吗？', '提示', { type: 'warning' })
    await store.deleteConnection(id)
    ElMessage.success('删除成功')
    loadList()
  } catch (e) {
    if (e !== 'cancel') ElMessage.error('删除失败')
  }
}

const handleTest = async (id) => {
  try {
    const res = await store.testConnection(id)
    if (res.success) ElMessage.success(res.message || '连接成功')
    else ElMessage.error(res.message || '连接失败')
  } catch (e) {
    ElMessage.error('连接失败')
  }
}

const handleTestTemp = async () => {
  try {
    testLoading.value = true
    const res = await store.testConnectionParams({ ...dialog.form })
    if (res.success) ElMessage.success(res.message || '连接成功')
    else ElMessage.error(res.message || '连接失败')
  } finally {
    testLoading.value = false
  }
}

// 复制相关方法
const copyAllConnInfo = async (conn) => {
  const driver = (conn.driver || 'mysql').toLowerCase()
  const info = [`名称：${conn.name}`, `主机：${conn.host}`, `端口：${conn.port || (driver === 'redis' ? 6379 : 3306)}`]

  if (driver === 'redis') {
    if (conn.database !== undefined && conn.database !== null) {
      info.push(`数据库编号：${conn.database}`)
    }
  } else {
    if (conn.database) {
      info.push(`数据库：${conn.database}`)
    }
    if (conn.username) {
      info.push(`用户名：${conn.username}`)
    }
  }

  if (conn.password) {
    info.push(`密码：${conn.password}`)
  }

  if (conn.driver) {
    info.push(`驱动：${conn.driver}`)
  }

  if (conn.charset && driver !== 'redis') {
    info.push(`字符集：${conn.charset}`)
  }

  if (conn.description) {
    info.push(`描述：${conn.description}`)
  }

  // 添加数据库连接命令
  info.push('')
  info.push(`连接命令：${getConnectionCommand(conn)}`)

  const infoText = info.join('\n')

  try {
    await navigator.clipboard.writeText(infoText)
    ElMessage.success('数据库连接信息已复制到剪贴板')
  } catch (err) {
    ElMessage.error('复制失败，请手动复制')
  }
}

// 生成数据库连接命令
const getConnectionCommand = (conn) => {
  const driver = (conn.driver || 'mysql').toLowerCase()
  const host = conn.host || 'localhost'
  const port = conn.port || (driver === 'redis' ? 6379 : 3306)

  if (driver === 'redis') {
    // Redis 连接命令
    // 格式: redis-cli -h 主机 -p 端口 [-a 密码] [-n 数据库编号]
    let command = `redis-cli -h ${host} -p ${port}`

    if (conn.password) {
      command += ` -a ${conn.password}`
    }

    if (conn.database) {
      command += ` -n ${conn.database}`
    }

    return command
  } else {
    // MySQL 连接命令
    // 格式: mysql -h主机 -P端口 -u用户名 -p密码 数据库名
    const username = conn.username || ''
    const password = conn.password || ''
    const database = conn.database || ''

    let command = `mysql -h${host} -P${port} -u${username}`

    if (password) {
      command += ` -p${password}`
    } else {
      command += ` -p`
    }

    if (database) {
      command += ` ${database}`
    }

    return command
  }
}

const getRowClassName = ({ row, rowIndex }) => {
  return 'db-conn-info-row'
}

onMounted(() => {
  loadList()
})
</script>

<style scoped>
/* 数据库连接名称单元格样式 */
.conn-name-cell {
  cursor: pointer;
  color: #1890ff;
  transition: color 0.2s;
}

.conn-name-cell:hover {
  color: #40a9ff;
  text-decoration: underline;
}

/* 数据库连接信息行样式 */
:deep(.db-conn-info-row) {
  cursor: pointer;
}

:deep(.db-conn-info-row:hover) {
  background-color: #f5f7fa;
}
</style>

<style>
/* 数据库连接信息 Popover 全局样式 */
.db-conn-info-popover {
  padding: 0 !important;
  border-radius: 8px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}

.db-conn-info-popover-content {
  padding: 16px;
  min-width: 280px;
}

.db-conn-info-item {
  display: flex;
  align-items: center;
  margin-bottom: 12px;
  padding: 8px;
  border-radius: 4px;
  transition: background-color 0.2s;
}

.db-conn-info-item:hover {
  background-color: #f5f7fa;
}

.info-label {
  font-size: 13px;
  color: #909399;
  min-width: 80px;
  margin-right: 8px;
  flex-shrink: 0;
}

.info-value {
  font-size: 13px;
  color: #303133;
  font-weight: 500;
  flex: 1;
  word-break: break-all;
}

.db-conn-info-divider {
  height: 1px;
  background-color: #e4e7ed;
  margin: 12px 0;
}

.copy-all-btn {
  width: 100%;
  margin-top: 8px;
}
</style>

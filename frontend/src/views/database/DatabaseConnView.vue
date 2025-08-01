<template>
  <div class="common-list-container">
    <!-- 顶部工具栏 -->
    <div class="common-header-bar">
      <div class="common-search-bar">
        <el-form :inline="true" :model="searchForm" class="demo-form-inline">
          <el-form-item label="名称">
            <el-input
              v-model="searchForm.name"
              placeholder="请输入名称"
              clearable
              @input="handleInputSearch"
            />
          </el-form-item>
          <el-form-item label="主机">
            <el-input
              v-model="searchForm.host"
              placeholder="请输入主机地址"
              clearable
              @input="handleInputSearch"
            />
          </el-form-item>
          <el-form-item label="数据库">
            <el-input
              v-model="searchForm.database"
              placeholder="请输入数据库名"
              clearable
              @input="handleInputSearch"
            />
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
    <el-table :data="store.connections" v-loading="store.loading" style="width: 100%" empty-text="暂无数据">
      <el-table-column prop="id" label="ID" min-width="60"/>
      <el-table-column prop="name" label="名称" min-width="160" show-overflow-tooltip />
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
          <el-select v-model="dialog.form.driver" style="width: 200px">
            <el-option label="MySQL" value="mysql" />
          </el-select>
        </el-form-item>
        <el-form-item label="主机" prop="host">
          <el-input v-model="dialog.form.host" placeholder="例如：127.0.0.1" />
        </el-form-item>
        <el-form-item label="端口" prop="port">
          <el-input-number v-model="dialog.form.port" :min="1" :max="65535" />
        </el-form-item>
        <el-form-item label="数据库" prop="database">
          <el-input v-model="dialog.form.database" placeholder="请输入数据库名" />
        </el-form-item>
        <el-form-item label="用户名" prop="username">
          <el-input v-model="dialog.form.username" placeholder="请输入用户名" />
        </el-form-item>
        <el-form-item label="密码" prop="password">
          <el-input v-model="dialog.form.password" type="password" placeholder="请输入密码" show-password />
        </el-form-item>
        <el-form-item label="字符集" prop="charset">
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
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
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

const rules = {
  name: [{ required: true, message: '请输入名称', trigger: 'blur' }],
  host: [{ required: true, message: '请输入主机', trigger: 'blur' }],
  port: [{ required: true, message: '请输入端口', trigger: 'change' }],
  database: [{ required: true, message: '请输入数据库名', trigger: 'blur' }],
  username: [{ required: true, message: '请输入用户名', trigger: 'blur' }],
  password: [{ required: true, message: '请输入密码', trigger: 'blur' }]
}

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

// CRUD
const showEditDialog = (row = null) => {
  dialog.isEdit = !!row
  dialog.form = row
    ? { ...row, password: '' }
    : {
        name: '', driver: 'mysql', host: '', port: 3306,
        database: '', username: '', password: '', charset: 'utf8mb4', description: ''
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

onMounted(() => {
  loadList()
})
</script>

<style scoped>
/* 使用公共样式，无需额外样式 */
</style>



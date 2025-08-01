<template>
  <el-form ref="formRef" :model="form" :rules="rules" label-width="120px">
    <el-form-item label="所属项目" prop="form.project_id">
      <el-select v-model="form.project_id" filterable placeholder="请选择项目" clearable style="width: 100%" @change="handleProjectChange"><el-option v-for="project in projectOptions" :key="project.id" :label="project.name" :value="project.id"/></el-select>
    </el-form-item>
    <el-form-item label="接口名称" prop="name" required><el-input v-model="form.name" /></el-form-item>
    <el-form-item label="接口路径" prop="path" required><el-input v-model="form.path" placeholder="/api/users"><template #prepend>http://localhost:5001</template></el-input></el-form-item>
    <el-form-item label="请求方法" prop="method" required>
      <el-select v-model="form.method" placeholder="请选择请求方法">
        <el-option label="GET" value="GET" />
        <el-option label="POST" value="POST" />
        <el-option label="PUT" value="PUT" />
        <el-option label="DELETE" value="DELETE" />
      </el-select>
    </el-form-item>
    <el-form-item label="状态码" prop="response_status" required><el-input-number v-model="form.response_status" :min="100" :max="599" /></el-form-item>
    <el-form-item label="响应延迟" prop="response_delay"><el-input-number v-model="form.response_delay" :min="0" :max="10000" :step="1" :precision="0"><template #append>ms</template></el-input-number><span class="tip-text">（0表示无延迟）</span></el-form-item>
    <el-form-item label="响应内容" prop="response_body"><el-input v-model="form.response_body" type="textarea" :rows="5" placeholder="请输入响应内容（支持JSON/XML/纯文本）"/></el-form-item>
    <el-form-item label="接口描述" prop="description"><el-input v-model="form.description" type="textarea" :rows="2" /></el-form-item>
    <el-form-item>
      <el-button type="primary" @click="submitForm">提交</el-button>
      <el-button @click="$emit('cancel')">取消</el-button>
    </el-form-item>
  </el-form>
</template>

<script setup>
import { ref, watch, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { projectService } from '@/services/project/projectService'

// 组件挂载时获取项目列表
onMounted(() => {
  fetchProjects()
})

const loadData = async () => {
  // 清空表单，如果是创建操作
  if (!props.mock) {
    Object.keys(form.value).forEach(key => {
      form.value[key] = '' // 或默认值
    })
    // 重置为默认值
    form.value.method = 'GET'
    form.value.response_status = 200
    form.value.response_delay = 0
  }
  await fetchProjects()
}

defineExpose({
  loadData
})

const props = defineProps({
  mock: {
    type: Object,
    default: null
  }
})

const emit = defineEmits(['submit', 'cancel'])

const form = ref({
  project_id: '',
  project_name: '',
  name: '',
  path: '',
  method: 'GET',
  response_status: 200,
  response_delay: 0,
  response_body: '',
  description: ''
})

const projectOptions = ref([])
const projectsLoaded = ref(false) // 创建：标记项目列表是否已加载
const formRef = ref(null)

// 获取项目列表
const fetchProjects = async () => {
  try {
    const response = await projectService.getProjectOptions({
      page: 1,
      per_page: 1000
    })
    console.log('API响应:', response) // 检查完整的响应结构
    projectOptions.value = response.data?.items || response.data || []
    projectsLoaded.value = true // 标记为已加载

    // 项目列表加载完成后，如果是在编辑模式下且有project_id，设置project_name
    if (props.mock && props.mock.project_id) {
      setProjectName(props.mock.project_id)
    }
  } catch (error) {
    console.error('Fetching projects error:', error);
    ElMessage.error('获取项目列表失败')
  }
}

// 设置项目名称
const setProjectName = (projectId) => {
  const selectedProject = projectOptions.value.find(p => p.id === projectId)
  if (selectedProject) {
    form.value.project_name = selectedProject.name
  }
}

// 处理项目选择变化
const handleProjectChange = (projectId) => {
  const selectedProject = projectOptions.value.find(p => p.id === projectId)
  if (selectedProject) {
    form.value.project_name = selectedProject.name
  } else {
    form.value.project_name = ''
  }
}

const validatePath = (rule, value, callback) => {
  if (!value) {
    callback(new Error('接口路径不能为空'))
    return
  }
  if (!value.startsWith('/')) {
    callback(new Error('接口路径必须以/开头'))
    return
  }
  callback()
}

const validateResponseBody = (rule, value, callback) => {
  if (!value || value.trim() === '') {
    callback(new Error('响应内容不能为空'))
    return
  }
  callback()
}

const rules = {
  name: [
    { required: true, message: '请输入接口名称', trigger: 'blur' },
    { min: 2, max: 50, message: '长度应在2到50个字符之间', trigger: 'blur' }
  ],
  path: [
    { required: true, validator: validatePath, trigger: 'blur' }
  ],
  method: [
    { required: true, message: '请选择请求方法', trigger: 'change' }
  ],
  response_status: [
    { required: true, message: '请输入状态码', trigger: 'blur' },
    { type: 'number', min: 100, max: 599, message: '状态码必须在100到599之间', trigger: 'blur' }
  ],
  response_delay: [
    { type: 'number', min: 0, max: 10000, message: '延迟时间必须在0-10000毫秒之间', trigger: 'blur' }
  ],
  response_body: [
    { validator: validateResponseBody, trigger: 'blur' }
  ],
  description: [
    { max: 200, message: '描述不能超过200个字符', trigger: 'blur' }
  ]
}

watch(() => props.mock, async (newVal) => {
  if (newVal) {
    form.value = {
      project_id: newVal.project_id || '', // 修改：确保project_id被设置
      project_name: newVal.project_name || '', // 修改：确保project_name被设置
      name: newVal.name,
      path: newVal.path,
      method: newVal.method,
      response_status: newVal.response_status,
      response_delay: newVal.response_delay || 0,
      response_body: typeof newVal.response_body === 'string'
        ? newVal.response_body
        : JSON.stringify(newVal.response_body, null, 2),
      description: newVal.description
    }

    // 修改：如果项目列表已经加载，直接设置项目名称
    if (newVal.project_id && projectsLoaded.value) {
      setProjectName(newVal.project_id)
    }
    // 创建：如果项目列表还未加载，等待项目列表加载完成
    else if (newVal.project_id && !projectsLoaded.value) {
      // 可以添加一个重试机制或者等待项目列表加载
      const checkAndSetProjectName = () => {
        if (projectsLoaded.value) {
          setProjectName(newVal.project_id)
        } else {
          setTimeout(checkAndSetProjectName, 100)
        }
      }
      checkAndSetProjectName()
    }
  }
}, { immediate: true, deep: true })

const submitForm = async () => {
  try {
    await formRef.value.validate()
    emit('submit', form.value) // 直接提交表单数据
  } catch (error) {
    ElMessage.error('请修正表单中的错误')
  }
}
</script>

<style scoped>
.tip-text {
  margin-left: 10px;
  color: var(--el-text-color-secondary);
  font-size: 12px;
}
</style>
<template>
  <el-dialog
    v-model="dialogVisible"
    :title="formTitle"
    width="600px"
    :close-on-click-modal="false"
    @close="handleClose"
  >
    <el-form
      ref="formRef"
      :model="form"
      :rules="rules"
      label-width="80px"
      label-position="top"
    >
      <el-form-item label="模板名称" prop="name">
        <el-input
          v-model="form.name"
          placeholder="请输入模板名称"
          maxlength="100"
          show-word-limit
        />
      </el-form-item>

      <el-form-item label="分类" prop="category">
        <el-select
          v-model="form.category"
          placeholder="请选择分类"
          style="width: 100%"
          filterable
          allow-create
          clearable
        >
          <!-- 确保这里使用了正确的分类数据源 -->
          <el-option
            v-for="category in categories"
            :key="category"
            :label="category"
            :value="category"
          />
        </el-select>
      </el-form-item>

      <el-form-item label="SQL内容" prop="sql_content">
        <el-input
          v-model="form.sql_content"
          type="textarea"
          :rows="8"
          placeholder="请输入SQL语句"
          resize="vertical"
        />
      </el-form-item>

      <el-form-item label="描述" prop="description">
        <el-input
          v-model="form.description"
          type="textarea"
          :rows="3"
          placeholder="请输入模板描述"
          maxlength="500"
          show-word-limit
        />
      </el-form-item>

    </el-form>

    <template #footer>
      <el-button @click="handleClose">取消</el-button>
      <el-button type="primary" :loading="loading" @click="handleSubmit">
        保存
      </el-button>
    </template>
  </el-dialog>
</template>

<script setup>
import { ref, reactive, computed, watch, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { useSQLStore } from '@/stores/database/sqlStore'

const props = defineProps({
  modelValue: {
    type: Boolean,
    default: false
  },
  template: {
    type: Object,
    default: null
  }
})

const emit = defineEmits(['update:modelValue', 'success'])

const sqlStore = useSQLStore()

// 响应式数据
const formRef = ref()
const loading = ref(false)
const form = reactive({
  name: '',
  category: '',
  description: '',
  sql_content: ''
})

// 计算属性
const dialogVisible = computed({
  get: () => props.modelValue,
  set: (value) => emit('update:modelValue', value)
})

const formTitle = computed(() => {
  return props.template ? '编辑' : '创建'
})

// 关键：确保这里正确获取分类数据
const categories = computed(() => {
  console.log('当前分类数据:', sqlStore.categories)
  return sqlStore.categories || []
})

// 表单验证规则
const rules = {
  name: [
    { required: true, message: '请输入模板名称', trigger: 'blur' }
  ],
  category: [
    { required: true, message: '请选择或输入分类', trigger: 'change' }
  ],
  sql_content: [
    { required: true, message: '请输入SQL内容', trigger: 'blur' }
  ]
}

// 方法
const resetForm = () => {
  form.name = ''
  form.category = ''
  form.description = ''
  form.sql_content = ''
  if (formRef.value) {
    formRef.value.clearValidate()
  }
}

const handleClose = () => {
  dialogVisible.value = false
  resetForm()
}

const handleSubmit = async () => {
  if (!formRef.value) return

  try {
    const valid = await formRef.value.validate()
    if (!valid) return

    loading.value = true

    if (props.template) {
      await sqlStore.updateTemplate(props.template.id, form)
    } else {
      await sqlStore.createTemplate(form)
    }

    ElMessage.success(props.template ? '模板更新成功' : '模板创建成功')
    emit('success')
    handleClose()
  } catch (error) {
    ElMessage.error('操作失败: ' + (error.message || '未知错误'))
  } finally {
    loading.value = false
  }
}

// 监听对话框打开，确保分类数据已加载
watch(dialogVisible, (newVal) => {
  if (newVal) {
    // 对话框打开时确保分类数据已加载
    if (sqlStore.categories.length === 0) {
      sqlStore.loadCategories()
    }
  }
})

// 监听模板变化，填充表单数据
watch(() => props.template, (newTemplate) => {
  if (newTemplate) {
    form.name = newTemplate.name
    form.category = newTemplate.category
    form.description = newTemplate.description
    form.sql_content = newTemplate.sql_content
  } else {
    resetForm()
  }
}, { immediate: true })
</script>
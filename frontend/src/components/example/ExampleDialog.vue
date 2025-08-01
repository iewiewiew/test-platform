<template>
  <el-form
    ref="formRef"
    :model="form"
    :rules="rules"
    label-width="100px"
  >
    <el-form-item label="名称" prop="name">
      <el-input v-model="form.name" placeholder="请输入名称" />
    </el-form-item>
    <el-form-item label="描述" prop="description">
      <el-input
        v-model="form.description"
        type="textarea"
        :rows="3"
        placeholder="请输入描述"
      />
    </el-form-item>
    <el-form-item label="状态" prop="status">
      <el-radio-group v-model="form.status">
        <el-radio value="active">激活</el-radio>
        <el-radio value="inactive">禁用</el-radio>
      </el-radio-group>
    </el-form-item>
    <el-form-item>
      <el-button @click="$emit('cancel')">取消</el-button>
      <el-button type="primary" @click="submitForm" :loading="loading">确认</el-button>
    </el-form-item>
  </el-form>
</template>

<script setup>
import { ref, watch } from 'vue'
import { ElMessage } from 'element-plus'

const props = defineProps({
  editingItem: {
    type: Object,
    default: null
  },
  loading: {
    type: Boolean,
    default: false
  }
})

const emit = defineEmits(['submit', 'cancel'])

const formRef = ref(null)
const form = ref({
  name: '',
  description: '',
  status: 'active'
})

const rules = {
  name: [
    { required: true, message: '请输入名称', trigger: 'blur' },
    { min: 1, max: 100, message: '长度在1到100个字符', trigger: 'blur' }
  ],
  description: [
    { max: 500, message: '不能超过500个字符', trigger: 'blur' }
  ],
  status: [
    { required: true, message: '请选择状态', trigger: 'change' }
  ]
}

// 如果传入 editingItem prop，则填充表单
watch(() => props.editingItem, (newVal) => {
  if (newVal) {
    form.value = {
      name: newVal.name || '',
      description: newVal.description || '',
      status: newVal.status || 'active'
    }
  } else {
    // 重置表单
    form.value = {
      name: '',
      description: '',
      status: 'active'
    }
  }
}, { immediate: true })

const submitForm = async () => {
  try {
    await formRef.value.validate()
    emit('submit', form.value)
  } catch (error) {
    ElMessage.error('请检查表单填写是否正确')
  }
}
</script>

<style scoped>
:deep(.el-form-item__label) {
  font-weight: 500;
}
</style>
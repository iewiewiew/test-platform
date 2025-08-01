<template>
  <el-form
    ref="formRef"
    :model="form"
    :rules="rules"
    label-width="100px"
  >
    <el-form-item label="项目名称" prop="name">
      <el-input v-model="form.name" placeholder="请输入项目名称" />
    </el-form-item>
    <el-form-item label="项目描述" prop="description">
      <el-input
        v-model="form.description"
        type="textarea"
        :rows="3"
        placeholder="请输入项目描述"
      />
    </el-form-item>
    <el-form-item>
      <el-button @click="$emit('cancel')">取消</el-button>
      <el-button type="primary" @click="submitForm">确认</el-button>
    </el-form-item>
  </el-form>
</template>

<script setup>
import { ref, watch } from 'vue'
import { ElMessage } from 'element-plus'

const props = defineProps({
  project: {
    type: Object,
    default: null
  }
})

const emit = defineEmits(['submit', 'cancel'])

const formRef = ref(null)
const form = ref({
  name: '',
  description: ''
})

const rules = {
  name: [
    { required: true, message: '请输入项目名称', trigger: 'blur' },
    { min: 2, max: 50, message: '长度在2到50个字符', trigger: 'blur' }
  ],
  description: [
    { max: 200, message: '不能超过200个字符', trigger: 'blur' }
  ]
}

// 如果传入project prop，则填充表单
watch(() => props.project, (newVal) => {
  if (newVal) {
    form.value = {
      name: newVal.name,
      description: newVal.description || ''
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
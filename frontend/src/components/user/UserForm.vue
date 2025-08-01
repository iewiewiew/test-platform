<template>
  <el-form
    ref="formRef"
    :model="form"
    :rules="rules"
    label-width="80px"
    @submit.prevent
  >
    <el-form-item label="用户名" prop="username">
      <el-input
        v-model="form.username"
        placeholder="请输入用户名"
        :disabled="isEdit"
      />
    </el-form-item>

    <el-form-item label="邮箱" prop="email">
      <el-input
        v-model="form.email"
        placeholder="请输入邮箱"
        type="email"
      />
    </el-form-item>

    <el-form-item label="姓名" prop="full_name">
      <el-input
        v-model="form.full_name"
        placeholder="请输入姓名"
      />
    </el-form-item>

    <el-form-item label="角色" prop="role_id">
      <el-select
        v-model="form.role_id"
        placeholder="请选择角色"
        style="width: 100%"
        clearable
      >
        <el-option
          v-for="role in roleOptions"
          :key="role.value"
          :label="role.label"
          :value="role.value"
        />
      </el-select>
    </el-form-item>

    <el-form-item label="密码" prop="password" v-if="!isEdit">
      <el-input
        v-model="form.password"
        type="password"
        placeholder="请输入密码"
        show-password
      />
    </el-form-item>

    <el-form-item label="确认密码" prop="confirmPassword" v-if="!isEdit">
      <el-input
        v-model="form.confirmPassword"
        type="password"
        placeholder="请确认密码"
        show-password
      />
    </el-form-item>

    <el-form-item label="状态" prop="is_active">
      <el-switch
        v-model="form.is_active"
        active-text="激活"
        inactive-text="禁用"
      />
    </el-form-item>

    <el-form-item>
      <el-button @click="handleCancel">取消</el-button>
      <el-button type="primary" :loading="loading" @click="handleSubmit">
        {{ isEdit ? '更新' : '创建' }}
      </el-button>
    </el-form-item>
  </el-form>
</template>

<script setup>
import { ref, reactive, watch, onMounted, computed } from 'vue'
import { ElMessage } from 'element-plus'
import { useRoleStore } from '@/stores/auth/roleStore'

const props = defineProps({
  user: {
    type: Object,
    default: null
  }
})

const emit = defineEmits(['submit', 'cancel'])

const roleStore = useRoleStore()
const formRef = ref()
const loading = ref(false)
const roleOptions = ref([])

const isEdit = computed(() => !!props.user)

const form = reactive({
  username: '',
  email: '',
  full_name: '',
  role_id: null,
  password: '',
  confirmPassword: '',
  is_active: true,
})

const rules = {
  username: [
    { required: true, message: '请输入用户名', trigger: 'blur' },
    { min: 3, max: 20, message: '用户名长度为 3 到 20 个字符', trigger: 'blur' }
  ],
  email: [
    { required: true, message: '请输入邮箱', trigger: 'blur' },
    { type: 'email', message: '请输入正确的邮箱格式', trigger: 'blur' }
  ],
  full_name: [
    { required: true, message: '请输入姓名', trigger: 'blur' }
  ],
  password: [
    {
      required: !isEdit.value,
      message: '请输入密码',
      trigger: 'blur'
    },
    {
      min: 6,
      message: '密码长度至少为 6 个字符',
      trigger: 'blur'
    }
  ],
  confirmPassword: [
    {
      required: !isEdit.value,
      message: '请确认密码',
      trigger: 'blur'
    },
    {
      validator: (rule, value, callback) => {
        if (!isEdit.value && value !== form.password) {
          callback(new Error('两次输入的密码不一致'))
        } else {
          callback()
        }
      },
      trigger: 'blur'
    }
  ]
}

// 监听用户数据变化
watch(() => props.user, (newUser) => {
  if (newUser) {
    Object.assign(form, {
      username: newUser.username,
      email: newUser.email,
      full_name: newUser.full_name,
      role_id: newUser.role_id,
      is_active: newUser.is_active,
      password: '',
      confirmPassword: ''
    })
  }
}, { immediate: true })

// 加载角色选项
const loadRoleOptions = async () => {
  const result = await roleStore.fetchRoles()
  if (result.success) {
    roleOptions.value = roleStore.roles.map(role => ({
      value: role.id,
      label: role.name
    }))
  }
}

// 提交表单
const handleSubmit = async () => {
  if (!formRef.value) return

  try {
    const valid = await formRef.value.validate()
    if (!valid) return

    loading.value = true

    const userData = {
      username: form.username,
      email: form.email,
      full_name: form.full_name,
      role_id: form.role_id,
      is_active: form.is_active,
    }

    if (!isEdit.value) {
      userData.password = form.password
    }

    emit('submit', userData)
  } catch (error) {
    console.error('Form validation error:', error)
  } finally {
    loading.value = false
  }
}

// 取消操作
const handleCancel = () => {
  emit('cancel')
}

onMounted(() => {
  loadRoleOptions()
})
</script>
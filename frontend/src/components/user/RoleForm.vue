<template>
  <el-form
    ref="formRef"
    :model="form"
    :rules="rules"
    label-width="100px"
    @submit.prevent
  >
    <el-form-item label="角色名称" prop="name">
      <el-input
        v-model="form.name"
        placeholder="请输入角色名称"
        maxlength="50"
        show-word-limit
      />
    </el-form-item>

    <el-form-item label="角色描述" prop="description">
      <el-input
        v-model="form.description"
        type="textarea"
        :rows="3"
        placeholder="请输入角色描述"
        maxlength="200"
        show-word-limit
      />
    </el-form-item>

    <el-form-item label="权限设置" prop="permissions">
      <div class="permissions-container" :class="{ readonly: isViewMode }">
        <div class="permission-group" v-for="group in permissionGroups" :key="group.title">
          <h4 class="permission-group-title">{{ group.title }}</h4>
          <div class="permission-items">
            <el-checkbox-group v-model="form.permissions" :disabled="isViewMode">
              <el-checkbox
                v-for="permission in group.permissions"
                :key="permission.value"
                :label="permission.value"
              >
                {{ permission.label }}
              </el-checkbox>
            </el-checkbox-group>
          </div>
        </div>

        <div class="permission-actions" v-if="!isViewMode">
          <el-button link type="primary" @click="selectAllPermissions">
            全选
          </el-button>
          <el-button link @click="clearAllPermissions">
            清空
          </el-button>
        </div>
      </div>
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
import { ref, reactive, watch, computed } from 'vue'
import { ElMessage } from 'element-plus'
import { PERMISSIONS, PERMISSION_LABELS, getAllPermissionOptions } from '@/constants/permissions'

const props = defineProps({
  role: {
    type: Object,
    default: null
  },
  mode: {
    type: String,
    default: 'edit' // 'edit' | 'view'
  }
})

const emit = defineEmits(['submit', 'cancel'])

const formRef = ref()
const loading = ref(false)

const isEdit = computed(() => !!props.role)
const isViewMode = computed(() => props.mode === 'view')

// 权限分组配置
const permissionGroups = ref([
  {
    title: '用户管理权限',
    permissions: [
      { value: PERMISSIONS.USER_READ, label: PERMISSION_LABELS[PERMISSIONS.USER_READ] },
      { value: PERMISSIONS.USER_WRITE, label: PERMISSION_LABELS[PERMISSIONS.USER_WRITE] },
      { value: PERMISSIONS.USER_DELETE, label: PERMISSION_LABELS[PERMISSIONS.USER_DELETE] }
    ]
  },
  {
    title: '角色管理权限',
    permissions: [
      { value: PERMISSIONS.ROLE_READ, label: PERMISSION_LABELS[PERMISSIONS.ROLE_READ] },
      { value: PERMISSIONS.ROLE_WRITE, label: PERMISSION_LABELS[PERMISSIONS.ROLE_WRITE] }
    ]
  }
])

const form = reactive({
  name: '',
  description: '',
  permissions: []
})

const rules = {
  name: [
    { required: true, message: '请输入角色名称', trigger: 'blur' },
    { min: 2, max: 50, message: '角色名称长度为 2 到 50 个字符', trigger: 'blur' },
    {
      validator: (rule, value, callback) => {
        if (value && !/^[a-zA-Z0-9_\u4e00-\u9fa5]+$/.test(value)) {
          callback(new Error('角色名称只能包含中文、英文、数字和下划线'))
        } else {
          callback()
        }
      },
      trigger: 'blur'
    }
  ],
  description: [
    { max: 200, message: '角色描述不能超过 200 个字符', trigger: 'blur' }
  ],
  permissions: [
    {
      validator: (rule, value, callback) => {
        if (!isViewMode.value && value.length === 0) {
          callback(new Error('请至少选择一个权限'))
        } else {
          callback()
        }
      },
      trigger: 'change'
    }
  ]
}

// 解析权限为数组（兼容字符串和数组）
const parsePermissions = (input) => {
  if (!input) return []
  if (Array.isArray(input)) return input
  try {
    const parsed = JSON.parse(input)
    return Array.isArray(parsed) ? parsed : []
  } catch {
    return []
  }
}

// 重置表单
const resetForm = () => {
  Object.assign(form, {
    name: '',
    description: '',
    permissions: []
  })
  if (formRef.value) {
    formRef.value.clearValidate()
  }
}

// 监听角色数据变化
watch(() => props.role, (newRole) => {
  if (newRole) {
    Object.assign(form, {
      name: newRole.name,
      description: newRole.description || '',
      permissions: parsePermissions(newRole.permissions)
    })
  } else {
    resetForm()
  }
}, { immediate: true })

// 全选权限
const selectAllPermissions = () => {
  const allPermissions = getAllPermissionOptions().map(item => item.value)
  form.permissions = [...allPermissions]
}

// 清空权限
const clearAllPermissions = () => {
  form.permissions = []
}

// 提交表单
const handleSubmit = async () => {
  if (!formRef.value) return

  try {
    const valid = await formRef.value.validate()
    if (!valid) return

    loading.value = true

    const roleData = {
      name: form.name.trim(),
      description: form.description.trim(),
      permissions: JSON.stringify(form.permissions)
    }

    emit('submit', roleData)
  } catch (error) {
    console.error('Form validation error:', error)
    ElMessage.error('表单验证失败，请检查输入')
  } finally {
    loading.value = false
  }
}

// 取消操作
const handleCancel = () => {
  emit('cancel')
}

// 暴露方法给父组件
defineExpose({
  resetForm
})
</script>

<style scoped>
.permissions-container {
  border: 1px solid #e4e7ed;
  border-radius: 4px;
  padding: 16px;
  background-color: #fafafa;
}

.permission-group {
  margin-bottom: 20px;
}

.permission-group:last-child {
  margin-bottom: 0;
}

.permission-group-title {
  margin: 0 0 12px 0;
  font-size: 14px;
  font-weight: 600;
  color: #303133;
  border-bottom: 1px solid #e4e7ed;
  padding-bottom: 8px;
}

.permission-items {
  display: flex;
  flex-wrap: wrap;
  gap: 16px;
}

:deep(.el-checkbox) {
  margin-right: 0;
  min-width: 120px;
}

.permission-actions {
  margin-top: 16px;
  padding-top: 16px;
  border-top: 1px solid #e4e7ed;
  display: flex;
  gap: 16px;
}

/* 只读模式样式 */
.permissions-container.readonly {
  background-color: #f5f7fa;
  border-color: #d3d4d6;
}

.readonly .permission-group-title {
  color: #909399;
}

:deep(.readonly .el-checkbox) {
  --el-checkbox-input-border-color-hover: #c0c4cc;
}

:deep(.readonly .el-checkbox__input.is-disabled .el-checkbox__inner) {
  background-color: #f5f7fa;
  border-color: #e4e7ed;
}

:deep(.readonly .el-checkbox__input.is-disabled.is-checked .el-checkbox__inner) {
  background-color: #a0cfff;
  border-color: #a0cfff;
}

:deep(.readonly .el-checkbox__input.is-disabled + .el-checkbox__label) {
  color: #606266;
}
</style>
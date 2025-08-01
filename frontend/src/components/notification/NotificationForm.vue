<template>
  <el-form ref="formRef" :model="form" :rules="rules" label-width="120px" @submit.prevent>
    <el-form-item label="通知名称" prop="name">
      <el-input v-model="form.name" placeholder="请输入通知名称" />
    </el-form-item>

    <el-form-item label="通知类型" prop="notification_type">
      <el-select v-model="form.notification_type" placeholder="请选择通知类型" style="width: 100%" @change="handleTypeChange">
        <el-option label="飞书" value="feishu" />
        <el-option label="钉钉" value="dingtalk" />
        <el-option label="企业微信" value="wechat_work" />
        <el-option label="自定义" value="custom" />
      </el-select>
    </el-form-item>

    <el-form-item label="Webhook URL" prop="webhook_url">
      <el-input v-model="form.webhook_url" placeholder="请输入Webhook URL" type="textarea" :rows="2" />
    </el-form-item>

    <el-form-item label="密钥" prop="secret">
      <el-input v-model="form.secret" placeholder="请输入密钥（可选，用于签名验证）" show-password />
      <div class="form-item-tip">用于签名验证，飞书和钉钉支持</div>
    </el-form-item>

    <el-form-item label="描述" prop="description">
      <el-input v-model="form.description" placeholder="请输入描述" type="textarea" :rows="3" />
    </el-form-item>

    <el-form-item label="是否启用" prop="is_enabled">
      <el-switch v-model="form.is_enabled" active-text="启用" inactive-text="禁用" />
    </el-form-item>

    <el-form-item label="额外配置" prop="config" v-if="form.notification_type === 'custom'">
      <el-input v-model="configJson" placeholder='请输入JSON格式配置，例如：{"headers": {"Authorization": "Bearer token"}, "timeout": 10}' type="textarea" :rows="4" />
      <div class="form-item-tip">JSON格式，用于自定义通知的headers、timeout等配置</div>
    </el-form-item>

    <el-form-item>
      <el-button @click="handleCancel">取消</el-button>
      <el-button type="primary" :loading="loading" @click="handleSubmit">
        {{ isEdit ? '更新' : '创建' }}
      </el-button>
      <el-button v-if="isEdit" type="success" :loading="testLoading" @click="handleTest">测试</el-button>
    </el-form-item>
  </el-form>
</template>

<script setup>
import { ref, reactive, watch, computed } from 'vue'
import { ElMessage } from 'element-plus'
import { useNotificationStore } from '@/stores/notification/notificationStore'

const props = defineProps({
  notification: {
    type: Object,
    default: null
  }
})

const emit = defineEmits(['submit', 'cancel'])

const notificationStore = useNotificationStore()
const formRef = ref()
const loading = ref(false)
const testLoading = ref(false)
const configJson = ref('')

const isEdit = computed(() => !!props.notification)

const form = reactive({
  name: '',
  notification_type: 'feishu',
  webhook_url: '',
  secret: '',
  description: '',
  is_enabled: true,
  config: null
})

const rules = {
  name: [
    { required: true, message: '请输入通知名称', trigger: 'blur' },
    { min: 2, max: 100, message: '通知名称长度为 2 到 100 个字符', trigger: 'blur' }
  ],
  notification_type: [{ required: true, message: '请选择通知类型', trigger: 'change' }],
  webhook_url: [
    { required: true, message: '请输入Webhook URL', trigger: 'blur' },
    { type: 'url', message: '请输入有效的URL', trigger: 'blur' }
  ]
}

// 监听通知数据变化
watch(
  () => props.notification,
  (newNotification) => {
    if (newNotification) {
      Object.assign(form, {
        name: newNotification.name || '',
        notification_type: newNotification.notification_type || 'feishu',
        webhook_url: newNotification.webhook_url || '',
        secret: newNotification.secret || '',
        description: newNotification.description || '',
        is_enabled: newNotification.is_enabled !== undefined ? newNotification.is_enabled : true,
        config: newNotification.config || null
      })
      // 处理config JSON
      if (newNotification.config) {
        try {
          configJson.value = JSON.stringify(newNotification.config, null, 2)
        } catch (e) {
          configJson.value = ''
        }
      } else {
        configJson.value = ''
      }
    }
  },
  { immediate: true }
)

// 监听通知类型变化
const handleTypeChange = () => {
  // 类型变化时清空config
  if (form.notification_type !== 'custom') {
    form.config = null
    configJson.value = ''
  }
}

// 提交表单
const handleSubmit = async () => {
  if (!formRef.value) return

  try {
    const valid = await formRef.value.validate()
    if (!valid) return

    loading.value = true

    // 处理config JSON
    let config = null
    if (form.notification_type === 'custom' && configJson.value) {
      try {
        config = JSON.parse(configJson.value)
      } catch (e) {
        ElMessage.error('额外配置JSON格式错误')
        loading.value = false
        return
      }
    }

    const notificationData = {
      name: form.name,
      notification_type: form.notification_type,
      webhook_url: form.webhook_url,
      secret: form.secret || null,
      description: form.description || '',
      is_enabled: form.is_enabled,
      config: config
    }

    emit('submit', notificationData)
  } catch (error) {
    console.error('Form validation error:', error)
  } finally {
    loading.value = false
  }
}

// 测试通知
const handleTest = async () => {
  if (!props.notification || !props.notification.id) {
    ElMessage.warning('请先保存通知配置')
    return
  }

  testLoading.value = true
  try {
    const result = await notificationStore.testNotification(props.notification.id, '这是一条测试消息')
    if (result.success) {
      ElMessage.success(result.message || '测试通知发送成功')
    } else {
      ElMessage.error(result.message || '测试通知发送失败')
    }
  } catch (error) {
    ElMessage.error('测试通知失败: ' + (error.message || '未知错误'))
  } finally {
    testLoading.value = false
  }
}

// 取消操作
const handleCancel = () => {
  emit('cancel')
}
</script>

<style scoped>
.form-item-tip {
  font-size: 12px;
  color: #909399;
  margin-top: 4px;
}
</style>

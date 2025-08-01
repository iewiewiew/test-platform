<template>
  <div class="common-list-container">
    <div class="tool-section">
      <h3>Base64 编码/解码</h3>
      <el-row :gutter="20">
        <el-col :span="12">
          <el-card>
            <template #header>Base64 编码</template>
            <el-input v-model="base64EncodeInput" type="textarea" :rows="5" placeholder="请输入要编码的文本，例如：Hello World" />
            <el-button type="primary" @click="handleBase64Encode" class="tool-button">编码</el-button>
            <el-input v-model="base64EncodeOutput" type="textarea" :rows="5" placeholder="编码结果" class="tool-output" />
          </el-card>
        </el-col>
        <el-col :span="12">
          <el-card>
            <template #header>Base64 解码</template>
            <el-input v-model="base64DecodeInput" type="textarea" :rows="5" placeholder="请输入要解码的文本，例如：SGVsbG8gV29ybGQ=" />
            <el-button type="primary" @click="handleBase64Decode" class="tool-button">解码</el-button>
            <el-input v-model="base64DecodeOutput" type="textarea" :rows="5" placeholder="解码结果" class="tool-output" />
          </el-card>
        </el-col>
      </el-row>
    </div>

    <div class="tool-section">
      <h3>JWT Token 解析</h3>
      <el-card>
        <el-input
          v-model="jwtTokenInput"
          type="textarea"
          :rows="3"
          placeholder="请输入 JWT Token，例如：eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNTE2MjM5MDIyfQ.SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c"
        />
        <div class="tool-flex-row">
          <el-input v-model="jwtSecretInput" placeholder="密钥（可选），例如：your-256-bit-secret" class="tool-flex-item" />
          <el-checkbox v-model="jwtVerify" class="tool-checkbox-item">验证签名</el-checkbox>
        </div>
        <el-button type="primary" @click="handleJwtDecode" class="tool-button">解析</el-button>
        <el-input v-model="jwtDecodeOutput" type="textarea" :rows="10" placeholder="解析结果（JSON格式）" class="tool-output" />
      </el-card>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { ElMessage } from 'element-plus'
import toolService from '@/services/tool/toolService'

// 编码/解码工具
const base64EncodeInput = ref('Hello World')
const base64EncodeOutput = ref('')
const base64DecodeInput = ref('SGVsbG8gV29ybGQ=')
const base64DecodeOutput = ref('')
const jwtTokenInput = ref('eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNTE2MjM5MDIyfQ.SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c')
const jwtSecretInput = ref('your-256-bit-secret')
const jwtVerify = ref(true)
const jwtDecodeOutput = ref('')

// 编码/解码处理函数
const handleBase64Encode = async () => {
  if (!base64EncodeInput.value) {
    ElMessage.warning('请输入要编码的文本')
    return
  }
  try {
    const response = await toolService.base64Encode(base64EncodeInput.value)
    if (response.data.success) {
      base64EncodeOutput.value = response.data.result
    } else {
      ElMessage.error(response.data.error || '编码失败')
    }
  } catch (error) {
    ElMessage.error('编码失败：' + (error.message || '未知错误'))
  }
}

const handleBase64Decode = async () => {
  if (!base64DecodeInput.value) {
    ElMessage.warning('请输入要解码的文本')
    return
  }
  try {
    const response = await toolService.base64Decode(base64DecodeInput.value)
    if (response.data.success) {
      base64DecodeOutput.value = response.data.result
    } else {
      ElMessage.error(response.data.error || '解码失败')
    }
  } catch (error) {
    ElMessage.error('解码失败：' + (error.message || '未知错误'))
  }
}

const handleJwtDecode = async () => {
  if (!jwtTokenInput.value) {
    ElMessage.warning('请输入 JWT Token')
    return
  }
  try {
    const response = await toolService.jwtDecode(jwtTokenInput.value, jwtSecretInput.value || null, jwtVerify.value)
    if (response.data.success) {
      jwtDecodeOutput.value = JSON.stringify(response.data.result, null, 2)
    } else {
      ElMessage.error(response.data.error || '解析失败')
      jwtDecodeOutput.value = ''
    }
  } catch (error) {
    ElMessage.error('解析失败：' + (error.message || '未知错误'))
  }
}
</script>

<style scoped>
.tool-section {
  margin-bottom: 20px;
}

.tool-section:last-child {
  margin-bottom: 0;
}

.tool-section h3 {
  margin-bottom: 12px;
  color: #303133;
  font-size: 15px;
  font-weight: 600;
}

.tool-section :deep(.el-card) {
  border-radius: 6px;
  box-shadow: 0 1px 4px 0 rgba(0, 0, 0, 0.08);
  border: 1px solid #ebeef5;
}

.tool-section :deep(.el-card__header) {
  font-weight: 500;
  background-color: #f8f9fa;
  border-bottom: 1px solid #ebeef5;
  padding: 10px 16px;
  font-size: 14px;
}

.tool-section :deep(.el-card__body) {
  padding: 16px;
}

.tool-section :deep(.el-textarea__inner) {
  font-family: 'Monaco', 'Menlo', 'Ubuntu Mono', monospace;
  font-size: 13px;
  line-height: 1.5;
}

.tool-button {
  margin-top: 12px;
  width: 100%;
}

.tool-output {
  margin-top: 12px;
}

.tool-flex-row {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-top: 12px;
}

.tool-flex-item {
  flex: 1;
}

.tool-checkbox-item {
  white-space: nowrap;
}
</style>

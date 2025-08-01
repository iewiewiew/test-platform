<template>
  <div class="common-list-container">
    <div class="tool-section">
      <h3>哈希算法</h3>
      <el-card>
        <el-input v-model="hashInput" type="textarea" :rows="3" placeholder="请输入要哈希的文本，例如：Hello World" />
        <div class="tool-hash-buttons">
          <el-button type="primary" @click="handleMd5Hash" size="default">MD5</el-button>
          <el-button type="primary" @click="handleSha1Hash" size="default">SHA1</el-button>
          <el-button type="primary" @click="handleSha256Hash" size="default">SHA256</el-button>
          <el-button type="primary" @click="handleSha512Hash" size="default">SHA512</el-button>
        </div>
        <el-input v-model="hashOutput" type="textarea" :rows="5" placeholder="哈希结果" class="tool-output" />
      </el-card>
    </div>

    <div class="tool-section">
      <h3>HMAC 哈希</h3>
      <el-card>
        <el-input v-model="hmacTextInput" type="textarea" :rows="3" placeholder="请输入要哈希的文本，例如：Hello World" />
        <el-input v-model="hmacKeyInput" placeholder="密钥，例如：secret-key" class="tool-input-group" />
        <el-select v-model="hmacAlgorithm" placeholder="选择算法" class="tool-input-group" style="width: 100%">
          <el-option label="MD5" value="md5" />
          <el-option label="SHA1" value="sha1" />
          <el-option label="SHA256" value="sha256" />
          <el-option label="SHA512" value="sha512" />
        </el-select>
        <el-button type="primary" @click="handleHmacHash" class="tool-button">计算 HMAC</el-button>
        <el-input v-model="hmacOutput" type="textarea" :rows="5" placeholder="HMAC 结果" class="tool-output" />
      </el-card>
    </div>

    <div class="tool-section">
      <h3>AES 加密/解密</h3>
      <el-row :gutter="20">
        <el-col :span="12">
          <el-card>
            <template #header>AES 加密</template>
            <el-input v-model="aesEncryptText" type="textarea" :rows="5" placeholder="请输入明文，例如：Hello World" />
            <el-input v-model="aesEncryptKey" placeholder="密钥（16/24/32字节），例如：1234567890123456" class="tool-input-group" />
            <el-select v-model="aesMode" placeholder="加密模式" class="tool-input-group" style="width: 100%">
              <el-option label="CBC" value="CBC" />
              <el-option label="ECB" value="ECB" />
            </el-select>
            <el-button type="primary" @click="handleAesEncrypt" class="tool-button">加密</el-button>
            <el-input v-model="aesEncryptOutput" type="textarea" :rows="5" placeholder="密文（Base64编码）" class="tool-output" />
          </el-card>
        </el-col>
        <el-col :span="12">
          <el-card>
            <template #header>AES 解密</template>
            <el-input v-model="aesDecryptText" type="textarea" :rows="5" placeholder="请输入密文（Base64编码），例如：xxxxxxxxxxxxxxxxx" />
            <el-input v-model="aesDecryptKey" placeholder="密钥（16/24/32字节），例如：1234567890123456" class="tool-input-group" />
            <el-select v-model="aesDecryptMode" placeholder="加密模式" class="tool-input-group" style="width: 100%">
              <el-option label="CBC" value="CBC" />
              <el-option label="ECB" value="ECB" />
            </el-select>
            <el-button type="primary" @click="handleAesDecrypt" class="tool-button">解密</el-button>
            <el-input v-model="aesDecryptOutput" type="textarea" :rows="5" placeholder="明文" class="tool-output" />
          </el-card>
        </el-col>
      </el-row>
    </div>

    <div class="tool-section">
      <h3>RSA 加密/解密</h3>
      <el-row :gutter="20">
        <el-col :span="12">
          <el-card>
            <template #header>RSA 加密</template>
            <el-input v-model="rsaEncryptText" type="textarea" :rows="3" placeholder="请输入明文，例如：Hello World" />
            <el-input v-model="rsaPublicKey" type="textarea" :rows="5" placeholder="公钥（PEM格式），例如：-----BEGIN PUBLIC KEY-----...-----END PUBLIC KEY-----" class="tool-input-group" />
            <el-button type="primary" @click="handleRsaEncrypt" class="tool-button">加密</el-button>
            <el-input v-model="rsaEncryptOutput" type="textarea" :rows="5" placeholder="密文（Base64编码）" class="tool-output" />
          </el-card>
        </el-col>
        <el-col :span="12">
          <el-card>
            <template #header>RSA 解密</template>
            <el-input v-model="rsaDecryptText" type="textarea" :rows="3" placeholder="请输入密文（Base64编码），例如：xxxxxxxxxxxxxxxxx" />
            <el-input v-model="rsaPrivateKey" type="textarea" :rows="5" placeholder="私钥（PEM格式），例如：-----BEGIN PRIVATE KEY-----...-----END PRIVATE KEY-----" class="tool-input-group" />
            <el-button type="primary" @click="handleRsaDecrypt" class="tool-button">解密</el-button>
            <el-input v-model="rsaDecryptOutput" type="textarea" :rows="5" placeholder="明文" class="tool-output" />
          </el-card>
        </el-col>
      </el-row>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { ElMessage } from 'element-plus'
import toolService from '@/services/tool/toolService'

// 加密/解密工具
const hashInput = ref('Hello World')
const hashOutput = ref('')
const hmacTextInput = ref('Hello World')
const hmacKeyInput = ref('secret-key')
const hmacAlgorithm = ref('sha256')
const hmacOutput = ref('')
const aesEncryptText = ref('Hello World')
const aesEncryptKey = ref('1234567890123456')
const aesMode = ref('CBC')
const aesEncryptOutput = ref('')
const aesDecryptText = ref('')
const aesDecryptKey = ref('1234567890123456')
const aesDecryptMode = ref('CBC')
const aesDecryptOutput = ref('')
const rsaEncryptText = ref('Hello World')
const rsaPublicKey = ref('-----BEGIN PUBLIC KEY-----\nMIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEAyOuDbk8w9AqhRVb7\n...\n-----END PUBLIC KEY-----')
const rsaEncryptOutput = ref('')
const rsaDecryptText = ref('')
const rsaPrivateKey = ref('-----BEGIN PRIVATE KEY-----\nMIIEvQIBADANBgkqhkiG9w0BAQEFAASCBKcwggSjAgEAAoIBAQDI64tZpjvd\n...\n-----END PRIVATE KEY-----')
const rsaDecryptOutput = ref('')

// 加密/解密处理函数
const handleMd5Hash = async () => {
  if (!hashInput.value) {
    ElMessage.warning('请输入要哈希的文本')
    return
  }
  try {
    const response = await toolService.md5Hash(hashInput.value)
    if (response.data.success) {
      hashOutput.value = response.data.result
    } else {
      ElMessage.error(response.data.error || '计算失败')
    }
  } catch (error) {
    ElMessage.error('计算失败：' + (error.message || '未知错误'))
  }
}

const handleSha1Hash = async () => {
  if (!hashInput.value) {
    ElMessage.warning('请输入要哈希的文本')
    return
  }
  try {
    const response = await toolService.sha1Hash(hashInput.value)
    if (response.data.success) {
      hashOutput.value = response.data.result
    } else {
      ElMessage.error(response.data.error || '计算失败')
    }
  } catch (error) {
    ElMessage.error('计算失败：' + (error.message || '未知错误'))
  }
}

const handleSha256Hash = async () => {
  if (!hashInput.value) {
    ElMessage.warning('请输入要哈希的文本')
    return
  }
  try {
    const response = await toolService.sha256Hash(hashInput.value)
    if (response.data.success) {
      hashOutput.value = response.data.result
    } else {
      ElMessage.error(response.data.error || '计算失败')
    }
  } catch (error) {
    ElMessage.error('计算失败：' + (error.message || '未知错误'))
  }
}

const handleSha512Hash = async () => {
  if (!hashInput.value) {
    ElMessage.warning('请输入要哈希的文本')
    return
  }
  try {
    const response = await toolService.sha512Hash(hashInput.value)
    if (response.data.success) {
      hashOutput.value = response.data.result
    } else {
      ElMessage.error(response.data.error || '计算失败')
    }
  } catch (error) {
    ElMessage.error('计算失败：' + (error.message || '未知错误'))
  }
}

const handleHmacHash = async () => {
  if (!hmacTextInput.value || !hmacKeyInput.value) {
    ElMessage.warning('请输入文本和密钥')
    return
  }
  try {
    const response = await toolService.hmacHash(hmacTextInput.value, hmacKeyInput.value, hmacAlgorithm.value)
    if (response.data.success) {
      hmacOutput.value = response.data.result
    } else {
      ElMessage.error(response.data.error || '计算失败')
    }
  } catch (error) {
    ElMessage.error('计算失败：' + (error.message || '未知错误'))
  }
}

const handleAesEncrypt = async () => {
  if (!aesEncryptText.value || !aesEncryptKey.value) {
    ElMessage.warning('请输入明文和密钥')
    return
  }
  try {
    const response = await toolService.aesEncrypt(aesEncryptText.value, aesEncryptKey.value, aesMode.value)
    if (response.data.success) {
      aesEncryptOutput.value = response.data.result
    } else {
      ElMessage.error(response.data.error || '加密失败')
    }
  } catch (error) {
    ElMessage.error('加密失败：' + (error.message || '未知错误'))
  }
}

const handleAesDecrypt = async () => {
  if (!aesDecryptText.value || !aesDecryptKey.value) {
    ElMessage.warning('请输入密文和密钥')
    return
  }
  try {
    const response = await toolService.aesDecrypt(aesDecryptText.value, aesDecryptKey.value, aesDecryptMode.value)
    if (response.data.success) {
      aesDecryptOutput.value = response.data.result
    } else {
      ElMessage.error(response.data.error || '解密失败')
    }
  } catch (error) {
    ElMessage.error('解密失败：' + (error.message || '未知错误'))
  }
}

const handleRsaEncrypt = async () => {
  if (!rsaEncryptText.value || !rsaPublicKey.value) {
    ElMessage.warning('请输入明文和公钥')
    return
  }
  try {
    const response = await toolService.rsaEncrypt(rsaEncryptText.value, rsaPublicKey.value)
    if (response.data.success) {
      rsaEncryptOutput.value = response.data.result
    } else {
      ElMessage.error(response.data.error || '加密失败')
    }
  } catch (error) {
    ElMessage.error('加密失败：' + (error.message || '未知错误'))
  }
}

const handleRsaDecrypt = async () => {
  if (!rsaDecryptText.value || !rsaPrivateKey.value) {
    ElMessage.warning('请输入密文和私钥')
    return
  }
  try {
    const response = await toolService.rsaDecrypt(rsaDecryptText.value, rsaPrivateKey.value)
    if (response.data.success) {
      rsaDecryptOutput.value = response.data.result
    } else {
      ElMessage.error(response.data.error || '解密失败')
    }
  } catch (error) {
    ElMessage.error('解密失败：' + (error.message || '未知错误'))
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

.tool-input-group {
  margin-top: 12px;
}

.tool-hash-buttons {
  display: flex;
  gap: 8px;
  margin-top: 12px;
  flex-wrap: wrap;
}

.tool-hash-buttons .el-button {
  flex: 1;
  min-width: 0;
  margin-top: 0;
}
</style>

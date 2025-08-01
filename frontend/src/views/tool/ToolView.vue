<template>
  <div class="common-list-container">
    <el-tabs v-model="activeTab" type="border-card" class="tool-tabs">
      <!-- 编码/解码工具 -->
      <el-tab-pane label="编码/解码" name="encode">
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
            <el-input v-model="jwtTokenInput" type="textarea" :rows="3" placeholder="请输入 JWT Token，例如：eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNTE2MjM5MDIyfQ.SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c" />
            <div class="tool-flex-row">
              <el-input v-model="jwtSecretInput" placeholder="密钥（可选），例如：your-256-bit-secret" class="tool-flex-item" />
              <el-checkbox v-model="jwtVerify" class="tool-checkbox-item">验证签名</el-checkbox>
            </div>
            <el-button type="primary" @click="handleJwtDecode" class="tool-button">解析</el-button>
            <el-input v-model="jwtDecodeOutput" type="textarea" :rows="10" placeholder="解析结果（JSON格式）" class="tool-output" />
          </el-card>
        </div>
      </el-tab-pane>

      <!-- 格式转换工具 -->
      <el-tab-pane label="格式转换" name="format">
        <div class="tool-section">
          <h3>时间戳转换</h3>
          <el-row :gutter="20">
            <el-col :span="12">
              <el-card>
                <template #header>时间戳转日期时间</template>
                <el-input v-model="timestampInput" placeholder="请输入时间戳（秒或毫秒），例如：1609459200 或 1609459200000" />
                <el-input v-model="timestampFormat" placeholder="日期格式（如：%Y-%m-%d %H:%M:%S）" class="tool-input-group" />
                <el-button type="primary" @click="handleTimestampToDatetime" class="tool-button">转换</el-button>
                <el-input v-model="timestampToDatetimeOutput" placeholder="转换结果" class="tool-input-group" />
              </el-card>
            </el-col>
            <el-col :span="12">
              <el-card>
                <template #header>日期时间转时间戳</template>
                <el-input v-model="datetimeInput" placeholder="请输入日期时间，例如：2025-01-01 12:00:00" />
                <el-input v-model="datetimeFormat" placeholder="日期格式（如：%Y-%m-%d %H:%M:%S）" class="tool-input-group" />
                <el-button type="primary" @click="handleDatetimeToTimestamp" class="tool-button">转换</el-button>
                <el-input v-model="datetimeToTimestampOutput" placeholder="转换结果（时间戳）" class="tool-input-group" />
              </el-card>
            </el-col>
          </el-row>
        </div>
        
        <div class="tool-section">
          <h3>JSON 格式化</h3>
          <el-row :gutter="20">
            <el-col :span="12">
              <el-card>
                <template #header>JSON 格式化</template>
                <el-input v-model="jsonFormatInput" type="textarea" :rows="10" placeholder="请输入 JSON 文本，例如：{&quot;name&quot;:&quot;John&quot;,&quot;age&quot;:30,&quot;city&quot;:&quot;New York&quot;}" />
                <el-input-number v-model="jsonIndent" :min="0" :max="8" label="缩进空格数" class="tool-input-group" style="width: 100%;" />
                <el-button type="primary" @click="handleJsonFormat" class="tool-button">格式化</el-button>
                <div class="tool-output-placeholder"></div>
              </el-card>
            </el-col>
            <el-col :span="12">
              <el-card>
                <template #header>格式化结果</template>
                <el-input v-model="jsonFormatOutput" type="textarea" :rows="10" placeholder="格式化后的 JSON" />
                <div class="tool-input-group"></div>
                <el-button type="success" @click="handleJsonCompact" class="tool-button">压缩</el-button>
              </el-card>
            </el-col>
          </el-row>
        </div>

        <div class="tool-section">
          <h3>XML 转 JSON</h3>
          <el-row :gutter="20">
            <el-col :span="12">
              <el-card>
                <template #header>XML 输入</template>
                <el-input v-model="xmlInput" type="textarea" :rows="10" placeholder="请输入 XML 文本，例如：&lt;root&gt;&lt;name&gt;John&lt;/name&gt;&lt;age&gt;30&lt;/age&gt;&lt;/root&gt;" />
                <el-button type="primary" @click="handleXmlToJson" class="tool-button">转换</el-button>
                <div class="tool-output-placeholder"></div>
              </el-card>
            </el-col>
            <el-col :span="12">
              <el-card>
                <template #header>JSON 输出</template>
                <el-input v-model="xmlToJsonOutput" type="textarea" :rows="10" placeholder="转换后的 JSON" />
                <div class="tool-output-placeholder"></div>
              </el-card>
            </el-col>
          </el-row>
        </div>

        
      </el-tab-pane>

      <!-- 加密/解密工具 -->
      <el-tab-pane label="加密/解密" name="encrypt">
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
            <el-select v-model="hmacAlgorithm" placeholder="选择算法" class="tool-input-group" style="width: 100%;">
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
                <el-select v-model="aesMode" placeholder="加密模式" class="tool-input-group" style="width: 100%;">
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
                <el-select v-model="aesDecryptMode" placeholder="加密模式" class="tool-input-group" style="width: 100%;">
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
      </el-tab-pane>

      <!-- 文本处理工具 -->
      <el-tab-pane label="文本处理" name="text">
        <div class="tool-section">
          <h3>正则表达式测试</h3>
          <el-card>
            <el-input v-model="regexTextInput" type="textarea" :rows="5" placeholder="请输入要匹配的文本，例如：Hello 123 World 456" />
            <div class="tool-flex-row">
              <el-input v-model="regexPatternInput" placeholder="正则表达式模式，例如：\\d+" class="tool-flex-item" />
              <el-button type="primary" @click="handleRegexTest" class="tool-action-button">测试</el-button>
            </div>
            <el-alert v-if="regexResult.match_count !== undefined" 
                      :title="`找到 ${regexResult.match_count} 个匹配`" 
                      type="success" 
                      :closable="false"
                      class="tool-alert" />
            <el-input v-model="regexOutput" type="textarea" :rows="10" placeholder="匹配结果（JSON格式）" class="tool-output" />
          </el-card>
        </div>

        <div class="tool-section">
          <h3>文本对比</h3>
          <el-card>
            <el-row :gutter="20">
              <el-col :span="12">
                <el-input v-model="compareText1" type="textarea" :rows="8" placeholder="文本1，例如：Hello World" />
              </el-col>
              <el-col :span="12">
                <el-input v-model="compareText2" type="textarea" :rows="8" placeholder="文本2，例如：hello world" />
              </el-col>
            </el-row>
            <div class="tool-flex-row tool-compare-options">
              <el-checkbox v-model="ignoreCase">忽略大小写</el-checkbox>
              <el-checkbox v-model="ignoreWhitespace">忽略空白字符</el-checkbox>
              <el-button type="primary" @click="handleTextCompare" class="tool-action-button">对比</el-button>
            </div>
            <el-input v-model="compareOutput" type="textarea" :rows="5" placeholder="对比结果（JSON格式）" class="tool-output" />
          </el-card>
        </div>
      </el-tab-pane>
    </el-tabs>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import { ElMessage } from 'element-plus';
import toolService from '@/services/tool/toolService';

const activeTab = ref('encode');

// 编码/解码工具
const base64EncodeInput = ref('Hello World');
const base64EncodeOutput = ref('');
const base64DecodeInput = ref('SGVsbG8gV29ybGQ=');
const base64DecodeOutput = ref('');
const jwtTokenInput = ref('eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNTE2MjM5MDIyfQ.SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c');
const jwtSecretInput = ref('your-256-bit-secret');
const jwtVerify = ref(true);
const jwtDecodeOutput = ref('');

// 格式转换工具
const jsonFormatInput = ref('{"name":"John","age":30,"city":"New York"}');
const jsonFormatOutput = ref('');
const jsonIndent = ref(2);
const xmlInput = ref('<root><name>John</name><age>30</age><city>New York</city></root>');
const xmlToJsonOutput = ref('');
const timestampInput = ref('');
const timestampFormat = ref('%Y-%m-%d %H:%M:%S');
const timestampToDatetimeOutput = ref('');
const datetimeInput = ref('');
const datetimeFormat = ref('%Y-%m-%d %H:%M:%S');
const datetimeToTimestampOutput = ref('');

// 加密/解密工具
const hashInput = ref('Hello World');
const hashOutput = ref('');
const hmacTextInput = ref('Hello World');
const hmacKeyInput = ref('secret-key');
const hmacAlgorithm = ref('sha256');
const hmacOutput = ref('');
const aesEncryptText = ref('Hello World');
const aesEncryptKey = ref('1234567890123456');
const aesMode = ref('CBC');
const aesEncryptOutput = ref('');
const aesDecryptText = ref('');
const aesDecryptKey = ref('1234567890123456');
const aesDecryptMode = ref('CBC');
const aesDecryptOutput = ref('');
const rsaEncryptText = ref('Hello World');
const rsaPublicKey = ref('-----BEGIN PUBLIC KEY-----\nMIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEAyOuDbk8w9AqhRVb7\n...\n-----END PUBLIC KEY-----');
const rsaEncryptOutput = ref('');
const rsaDecryptText = ref('');
const rsaPrivateKey = ref('-----BEGIN PRIVATE KEY-----\nMIIEvQIBADANBgkqhkiG9w0BAQEFAASCBKcwggSjAgEAAoIBAQDI64tZpjvd\n...\n-----END PRIVATE KEY-----');
const rsaDecryptOutput = ref('');

// 文本处理工具
const regexTextInput = ref('Hello 123 World 456');
const regexPatternInput = ref('\\d+');
const regexOutput = ref('');
const regexResult = ref({});
const compareText1 = ref('Hello World');
const compareText2 = ref('hello world');
const ignoreCase = ref(false);
const ignoreWhitespace = ref(false);
const compareOutput = ref('');

// 编码/解码处理函数
const handleBase64Encode = async () => {
  if (!base64EncodeInput.value) {
    ElMessage.warning('请输入要编码的文本');
    return;
  }
  try {
    const response = await toolService.base64Encode(base64EncodeInput.value);
    if (response.data.success) {
      base64EncodeOutput.value = response.data.result;
    } else {
      ElMessage.error(response.data.error || '编码失败');
    }
  } catch (error) {
    ElMessage.error('编码失败：' + (error.message || '未知错误'));
  }
};

const handleBase64Decode = async () => {
  if (!base64DecodeInput.value) {
    ElMessage.warning('请输入要解码的文本');
    return;
  }
  try {
    const response = await toolService.base64Decode(base64DecodeInput.value);
    if (response.data.success) {
      base64DecodeOutput.value = response.data.result;
    } else {
      ElMessage.error(response.data.error || '解码失败');
    }
  } catch (error) {
    ElMessage.error('解码失败：' + (error.message || '未知错误'));
  }
};

const handleJwtDecode = async () => {
  if (!jwtTokenInput.value) {
    ElMessage.warning('请输入 JWT Token');
    return;
  }
  try {
    const response = await toolService.jwtDecode(jwtTokenInput.value, jwtSecretInput.value || null, jwtVerify.value);
    if (response.data.success) {
      jwtDecodeOutput.value = JSON.stringify(response.data.result, null, 2);
    } else {
      ElMessage.error(response.data.error || '解析失败');
      jwtDecodeOutput.value = '';
    }
  } catch (error) {
    ElMessage.error('解析失败：' + (error.message || '未知错误'));
  }
};

// 格式转换处理函数
const handleJsonFormat = async () => {
  if (!jsonFormatInput.value) {
    ElMessage.warning('请输入 JSON 文本');
    return;
  }
  try {
    const response = await toolService.jsonFormat(jsonFormatInput.value, jsonIndent.value);
    if (response.data.success) {
      jsonFormatOutput.value = response.data.result;
    } else {
      ElMessage.error(response.data.error || '格式化失败');
    }
  } catch (error) {
    ElMessage.error('格式化失败：' + (error.message || '未知错误'));
  }
};

const handleJsonCompact = async () => {
  if (!jsonFormatOutput.value) {
    ElMessage.warning('请先格式化 JSON');
    return;
  }
  try {
    const response = await toolService.jsonCompact(jsonFormatOutput.value);
    if (response.data.success) {
      jsonFormatOutput.value = response.data.result;
    } else {
      ElMessage.error(response.data.error || '压缩失败');
    }
  } catch (error) {
    ElMessage.error('压缩失败：' + (error.message || '未知错误'));
  }
};

const handleXmlToJson = async () => {
  if (!xmlInput.value) {
    ElMessage.warning('请输入 XML 文本');
    return;
  }
  try {
    const response = await toolService.xmlToJson(xmlInput.value);
    if (response.data.success) {
      xmlToJsonOutput.value = response.data.result;
    } else {
      ElMessage.error(response.data.error || '转换失败');
    }
  } catch (error) {
    ElMessage.error('转换失败：' + (error.message || '未知错误'));
  }
};

const handleTimestampToDatetime = async () => {
  if (!timestampInput.value) {
    ElMessage.warning('请输入时间戳');
    return;
  }
  try {
    const response = await toolService.timestampToDatetime(parseInt(timestampInput.value), timestampFormat.value);
    if (response.data.success) {
      timestampToDatetimeOutput.value = response.data.result;
    } else {
      ElMessage.error(response.data.error || '转换失败');
    }
  } catch (error) {
    ElMessage.error('转换失败：' + (error.message || '未知错误'));
  }
};

const handleDatetimeToTimestamp = async () => {
  if (!datetimeInput.value) {
    ElMessage.warning('请输入日期时间');
    return;
  }
  try {
    const response = await toolService.datetimeToTimestamp(datetimeInput.value, datetimeFormat.value);
    if (response.data.success) {
      datetimeToTimestampOutput.value = response.data.result.toString();
    } else {
      ElMessage.error(response.data.error || '转换失败');
    }
  } catch (error) {
    ElMessage.error('转换失败：' + (error.message || '未知错误'));
  }
};

// 格式化当前时间为字符串
const formatCurrentDateTime = () => {
  const now = new Date();
  const year = now.getFullYear();
  const month = String(now.getMonth() + 1).padStart(2, '0');
  const day = String(now.getDate()).padStart(2, '0');
  const hours = String(now.getHours()).padStart(2, '0');
  const minutes = String(now.getMinutes()).padStart(2, '0');
  const seconds = String(now.getSeconds()).padStart(2, '0');
  return `${year}-${month}-${day} ${hours}:${minutes}:${seconds}`;
};

// 获取当前时间戳（秒）
const getCurrentTimestamp = () => {
  return Math.floor(Date.now() / 1000);
};

// 初始化默认值
onMounted(() => {
  // 默认填写当前时间
  datetimeInput.value = formatCurrentDateTime();
  // 默认填写当前时间戳
  timestampInput.value = getCurrentTimestamp().toString();
});

// 加密/解密处理函数
const handleMd5Hash = async () => {
  if (!hashInput.value) {
    ElMessage.warning('请输入要哈希的文本');
    return;
  }
  try {
    const response = await toolService.md5Hash(hashInput.value);
    if (response.data.success) {
      hashOutput.value = response.data.result;
    } else {
      ElMessage.error(response.data.error || '计算失败');
    }
  } catch (error) {
    ElMessage.error('计算失败：' + (error.message || '未知错误'));
  }
};

const handleSha1Hash = async () => {
  if (!hashInput.value) {
    ElMessage.warning('请输入要哈希的文本');
    return;
  }
  try {
    const response = await toolService.sha1Hash(hashInput.value);
    if (response.data.success) {
      hashOutput.value = response.data.result;
    } else {
      ElMessage.error(response.data.error || '计算失败');
    }
  } catch (error) {
    ElMessage.error('计算失败：' + (error.message || '未知错误'));
  }
};

const handleSha256Hash = async () => {
  if (!hashInput.value) {
    ElMessage.warning('请输入要哈希的文本');
    return;
  }
  try {
    const response = await toolService.sha256Hash(hashInput.value);
    if (response.data.success) {
      hashOutput.value = response.data.result;
    } else {
      ElMessage.error(response.data.error || '计算失败');
    }
  } catch (error) {
    ElMessage.error('计算失败：' + (error.message || '未知错误'));
  }
};

const handleSha512Hash = async () => {
  if (!hashInput.value) {
    ElMessage.warning('请输入要哈希的文本');
    return;
  }
  try {
    const response = await toolService.sha512Hash(hashInput.value);
    if (response.data.success) {
      hashOutput.value = response.data.result;
    } else {
      ElMessage.error(response.data.error || '计算失败');
    }
  } catch (error) {
    ElMessage.error('计算失败：' + (error.message || '未知错误'));
  }
};

const handleHmacHash = async () => {
  if (!hmacTextInput.value || !hmacKeyInput.value) {
    ElMessage.warning('请输入文本和密钥');
    return;
  }
  try {
    const response = await toolService.hmacHash(hmacTextInput.value, hmacKeyInput.value, hmacAlgorithm.value);
    if (response.data.success) {
      hmacOutput.value = response.data.result;
    } else {
      ElMessage.error(response.data.error || '计算失败');
    }
  } catch (error) {
    ElMessage.error('计算失败：' + (error.message || '未知错误'));
  }
};

const handleAesEncrypt = async () => {
  if (!aesEncryptText.value || !aesEncryptKey.value) {
    ElMessage.warning('请输入明文和密钥');
    return;
  }
  try {
    const response = await toolService.aesEncrypt(aesEncryptText.value, aesEncryptKey.value, aesMode.value);
    if (response.data.success) {
      aesEncryptOutput.value = response.data.result;
    } else {
      ElMessage.error(response.data.error || '加密失败');
    }
  } catch (error) {
    ElMessage.error('加密失败：' + (error.message || '未知错误'));
  }
};

const handleAesDecrypt = async () => {
  if (!aesDecryptText.value || !aesDecryptKey.value) {
    ElMessage.warning('请输入密文和密钥');
    return;
  }
  try {
    const response = await toolService.aesDecrypt(aesDecryptText.value, aesDecryptKey.value, aesDecryptMode.value);
    if (response.data.success) {
      aesDecryptOutput.value = response.data.result;
    } else {
      ElMessage.error(response.data.error || '解密失败');
    }
  } catch (error) {
    ElMessage.error('解密失败：' + (error.message || '未知错误'));
  }
};

const handleRsaEncrypt = async () => {
  if (!rsaEncryptText.value || !rsaPublicKey.value) {
    ElMessage.warning('请输入明文和公钥');
    return;
  }
  try {
    const response = await toolService.rsaEncrypt(rsaEncryptText.value, rsaPublicKey.value);
    if (response.data.success) {
      rsaEncryptOutput.value = response.data.result;
    } else {
      ElMessage.error(response.data.error || '加密失败');
    }
  } catch (error) {
    ElMessage.error('加密失败：' + (error.message || '未知错误'));
  }
};

const handleRsaDecrypt = async () => {
  if (!rsaDecryptText.value || !rsaPrivateKey.value) {
    ElMessage.warning('请输入密文和私钥');
    return;
  }
  try {
    const response = await toolService.rsaDecrypt(rsaDecryptText.value, rsaPrivateKey.value);
    if (response.data.success) {
      rsaDecryptOutput.value = response.data.result;
    } else {
      ElMessage.error(response.data.error || '解密失败');
    }
  } catch (error) {
    ElMessage.error('解密失败：' + (error.message || '未知错误'));
  }
};

// 文本处理处理函数
const handleRegexTest = async () => {
  if (!regexPatternInput.value) {
    ElMessage.warning('请输入正则表达式');
    return;
  }
  try {
    const response = await toolService.regexTest(regexTextInput.value, regexPatternInput.value, 0);
    if (response.data.success) {
      regexResult.value = response.data;
      regexOutput.value = JSON.stringify(response.data, null, 2);
    } else {
      ElMessage.error(response.data.error || '测试失败');
      regexOutput.value = '';
    }
  } catch (error) {
    ElMessage.error('测试失败：' + (error.message || '未知错误'));
  }
};

const handleTextCompare = async () => {
  try {
    const response = await toolService.textCompare(compareText1.value, compareText2.value, ignoreCase.value, ignoreWhitespace.value);
    if (response.data.success) {
      compareOutput.value = JSON.stringify(response.data, null, 2);
    } else {
      ElMessage.error(response.data.error || '对比失败');
    }
  } catch (error) {
    ElMessage.error('对比失败：' + (error.message || '未知错误'));
  }
};
</script>

<style scoped>
.tool-tabs {
  background-color: transparent;
  box-shadow: none;
}

.tool-tabs :deep(.el-tabs__content) {
  padding: 16px 0;
}

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

.tool-section :deep(.el-button) {
  border-radius: 4px;
}

.tool-section :deep(.el-input) {
  border-radius: 4px;
}

.tool-section :deep(.el-select) {
  border-radius: 4px;
}

.tool-section :deep(.el-card__body > *) {
  margin-top: 12px;
}

.tool-section :deep(.el-card__body > *:first-child) {
  margin-top: 0;
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

.tool-input-group:first-child {
  margin-top: 0;
}

/* 新增布局优化样式 */
.tool-flex-row {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-top: 12px;
}

.tool-flex-row:first-child {
  margin-top: 0;
}

.tool-flex-item {
  flex: 1;
  margin-top: 0;
}

.tool-checkbox-item {
  white-space: nowrap;
  margin-top: 0;
}

.tool-action-button {
  white-space: nowrap;
  margin-top: 0;
  min-width: 80px;
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

.tool-compare-options {
  justify-content: space-between;
}

.tool-compare-options .el-checkbox {
  margin-top: 0;
}

.tool-alert {
  margin-top: 12px;
}

.tool-output-placeholder {
  height: 0;
  visibility: hidden;
}

/* 响应式设计 */
@media (max-width: 1200px) {
  .tool-tabs :deep(.el-tabs__content) {
    padding: 12px 0;
  }
  
  .tool-section {
    margin-bottom: 16px;
  }
  
  .tool-section :deep(.el-card__body) {
    padding: 14px;
  }
}

@media (max-width: 768px) {
  .tool-tabs :deep(.el-tabs__content) {
    padding: 8px 0;
  }
  
  .tool-section {
    margin-bottom: 16px;
  }
  
  .tool-section h3 {
    font-size: 14px;
    margin-bottom: 10px;
  }
  
  .tool-section :deep(.el-card__body) {
    padding: 12px;
  }
  
  .tool-section :deep(.el-card__header) {
    padding: 8px 12px;
    font-size: 13px;
  }
  
  .tool-flex-row {
    flex-direction: column;
    align-items: stretch;
    gap: 8px;
  }
  
  .tool-flex-item {
    width: 100%;
  }
  
  .tool-action-button {
    width: 100%;
    min-width: auto;
  }
  
  .tool-hash-buttons .el-button {
    flex: 1 1 calc(50% - 4px);
    min-width: calc(50% - 4px);
  }
  
  .tool-compare-options {
    flex-direction: column;
    align-items: stretch;
  }
  
  .tool-compare-options .el-button {
    width: 100%;
  }
}
</style>


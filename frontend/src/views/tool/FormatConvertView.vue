<template>
  <div class="common-list-container">
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
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import { ElMessage } from 'element-plus';
import toolService from '@/services/tool/toolService';

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

.tool-input-group {
  margin-top: 12px;
}

.tool-output-placeholder {
  height: 0;
  visibility: hidden;
}
</style>


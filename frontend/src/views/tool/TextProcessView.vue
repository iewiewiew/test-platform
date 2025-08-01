<template>
  <div class="common-list-container">
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
  </div>
</template>

<script setup>
import { ref } from 'vue';
import { ElMessage } from 'element-plus';
import toolService from '@/services/tool/toolService';

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

.tool-action-button {
  white-space: nowrap;
  min-width: 80px;
}

.tool-alert {
  margin-top: 12px;
}

.tool-compare-options {
  justify-content: space-between;
}

.tool-compare-options .el-checkbox {
  margin-top: 0;
}
</style>


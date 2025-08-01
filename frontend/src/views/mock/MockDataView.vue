<template>
  <div class="common-list-container">
    <!-- 错误提示 -->
    <el-alert
      v-if="error"
      :title="error"
      type="error"
      show-icon
      closable
      @close="clearError"
      class="error-alert"
    />

    <!-- 配置区域 -->
    <div class="config-section">
      <div class="section-header">
        <div class="action-buttons">
          <el-button @click="addField">
            <el-icon><Plus /></el-icon>
            添加字段
          </el-button>
          <el-form label-width="80px">
           <el-form-item label="生成条数">
            <el-input-number
              :model-value="count"
              @update:model-value="handleCountChange"
              :min="1"
              :max="1000"
              controls-position="right"
            />
           </el-form-item>
          </el-form>
          <el-button @click="resetFields"><el-icon><Refresh /></el-icon>重置</el-button>
          <el-button type="primary" @click="generateData" :loading="loading">生成数据</el-button>
        </div>
      </div>

      <!-- 字段配置表格 -->
      <div class="fields-table">
        <el-table :data="fields" border :key="tableKey">
          <el-table-column label="字段名" width="150">
            <template #default="{ $index }">
              <el-input
                :model-value="getFieldName($index)"
                @update:model-value="(value) => updateFieldName($index, value)"
                placeholder="请输入字段名"
                @blur="validateFieldName($index)"
              />
            </template>
          </el-table-column>

          <el-table-column label="字段类型" width="200">
            <template #default="{ $index }">
              <el-select
                :model-value="getFieldType($index)"
                @update:model-value="(value) => handleFieldTypeChange($index, value)"
                placeholder="请选择字段类型"
              >
                <el-option
                  v-for="type in fieldTypes"
                  :key="type.value"
                  :label="type.label"
                  :value="type.value"
                />
              </el-select>
            </template>
          </el-table-column>

          <el-table-column label="字段选项">
            <template #default="{ $index }">
              <FieldOptions
                :field-type="getFieldType($index)"
                :options="getFieldOptions($index)"
                @update="(newOptions) => updateFieldOptions($index, newOptions)"
              />
            </template>
          </el-table-column>

          <el-table-column label="操作" width="80">
            <template #default="{ $index }">
              <el-button type="danger" link @click="removeField($index)">
                删除
              </el-button>
            </template>
          </el-table-column>
        </el-table>
      </div>
    </div>

    <!-- 生成的数据展示 -->
    <div class="result-section" v-if="generatedData.length > 0">
      <div class="section-header">
        <h3>生成结果 (共 {{ generatedData.length }} 条)</h3>
        <div class="export-buttons">
          <el-button @click="exportData" type="success">
            <el-icon><Download /></el-icon>
            导出JSON
          </el-button>
          <el-button @click="exportCSV" type="warning">
            <el-icon><Document /></el-icon>
            导出CSV
          </el-button>
        </div>
      </div>

      <el-table :data="generatedData" border class="result-table">
        <el-table-column
          v-for="field in validFields"
          :key="field.id"
          :prop="field.name"
          :label="field.name"
          min-width="150"
        >
          <template #default="{ row }">
            {{ row[field.name] }}
          </template>
        </el-table-column>
      </el-table>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { ElMessage } from 'element-plus'
import { Plus, Refresh, Download, Document } from '@element-plus/icons-vue'
import { useMockDataStore } from '@/stores/mock/mockDataStore'
import FieldOptions from '@/components/mock/FieldOptions.vue'

const mockDataStore = useMockDataStore()
const tableKey = ref(0)

// 字段类型映射
const FIELD_NAME_MAPPING = {
  '姓名': 'name',
  '身份证号': 'id_card',
  '手机号': 'phone',
  '邮箱': 'email',
  '地址': 'address',
  '日期': 'date',
  '日期时间': 'datetime',
  '文本': 'text',
  '数字': 'number',
  '布尔值': 'boolean',
  '公司名称': 'company',
  '银行卡号': 'bank_card',
  '年龄': 'age',
  '省份': 'province',
  '城市': 'city',
  '邮编': 'postcode',
  '职业': 'job',
  '社保号': 'ssn',
  '车牌号': 'license_plate'
}

// 默认字段配置 - 前5个常用字段
const DEFAULT_FIELDS = [
  { name: 'name', type: 'name', options: {} },
  { name: 'phone', type: 'phone', options: {} },
  { name: 'email', type: 'email', options: {} },
  { name: 'address', type: 'address', options: {} },
  { name: 'age', type: 'age', options: {} }
]

// 计算属性
const fieldTypes = computed(() => mockDataStore.fieldTypes)
const fields = computed(() => mockDataStore.fields)
const generatedData = computed(() => mockDataStore.generatedData)
const count = computed(() => mockDataStore.count)
const loading = computed(() => mockDataStore.loading)
const error = computed(() => mockDataStore.error)

const validFields = computed(() => {
  return fields.value.filter(field => field.name && field.type)
})

// 字段操作方法
const getFieldName = (index) => fields.value[index]?.name || ''
const getFieldType = (index) => fields.value[index]?.type || ''
const getFieldOptions = (index) => fields.value[index]?.options || {}

const getFieldNameByType = (fieldType) => {
  const fieldTypeObj = fieldTypes.value.find(type => type.value === fieldType)
  return fieldTypeObj ? FIELD_NAME_MAPPING[fieldTypeObj.label] || fieldType : fieldType
}

const handleFieldTypeChange = (index, value) => {
  const currentField = fields.value[index]
  const shouldAutoFill = !currentField.name || 
                        currentField.name === getFieldNameByType(currentField.type)
  
  mockDataStore.updateField(index, { 
    type: value,
    options: {}
  })
  
  if (shouldAutoFill) {
    const fieldName = getFieldNameByType(value)
    mockDataStore.updateField(index, { name: fieldName })
  }
  
  forceTableUpdate()
}

// 字段管理
const addField = () => {
  mockDataStore.addField()
  forceTableUpdate()
}

const removeField = (index) => {
  mockDataStore.removeField(index)
  forceTableUpdate()
}

const updateFieldName = (index, value) => {
  mockDataStore.updateField(index, { name: value })
}

const updateFieldOptions = (index, options) => {
  mockDataStore.updateField(index, { options })
}

const handleCountChange = (value) => {
  mockDataStore.count = value
}

const clearError = () => {
  mockDataStore.error = null
}

const resetFields = () => {
  mockDataStore.resetFields()
  // 重置后重新添加默认字段
  setTimeout(() => {
    initializeDefaultFields()
  }, 0)
}

const validateFieldName = (index) => {
  const fieldName = getFieldName(index)
  if (fieldName && !/^[a-zA-Z_][a-zA-Z0-9_]*$/.test(fieldName)) {
    ElMessage.warning('字段名只能包含字母、数字和下划线，且不能以数字开头')
    mockDataStore.updateField(index, { name: '' })
  }
}

const forceTableUpdate = () => {
  tableKey.value += 1
}

// 初始化默认字段
const initializeDefaultFields = () => {
  DEFAULT_FIELDS.forEach(field => {
    mockDataStore.addField(field)
  })
  forceTableUpdate()
}

// 数据操作
const generateData = async () => {
  if (fields.value.length === 0) {
    ElMessage.warning('请至少添加一个字段')
    return
  }

  if (validFields.value.length === 0) {
    ElMessage.warning('请填写有效的字段名称和类型')
    return
  }

  const fieldNames = validFields.value.map(field => field.name)
  const uniqueNames = new Set(fieldNames)
  if (uniqueNames.size !== fieldNames.length) {
    ElMessage.warning('字段名称不能重复')
    return
  }

  await mockDataStore.generateMockData()
  if (!error.value) {
    ElMessage.success('数据生成成功')
  }
}

const exportData = () => {
  const dataStr = JSON.stringify(generatedData.value, null, 2)
  const dataBlob = new Blob([dataStr], { type: 'application/json' })
  const url = URL.createObjectURL(dataBlob)
  const link = document.createElement('a')
  link.href = url
  link.download = `mock_data_${new Date().getTime()}.json`
  link.click()
  URL.revokeObjectURL(url)
  ElMessage.success('数据导出成功')
}

// 导出CSV功能
const exportCSV = () => {
  if (generatedData.value.length === 0) {
    ElMessage.warning('没有数据可导出')
    return
  }

  try {
    // 获取表头
    const headers = validFields.value.map(field => field.name)
    
    // 构建CSV内容
    let csvContent = ''
    
    // 添加表头
    csvContent += headers.map(header => `"${header}"`).join(',') + '\n'
    
    // 添加数据行
    generatedData.value.forEach(row => {
      const rowData = headers.map(header => {
        // 处理特殊字符，确保CSV格式正确
        let cellValue = row[header] || ''
        // 将值转换为字符串
        cellValue = String(cellValue)
        // 转义引号，并用引号包围字段
        cellValue = cellValue.replace(/"/g, '""')
        // 如果值包含逗号、换行或引号，用引号包围
        if (cellValue.includes(',') || cellValue.includes('\n') || cellValue.includes('"')) {
          return `"${cellValue}"`
        }
        return cellValue
      })
      csvContent += rowData.join(',') + '\n'
    })
    
    // 创建Blob并下载
    const blob = new Blob(['\uFEFF' + csvContent], { type: 'text/csv;charset=utf-8;' })
    const url = URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url
    link.download = `mock_data_${new Date().getTime()}.csv`
    link.click()
    URL.revokeObjectURL(url)
    ElMessage.success('CSV导出成功')
  } catch (err) {
    console.error('导出CSV失败:', err)
    ElMessage.error('导出CSV失败，请重试')
  }
}

// 初始化
onMounted(async () => {
  await mockDataStore.fetchFieldTypes()
  if (fields.value.length === 0) {
    initializeDefaultFields()
  }
})
</script>

<style scoped>
.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  align-items: flex-start;
  margin-bottom: 20px;
  flex-wrap: wrap;
  gap: 20px;
}

.error-alert {
  margin-bottom: 0;
}

.config-section,
.result-section {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.action-buttons {
  display: flex;
  gap: 8px;
}

.export-buttons {
  display: flex;
  gap: 8px;
}

.count-config {
  max-width: 300px;
}

.fields-table,
.result-table {
  width: 100%;
}

.result-table {
  margin-top: 8px;
}
</style>
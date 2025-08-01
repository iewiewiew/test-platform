import { defineStore } from 'pinia'
import { ref } from 'vue'
import { mockDataService } from '@/services/mock/mockDataService'

export const useMockDataStore = defineStore('mockData', () => {
  // 状态
  const fieldTypes = ref([])
  const fields = ref([])
  const generatedData = ref([])
  const count = ref(5)
  const loading = ref(false)
  const error = ref(null)

  // 获取支持的字段类型
  const fetchFieldTypes = async () => {
    try {
      loading.value = true
      const response = await mockDataService.getFieldTypes()
      if (response.data.success) {
        fieldTypes.value = Object.entries(response.data.data).map(([value, label]) => ({
          value,
          label
        }))
      }
    } catch (err) {
      error.value = err.message
    } finally {
      loading.value = false
    }
  }

  // 添加字段
  const addField = (field = { name: '', type: '', options: {} }) => {
    const newField = {
      id: Date.now() + Math.random(),
      name: field.name || '',
      type: field.type || '',
      options: field.options || {}
    }
    fields.value.push(newField)
    return newField
  }

  // 删除字段
  const removeField = (index) => {
    if (index >= 0 && index < fields.value.length) {
      fields.value.splice(index, 1)
    }
  }

  // 更新字段 - 确保响应式更新
  const updateField = (index, fieldUpdate) => {
    if (index >= 0 && index < fields.value.length) {
      // 创建新对象以确保响应式更新
      const updatedField = {
        ...fields.value[index],
        ...fieldUpdate
      }
      fields.value[index] = updatedField
    }
  }

  // 生成模拟数据
  const generateMockData = async () => {
    try {
      loading.value = true
      error.value = null
      
      const validFields = fields.value.filter(field => field.name && field.type)
      
      if (validFields.length === 0) {
        error.value = '没有有效的字段配置'
        return
      }

      const payload = {
        fields: validFields.map(field => ({
          name: field.name,
          type: field.type,
          options: field.options
        })),
        count: count.value
      }

      const response = await mockDataService.generateMockData(payload)
      if (response.data.success) {
        generatedData.value = response.data.data
      } else {
        error.value = response.data.error || '生成数据失败'
      }
    } catch (err) {
      error.value = err.message
    } finally {
      loading.value = false
    }
  }

  // 清空生成的数据
  const clearGeneratedData = () => {
    generatedData.value = []
  }

  // 重置所有字段
  const resetFields = () => {
    fields.value = []
    generatedData.value = []
    error.value = null
    count.value = 5
  }

  return {
    // 状态
    fieldTypes,
    fields,
    generatedData,
    count,
    loading,
    error,
    
    // 方法
    fetchFieldTypes,
    addField,
    removeField,
    updateField,
    generateMockData,
    clearGeneratedData,
    resetFields
  }
})
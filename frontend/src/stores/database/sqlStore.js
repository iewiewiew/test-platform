import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { sqlService } from '@/services/database/sqlService'

export const useSQLStore = defineStore('sql', () => {
  // 状态
  const queryResult = ref(null)
  const executionTime = ref(0)
  const templates = ref([])
  const queryHistory = ref([])
  const loading = ref(false)
  const currentTemplate = ref(null)
  const categories = ref([])
  const error = ref(null)

  // Getter
  const categoriesOptions = computed(() => {
    console.log('categories getter:', categories.value)
    // 如果分类数据为空，尝试从模板数据中提取
    if (categories.value.length === 0 && templates.value.length > 0) {
      const uniqueCategories = [...new Set(templates.value.map(t => t.category))].filter(Boolean)
      console.log('从模板提取分类:', uniqueCategories)
      return uniqueCategories
    }
    return categories.value
  })
  
  const templatesByCategory = computed(() => {
    const grouped = {}
    templates.value.forEach(template => {
      if (!grouped[template.category]) {
        grouped[template.category] = []
      }
      grouped[template.category].push(template)
    })
    return grouped
  })

  const hasTemplates = computed(() => templates.value.length > 0)
  const hasCategories = computed(() => categoriesOptions.value.length > 0)

  // Actions
  const executeQuery = async (sqlQuery, limit = 1000, connectionId = null, databaseName = null) => {
    loading.value = true
    error.value = null
    try {
      const response = await sqlService.executeSQL(sqlQuery, limit, connectionId, databaseName)
      console.log("查询结果: ")
      console.log(response)
      if (response.success) {
        queryResult.value = response.data
        executionTime.value = response.execution_time
      } else {
        throw new Error(response.error)
      }
      await loadHistory()
      return response
    } catch (error) {
      error.value = error.message
      throw error
    } finally {
      loading.value = false
    }
  }

  const loadTemplates = async (params = {}) => {
    loading.value = true
    error.value = null
    try {
      console.log('开始加载模板数据...')
      const response = await sqlService.getTemplates(params)
      templates.value = response.data || []
      console.log('模板数据加载完成:', templates.value.length, '条记录')
      
      // 如果分类数据为空，从模板数据中提取分类
      if (categories.value.length === 0 && templates.value.length > 0) {
        const uniqueCategories = [...new Set(templates.value.map(t => t.category))].filter(Boolean)
        console.log('从模板数据提取分类:', uniqueCategories)
        categories.value = uniqueCategories
      }
      
      return response
    } catch (error) {
      console.error('加载模板失败:', error)
      error.value = error.message
      templates.value = []
      throw error
    } finally {
      loading.value = false
    }
  }

  const loadHistory = async (params = {}) => {
    loading.value = true
    error.value = null
    try {
      console.log('开始加载查询历史...')
      const response = await sqlService.getHistory(params)
      queryHistory.value = response.data || []
      console.log('查询历史加载完成:', queryHistory.value.length, '条记录')
      return response
    } catch (error) {
      console.error('加载历史失败:', error)
      error.value = error.message
      queryHistory.value = []
      throw error
    } finally {
      loading.value = false
    }
  }

  const loadCategories = async () => {
    loading.value = true
    error.value = null
    try {
      console.log('开始加载分类数据...')
      const response = await sqlService.getCategories()
      categories.value = response.data || []
      console.log('分类数据加载完成:', categories.value)
      
      // 如果API返回空，尝试从模板数据中提取
      if (categories.value.length === 0 && templates.value.length > 0) {
        const uniqueCategories = [...new Set(templates.value.map(t => t.category))].filter(Boolean)
        console.log('从模板数据提取分类作为备选:', uniqueCategories)
        categories.value = uniqueCategories
      }
      
      // 如果仍然为空，设置默认分类
      if (categories.value.length === 0) {
        categories.value = getDefaultCategories()
        console.log('使用默认分类:', categories.value)
      }
      
      return response
    } catch (error) {
      console.error('加载分类失败:', error)
      error.value = error.message
      
      // API失败时的备选方案
      if (templates.value.length > 0) {
        const uniqueCategories = [...new Set(templates.value.map(t => t.category))].filter(Boolean)
        categories.value = uniqueCategories
        console.log('API失败，使用模板提取的分类:', categories.value)
      } else {
        categories.value = getDefaultCategories()
        console.log('API失败，使用默认分类:', categories.value)
      }
      
      throw error
    } finally {
      loading.value = false
    }
  }

  const createTemplate = async (templateData) => {
    loading.value = true
    error.value = null
    try {
      console.log('创建模板:', templateData)
      const response = await sqlService.createTemplate(templateData)
      if (response.success) {
        // 重新加载模板和分类数据
        await loadTemplates()
        // await loadCategories()
      }
      return response
    } catch (error) {
      console.error('创建模板失败:', error)
      error.value = error.message
      throw error
    } finally {
      loading.value = false
    }
  }

  const updateTemplate = async (templateId, templateData) => {
    loading.value = true
    error.value = null
    try {
      console.log('更新模板:', templateId, templateData)
      const response = await sqlService.updateTemplate(templateId, templateData)
      if (response.success) {
        // 重新加载模板和分类数据
        await loadTemplates()
        await loadCategories()
      }
      return response
    } catch (error) {
      console.error('更新模板失败:', error)
      error.value = error.message
      throw error
    } finally {
      loading.value = false
    }
  }

  const deleteTemplate = async (templateId) => {
    loading.value = true
    error.value = null
    try {
      console.log('删除模板:', templateId)
      const response = await sqlService.deleteTemplate(templateId)
      if (response.success) {
        // 重新加载模板和分类数据
        await loadTemplates()
        await loadCategories()
      }
      return response
    } catch (error) {
      console.error('删除模板失败:', error)
      error.value = error.message
      throw error
    } finally {
      loading.value = false
    }
  }

  const batchDeleteHistory = async (historyIds) => {
    loading.value = true
    error.value = null
    try {
      console.log('批量删除历史记录:', historyIds)
      const response = await sqlService.deleteHistoryBatch(historyIds)
      if (response.success) {
        await loadHistory()
      }
      return response
    } catch (error) {
      console.error('批量删除历史记录失败:', error)
      error.value = error.message
      throw error
    } finally {
      loading.value = false
    }
  }

  const clearHistory = async () => {
    loading.value = true
    error.value = null
    try {
      console.log('清空历史记录')
      const response = await sqlService.clearHistory()
      if (response.success) {
        await loadHistory()
      }
      return response
    } catch (error) {
      console.error('清空历史记录失败:', error)
      error.value = error.message
      throw error
    } finally {
      loading.value = false
    }
  }

  const setCurrentTemplate = (template) => {
    currentTemplate.value = template
    console.log('设置当前模板:', template)
  }

  const clearError = () => {
    error.value = null
  }

  const clearQueryResult = () => {
    queryResult.value = null
    executionTime.value = 0
  }

  // 工具函数
  const getDefaultCategories = () => {
    return [
      '常用SQL模版1',
      '常用SQL模版2', 
      '其他'
    ]
  }

  const initializeData = async () => {
    try {
      console.log('初始化数据加载...')
      await loadTemplates()
      await loadCategories()
      await loadHistory()
      console.log('数据初始化完成')
    } catch (error) {
      console.error('数据初始化失败:', error)
    }
  }

  return {
    // 状态
    queryResult,
    executionTime,
    templates,
    queryHistory,
    loading,
    currentTemplate,
    categories,
    error,
    
    // Getter
    categoriesOptions,
    templatesByCategory,
    hasTemplates,
    hasCategories,
    
    // Actions
    executeQuery,
    loadTemplates,
    loadHistory,
    loadCategories,
    createTemplate,
    updateTemplate,
    deleteTemplate,
    batchDeleteHistory,
    clearHistory,
    setCurrentTemplate,
    clearError,
    clearQueryResult,
    initializeData
  }
})
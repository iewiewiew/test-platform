import { defineStore } from 'pinia'
import { testCaseService } from '@/services/test/testCaseService'

export const useTestCaseStore = defineStore('testCase', {
  state: () => ({
    testCases: [],
    currentTestCase: null,
    testResult: null,
    pagination: {
      currentPage: 1,
      pageSize: 10,
      total: 0,
      totalPages: 1
    },
    loading: false,
    error: null,
    searchKeyword: '',
    selectedEnvironment: null,
    selectedModuleName: null,
    moduleNames: [],
    componentNames: []
  }),

  actions: {
    // 解析测试用例
    async parseTestCases(directoryPath) {
      this.loading = true
      this.error = null
      try {
        const response = await testCaseService.parseTestCases(directoryPath)
        return response.data
      } catch (error) {
        this.error = error.response?.data?.error || error.message || '解析测试用例失败'
        throw error
      } finally {
        this.loading = false
      }
    },

    // 获取模块名称列表
    async fetchModuleNames() {
      try {
        const response = await testCaseService.getModuleNames()
        this.moduleNames = response.data || []
        return this.moduleNames
      } catch (error) {
        this.error = error.response?.data?.error || error.message || '获取模块名称列表失败'
        return []
      }
    },

    // 获取组件名称列表
    async fetchComponentNames() {
      try {
        const response = await testCaseService.getComponentNames()
        this.componentNames = response.data || []
        return this.componentNames
      } catch (error) {
        this.error = error.response?.data?.error || error.message || '获取组件名称列表失败'
        return []
      }
    },

    // 测试用例列表分页查询
    async fetchTestCases(params = {}) {
      this.loading = true
      this.error = null
      try {
        const response = await testCaseService.getTestCases({
          page: params.page || this.pagination.currentPage,
          per_page: params.pageSize || this.pagination.pageSize,
          search: params.search || this.searchKeyword,
          environment: params.environment || this.selectedEnvironment,
          module_name: params.module_name || this.selectedModuleName,
          component_name: params.component_name
        })

        this.testCases = response.data || []

        // 处理分页数据
        this.pagination = {
          currentPage: response.page || this.pagination.currentPage,
          pageSize: response.per_page || this.pagination.pageSize,
          total: response.total || 0,
          totalPages: Math.ceil((response.total || 0) / (response.per_page || 10))
        }
        
        return this.testCases
      } catch (error) {
        this.error = error.response?.data?.error || error.message || '获取测试用例列表失败'
        this.testCases = []
        throw error
      } finally {
        this.loading = false
      }
    },

    // 获取测试用例详情
    async fetchTestCase(id) {
      this.loading = true
      this.error = null
      try {
        const response = await testCaseService.getTestCase(id)
        this.currentTestCase = response?.data || null
        return this.currentTestCase
      } catch (error) {
        this.error = error.response?.data?.error || error.message || '获取测试用例详情失败'
        this.currentTestCase = null
        throw error
      } finally {
        this.loading = false
      }
    },

    // 执行测试用例
    async executeTestCase(id, options = {}) {
      this.loading = true
      this.error = null
      try {
        const response = await testCaseService.executeTestCase(id, options)
        this.testResult = response?.data || null
        return this.testResult
      } catch (error) {
        this.error = error.response?.data?.error || error.message || '执行测试用例失败'
        this.testResult = null
        throw error
      } finally {
        this.loading = false
      }
    },

    // 创建测试用例
    async createTestCase(data) {
      this.loading = true
      this.error = null
      try {
        const response = await testCaseService.createTestCase(data)
        await this.fetchTestCases({
          page: this.pagination.currentPage,
          pageSize: this.pagination.pageSize
        })
        return response.data
      } catch (error) {
        this.error = error.response?.data?.error || error.message || '创建测试用例失败'
        throw error
      } finally {
        this.loading = false
      }
    },

    // 更新测试用例
    async updateTestCase(id, data) {
      this.loading = true
      this.error = null
      try {
        const response = await testCaseService.updateTestCase(id, data)
        await this.fetchTestCases({
          page: this.pagination.currentPage,
          pageSize: this.pagination.pageSize
        })
        return response.data
      } catch (error) {
        this.error = error.response?.data?.error || error.message || '更新测试用例失败'
        throw error
      } finally {
        this.loading = false
      }
    },

    // 删除测试用例
    async deleteTestCase(id) {
      this.loading = true
      this.error = null
      try {
        await testCaseService.deleteTestCase(id)
        await this.fetchTestCases({
          page: this.pagination.currentPage,
          pageSize: this.pagination.pageSize
        })
      } catch (error) {
        this.error = error.response?.data?.error || error.message || '删除测试用例失败'
        throw error
      } finally {
        this.loading = false
      }
    },

    // 设置搜索关键词
    setSearchKeyword(keyword) {
      this.searchKeyword = keyword
    },

    // 设置选中的环境
    setSelectedEnvironment(environment) {
      this.selectedEnvironment = environment
    },

    // 设置选中的模块名称
    setSelectedModuleName(moduleName) {
      this.selectedModuleName = moduleName
    }
  }
})


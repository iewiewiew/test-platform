import { defineStore } from 'pinia'
import { testEnvironmentService } from '@/services/test/testEnvironmentService'

export const useTestEnvironmentStore = defineStore('testEnvironment', {
  state: () => ({
    testEnvironments: [],
    currentEnvironment: null,
    pagination: {
      currentPage: 1,
      pageSize: 10,
      total: 0,
      totalPages: 1
    },
    loading: false,
    error: null,
    searchKeyword: ''
  }),

  actions: {
    // 解析测试环境
    async parseTestEnvironments(configFile) {
      this.loading = true
      this.error = null
      try {
        const response = await testEnvironmentService.parseTestEnvironments(configFile)
        await this.fetchTestEnvironments()
        return response.data
      } catch (error) {
        this.error = error.response?.data?.error || error.message || '解析测试环境失败'
        throw error
      } finally {
        this.loading = false
      }
    },

    // 测试环境列表分页查询
    async fetchTestEnvironments(params = {}) {
      this.loading = true
      this.error = null
      try {
        const response = await testEnvironmentService.getTestEnvironments({
          page: params.page || this.pagination.currentPage,
          per_page: params.pageSize || this.pagination.pageSize,
          search: params.search || this.searchKeyword
        })

        this.testEnvironments = response.data || []

        // 处理分页数据
        this.pagination = {
          currentPage: response.page || this.pagination.currentPage,
          pageSize: response.per_page || this.pagination.pageSize,
          total: response.total || 0,
          totalPages: Math.ceil((response.total || 0) / (response.per_page || 10))
        }
        
        return this.testEnvironments
      } catch (error) {
        this.error = error.response?.data?.error || error.message || '获取测试环境列表失败'
        this.testEnvironments = []
        throw error
      } finally {
        this.loading = false
      }
    },

    // 获取所有测试环境（用于下拉选择）
    async fetchTestEnvironmentsForSelect() {
      try {
        const response = await testEnvironmentService.getTestEnvironmentsForSelect()
        return response.data || []
      } catch (error) {
        this.error = error.response?.data?.error || error.message || '获取测试环境列表失败'
        return []
      }
    },

    // 获取测试环境详情
    async fetchTestEnvironment(id) {
      this.loading = true
      this.error = null
      try {
        const response = await testEnvironmentService.getTestEnvironment(id)
        this.currentEnvironment = response?.data || null
        return this.currentEnvironment
      } catch (error) {
        this.error = error.response?.data?.error || error.message || '获取测试环境详情失败'
        this.currentEnvironment = null
        throw error
      } finally {
        this.loading = false
      }
    },

    // 创建测试环境
    async createTestEnvironment(environmentData) {
      this.loading = true
      this.error = null
      try {
        const response = await testEnvironmentService.createTestEnvironment(environmentData)
        await this.fetchTestEnvironments({
          page: this.pagination.currentPage,
          pageSize: this.pagination.pageSize
        })
        return response?.data
      } catch (error) {
        this.error = error.response?.data?.error || error.message || '创建测试环境失败'
        throw error
      } finally {
        this.loading = false
      }
    },

    // 更新测试环境
    async updateTestEnvironment(id, environmentData) {
      this.loading = true
      this.error = null
      try {
        const response = await testEnvironmentService.updateTestEnvironment(id, environmentData)
        this.currentEnvironment = response?.data || null
        await this.fetchTestEnvironments({
          page: this.pagination.currentPage,
          pageSize: this.pagination.pageSize
        })
        return response?.data
      } catch (error) {
        this.error = error.response?.data?.error || error.message || '更新测试环境失败'
        throw error
      } finally {
        this.loading = false
      }
    },

    // 删除测试环境
    async deleteTestEnvironment(id) {
      this.loading = true
      this.error = null
      try {
        await testEnvironmentService.deleteTestEnvironment(id)
        await this.fetchTestEnvironments({
          page: this.pagination.currentPage,
          pageSize: this.pagination.pageSize
        })
      } catch (error) {
        this.error = error.response?.data?.error || error.message || '删除测试环境失败'
        throw error
      } finally {
        this.loading = false
      }
    },

    // 设置搜索关键词
    setSearchKeyword(keyword) {
      this.searchKeyword = keyword
    }
  }
})


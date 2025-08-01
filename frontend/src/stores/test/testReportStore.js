import { defineStore } from 'pinia'
import { testReportService } from '@/services/test/testReportService'

export const useTestReportStore = defineStore('testReport', {
  state: () => ({
    testReports: [],
    currentReport: null,
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
    // 解析测试报告
    async parseTestReports(reportDir) {
      this.loading = true
      this.error = null
      try {
        const response = await testReportService.parseTestReports(reportDir)
        return response.data
      } catch (error) {
        this.error = error.response?.data?.error || error.message || '解析测试报告失败'
        throw error
      } finally {
        this.loading = false
      }
    },

    // 测试报告列表分页查询
    async fetchTestReports(params = {}) {
      this.loading = true
      this.error = null
      try {
        const response = await testReportService.getTestReports({
          page: params.page || this.pagination.currentPage,
          per_page: params.pageSize || this.pagination.pageSize,
          search: params.search || this.searchKeyword
        })

        this.testReports = response.data || []

        // 处理分页数据
        this.pagination = {
          currentPage: response.page || this.pagination.currentPage,
          pageSize: response.per_page || this.pagination.pageSize,
          total: response.total || 0,
          totalPages: Math.ceil((response.total || 0) / (response.per_page || 10))
        }
        
        return this.testReports
      } catch (error) {
        this.error = error.response?.data?.error || error.message || '获取测试报告列表失败'
        this.testReports = []
        throw error
      } finally {
        this.loading = false
      }
    },

    // 获取测试报告详情
    async fetchTestReport(id, parse = false) {
      this.loading = true
      this.error = null
      try {
        const response = await testReportService.getTestReport(id, parse)
        this.currentReport = response?.data || null
        return this.currentReport
      } catch (error) {
        this.error = error.response?.data?.error || error.message || '获取测试报告详情失败'
        this.currentReport = null
        throw error
      } finally {
        this.loading = false
      }
    },

    // 解析测试报告
    async parseTestReport(id) {
      this.loading = true
      this.error = null
      try {
        const response = await testReportService.parseTestReport(id)
        this.currentReport = response?.data || null
        return this.currentReport
      } catch (error) {
        this.error = error.response?.data?.error || error.message || '解析测试报告失败'
        throw error
      } finally {
        this.loading = false
      }
    },

    // 删除测试报告
    async deleteTestReport(id) {
      this.loading = true
      this.error = null
      try {
        await testReportService.deleteTestReport(id)
        await this.fetchTestReports({
          page: this.pagination.currentPage,
          pageSize: this.pagination.pageSize
        })
      } catch (error) {
        this.error = error.response?.data?.error || error.message || '删除测试报告失败'
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


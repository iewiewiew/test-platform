import { defineStore } from 'pinia'
import { exampleService } from '@/services/tool/exampleService'

export const useExampleStore = defineStore('example', {
  state: () => ({
    examples: [], // 确保初始值为空数组
    currentExample: null,
    pagination: {
      currentPage: 1,
      pageSize: 10,
      total: 0,
      totalPages: 1
    },
    loading: false,
    error: null
  }),

  actions: {
    // 示例列表分页查询
    async fetchExamples(params = {}) {
      this.loading = true
      this.error = null
      try {
        const response = await exampleService.getExamples({
          page: params.page || this.pagination.currentPage,
          per_page: params.pageSize || this.pagination.pageSize,
          name: params.name,
          status: params.status,
          sort: params.sort,
          order: params.order
        })

        console.log("示例数据: ", response.data.data)
        this.examples = response.data.data

        // 处理分页数据
        const paginationData = response?.data || {}
        this.pagination = {
          currentPage: paginationData.current_page || params.page || this.pagination.currentPage,
          pageSize: params.pageSize || this.pagination.pageSize,
          total: paginationData.total || 0,
          totalPages: paginationData.pages || 1
        }
        
        return this.examples
      } catch (error) {
        this.error = error.response?.data?.message || error.message || '获取示例列表失败'
        this.examples = [] // 出错时确保是空数组
        throw error
      } finally {
        this.loading = false
      }
    },

    // 获取示例详情
    async fetchExample(id) {
      this.loading = true
      this.error = null
      try {
        const response = await exampleService.getExample(id)
        this.currentExample = response?.data.data || null
        return this.currentExample
      } catch (error) {
        this.error = error.response?.data?.message || error.message || '获取示例详情失败'
        this.currentExample = null
        throw error
      } finally {
        this.loading = false
      }
    },

    // 创建示例
    async createExample(exampleData) {
      this.loading = true
      this.error = null
      try {
        const response = await exampleService.createExample(exampleData)
        await this.fetchExamples({
          page: this.pagination.currentPage,
          pageSize: this.pagination.pageSize
        })
        return response?.data
      } catch (error) {
        this.error = error.response?.data?.message || error.message || '创建示例失败'
        throw error
      } finally {
        this.loading = false
      }
    },

    // 更新示例
    async updateExample(id, exampleData) {
      this.loading = true
      this.error = null
      try {
        const response = await exampleService.updateExample(id, exampleData)
        this.currentExample = response?.data || null
        await this.fetchExamples({
          page: this.pagination.currentPage,
          pageSize: this.pagination.pageSize
        })
        return this.currentExample
      } catch (error) {
        this.error = error.response?.data?.message || error.message || '更新示例失败'
        throw error
      } finally {
        this.loading = false
      }
    },

    // 删除示例
    async deleteExample(id) {
      this.loading = true
      this.error = null
      try {
        await exampleService.deleteExample(id)
        
        if (this.currentExample?.id === id) {
          this.currentExample = null
        }
        
        await this.fetchExamples({
          page: this.examples.length === 1 && this.pagination.currentPage > 1
            ? this.pagination.currentPage - 1
            : this.pagination.currentPage,
          pageSize: this.pagination.pageSize
        })
      } catch (error) {
        this.error = error.response?.data?.message || error.message || '删除示例失败'
        throw error
      } finally {
        this.loading = false
      }
    },

    // 批量删除示例
    async batchDeleteExamples(ids) {
      this.loading = true
      this.error = null
      try {
        const response = await exampleService.batchDeleteExamples(ids)
        
        // 清除当前选中的示例（如果被删除）
        if (this.currentExample && ids.includes(this.currentExample.id)) {
          this.currentExample = null
        }
        
        // 判断是否需要跳转到上一页（如果当前页数据全部被删除）
        const currentPageCount = this.examples.length
        const deletedCount = response?.data?.data?.success_count || ids.length
        const shouldGoToPreviousPage = currentPageCount <= deletedCount && this.pagination.currentPage > 1
        
        await this.fetchExamples({
          page: shouldGoToPreviousPage ? this.pagination.currentPage - 1 : this.pagination.currentPage,
          pageSize: this.pagination.pageSize
        })
        
        return response?.data
      } catch (error) {
        this.error = error.response?.data?.message || error.message || '批量删除示例失败'
        throw error
      } finally {
        this.loading = false
      }
    },

    // 搜索示例
    async searchExamples(query) {
      return this.fetchExamples({
        page: 1,
        name: query
      })
    },

    // 改变页码
    async changePage(page) {
      return this.fetchExamples({
        page: page,
        pageSize: this.pagination.pageSize
      })
    },

    // 改变每页大小
    async changePageSize(size) {
      return this.fetchExamples({
        page: 1,
        pageSize: size
      })
    },

    // 清除错误
    clearError() {
      this.error = null
    },

    // 清除当前选中的示例
    clearCurrentExample() {
      this.currentExample = null
    },

    // 静默获取示例列表（不更新loading状态，不更新store状态，仅返回数据）
    // 用于需要获取数据但不影响UI的场景，如全选所有页时获取所有ID
    async fetchExamplesSilently(params = {}) {
      try {
        const response = await exampleService.getExamples({
          page: params.page || this.pagination.currentPage,
          per_page: params.pageSize || this.pagination.pageSize,
          name: params.name,
          status: params.status,
          sort: params.sort,
          order: params.order
        })
        return response.data.data || []
      } catch (error) {
        console.error('静默获取示例列表失败:', error)
        return []
      }
    }
  }
})
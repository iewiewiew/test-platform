import { defineStore } from 'pinia'
import { mockService } from '@/services/mock/mockService'

export const useMockStore = defineStore('mock', {
  state: () => ({
    mocks: [],
    currentMock: null,
    pagination: {
      currentPage: 1,
      pageSize: 10,
      total: 0
    },
    loading: false,
    error: null
  }),

  actions: {
    async fetchMocks(params = {}) {
      this.loading = true
      this.error = null
      try {
        const response = await mockService.getMocks({
          page: params.page || this.pagination.currentPage,
          per_page: params.pageSize || this.pagination.pageSize,
          name: params.name,
          path: params.path,
          method: params.method,
          project_id: params.project_id
        })

        this.mocks = response.data
        this.pagination = {
          currentPage: params.page || this.pagination.currentPage,
          pageSize: params.pageSize || this.pagination.pageSize,
          total: response.total
        }
      } catch (error) {
        this.error = error.message || 'Failed to fetch mocks'
        throw error
      } finally {
        this.loading = false
      }
    },

    async fetchMock(id) {
      this.loading = true
      try {
        const response = await mockService.getMock(id)
        this.currentMock = response.data
      } catch (error) {
        this.error = error.message || 'Failed to fetch mock'
        throw error
      } finally {
        this.loading = false
      }
    },

    async createMock(mockData) {
      try {
        const response = await mockService.createMock(mockData)
        await this.fetchMocks({
          page: this.pagination.currentPage,
          pageSize: this.pagination.pageSize
        })
        return response.data
      } catch (error) {
        this.error = error.message || 'Failed to create mock'
        throw error
      }
    },

    async updateMock(id, mockData) {
      try {
        const response = await mockService.updateMock(id, mockData)
        await this.fetchMocks({
          page: this.pagination.currentPage,
          pageSize: this.pagination.pageSize
        })
        this.currentMock = null
        return response.data
      } catch (error) {
        this.error = error.message || 'Failed to update mock'
        throw error
      }
    },

    async deleteMock(id) {
      try {
        await mockService.deleteMock(id)
        if (this.currentMock?.id === id) {
          this.currentMock = null
        }
        await this.fetchMocks({
          page: this.mocks.length === 1 && this.pagination.currentPage > 1
            ? this.pagination.currentPage - 1
            : this.pagination.currentPage,
          pageSize: this.pagination.pageSize
        })
      } catch (error) {
        this.error = error.message || 'Failed to delete mock'
        throw error
      }
    },

    async generateCurlCommand(params) {
      try {
        if (!params || typeof params !== 'object') {
          throw new Error('参数必须为对象');
        }
    
        const apiPath = (params.api_path && typeof params.api_path === 'string')
          ? params.api_path.replace(/^\/+/, '').replace(/\/+/g, '/')
          : '';
    
        if (!apiPath) {
          throw new Error('缺少有效的API路径');
        }
    
        const method = (params.method && typeof params.method === 'string')
          ? params.method.toUpperCase()
          : 'GET';
    
        const response = await mockService.generateCurlCommand(`/${apiPath}`, {
          params: { method }
        });
    
        if (!response.data?.curl_command) {
          throw new Error('无效的响应格式');
        }
    
        return response.data;
      } catch (error) {
        console.error('生成CURL失败:', error);
        throw new Error(error.response?.data?.message || error.message);
      }
    }
  }
})
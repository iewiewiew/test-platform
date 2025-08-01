import { defineStore } from 'pinia'
import { environmentService } from '@/services/project/environmentService'

export const useEnvironmentStore = defineStore('environment', {
  state: () => ({
    environments: [],
    currentEnvironment: null,
    parameters: [],
    pagination: {
      currentPage: 1,
      pageSize: 10,
      total: 0
    },
    parameterPagination: {
      currentPage: 1,
      pageSize: 10,
      total: 0
    },
    loading: false,
    error: null,
    searchQuery: '',
    parameterSearchQuery: ''
  }),

  getters: {
    /**
     * 获取当前环境的参数数量
     */
    currentEnvironmentParameterCount: (state) => {
      return state.currentEnvironment?.parameter_count || 0
    },

    /**
     * 获取活跃的环境列表（未删除的）
     */
    activeEnvironments: (state) => {
      return state.environments.filter(env => !env.is_deleted)
    },

    /**
     * 获取环境的参数键值对映射
     */
    environmentParametersMap: (state) => {
      const map = {}
      state.parameters.forEach(param => {
        if (!param.is_deleted) {
          map[param.param_key] = param.param_value
        }
      })
      return map
    },

    /**
     * 获取环境名称映射（用于下拉选择）
     */
    environmentNameMap: (state) => {
      const map = {}
      state.environments.forEach(env => {
        if (!env.is_deleted) {
          map[env.id] = env.name
        }
      })
      return map
    },

    /**
     * 获取简化的环境列表（用于下拉选择）
     */
    environmentOptions: (state) => {
      return state.environments
        .filter(env => !env.is_deleted)
        .map(env => ({
          value: env.id,
          label: env.name,
          base_url: env.base_url
        }))
    }
  },

  actions: {
    /**
     * 获取环境列表
     */
    async fetchEnvironments(params = {}) {
      this.loading = true
      this.error = null
      try {
        const response = await environmentService.getEnvironments({
          page: params.page || this.pagination.currentPage,
          per_page: params.pageSize || this.pagination.pageSize,
          search: params.search || this.searchQuery,
          project_id: params.project_id
        })

        this.environments = response.data
        this.pagination = {
          currentPage: params.page || this.pagination.currentPage,
          pageSize: params.pageSize || this.pagination.pageSize,
          total: response.total
        }

        // 更新搜索查询
        if (params.search !== undefined) {
          this.searchQuery = params.search
        }
      } catch (error) {
        this.error = error.message || '获取环境列表失败'
        throw error
      } finally {
        this.loading = false
      }
    },

    /**
     * 获取环境详情
     */
    async fetchEnvironment(id) {
      this.loading = true
      try {
        const response = await environmentService.getEnvironment(id)
        this.currentEnvironment = response.data
        return response.data
      } catch (error) {
        this.error = error.message || '获取环境详情失败'
        throw error
      } finally {
        this.loading = false
      }
    },

    /**
     * 创建环境
     */
    async createEnvironment(environmentData) {
      try {
        const response = await environmentService.createEnvironment(environmentData)
        await this.fetchEnvironments({
          page: this.pagination.currentPage,
          pageSize: this.pagination.pageSize,
          search: this.searchQuery
        })
        return response.data
      } catch (error) {
        this.error = error.message || '创建环境失败'
        throw error
      }
    },

    /**
     * 更新环境
     */
    async updateEnvironment(id, environmentData) {
      try {
        const response = await environmentService.updateEnvironment(id, environmentData)
        await this.fetchEnvironments({
          page: this.pagination.currentPage,
          pageSize: this.pagination.pageSize,
          search: this.searchQuery
        })
        
        // 如果更新的是当前环境，则更新当前环境数据
        if (this.currentEnvironment?.id === id) {
          this.currentEnvironment = { ...this.currentEnvironment, ...environmentData }
        }
        
        return response.data
      } catch (error) {
        this.error = error.message || '更新环境失败'
        throw error
      }
    },

    /**
     * 删除环境
     */
    async deleteEnvironment(id) {
      try {
        await environmentService.deleteEnvironment(id)
        
        // 如果删除的是当前环境，则清空当前环境
        if (this.currentEnvironment?.id === id) {
          this.currentEnvironment = null
        }
        
        // 重新获取环境列表，处理分页逻辑
        await this.fetchEnvironments({
          page: this.environments.length === 1 && this.pagination.currentPage > 1
            ? this.pagination.currentPage - 1
            : this.pagination.currentPage,
          pageSize: this.pagination.pageSize,
          search: this.searchQuery
        })
      } catch (error) {
        this.error = error.message || '删除环境失败'
        throw error
      }
    },

    /**
     * 复制环境
     */
    async copyEnvironment(id, newName) {
      try {
        const response = await environmentService.copyEnvironment(id, newName)
        await this.fetchEnvironments({
          page: this.pagination.currentPage,
          pageSize: this.pagination.pageSize,
          search: this.searchQuery
        })
        return response.data
      } catch (error) {
        this.error = error.message || '复制环境失败'
        throw error
      }
    },

    /**
     * 获取环境参数列表
     */
    async fetchEnvironmentParameters(environmentId, params = {}) {
      this.loading = true
      this.error = null
      try {
        const response = await environmentService.getEnvironmentParameters(environmentId, {
          page: params.page || this.parameterPagination.currentPage,
          per_page: params.pageSize || this.parameterPagination.pageSize,
          search: params.search || this.parameterSearchQuery
        })

        this.parameters = response.data
        this.parameterPagination = {
          currentPage: params.page || this.parameterPagination.currentPage,
          pageSize: params.pageSize || this.parameterPagination.pageSize,
          total: response.total
        }

        // 更新参数搜索查询
        if (params.search !== undefined) {
          this.parameterSearchQuery = params.search
        }

        return response
      } catch (error) {
        this.error = error.message || '获取环境参数失败'
        throw error
      } finally {
        this.loading = false
      }
    },

    /**
     * 创建环境参数
     */
    async createEnvironmentParameter(environmentId, parameterData) {
      try {
        const response = await environmentService.createEnvironmentParameter(environmentId, parameterData)
        
        // 重新获取参数列表
        await this.fetchEnvironmentParameters(environmentId, {
          page: this.parameterPagination.currentPage,
          pageSize: this.parameterPagination.pageSize,
          search: this.parameterSearchQuery
        })
        
        // 更新当前环境的参数计数
        if (this.currentEnvironment?.id === environmentId) {
          this.currentEnvironment.parameter_count = this.parameterPagination.total
        }
        
        return response.data
      } catch (error) {
        this.error = error.message || '创建环境参数失败'
        throw error
      }
    },

    /**
     * 更新环境参数
     */
    async updateEnvironmentParameter(parameterId, parameterData) {
      try {
        const response = await environmentService.updateEnvironmentParameter(parameterId, parameterData)
        
        // 重新获取参数列表
        if (this.currentEnvironment) {
          await this.fetchEnvironmentParameters(this.currentEnvironment.id, {
            page: this.parameterPagination.currentPage,
            pageSize: this.parameterPagination.pageSize,
            search: this.parameterSearchQuery
          })
        }
        
        return response.data
      } catch (error) {
        this.error = error.message || '更新环境参数失败'
        throw error
      }
    },

    /**
     * 删除环境参数
     */
    async deleteEnvironmentParameter(parameterId) {
      try {
        await environmentService.deleteEnvironmentParameter(parameterId)
        
        // 重新获取参数列表
        if (this.currentEnvironment) {
          await this.fetchEnvironmentParameters(this.currentEnvironment.id, {
            page: this.parameters.length === 1 && this.parameterPagination.currentPage > 1
              ? this.parameterPagination.currentPage - 1
              : this.parameterPagination.currentPage,
            pageSize: this.parameterPagination.pageSize,
            search: this.parameterSearchQuery
          })
          
          // 更新当前环境的参数计数
          this.currentEnvironment.parameter_count = this.parameterPagination.total
        }
      } catch (error) {
        this.error = error.message || '删除环境参数失败'
        throw error
      }
    },

    /**
     * 批量操作环境
     */
    async batchEnvironments(operation, environmentIds) {
      try {
        const response = await environmentService.batchEnvironments(operation, environmentIds)
        
        // 重新获取环境列表
        await this.fetchEnvironments({
          page: this.pagination.currentPage,
          pageSize: this.pagination.pageSize,
          search: this.searchQuery
        })
        
        return response.data
      } catch (error) {
        this.error = error.message || '批量操作失败'
        throw error
      }
    },

    /**
     * 验证环境配置
     */
    async validateEnvironment(environmentData) {
      try {
        const response = await environmentService.validateEnvironment(environmentData)
        return response.data
      } catch (error) {
        this.error = error.message || '环境配置验证失败'
        throw error
      }
    },

    /**
     * 检查环境名称是否可用
     */
    async checkEnvironmentName(name, projectId = null) {
      try {
        const result = await environmentService.checkEnvironmentName(name, projectId)
        return result
      } catch (error) {
        this.error = error.message || '检查环境名称失败'
        throw error
      }
    },

    /**
     * 获取环境统计信息
     */
    async fetchEnvironmentStats(environmentId) {
      try {
        const response = await environmentService.getEnvironmentStats(environmentId)
        return response.data
      } catch (error) {
        this.error = error.message || '获取环境统计信息失败'
        throw error
      }
    },

    /**
     * 搜索环境
     */
    async searchEnvironments(params = {}) {
      this.loading = true
      this.error = null
      try {
        const response = await environmentService.searchEnvironments({
          type: params.type || 'all',
          keyword: params.keyword || '',
          project_id: params.project_id,
          page: params.page || this.pagination.currentPage,
          per_page: params.pageSize || this.pagination.pageSize
        })

        this.environments = response.data
        this.pagination = {
          currentPage: params.page || this.pagination.currentPage,
          pageSize: params.pageSize || this.pagination.pageSize,
          total: response.total
        }

        return response
      } catch (error) {
        this.error = error.message || '搜索环境失败'
        throw error
      } finally {
        this.loading = false
      }
    },

    /**
     * 清空错误信息
     */
    clearError() {
      this.error = null
    },

    /**
     * 清空当前环境
     */
    clearCurrentEnvironment() {
      this.currentEnvironment = null
    },

    /**
     * 清空参数列表
     */
    clearParameters() {
      this.parameters = []
      this.parameterPagination = {
        currentPage: 1,
        pageSize: 10,
        total: 0
      }
      this.parameterSearchQuery = ''
    },

    /**
     * 设置当前环境
     */
    setCurrentEnvironment(environment) {
      this.currentEnvironment = environment
    },

    /**
     * 更新分页信息
     */
    updatePagination(page, pageSize) {
      this.pagination.currentPage = page
      this.pagination.pageSize = pageSize
    },

    /**
     * 更新参数分页信息
     */
    updateParameterPagination(page, pageSize) {
      this.parameterPagination.currentPage = page
      this.parameterPagination.pageSize = pageSize
    }
  }
})
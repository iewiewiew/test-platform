import { defineStore } from 'pinia'
import { scriptManagementService } from '@/services/tool/scriptManagementService'

export const useScriptManagementStore = defineStore('scriptManagement', {
  state: () => ({
    scripts: [],
    currentScript: null,
    executionHistory: [], // 仅用于存储最新执行记录（用于查看功能）
    currentExecution: null,
    pagination: {
      currentPage: 1,
      pageSize: 20,
      total: 0
    },
    loading: false,
    executing: false,
    error: null
  }),

  actions: {
    /**
     * 获取脚本列表
     */
    async fetchScripts(params = {}) {
      this.loading = true
      this.error = null
      try {
        const response = await scriptManagementService.getScripts({
          page: params.page || this.pagination.currentPage,
          per_page: params.per_page || this.pagination.pageSize,
          name: params.name,
          script_type: params.script_type
        })

        this.scripts = response.data.data || []
        this.pagination = {
          currentPage: response.data.page || this.pagination.currentPage,
          pageSize: response.data.per_page || this.pagination.pageSize,
          total: response.data.total || 0
        }
        return response.data
      } catch (error) {
        this.error = error.response?.data?.error || error.message || '获取脚本列表失败'
        throw error
      } finally {
        this.loading = false
      }
    },

    /**
     * 获取脚本详情
     */
    async fetchScriptById(id) {
      this.loading = true
      this.error = null
      try {
        const response = await scriptManagementService.getScriptById(id)
        this.currentScript = response.data
        return response.data
      } catch (error) {
        this.error = error.response?.data?.error || error.message || '获取脚本详情失败'
        throw error
      } finally {
        this.loading = false
      }
    },

    /**
     * 创建脚本
     */
    async createScript(scriptData) {
      this.loading = true
      this.error = null
      try {
        const response = await scriptManagementService.createScript(scriptData)
        await this.fetchScripts({
          page: this.pagination.currentPage,
          per_page: this.pagination.pageSize
        })
        return response.data
      } catch (error) {
        this.error = error.response?.data?.error || error.message || '创建脚本失败'
        throw error
      } finally {
        this.loading = false
      }
    },

    /**
     * 更新脚本
     */
    async updateScript(id, scriptData) {
      this.loading = true
      this.error = null
      try {
        const response = await scriptManagementService.updateScript(id, scriptData)
        await this.fetchScripts({
          page: this.pagination.currentPage,
          per_page: this.pagination.pageSize
        })
        if (this.currentScript && this.currentScript.id === id) {
          this.currentScript = response.data
        }
        return response.data
      } catch (error) {
        this.error = error.response?.data?.error || error.message || '更新脚本失败'
        throw error
      } finally {
        this.loading = false
      }
    },

    /**
     * 删除脚本
     */
    async deleteScript(id) {
      this.loading = true
      this.error = null
      try {
        await scriptManagementService.deleteScript(id)
        await this.fetchScripts({
          page: this.pagination.currentPage,
          per_page: this.pagination.pageSize
        })
        if (this.currentScript && this.currentScript.id === id) {
          this.currentScript = null
        }
      } catch (error) {
        this.error = error.response?.data?.error || error.message || '删除脚本失败'
        throw error
      } finally {
        this.loading = false
      }
    },

    /**
     * 执行脚本
     */
    async executeScript(id, triggeredBy = 'manual') {
      this.executing = true
      this.error = null
      try {
        const response = await scriptManagementService.executeScript(id, triggeredBy)
        return response.data
      } catch (error) {
        this.error = error.response?.data?.error || error.message || '执行脚本失败'
        throw error
      } finally {
        this.executing = false
      }
    },

    /**
     * 执行脚本（不刷新执行历史，避免重复请求）
     */
    async executeScriptWithoutHistory(id, triggeredBy = 'manual') {
      this.executing = true
      this.error = null
      try {
        const response = await scriptManagementService.executeScript(id, triggeredBy)
        return response.data
      } catch (error) {
        this.error = error.response?.data?.error || error.message || '执行脚本失败'
        throw error
      } finally {
        this.executing = false
      }
    },

    /**
     * 获取执行历史（仅用于获取最新执行记录，用于查看功能）
     */
    async fetchExecutionHistory(params = {}) {
      this.loading = true
      this.error = null
      try {
        const response = await scriptManagementService.getExecutionHistory({
          page: params.page || 1,
          per_page: params.per_page || 1,
          script_id: params.script_id,
          status: params.status
        })

        this.executionHistory = response.data.data || []
        return response.data
      } catch (error) {
        this.error = error.response?.data?.error || error.message || '获取执行记录失败'
        throw error
      } finally {
        this.loading = false
      }
    },

    /**
     * 获取执行记录详情
     */
    async fetchExecutionById(id) {
      this.loading = true
      this.error = null
      try {
        const response = await scriptManagementService.getExecutionById(id)
        this.currentExecution = response.data
        return response.data
      } catch (error) {
        this.error = error.response?.data?.error || error.message || '获取执行记录失败'
        throw error
      } finally {
        this.loading = false
      }
    },

    /**
     * 取消执行
     */
    async cancelExecution(id) {
      this.loading = true
      this.error = null
      try {
        await scriptManagementService.cancelExecution(id)
      } catch (error) {
        this.error = error.response?.data?.error || error.message || '取消执行失败'
        throw error
      } finally {
        this.loading = false
      }
    }
  }
})

import { defineStore } from 'pinia'
import { databaseConnService } from '@/services/database/databaseConnService'

export const useDatabaseConnStore = defineStore('databaseConn', {
  state: () => ({
    connections: [],
    currentConnection: null,
    pagination: {
      currentPage: 1,
      pageSize: 10,
      total: 0
    },
    loading: false,
    error: null,
    searchQuery: {
      name: '',
      host: '',
      database: ''
    }
  }),

  getters: {
    /**
     * 获取活跃的连接列表
     */
    activeConnections: (state) => {
      return state.connections.filter(conn => conn.is_active)
    },

    /**
     * 获取连接选项（用于下拉选择）
     */
    connectionOptions: (state) => {
      return state.connections
        .filter(conn => conn.is_active)
        .map(conn => ({
          value: conn.id,
          label: conn.name,
          host: conn.host,
          database: conn.database
        }))
    },

    /**
     * 获取连接名称映射
     */
    connectionNameMap: (state) => {
      const map = {}
      state.connections.forEach(conn => {
        if (conn.is_active) {
          map[conn.id] = conn.name
        }
      })
      return map
    },
  },

  actions: {
    /**
     * 获取数据库连接列表
     */
    async fetchConnections(params = {}) {
      this.loading = true
      this.error = null
      try {
        const searchParams = params.search || this.searchQuery
        const response = await databaseConnService.getDatabaseConnections({
          page: params.page || this.pagination.currentPage,
          per_page: params.pageSize || this.pagination.pageSize,
          name: searchParams.name || params.name,
          host: searchParams.host || params.host,
          database: searchParams.database || params.database,
        })

        this.connections = response.data
        this.pagination = {
          currentPage: params.page || this.pagination.currentPage,
          pageSize: params.pageSize || this.pagination.pageSize,
          total: response.total
        }

        // 更新搜索查询
        if (params.search !== undefined) {
          this.searchQuery = { ...this.searchQuery, ...params.search }
        }
      } catch (error) {
        this.error = error.message || '获取数据库连接列表失败'
        throw error
      } finally {
        this.loading = false
      }
    },

    /**
     * 获取所有数据库连接（用于下拉选择）
     */
    async fetchConnectionsForSelect() {
      this.loading = true
      this.error = null
      try {
        const response = await databaseConnService.getDatabaseConnectionsForSelect()
        this.connections = response.data
      } catch (error) {
        this.error = error.message || '获取数据库连接列表失败'
        throw error
      } finally {
        this.loading = false
      }
    },

    /**
     * 获取数据库连接详情
     */
    async fetchConnection(id) {
      this.loading = true
      try {
        const response = await databaseConnService.getDatabaseConnection(id)
        this.currentConnection = response.data
        return response.data
      } catch (error) {
        this.error = error.message || '获取数据库连接详情失败'
        throw error
      } finally {
        this.loading = false
      }
    },

    /**
     * 创建数据库连接
     */
    async createConnection(connectionData) {
      try {
        const response = await databaseConnService.createDatabaseConnection(connectionData)
        await this.fetchConnections({
          page: this.pagination.currentPage,
          pageSize: this.pagination.pageSize,
          search: this.searchQuery
        })
        return response.data
      } catch (error) {
        this.error = error.message || '创建数据库连接失败'
        throw error
      }
    },

    /**
     * 更新数据库连接
     */
    async updateConnection(id, connectionData) {
      try {
        const response = await databaseConnService.updateDatabaseConnection(id, connectionData)
        await this.fetchConnections({
          page: this.pagination.currentPage,
          pageSize: this.pagination.pageSize,
          search: this.searchQuery
        })
        
        // 如果更新的是当前连接，则更新当前连接数据
        if (this.currentConnection?.id === id) {
          this.currentConnection = { ...this.currentConnection, ...connectionData }
        }
        
        return response.data
      } catch (error) {
        this.error = error.message || '更新数据库连接失败'
        throw error
      }
    },

    /**
     * 删除数据库连接
     */
    async deleteConnection(id) {
      try {
        await databaseConnService.deleteDatabaseConnection(id)
        
        // 如果删除的是当前连接，则清空当前连接
        if (this.currentConnection?.id === id) {
          this.currentConnection = null
        }
        
        // 重新获取连接列表，处理分页逻辑
        await this.fetchConnections({
          page: this.connections.length === 1 && this.pagination.currentPage > 1
            ? this.pagination.currentPage - 1
            : this.pagination.currentPage,
          pageSize: this.pagination.pageSize,
          search: this.searchQuery
        })
      } catch (error) {
        this.error = error.message || '删除数据库连接失败'
        throw error
      }
    },

    /**
     * 测试数据库连接
     */
    async testConnection(id) {
      try {
        const response = await databaseConnService.testDatabaseConnection(id)
        return response.data
      } catch (error) {
        this.error = error.message || '测试数据库连接失败'
        throw error
      }
    },

    /**
     * 测试数据库连接参数（不保存）
     */
    async testConnectionParams(connectionParams) {
      try {
        const response = await databaseConnService.testDatabaseConnectionParams(connectionParams)
        return response.data
      } catch (error) {
        this.error = error.message || '测试数据库连接参数失败'
        throw error
      }
    },

    /**
     * 清空错误信息
     */
    clearError() {
      this.error = null
    },

    /**
     * 清空当前连接
     */
    clearCurrentConnection() {
      this.currentConnection = null
    },

    /**
     * 设置当前连接
     */
    setCurrentConnection(connection) {
      this.currentConnection = connection
    },

    /**
     * 更新分页信息
     */
    updatePagination(page, pageSize) {
      this.pagination.currentPage = page
      this.pagination.pageSize = pageSize
    }
  }
})

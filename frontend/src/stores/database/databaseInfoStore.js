import { defineStore } from 'pinia'
import { databaseInfoService } from '@/services/database/databaseInfoService'

export const useDatabaseInfoStore = defineStore('databaseInfo', {
  state: () => ({
    currentConnection: null, // 当前选择的数据库连接
    databases: [], // 数据库列表
    tables: {}, // 数据库表映射 { databaseName: [tables] }
    tableData: null, // 当前表的数据
    tableStructure: null, // 当前表的结构
    currentDatabase: null, // 当前选中的数据库
    currentTable: null, // 当前选中的表
    loading: false,
    dataLoading: false,
    error: null,
    pagination: {
      currentPage: 1,
      pageSize: 50,
      total: 0
    }
  }),

  getters: {
    /**
     * 当前数据库的表列表
     */
    currentTables: (state) => {
      if (!state.currentDatabase) return []
      return state.tables[state.currentDatabase] || []
    },

    /**
     * 是否已选择连接
     */
    hasConnection: (state) => !!state.currentConnection
  },

  actions: {
    /**
     * 设置当前数据库连接
     */
    setCurrentConnection(connection) {
      this.currentConnection = connection
      this.databases = []
      this.tables = {}
      this.currentDatabase = null
      this.currentTable = null
      this.tableData = null
      this.tableStructure = null
    },

    /**
     * 获取数据库列表
     */
    async fetchDatabases() {
      if (!this.currentConnection) {
        throw new Error('请先选择数据库连接')
      }

      this.loading = true
      this.error = null
      try {
        const response = await databaseInfoService.getDatabases(this.currentConnection.id)
        this.databases = response.data.data || []
      } catch (error) {
        // 优先使用后端返回的错误消息
        this.error = error.response?.data?.message || '获取数据库列表失败'
        throw error
      } finally {
        this.loading = false
      }
    },

    /**
     * 获取指定数据库的表列表
     */
    async fetchTables(databaseName, keyword) {
      if (!this.currentConnection) {
        throw new Error('请先选择数据库连接')
      }

      this.loading = true
      this.error = null
      try {
        const response = await databaseInfoService.getTables(this.currentConnection.id, databaseName, keyword)
        this.tables[databaseName] = response.data.data || []
        this.currentDatabase = databaseName
      } catch (error) {
        this.error = error.message || '获取表列表失败'
        throw error
      } finally {
        this.loading = false
      }
    },

    /**
     * 获取数据表数据
     */
    async fetchTableData(databaseName, tableName, page = 1, pageSize = 50, filters = null, append = false) {
      if (!this.currentConnection) {
        throw new Error('请先选择数据库连接')
      }

      this.dataLoading = true
      this.error = null
      try {
        const response = await databaseInfoService.getTableData(this.currentConnection.id, databaseName, tableName, { page, per_page: pageSize, filters })

        if (append && this.tableData && Array.isArray(this.tableData.data)) {
          const merged = {
            ...response.data,
            data: [...this.tableData.data, ...(response.data.data || [])]
          }
          this.tableData = merged
        } else {
          this.tableData = response.data
        }
        this.currentTable = tableName
        this.pagination = {
          currentPage: page,
          pageSize: pageSize,
          total: response.data.total || 0
        }

        return response.data
      } catch (error) {
        this.error = error.message || '获取表数据失败'
        throw error
      } finally {
        this.dataLoading = false
      }
    },

    /**
     * 是否还有更多数据
     */
    hasMore() {
      const count = this.tableData?.data?.length || 0
      const total = this.tableData?.total || 0
      return count < total
    },

    /**
     * 获取数据表结构
     */
    async fetchTableStructure(databaseName, tableName) {
      if (!this.currentConnection) {
        throw new Error('请先选择数据库连接')
      }

      this.loading = true
      this.error = null
      try {
        const response = await databaseInfoService.getTableStructure(this.currentConnection.id, databaseName, tableName)
        this.tableStructure = response.data
        return response.data
      } catch (error) {
        this.error = error.message || '获取表结构失败'
        throw error
      } finally {
        this.loading = false
      }
    },

    /**
     * 执行SQL查询
     */
    async executeQuery(query, databaseName = null) {
      if (!this.currentConnection) {
        throw new Error('请先选择数据库连接')
      }

      this.loading = true
      this.error = null
      try {
        const response = await databaseInfoService.executeQuery(this.currentConnection.id, {
          database_name: databaseName,
          query
        })
        return response.data
      } catch (error) {
        this.error = error.message || '执行查询失败'
        throw error
      } finally {
        this.loading = false
      }
    },

    /**
     * 关闭数据库连接
     */
    async closeConnection() {
      if (!this.currentConnection) {
        return
      }

      try {
        await databaseInfoService.closeConnection(this.currentConnection.id)
      } catch (error) {
        console.error('关闭连接失败:', error)
      } finally {
        this.currentConnection = null
        this.databases = []
        this.tables = {}
        this.currentDatabase = null
        this.currentTable = null
        this.tableData = null
        this.tableStructure = null
      }
    },

    /**
     * 清空错误信息
     */
    clearError() {
      this.error = null
    },

    /**
     * 重置状态
     */
    reset() {
      this.currentConnection = null
      this.databases = []
      this.tables = {}
      this.currentDatabase = null
      this.currentTable = null
      this.tableData = null
      this.tableStructure = null
      this.loading = false
      this.dataLoading = false
      this.error = null
      this.pagination = {
        currentPage: 1,
        pageSize: 50,
        total: 0
      }
    }
  }
})

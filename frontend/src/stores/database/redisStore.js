import { defineStore } from 'pinia'
import { redisService } from '@/services/database/redisService'

export const useRedisStore = defineStore('redis', {
  state: () => ({
    currentConnection: null,  // 当前选择的 Redis 连接
    keys: [],                 // Redis keys 列表
    currentKey: null,         // 当前选中的 key
    keyInfo: null,           // 当前 key 的详细信息
    loading: false,
    dataLoading: false,
    error: null,
    pagination: {
      cursor: 0,
      count: 0,
      hasMore: false
    },
    searchPattern: '*'        // 搜索模式
  }),

  getters: {
    /**
     * 是否已选择连接
     */
    hasConnection: (state) => !!state.currentConnection
  },

  actions: {
    /**
     * 设置当前 Redis 连接
     */
    setCurrentConnection(connection) {
      this.currentConnection = connection
    },

    /**
     * 获取 Redis keys
     */
    async fetchKeys(pattern = '*', cursor = 0, count = 100) {
      if (!this.currentConnection) {
        throw new Error('请先选择 Redis 连接')
      }

      this.loading = true
      this.error = null
      try {
        const response = await redisService.getKeys(this.currentConnection.id, {
          pattern,
          cursor,
          count
        })
        
        if (cursor === 0) {
          // 首次加载或重置，替换列表
          this.keys = response.data.keys || []
        } else {
          // 追加加载
          this.keys = [...this.keys, ...(response.data.keys || [])]
        }
        
        this.pagination = {
          cursor: response.data.cursor || 0,
          count: response.data.count || 0,
          hasMore: response.data.has_more || false
        }
        this.searchPattern = pattern

        return response.data
      } catch (error) {
        this.error = error.message || '获取 keys 失败'
        throw error
      } finally {
        this.loading = false
      }
    },

    /**
     * 获取 key 的详细信息
     */
    async fetchKeyInfo(key) {
      if (!this.currentConnection) {
        throw new Error('请先选择 Redis 连接')
      }

      this.dataLoading = true
      this.error = null
      try {
        const response = await redisService.getKeyInfo(this.currentConnection.id, key)
        this.keyInfo = response.data
        this.currentKey = key
        return response.data
      } catch (error) {
        this.error = error.message || '获取 key 信息失败'
        throw error
      } finally {
        this.dataLoading = false
      }
    },

    /**
     * 设置 key 的值
     */
    async setKeyValue(key, data) {
      if (!this.currentConnection) {
        throw new Error('请先选择 Redis 连接')
      }

      this.dataLoading = true
      this.error = null
      try {
        const response = await redisService.setKeyValue(this.currentConnection.id, key, data)
        // 刷新当前 key 信息
        if (this.currentKey === key) {
          await this.fetchKeyInfo(key)
        }
        return response.data
      } catch (error) {
        this.error = error.message || '设置 key 失败'
        throw error
      } finally {
        this.dataLoading = false
      }
    },

    /**
     * 更新 key 的值
     */
    async updateKeyValue(key, data) {
      if (!this.currentConnection) {
        throw new Error('请先选择 Redis 连接')
      }

      this.dataLoading = true
      this.error = null
      try {
        const response = await redisService.updateKeyValue(this.currentConnection.id, key, data)
        // 刷新当前 key 信息
        if (this.currentKey === key) {
          await this.fetchKeyInfo(key)
        }
        return response.data
      } catch (error) {
        this.error = error.message || '更新 key 失败'
        throw error
      } finally {
        this.dataLoading = false
      }
    },

    /**
     * 删除 key
     */
    async deleteKey(key) {
      if (!this.currentConnection) {
        throw new Error('请先选择 Redis 连接')
      }

      this.dataLoading = true
      this.error = null
      try {
        const response = await redisService.deleteKey(this.currentConnection.id, key)
        // 从列表中移除
        this.keys = this.keys.filter(k => k !== key)
        // 如果删除的是当前 key，清空信息
        if (this.currentKey === key) {
          this.currentKey = null
          this.keyInfo = null
        }
        return response.data
      } catch (error) {
        this.error = error.message || '删除 key 失败'
        throw error
      } finally {
        this.dataLoading = false
      }
    },

    /**
     * 批量删除 keys
     */
    async deleteKeys(keys) {
      if (!this.currentConnection) {
        throw new Error('请先选择 Redis 连接')
      }

      this.dataLoading = true
      this.error = null
      try {
        const response = await redisService.deleteKeys(this.currentConnection.id, keys)
        // 从列表中移除
        this.keys = this.keys.filter(k => !keys.includes(k))
        // 如果删除的包含当前 key，清空信息
        if (keys.includes(this.currentKey)) {
          this.currentKey = null
          this.keyInfo = null
        }
        return response.data
      } catch (error) {
        this.error = error.message || '批量删除 keys 失败'
        throw error
      } finally {
        this.dataLoading = false
      }
    },

    /**
     * 获取 key 数量
     */
    async fetchKeyCount(pattern = '*') {
      if (!this.currentConnection) {
        throw new Error('请先选择 Redis 连接')
      }

      try {
        const response = await redisService.getKeyCount(this.currentConnection.id, pattern)
        return response.data.count || 0
      } catch (error) {
        this.error = error.message || '获取 key 数量失败'
        throw error
      }
    },

    /**
     * 关闭连接
     */
    async closeConnection() {
      if (!this.currentConnection) {
        return
      }

      try {
        await redisService.closeConnection(this.currentConnection.id)
      } catch (error) {
        console.error('关闭连接失败:', error)
      } finally {
        this.currentConnection = null
        this.keys = []
        this.currentKey = null
        this.keyInfo = null
      }
    },

    /**
     * 重置状态
     */
    reset() {
      this.currentConnection = null
      this.keys = []
      this.currentKey = null
      this.keyInfo = null
      this.error = null
      this.pagination = {
        cursor: 0,
        count: 0,
        hasMore: false
      }
      this.searchPattern = '*'
    }
  }
})


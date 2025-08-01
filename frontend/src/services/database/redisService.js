import apiClient from '../../utils/request'

/**
 * Redis 数据库服务相关 API
 */
export const redisService = {
  /**
   * 获取 Redis keys（支持分页）
   */
  getKeys(connectionId, { pattern = '*', cursor = 0, count = 100 } = {}) {
    return apiClient.get(`/redis/${connectionId}/keys`, {
      params: { pattern, cursor, count }
    })
  },

  /**
   * 获取 key 的详细信息
   */
  getKeyInfo(connectionId, key) {
    return apiClient.get(`/redis/${connectionId}/keys/${encodeURIComponent(key)}`)
  },

  /**
   * 设置 key 的值
   */
  setKeyValue(connectionId, key, { value, type = 'string', ttl, ...otherParams }) {
    return apiClient.post(`/redis/${connectionId}/keys/${encodeURIComponent(key)}`, {
      value,
      type,
      ttl,
      ...otherParams
    })
  },

  /**
   * 更新 key 的值
   */
  updateKeyValue(connectionId, key, { value, type, ttl, ...otherParams }) {
    return apiClient.put(`/redis/${connectionId}/keys/${encodeURIComponent(key)}`, {
      value,
      type,
      ttl,
      ...otherParams
    })
  },

  /**
   * 删除 key
   */
  deleteKey(connectionId, key) {
    return apiClient.delete(`/redis/${connectionId}/keys/${encodeURIComponent(key)}`)
  },

  /**
   * 批量删除 keys
   */
  deleteKeys(connectionId, keys) {
    return apiClient.delete(`/redis/${connectionId}/keys/batch`, {
      data: { keys }
    })
  },

  /**
   * 获取 key 的数量
   */
  getKeyCount(connectionId, pattern = '*') {
    return apiClient.get(`/redis/${connectionId}/keys/count`, {
      params: { pattern }
    })
  },

  /**
   * 执行 Redis 命令
   */
  executeCommand(connectionId, command) {
    return apiClient.post(`/redis/${connectionId}/execute`, {
      command
    })
  },

  /**
   * 关闭 Redis 连接
   */
  closeConnection(connectionId) {
    return apiClient.post(`/redis/${connectionId}/close`)
  }
}

export default redisService

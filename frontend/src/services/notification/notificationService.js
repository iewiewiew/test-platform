import apiClient from '../../utils/request'

/**
 * 消息通知相关 API 服务
 */
export const notificationService = {
  /**
   * 通知列表分页查询
   */
  getNotifications({ page = 1, per_page = 10, name, notification_type } = {}) {
    const params = {
      page,
      per_page
    }

    if (name) params.name = name
    if (notification_type) params.notification_type = notification_type

    return apiClient.get('/notifications', { params }).then((response) => ({
      data: response.data.data || [],
      total: response.data.total || 0,
      current_page: response.data.current_page || page,
      per_page: response.data.per_page || per_page
    }))
  },

  /**
   * 获取所有通知配置
   */
  getAllNotifications() {
    return apiClient.get('/notifications/all')
  },

  /**
   * 获取通知详情
   */
  getNotificationById(id) {
    return apiClient.get(`/notifications/${id}`)
  },

  /**
   * 创建通知配置
   */
  createNotification(notificationData) {
    return apiClient.post('/notifications', notificationData)
  },

  /**
   * 更新通知配置
   */
  updateNotification(id, notificationData) {
    return apiClient.put(`/notifications/${id}`, notificationData)
  },

  /**
   * 删除通知配置
   */
  deleteNotification(id) {
    return apiClient.delete(`/notifications/${id}`)
  },

  /**
   * 测试通知配置
   */
  testNotification(id, message = '这是一条测试消息') {
    return apiClient.post(`/notifications/${id}/test`, { message })
  }
}

export default notificationService

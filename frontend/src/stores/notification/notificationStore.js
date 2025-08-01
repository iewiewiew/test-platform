import { defineStore } from 'pinia'
import { notificationService } from '@/services/notification/notificationService'

export const useNotificationStore = defineStore('notification', {
  state: () => ({
    notifications: [],
    currentNotification: null,
    pagination: {
      currentPage: 1,
      total: 0,
      pageSize: 10
    },
    loading: false
  }),

  getters: {
    notificationList: (state) => state.notifications,
    paginationInfo: (state) => state.pagination
  },

  actions: {
    async fetchNotifications(params = {}) {
      this.loading = true
      try {
        const response = await notificationService.getNotifications(params)
        this.notifications = response.data
        this.pagination = {
          currentPage: response.current_page || params.page || this.pagination.currentPage,
          total: response.total || 0,
          pageSize: response.per_page || params.per_page || this.pagination.pageSize
        }
        return { success: true }
      } catch (error) {
        return {
          success: false,
          message: error.response?.data?.message || '获取通知列表失败'
        }
      } finally {
        this.loading = false
      }
    },

    async fetchNotificationById(id) {
      try {
        const response = await notificationService.getNotificationById(id)
        this.currentNotification = response.data
        return response.data
      } catch (error) {
        return {
          success: false,
          message: error.response?.data?.message || '获取通知信息失败'
        }
      }
    },

    async createNotification(notificationData) {
      try {
        const response = await notificationService.createNotification(notificationData)
        this.notifications.unshift(response.data)
        return { success: true, data: response.data }
      } catch (error) {
        return {
          success: false,
          message: error.response?.data?.error || error.response?.data?.message || '创建通知失败'
        }
      }
    },

    async updateNotification(id, notificationData) {
      try {
        const response = await notificationService.updateNotification(id, notificationData)
        const index = this.notifications.findIndex((notification) => notification.id === id)
        if (index !== -1) {
          this.notifications[index] = response.data
        }
        return { success: true, data: response.data }
      } catch (error) {
        return {
          success: false,
          message: error.response?.data?.error || error.response?.data?.message || '更新通知失败'
        }
      }
    },

    async deleteNotification(id) {
      try {
        await notificationService.deleteNotification(id)
        this.notifications = this.notifications.filter((notification) => notification.id !== id)
        return { success: true }
      } catch (error) {
        return {
          success: false,
          message: error.response?.data?.error || error.response?.data?.message || '删除通知失败'
        }
      }
    },

    async testNotification(id, message) {
      try {
        const response = await notificationService.testNotification(id, message)
        return { success: response.data.success || false, message: response.data.message || response.data.error }
      } catch (error) {
        return {
          success: false,
          message: error.response?.data?.error || error.response?.data?.message || '测试通知失败'
        }
      }
    }
  }
})

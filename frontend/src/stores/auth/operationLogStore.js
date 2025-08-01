import { defineStore } from 'pinia';
import { operationLogService } from '@/services/auth/operationLogService';

export const useOperationLogStore = defineStore('operationLog', {
  state: () => ({
    operationLogs: [],
    currentLog: null,
    pagination: {
      currentPage: 1,
      total: 0,
      pageSize: 10
    },
    loading: false
  }),

  getters: {
    logList: (state) => state.operationLogs,
    paginationInfo: (state) => state.pagination
  },

  actions: {
    async fetchOperationLogs(params = {}) {
      this.loading = true;
      try {
        const response = await operationLogService.getOperationLogs(params);
        this.operationLogs = response.data.operation_logs || [];
        this.pagination = {
          currentPage: response.data.current_page || params.page || this.pagination.currentPage,
          total: response.data.total || 0,
          pageSize: response.data.per_page || params.per_page || this.pagination.pageSize
        };
        return { success: true };
      } catch (error) {
        return {
          success: false,
          message: error.response?.data?.message || '获取操作日志列表失败'
        };
      } finally {
        this.loading = false;
      }
    },

    async fetchOperationLogById(id) {
      try {
        const response = await operationLogService.getOperationLogById(id);
        this.currentLog = response.data.operation_log;
        return response.data;
      } catch (error) {
        return {
          success: false,
          message: error.response?.data?.message || '获取操作日志详情失败'
        };
      }
    },

    async deleteOperationLog(id) {
      try {
        await operationLogService.deleteOperationLog(id);
        this.operationLogs = this.operationLogs.filter(log => log.id !== id);
        return { success: true };
      } catch (error) {
        return {
          success: false,
          message: error.response?.data?.message || '删除操作日志失败'
        };
      }
    }
  }
});


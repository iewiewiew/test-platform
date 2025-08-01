import apiClient from "../../utils/request";

/**
 * 操作日志相关 API 服务
 */
export const operationLogService = {
  /**
   * 获取操作日志列表
   */
  getOperationLogs(params = {}) {
    return apiClient.get("/operation-logs", { params });
  },

  /**
   * 获取单个操作日志详情
   */
  getOperationLogById(id) {
    return apiClient.get(`/operation-logs/${id}`);
  },

  /**
   * 删除操作日志
   */
  deleteOperationLog(id) {
    return apiClient.delete(`/operation-logs/${id}`);
  },
};

export default operationLogService;


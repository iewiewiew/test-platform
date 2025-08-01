import apiClient from "../../utils/request";

/**
 * API访问日志相关 API 服务
 */
export const apiAccessLogService = {
  /**
   * 获取API访问日志列表
   */
  getApiAccessLogs(params = {}) {
    return apiClient.get("/api-access-logs", { params });
  },

  /**
   * 获取单个API访问日志详情
   */
  getApiAccessLogById(id) {
    return apiClient.get(`/api-access-logs/${id}`);
  },

  /**
   * 获取指定用户的API访问日志
   */
  getUserApiAccessLogs(username, params = {}) {
    return apiClient.get(`/api-access-logs/user/${username}`, { params });
  },

  /**
   * 删除API访问日志
   */
  deleteApiAccessLog(id) {
    return apiClient.delete(`/api-access-logs/${id}`);
  },
};

export default apiAccessLogService;


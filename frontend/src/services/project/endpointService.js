import apiClient from "../../utils/request";

/**
 * 接口端点相关 API 服务
 */
export const endpointService = {
  /**
   * 刷新API文档
   */
  refreshApiDocs() {
    return apiClient.post("/api-docs/refresh");
  },

  /**
   * 获取所有接口端点列表
   */
  getEndpoints(params = {}) {
    return apiClient.get("/api-docs/endpoints", { params });
  },

  /**
   * 按分类获取接口端点（用于目录树）
   */
  getEndpointsByCategories() {
    return apiClient.get("/api-docs/endpoints/categories");
  },

  /**
   * 获取特定接口端点的详细信息
   */
  getEndpointDetail(endpointId) {
    return apiClient.get(`/api-docs/endpoints/${endpointId}`);
  },

  /**
   * 创建新的接口端点
   */
  createEndpoint(data) {
    return apiClient.post("/api-docs/endpoints", data);
  },

  /**
   * 更新接口端点
   */
  updateEndpoint(endpointId, data) {
    return apiClient.put(`/api-docs/endpoints/${endpointId}`, data);
  },

  /**
   * 删除接口端点
   */
  deleteEndpoint(endpointId) {
    return apiClient.delete(`/api-docs/endpoints/${endpointId}`);
  },

  /**
   * 获取接口端点的所有参数
   */
  getEndpointParameters(endpointId) {
    return apiClient.get(`/api-docs/endpoints/${endpointId}/parameters`);
  },

  /**
   * 测试接口端点
   */
  testEndpoint(endpointId, testData = {}) {
    return apiClient.post(`/api-docs/endpoints/${endpointId}/test`, testData);
  },
};

export default endpointService;

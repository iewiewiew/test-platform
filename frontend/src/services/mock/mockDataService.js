import apiClient from "../../utils/request";

/**
 * MockData 相关 API 服务
 */
export const mockDataService = {
  /**
   * 获取调用 Mock 接口的 CURL 命令
   */
  generateCurlCommand(api_path, method) {
    return apiClient.get(`/mock/curl/${api_path}`, {
      params: {
        method: method,
      },
    });
  },

  // 生成模拟数据
  generateMockData(data) {
    return apiClient.post(`/mock_data/generate`, data);
  },

  // 获取字段类型
  getFieldTypes() {
    return apiClient.get(`/mock_data/field-types`);
  },
};

export default mockDataService;

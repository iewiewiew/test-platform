import apiClient from "../../utils/request";

/**
 * 测试环境相关 API 服务
 */
export const testEnvironmentService = {
  /**
   * 解析配置文件并初始化数据库
   */
  parseTestEnvironments(configFile) {
    return apiClient.post("/test-environments/parse", {
      config_file: configFile
    });
  },

  /**
   * 测试环境列表分页查询
   */
  getTestEnvironments({ page = 1, per_page = 10, search } = {}) {
    const params = { page, per_page };
    if (search) params.search = search;

    return apiClient.get("/test-environments", { params }).then((response) => ({
      data: response.data.data,
      total: response.data.total,
      page: response.data.page,
      per_page: response.data.per_page,
    }));
  },

  /**
   * 获取所有测试环境（用于下拉选择）
   */
  getTestEnvironmentsForSelect() {
    return apiClient.get("/test-environments", { params: { page: 1, per_page: 100 } }).then((response) => ({
      data: response.data.data,
    }));
  },

  /**
   * 获取测试环境详情
   */
  getTestEnvironment(id) {
    return apiClient.get(`/test-environments/${id}`);
  },

  /**
   * 创建测试环境
   */
  createTestEnvironment(environmentData) {
    return apiClient.post("/test-environments", environmentData);
  },

  /**
   * 更新测试环境
   */
  updateTestEnvironment(id, environmentData) {
    return apiClient.put(`/test-environments/${id}`, environmentData);
  },

  /**
   * 删除测试环境
   */
  deleteTestEnvironment(id) {
    return apiClient.delete(`/test-environments/${id}`);
  },
};

export default testEnvironmentService;


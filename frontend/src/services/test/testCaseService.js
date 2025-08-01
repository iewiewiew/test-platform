import apiClient from "../../utils/request";

/**
 * 测试用例相关 API 服务
 */
export const testCaseService = {
  /**
   * 解析测试用例文件
   */
  parseTestCases(directoryPath) {
    return apiClient.post("/test-cases/parse", {
      directory_path: directoryPath
    });
  },

  /**
   * 测试用例列表分页查询
   */
  getTestCases({ page = 1, per_page = 10, search, environment, module_name, component_name } = {}) {
    const params = { page, per_page };
    if (search) params.search = search;
    if (environment) params.environment = environment;
    if (module_name) params.module_name = module_name;
    if (component_name) params.component_name = component_name;

    return apiClient.get("/test-cases", { params }).then((response) => ({
      data: response.data.data,
      total: response.data.total,
      page: response.data.page,
      per_page: response.data.per_page,
    }));
  },

  /**
   * 获取所有模块名称列表
   */
  getModuleNames() {
    return apiClient.get("/test-cases/module-names").then((response) => ({
      data: response.data.data || [],
    }));
  },

  /**
   * 获取所有组件名称列表
   */
  getComponentNames() {
    return apiClient.get("/test-cases/component-names").then((response) => ({
      data: response.data.data || [],
    }));
  },

  /**
   * 获取测试用例详情
   */
  getTestCase(id) {
    return apiClient.get(`/test-cases/${id}`);
  },

  /**
   * 执行测试用例
   */
  executeTestCase(id, { environment_name, base_url } = {}) {
    return apiClient.post(`/test-cases/${id}/execute`, {
      environment_name,
      base_url
    });
  },

  /**
   * 创建测试用例
   */
  createTestCase(data) {
    return apiClient.post("/test-cases", data);
  },

  /**
   * 更新测试用例
   */
  updateTestCase(id, data) {
    return apiClient.put(`/test-cases/${id}`, data);
  },

  /**
   * 删除测试用例
   */
  deleteTestCase(id) {
    return apiClient.delete(`/test-cases/${id}`);
  },
};

export default testCaseService;


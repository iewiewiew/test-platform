import apiClient from "../../utils/request";

/**
 * Pytest执行相关 API 服务
 */
export const pytestExecutorService = {
  /**
   * 执行Pytest测试并生成Allure报告
   * 注意：Pytest执行可能需要较长时间，因此设置较长的超时时间
   */
  executePytest({ module_name, environment_name, component_name } = {}) {
    return apiClient.post("/pytest-executor/execute", {
      module_name,
      environment_name,
      component_name
    }, {
      timeout: 600000 // 10分钟超时（600秒），因为测试执行可能需要较长时间
    });
  },
};

export default pytestExecutorService;


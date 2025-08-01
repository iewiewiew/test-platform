import apiClient from "../../utils/request";

/**
 * 测试报告相关 API 服务
 */
export const testReportService = {
  /**
   * 解析Pytest测试报告
   */
  parseTestReports(reportDir) {
    return apiClient.post("/test-reports/parse", {
      report_dir: reportDir
    });
  },

  /**
   * 测试报告列表分页查询
   */
  getTestReports({ page = 1, per_page = 10, search } = {}) {
    const params = { page, per_page };
    if (search) params.search = search;

    return apiClient.get("/test-reports", { params }).then((response) => ({
      data: response.data.data,
      total: response.data.total,
      page: response.data.page,
      per_page: response.data.per_page,
    }));
  },

  /**
   * 获取测试报告详情
   */
  getTestReport(id, parse = false) {
    return apiClient.get(`/test-reports/${id}`, {
      params: { parse: parse }
    });
  },

  /**
   * 解析单个测试报告
   */
  parseTestReport(id) {
    return apiClient.post(`/test-reports/${id}/parse`);
  },

  /**
   * 获取测试日志
   */
  getTestLogs(id, testMethod) {
    return apiClient.get(`/test-reports/${id}/logs`, {
      params: testMethod ? { test_method: testMethod } : {}
    });
  },

  /**
   * 删除测试报告
   */
  deleteTestReport(id) {
    return apiClient.delete(`/test-reports/${id}`);
  },

  /**
   * 获取Allure报告URL
   */
  getAllureReportUrl(id) {
    return apiClient.get(`/test-reports/${id}/allure`);
  },
};

export default testReportService;


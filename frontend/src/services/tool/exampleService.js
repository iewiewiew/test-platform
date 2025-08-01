import apiClient from "../../utils/request";

/**
 * 示例数据相关 API 服务
 */
export const exampleService = {
  /**
   * 示例列表分页查询
   */
  getExamples({ page = 1, per_page = 10, name, status, sort, order } = {}) {
    const params = {
      page,
      per_page,
    };

    if (name) params.name = name;
    if (status) params.status = status;
    if (sort) params.sort = sort;
    if (order) params.order = order;

    return apiClient.get("/examples", { params }).then((response) => ({
      data: response.data.data,
      total: response.data.total,
    }));
  },

  /**
   * 获取示例详情
   */
  getExample(id) {
    return apiClient.get(`/examples/${id}`);
  },

  /**
   * 获取示例选项列表，用于下拉选择
   */
  getExampleOptions({ page = 1, per_page = 100 } = {}) {
    return this.getExamples({ page, per_page });
  },

  /**
   * 创建示例
   */
  createExample(exampleData) {
    return apiClient.post("/examples", exampleData);
  },

  /**
   * 更新示例
   */
  updateExample(id, exampleData) {
    return apiClient.put(`/examples/${id}`, exampleData);
  },

  /**
   * 删除示例
   */
  deleteExample(id) {
    return apiClient.delete(`/examples/${id}`);
  },

  /**
   * 批量删除示例
   */
  batchDeleteExamples(ids) {
    return apiClient.delete("/examples/batch", {
      data: { ids }
    });
  },
};

export default exampleService;
import apiClient from "../../utils/request";

/**
 * Mock 相关 API 服务
 */
export const mockService = {
  /**
   * Mocl 列表默认查询，没有分页, 用于获取所有 Mock 列表
   */
  getMocks_default() {
    return apiClient.get("/mock");
  },

  /**
   * Mock 列表分页查询
   */
  async getMocks({
    page = 1,
    per_page = 10,
    name,
    path,
    method,
    project_id,
  } = {}) {
    const params = { page, per_page };

    // 添加搜索条件（如果存在）
    if (name) params.name = name;
    if (path) params.path = path;
    if (method) params.method = method;
    if (project_id) params.project_id = project_id;

    const response = await apiClient.get("/mock", { params });
    return {
      data: response.data.data,
      total: response.data.total,
    };
  },

  /**
   * 查看 Mock 详情
   */
  getMock(id) {
    return apiClient.get(`/mock/${id}`);
  },

  /**
   * 创建 Mock
   */
  createMock(mock) {
    return apiClient.post("/mock", mock);
  },

  /**
   * 更新 Mock
   */
  updateMock(id, mock) {
    return apiClient.put(`/mock/${id}`, mock);
  },

  /**
   * 删除 Mock
   */
  deleteMock(id) {
    return apiClient.delete(`/mock/${id}`);
  },

  /**
   * 调用 Mock 接口
   */
  executeMock(path, method) {
    return apiClient.request({
      url: `/mock/execute/${path}`,
      method: method,
    });
  },

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
};

export default mockService;

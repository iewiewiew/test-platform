import apiClient from "../../utils/request";

/**
 * 数据库连接管理相关 API 服务
 */
export const databaseConnService = {
  /**
   * 数据库连接列表分页查询
   */
  async getDatabaseConnections({
    page = 1,
    per_page = 10,
    name,
    host,
    database,
  } = {}) {
    const params = { page, per_page };

    // 添加搜索条件（如果存在）
    if (name) params.name = name;
    if (host) params.host = host;
    if (database) params.database = database;

    const response = await apiClient.get("/database-connections", { params });
    return {
      data: response.data.data,
      total: response.data.total,
      page: response.data.page,
      per_page: response.data.per_page,
    };
  },

  /**
   * 获取所有数据库连接（用于下拉选择）
   */
  async getDatabaseConnectionsForSelect() {
    const response = await apiClient.get("/database-connections/select");
    return {
      data: response.data.data,
    };
  },

  /**
   * 查看数据库连接详情
   */
  getDatabaseConnection(id) {
    return apiClient.get(`/database-connections/${id}`);
  },

  /**
   * 创建数据库连接
   */
  createDatabaseConnection(connection) {
    return apiClient.post("/database-connections", connection);
  },

  /**
   * 更新数据库连接
   */
  updateDatabaseConnection(id, connection) {
    return apiClient.put(`/database-connections/${id}`, connection);
  },

  /**
   * 删除数据库连接
   */
  deleteDatabaseConnection(id) {
    return apiClient.delete(`/database-connections/${id}`);
  },

  /**
   * 测试数据库连接
   */
  testDatabaseConnection(id) {
    return apiClient.post(`/database-connections/${id}/test`);
  },

  /**
   * 测试数据库连接参数（不保存）
   */
  testDatabaseConnectionParams(connectionParams) {
    return apiClient.post("/database-connections/test", connectionParams);
  },
};

export default databaseConnService;

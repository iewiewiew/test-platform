import apiClient from "../../utils/request";

/**
 * Linux 服务器管理 API 服务
 */
export const linuxInfoService = {
  /**
   * 获取服务器列表
   */
  getServers({ page = 1, per_page = 10, server_name, host, sort, order } = {}) {
    const params = {
      page,
      per_page,
    };

    if (server_name) params.server_name = server_name;
    if (host) params.host = host;
    if (sort) params.sort = sort;
    if (order) params.order = order;

    return apiClient.get("/servers", { params }).then((response) => ({
      data: response.data.data,
      total: response.data.total,
    }));
  },

  /**
   * 获取所有服务器列表（不分页）
   */
  getAllServers() {
    return apiClient.get("/servers").then((response) => ({
      data: response.data.data,
      total: response.data.total,
    }));
  },

  /**
   * 获取服务器详情
   */
  getServer(id) {
    return apiClient.get(`/servers/${id}`);
  },

  /**
   * 创建服务器
   */
  createServer(serverData) {
    return apiClient.post("/servers", serverData);
  },

  /**
   * 更新服务器
   */
  updateServer(id, serverData) {
    return apiClient.put(`/servers/${id}`, serverData);
  },

  /**
   * 删除服务器
   */
  deleteServer(id) {
    return apiClient.delete(`/servers/${id}`);
  },

  /**
   * 在服务器上执行命令
   */
  executeCommand(serverId, command) {
    return apiClient.post(`/servers/${serverId}/execute`, {
      command
    });
  },

  /**
   * 获取服务器信息
   */
  getServerInfo(serverId) {
    return apiClient.get(`/servers/${serverId}/info`);
  },

  /**
   * 获取单台服务器资源指标
   */
  getServerMetrics(serverId) {
    return apiClient.get(`/servers/${serverId}/metrics`)
  },

  /**
   * 获取所有服务器资源指标
   */
  getAllServerMetrics() {
    return apiClient.get(`/servers/metrics`)
  },

  /**
   * 获取服务器选项列表，用于下拉选择
   */
  getServerOptions({ page = 1, per_page = 100 } = {}) {
    return this.getServers({ page, per_page }).then((response) => ({
      data: response.data.map(server => ({
        value: server.id,
        label: `${server.server_name} (${server.host})`
      })),
      total: response.total
    }));
  }
};

export default linuxInfoService;
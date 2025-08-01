import apiClient from "../../utils/request";

/**
 * 用户相关 API 服务
 */
export const userService = {
  /**
   * 用户列表分页查询
   */
  getUsers({ page = 1, per_page = 10, search, sort, order } = {}) {
    const params = {
      page,
      per_page,
    };

    if (search) params.search = search;
    if (sort) params.sort = sort;
    if (order) params.order = order;

    return apiClient.get("/users", { params }).then((response) => ({
      data: response.data.users,
      total: response.data.total,
      current_page: response.data.current_page,
      per_page: response.data.per_page || per_page,
    }));
  },

  /**
   * 获取用户详情
   */
  getUserById(id) {
    return apiClient.get(`/users/${id}`);
  },

  /**
   * 创建用户
   */
  createUser(userData) {
    return apiClient.post("/users", userData);
  },

  /**
   * 更新用户
   */
  updateUser(id, userData) {
    return apiClient.put(`/users/${id}`, userData);
  },

  /**
   * 删除用户
   */
  deleteUser(id) {
    return apiClient.delete(`/users/${id}`);
  },
};

export default userService;
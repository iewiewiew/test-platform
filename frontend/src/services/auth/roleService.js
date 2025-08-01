import apiClient from "../../utils/request";

/**
 * 角色相关 API 服务
 */
export const roleService = {
  /**
   * 获取角色列表
   */
  getRoles({ page = 1, per_page = 10, name, sort, order } = {}) {
    const params = {
      page,
      per_page,
    };

    if (name) params.name = name;
    if (sort) params.sort = sort;
    if (order) params.order = order;

    return apiClient.get("/roles", { params }).then((response) => ({
      data: response.data.roles,
      total: response.data.total,
    }));
  },

  /**
   * 获取角色详情
   */
  getRoleById(id) {
    return apiClient.get(`/roles/${id}`);
  },

  /**
   * 获取角色选项，用于用户表单中选择角色
   */
  getRoleOptions() {
    return this.getRoles({ per_page: 100 }).then(response => ({
      data: response.data.map(role => ({
        value: role.id,
        label: role.name,
        description: role.description
      }))
    }));
  },

  /**
   * 创建角色
   */
  createRole(roleData) {
    return apiClient.post("/roles", roleData);
  },

  /**
   * 更新角色
   */
  updateRole(id, roleData) {
    return apiClient.put(`/roles/${id}`, roleData);
  },

  /**
   * 删除角色
   */
  deleteRole(id) {
    return apiClient.delete(`/roles/${id}`);
  },
};

export default roleService;
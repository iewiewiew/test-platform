import apiClient from "../../utils/request";

/**
 * 项目相关 API 服务
 */
export const projectService = {
  /**
   * 项目列表分页查询
   */
  getProjects({ page = 1, per_page = 10, name, status, sort, order } = {}) {
    const params = {
      page,
      per_page,
    };

    if (name) params.name = name;
    if (status) params.status = status;
    if (sort) params.sort = sort;
    if (order) params.order = order;

    return apiClient.get("/projects", { params }).then((response) => ({
      data: response.data.data,
      total: response.data.total,
    }));
  },

  /**
   * 获取项目详情
   */
  getProject(id) {
    return apiClient.get(`/projects/${id}`);
  },

  /**
   * 获取项目列表，用于创建 Mock 接口时选择项目
   */
  getProjectOptions({ page = 1, per_page = 10 } = {}) {
    return this.getProjects({ page, per_page });
  },

  /**
   * 创建项目
   */
  createProject(projectData) {
    return apiClient.post("/projects", projectData);
  },

  /**
   * 更新项目
   */
  updateProject(id, projectData) {
    return apiClient.put(`/projects/${id}`, projectData);
  },

  /**
   * 删除项目
   */
  deleteProject(id) {
    return apiClient.delete(`/projects/${id}`);
  },
};

export default projectService;

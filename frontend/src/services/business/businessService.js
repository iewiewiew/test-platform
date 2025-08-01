import apiClient from "../../utils/request";

/**
 * 通用业务相关 API 服务
 */
export const businessService = {
  /**
   * 新建仓库
   */
  createRepository({ environment_id, project_data }) {
    return apiClient.post("/business/create-repository", {
      environment_id,
      project_data,
    });
  },

  /**
   * 新建工作项
   */
  createIssue({ environment_id, issue_data }) {
    return apiClient.post("/business/create-issue", {
      environment_id,
      issue_data,
    });
  },
};

export default businessService;


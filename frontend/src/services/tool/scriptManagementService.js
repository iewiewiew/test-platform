import apiClient from "../../utils/request";

/**
 * 自动化脚本管理相关 API
 */
export const scriptManagementService = {
  /**
   * 获取脚本列表（分页）
   */
  getScripts({ page = 1, per_page = 20, name, script_type } = {}) {
    const params = { page, per_page };
    if (name) params.name = name;
    if (script_type) params.script_type = script_type;
    
    return apiClient.get("/script-management/scripts", { params });
  },

  /**
   * 根据ID获取脚本详情
   */
  getScriptById(id) {
    return apiClient.get(`/script-management/scripts/${id}`);
  },

  /**
   * 创建脚本
   */
  createScript(scriptData) {
    return apiClient.post("/script-management/scripts", scriptData);
  },

  /**
   * 更新脚本
   */
  updateScript(id, scriptData) {
    return apiClient.put(`/script-management/scripts/${id}`, scriptData);
  },

  /**
   * 删除脚本
   */
  deleteScript(id) {
    return apiClient.delete(`/script-management/scripts/${id}`);
  },

  /**
   * 手动执行脚本
   */
  executeScript(id, triggeredBy = 'manual') {
    return apiClient.post(`/script-management/scripts/${id}/execute`, {
      triggered_by: triggeredBy
    });
  },

  /**
   * 获取执行记录（仅用于获取最新执行记录，用于查看功能）
   */
  getExecutionHistory({ page = 1, per_page = 1, script_id, status } = {}) {
    const params = { page, per_page };
    if (script_id) params.script_id = script_id;
    if (status) params.status = status;
    
    return apiClient.get("/script-management/executions", { params });
  },

  /**
   * 获取执行记录详情
   */
  getExecutionById(id) {
    return apiClient.get(`/script-management/executions/${id}`);
  },

  /**
   * 取消正在执行的脚本
   */
  cancelExecution(id) {
    return apiClient.post(`/script-management/executions/${id}/cancel`);
  },
};

export default scriptManagementService;

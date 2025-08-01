import apiClient from "../../utils/request";

/**
 * 文档相关 API 服务
 */
export const docsService = {
  /**
   * 获取指定路径的文档内容（支持子目录路径）
   */
  getDoc(docPath) {
    return apiClient.get(`/docs/${encodeURIComponent(docPath)}`);
  },

  /**
   * 获取所有可用文档列表
   */
  getDocsList() {
    return apiClient.get("/docs/list");
  },

  /**
   * 创建新文档（支持子目录路径）
   */
  createDoc(docPath, content = '') {
    return apiClient.post("/docs", {
      path: docPath,
      content: content
    });
  },

  /**
   * 更新文档内容（支持子目录路径）
   */
  updateDoc(docPath, content) {
    return apiClient.put(`/docs/${encodeURIComponent(docPath)}`, {
      content: content
    });
  },

  /**
   * 删除文档（支持子目录路径）
   */
  deleteDoc(docPath) {
    return apiClient.delete(`/docs/${encodeURIComponent(docPath)}`);
  },
};

export default docsService;


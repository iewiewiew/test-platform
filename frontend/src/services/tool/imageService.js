import apiClient from "../../utils/request";

/**
 * 图片相关 API 服务
 */
export const imageService = {
  /**
   * 图片列表分页查询
   */
  getImages({ page = 1, per_page = 20, filename, tags } = {}) {
    const params = {
      page,
      per_page,
    };

    if (filename) params.filename = filename;
    if (tags) params.tags = tags;

    return apiClient.get("/images", { params });
  },

  /**
   * 获取图片详情
   */
  getImage(id) {
    return apiClient.get(`/images/${id}`);
  },

  /**
   * 上传图片
   */
  uploadImage(file, description = '', tags = '') {
    const formData = new FormData();
    formData.append('file', file);
    if (description) formData.append('description', description);
    if (tags) formData.append('tags', tags);

    return apiClient.post("/images", formData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      }
    });
  },

  /**
   * 更新图片信息（支持更新图片文件，但保留原有 UUID）
   * @param {number} id - 图片ID
   * @param {object} imageData - 图片数据对象
   * @param {string} imageData.description - 图片描述（可选）
   * @param {string} imageData.tags - 图片标签（可选）
   * @param {File} imageData.file - 新的图片文件（可选，如果提供将替换原文件但保留UUID）
   */
  updateImage(id, imageData) {
    // 如果包含文件，使用 FormData 上传
    if (imageData.file) {
      const formData = new FormData();
      formData.append('file', imageData.file);
      if (imageData.description !== undefined) {
        formData.append('description', imageData.description || '');
      }
      if (imageData.tags !== undefined) {
        formData.append('tags', imageData.tags || '');
      }

      return apiClient.put(`/images/${id}`, formData, {
        headers: {
          'Content-Type': 'multipart/form-data'
        }
      });
    } else {
      // 如果没有文件，使用 JSON 格式
      return apiClient.put(`/images/${id}`, imageData);
    }
  },

  /**
   * 删除图片
   */
  deleteImage(id) {
    return apiClient.delete(`/images/${id}`);
  },

  /**
   * 批量删除图片
   */
  batchDeleteImages(ids) {
    return apiClient.delete("/images/batch", {
      data: { ids }
    });
  },
};

export default imageService;


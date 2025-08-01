import apiClient from '../../utils/request'

/**
 * 环境管理相关 API 服务
 */
export const environmentService = {
  /**
   * 环境列表默认查询，没有分页, 用于获取所有环境列表
   */
  getEnvironments_default() {
    return apiClient.get('/environments')
  },

  /**
   * 环境列表分页查询
   */
  async getEnvironments({ page = 1, per_page = 10, search, project_id } = {}) {
    const params = { page, per_page }

    // 添加搜索条件（如果存在）
    if (search) params.search = search
    if (project_id) params.project_id = project_id

    const response = await apiClient.get('/environments', { params })
    return {
      data: response.data.data,
      total: response.data.total,
      page: response.data.page,
      per_page: response.data.per_page
    }
  },

  /**
   * 查看环境详情
   */
  getEnvironment(id) {
    return apiClient.get(`/environments/${id}`)
  },

  /**
   * 创建环境
   */
  createEnvironment(environment) {
    return apiClient.post('/environments', environment)
  },

  /**
   * 更新环境
   */
  updateEnvironment(id, environment) {
    return apiClient.put(`/environments/${id}`, environment)
  },

  /**
   * 删除环境
   */
  deleteEnvironment(id) {
    return apiClient.delete(`/environments/${id}`)
  },

  /**
   * 复制环境
   */
  copyEnvironment(id, new_name) {
    return apiClient.post(`/environments/${id}/copy`, { new_name })
  },

  /**
   * 获取环境统计信息
   */
  getEnvironmentStats(id) {
    return apiClient.get(`/environments/${id}/stats`)
  },

  /**
   * 环境参数列表分页查询
   */
  async getEnvironmentParameters(environment_id, { page = 1, per_page = 10, search } = {}) {
    const params = { page, per_page }

    // 添加搜索条件（如果存在）
    if (search) params.search = search

    const response = await apiClient.get(`/environments/${environment_id}/parameters`, { params })
    return {
      data: response.data.data,
      total: response.data.total,
      page: response.data.page,
      per_page: response.data.per_page,
      environment: response.data.environment
    }
  },

  /**
   * 创建环境参数
   */
  createEnvironmentParameter(environment_id, parameter) {
    return apiClient.post(`/environments/${environment_id}/parameters`, parameter)
  },

  /**
   * 更新环境参数
   */
  updateEnvironmentParameter(id, parameter) {
    return apiClient.put(`/parameters/${id}`, parameter)
  },

  /**
   * 删除环境参数
   */
  deleteEnvironmentParameter(id) {
    return apiClient.delete(`/parameters/${id}`)
  },

  /**
   * 批量操作环境
   */
  batchEnvironments(operation, environment_ids) {
    return apiClient.post('/environments/batch', {
      operation,
      environment_ids
    })
  },

  /**
   * 导出环境配置
   */
  exportEnvironment(id) {
    return apiClient.get(`/environments/export/${id}`)
  },

  /**
   * 导入环境配置
   */
  importEnvironment(import_data) {
    return apiClient.post('/environments/import', import_data)
  },

  /**
   * 验证环境配置
   */
  validateEnvironment(environment_data) {
    return apiClient.post('/environments/validate', environment_data)
  },

  /**
   * 搜索环境（支持多种搜索条件）
   */
  async searchEnvironments({ type = 'all', keyword = '', project_id, page = 1, per_page = 10 } = {}) {
    const params = {
      type,
      keyword,
      page,
      per_page
    }

    // 添加项目ID条件（如果存在）
    if (project_id) params.project_id = project_id

    const response = await apiClient.get('/environments/search', { params })
    return {
      search_type: response.data.search_type,
      keyword: response.data.keyword,
      data: response.data.results.data,
      total: response.data.results.total,
      page: response.data.results.page,
      per_page: response.data.results.per_page
    }
  },

  /**
   * 获取环境参数统计
   */
  async getEnvironmentParameterStats(environment_id) {
    const response = await this.getEnvironmentStats(environment_id)
    return {
      parameter_stats: response.data.parameter_stats,
      total_parameters: response.data.total_parameters
    }
  },

  /**
   * 快速创建环境（带默认参数）
   */
  quickCreateEnvironment(name, base_url, description = '') {
    return this.createEnvironment({
      name,
      base_url,
      description
    })
  },

  /**
   * 批量创建环境参数
   */
  async batchCreateParameters(environment_id, parameters) {
    const results = []

    for (const parameter of parameters) {
      try {
        const response = await this.createEnvironmentParameter(environment_id, parameter)
        results.push({
          param_key: parameter.param_key,
          status: 'success',
          data: response.data
        })
      } catch (error) {
        results.push({
          param_key: parameter.param_key,
          status: 'error',
          error: error.message
        })
      }
    }

    return results
  },

  /**
   * 检查环境名称是否可用
   */
  async checkEnvironmentName(name, project_id = null) {
    try {
      // 尝试搜索该名称的环境
      const params = { search: name, per_page: 1 }
      if (project_id) params.project_id = project_id

      const response = await this.getEnvironments(params)

      // 检查是否有重名的环境
      const existing = response.data.find((env) => env.name === name)

      return {
        available: !existing,
        existing_environment: existing || null
      }
    } catch (error) {
      return {
        available: false,
        error: error.message
      }
    }
  },

  /**
   * 获取环境的基础URL
   */
  async getEnvironmentBaseUrl(environment_id) {
    try {
      const response = await this.getEnvironment(environment_id)
      return response.data.base_url
    } catch (error) {
      throw new Error(`获取环境基础URL失败: ${error.message}`)
    }
  },

  /**
   * 获取环境的完整参数列表（不分页）
   */
  async getAllEnvironmentParameters(environment_id) {
    try {
      // 使用较大的 per_page 值获取所有参数
      const response = await this.getEnvironmentParameters(environment_id, {
        page: 1,
        per_page: 1000 // 假设最多1000个参数
      })
      return response.data
    } catch (error) {
      throw new Error(`获取环境参数失败: ${error.message}`)
    }
  },

  /**
   * 根据参数键获取参数值
   */
  async getParameterValue(environment_id, param_key) {
    try {
      const parameters = await this.getAllEnvironmentParameters(environment_id)
      const parameter = parameters.find((param) => param.param_key === param_key)
      return parameter ? parameter.param_value : null
    } catch (error) {
      throw new Error(`获取参数值失败: ${error.message}`)
    }
  },

  /**
   * 环境配置预览
   */
  async previewEnvironmentConfig(environment_id) {
    try {
      const [environment, parameters, stats] = await Promise.all([this.getEnvironment(environment_id), this.getAllEnvironmentParameters(environment_id), this.getEnvironmentStats(environment_id)])

      return {
        environment: environment.data,
        parameters: parameters,
        stats: stats.data,
        preview_time: new Date().toISOString()
      }
    } catch (error) {
      throw new Error(`生成环境配置预览失败: ${error.message}`)
    }
  },

  /**
   * 环境健康检查（通过后端代理，避免CORS问题）
   */
  async healthCheck(environment_id) {
    try {
      const response = await apiClient.post(`/environments/${environment_id}/health-check`)
      return response.data
    } catch (error) {
      throw new Error(`环境健康检查失败: ${error.message}`)
    }
  }
}

export default environmentService

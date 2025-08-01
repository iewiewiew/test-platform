import apiClient from '../../utils/request'

/**
 * MCP (Model Context Protocol) API 服务
 */
export const mcpService = {
  // ==================== MCP 资源管理 ====================

  /**
   * 列出所有可用的 MCP 资源
   */
  listResources() {
    return apiClient.get('/mcp/resources')
  },

  /**
   * 读取指定的 MCP 资源
   * @param {string} uri - 资源 URI
   */
  readResource(uri) {
    return apiClient.post('/mcp/resources/read', { uri })
  },

  // ==================== MCP 工具管理 ====================

  /**
   * 列出所有可用的 MCP 工具
   */
  listTools() {
    return apiClient.get('/mcp/tools')
  },

  /**
   * 调用指定的 MCP 工具
   * @param {string} name - 工具名称
   * @param {object} args - 工具参数
   */
  callTool(name, args) {
    return apiClient.post('/mcp/tools/call', { name, arguments: args })
  },

  // ==================== MCP 提示管理 ====================

  /**
   * 列出所有可用的 MCP 提示模板
   */
  listPrompts() {
    return apiClient.get('/mcp/prompts')
  },

  /**
   * 获取指定的 MCP 提示模板
   * @param {string} name - 提示名称
   * @param {object} args - 提示参数
   */
  getPrompt(name, args) {
    return apiClient.post('/mcp/prompts/get', { name, arguments: args })
  }
}

export default mcpService

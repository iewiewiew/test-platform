import apiClient from "../../utils/request";

/**
 * SQL工具箱相关 API 服务
 */
export const sqlService = {
  /**
   * 执行SQL查询
   * @param {string} sqlQuery - SQL查询语句
   * @param {number} limit - 结果限制条数
   * @param {number} connectionId - 连接ID
   * @param {string} databaseName - 数据库名称
   */
  executeSQL(sqlQuery, limit = 1000, connectionId = null, databaseName = null) {
    const data = {
      sql_query: sqlQuery,
      limit: limit
    };

    if (connectionId) data.connection_id = connectionId;
    if (databaseName) data.database_name = databaseName;

    return apiClient.post("/sql/execute", data).then((response) => ({
      success: response.data.success,
      data: response.data.data,
      execution_time: response.data.execution_time,
      error: response.data.error,
      connection_id: response.data.connection_id,
      database: response.data.database
    }));
  },

  /**
   * 获取数据库连接列表
   */
  getConnections() {
    return apiClient.get("/sql/connections").then((response) => ({
      data: response.data.data,
      total: response.data.total || response.data.data.length
    }));
  },

  /**
   * 获取数据库连接详情
   * @param {number} connectionId - 连接ID
   */
  getConnection(connectionId) {
    return apiClient.get(`/sql/connections/${connectionId}`).then((response) => ({
      success: response.data.success,
      data: response.data.data
    }));
  },

  /**
   * 测试数据库连接
   * @param {Object} connectionData - 连接数据
   */
  testConnection(connectionData) {
    return apiClient.post("/sql/connections/test", connectionData).then((response) => ({
      success: response.data.success,
      message: response.data.message,
      error: response.data.error
    }));
  },

  /**
   * 创建数据库连接
   * @param {Object} connectionData - 连接数据
   */
  createConnection(connectionData) {
    return apiClient.post("/sql/connections", connectionData).then((response) => ({
      success: response.data.success,
      data: response.data.data,
      message: response.data.message
    }));
  },

  /**
   * 更新数据库连接
   * @param {number} connectionId - 连接ID
   * @param {Object} connectionData - 连接数据
   */
  updateConnection(connectionId, connectionData) {
    return apiClient.put(`/sql/connections/${connectionId}`, connectionData).then((response) => ({
      success: response.data.success,
      data: response.data.data,
      message: response.data.message
    }));
  },

  /**
   * 删除数据库连接
   * @param {number} connectionId - 连接ID
   */
  deleteConnection(connectionId) {
    return apiClient.delete(`/sql/connections/${connectionId}`).then((response) => ({
      success: response.data.success,
      message: response.data.message
    }));
  },

  /**
   * 获取连接下的数据库列表
   * @param {number} connectionId - 连接ID
   */
  getConnectionDatabases(connectionId) {
    return apiClient.get(`/sql/connections/${connectionId}/databases`).then((response) => ({
      success: response.data.success,
      data: response.data.data,
      databases: response.data.databases,
      error: response.data.error
    }));
  },

  /**
   * 获取连接信息
   * @param {number} connectionId - 连接ID
   */
  getConnectionInfo(connectionId) {
    return apiClient.get(`/sql/connections/${connectionId}/info`).then((response) => ({
      success: response.data.success,
      data: response.data.data,
      databases: response.data.databases,
      current_database: response.data.current_database,
      version: response.data.version,
      error: response.data.error
    }));
  },

  /**
   * 切换数据库
   * @param {number} connectionId - 连接ID
   * @param {string} databaseName - 数据库名称
   */
  switchDatabase(connectionId, databaseName) {
    return apiClient.post("/sql/databases/switch", {
      connection_id: connectionId,
      database_name: databaseName
    }).then((response) => ({
      success: response.data.success,
      message: response.data.message,
      error: response.data.error
    }));
  },

  /**
   * 获取数据库表列表
   * @param {number} connectionId - 连接ID
   * @param {string} databaseName - 数据库名称
   */
  getDatabaseTables(connectionId, databaseName) {
    return apiClient.get(`/sql/databases/${databaseName}/tables`, {
      params: { connection_id: connectionId }
    }).then((response) => ({
      success: response.data.success,
      tables: response.data.tables,
      error: response.data.error
    }));
  },

  /**
   * 获取表结构信息
   * @param {number} connectionId - 连接ID
   * @param {string} databaseName - 数据库名称
   * @param {string} tableName - 表名称
   */
  getTableStructure(connectionId, databaseName, tableName) {
    return apiClient.get(`/sql/databases/${databaseName}/tables/${tableName}/structure`, {
      params: { connection_id: connectionId }
    }).then((response) => ({
      success: response.data.success,
      structure: response.data.structure,
      error: response.data.error
    }));
  },

  /**
   * 获取数据库信息
   * @param {number} connectionId - 连接ID
   */
  getDatabaseInfo(connectionId = null) {
    const params = connectionId ? { connection_id: connectionId } : {};
    return apiClient.get("/sql/database-info", { params }).then((response) => ({
      success: response.data.success,
      data: response.data.data,
      databases: response.data.databases,
      current_database: response.data.current_database,
      version: response.data.version,
      error: response.data.error
    }));
  },

  /**
   * 获取SQL模板列表
   * @param {Object} params - 查询参数
   * @param {number} params.page - 页码
   * @param {number} params.per_page - 每页数量
   * @param {string} params.name - 模板名称搜索
   * @param {string} params.category - 分类筛选
   */
  getTemplates({ page = 1, per_page = 100, name, category } = {}) {
    const params = {
      page,
      per_page
    };

    if (name) params.name = name;
    if (category) params.category = category;

    return apiClient.get("/sql/templates", { params }).then((response) => ({
      data: response.data.data,
      total: response.data.total || response.data.data.length
    }));
  },

  /**
   * 获取SQL模板详情
   * @param {number} templateId - 模板ID
   */
  getTemplate(templateId) {
    return apiClient.get(`/sql/templates/${templateId}`).then((response) => ({
      success: response.data.success,
      data: response.data.data
    }));
  },

  /**
   * 创建SQL模板
   * @param {Object} templateData - 模板数据
   */
  createTemplate(templateData) {
    return apiClient.post("/sql/templates", templateData).then((response) => ({
      success: response.data.success,
      data: response.data.data,
      message: response.data.message
    }));
  },

  /**
   * 更新SQL模板
   * @param {number} templateId - 模板ID
   * @param {Object} templateData - 模板数据
   */
  updateTemplate(templateId, templateData) {
    return apiClient.put(`/sql/templates/${templateId}`, templateData).then((response) => ({
      success: response.data.success,
      data: response.data.data,
      message: response.data.message
    }));
  },

  /**
   * 删除SQL模板
   * @param {number} templateId - 模板ID
   */
  deleteTemplate(templateId) {
    return apiClient.delete(`/sql/templates/${templateId}`).then((response) => ({
      success: response.data.success,
      message: response.data.message
    }));
  },

  /**
   * 获取查询历史记录
   * @param {Object} params - 查询参数
   * @param {number} params.page - 页码
   * @param {number} params.per_page - 每页数量
   * @param {boolean} params.success - 执行状态筛选
   * @param {number} params.connection_id - 连接ID筛选
   */
  getHistory({ page = 1, per_page = 50, success, connection_id } = {}) {
    const params = {
      page,
      per_page
    };

    if (success !== undefined) params.success = success;
    if (connection_id) params.connection_id = connection_id;

    return apiClient.get("/sql/history", { params }).then((response) => ({
      data: response.data.data,
      total: response.data.total || response.data.data.length
    }));
  },

  /**
   * 获取分类列表
   */
  getCategories() {
    return apiClient.get("/sql/categories").then((response) => ({
      data: response.data.data,
      total: response.data.total
    }));
  },

  /**
   * 批量删除查询历史
   * @param {Array} historyIds - 历史记录ID数组
   */
  deleteHistoryBatch(historyIds) {
    return apiClient.post("/sql/history/batch-delete", {
      history_ids: historyIds
    }).then((response) => ({
      success: response.data.success,
      message: response.data.message,
      deleted_count: response.data.deleted_count
    }));
  },

  /**
   * 清空查询历史
   */
  clearHistory() {
    return apiClient.delete("/sql/history/clear").then((response) => ({
      success: response.data.success,
      message: response.data.message
    }));
  },

  /**
   * 设置当前连接
   * @param {Object} connection - 连接对象
   */
  setCurrentConnection(connection) {
    // 这里可以添加本地存储逻辑
    if (connection) {
      localStorage.setItem('currentConnection', JSON.stringify(connection));
    } else {
      localStorage.removeItem('currentConnection');
    }
    return Promise.resolve({ success: true });
  },

  /**
   * 获取当前连接
   */
  getCurrentConnection() {
    const saved = localStorage.getItem('currentConnection');
    return saved ? JSON.parse(saved) : null;
  },

  /**
   * 设置当前数据库
   * @param {string} database - 数据库名称
   */
  setCurrentDatabase(database) {
    if (database) {
      localStorage.setItem('currentDatabase', database);
    } else {
      localStorage.removeItem('currentDatabase');
    }
    return Promise.resolve({ success: true });
  },

  /**
   * 获取当前数据库
   */
  getCurrentDatabase() {
    return localStorage.getItem('currentDatabase') || '';
  }
};

export default sqlService;
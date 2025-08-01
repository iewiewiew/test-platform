import apiClient from "../../utils/request";

/**
 * 认证相关 API 服务
 */
export const authService = {
  /**
   * 用户登录
   */
  login(credentials) {
    console.log('🔐 authService.login - 发送登录请求');
    return apiClient.post("/auth/login", credentials);
  },

  /**
   * 获取当前用户信息
   */
  getCurrentUser() {
    console.log('👤 authService.getCurrentUser - 获取当前用户');
    return apiClient.get("/auth/me");
  },
};

export default authService;
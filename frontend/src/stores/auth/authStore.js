import { defineStore } from 'pinia';
import { authService } from '@/services/auth/authService';

export const useAuthStore = defineStore('auth', {
  state: () => ({
    user: null, // 用户信息，包含 role 和 permissions
    token: null,
    isAuthenticated: false,
    initialized: false
  }),

  getters: {
    currentUser: (state) => state.user,
    isLoggedIn: (state) => state.isAuthenticated,
    // 添加权限相关的 getter
    userPermissions: (state) => {
      return state.user?.role?.permissions || [];
    },
    hasPermission: (state) => {
      return (permission) => {
        const permissions = state.user?.role?.permissions || [];
        return permissions.includes(permission);
      };
    }
  },

  actions: {
    async login(credentials) {
      try {
        console.log('🔐 开始登录，用户名:', credentials.username);

        const response = await authService.login(credentials);
        const { token, user } = response.data;

        console.log('✅ 登录响应:', { token: !!token, user: !!user });

        if (!token) {
          throw new Error('服务器未返回 token');
        }

        // 确保用户数据结构包含权限信息
        const userWithPermissions = this.normalizeUserData(user);
        
        // 保存到 store 和 localStorage
        this.setAuthData(token, userWithPermissions);

        console.log('💾 登录成功 - localStorage token:', localStorage.getItem('token') ? '已保存' : '未保存');
        console.log('👤 登录成功 - 用户信息:', this.user);
        console.log('🔑 用户权限:', this.user?.role?.permissions);

        return { success: true };
      } catch (error) {
        console.error('❌ 登录失败:', error);
        this.clearAuthData();
        return {
          success: false,
          message: error.response?.data?.message || error.message || '登录失败'
        };
      }
    },

    async checkAuth() {
      console.log('🔍 开始检查认证状态');

      const token = this.getValidToken();
      console.log('🔑 checkAuth - localStorage token:', token ? '存在' : '不存在');

      if (!token) {
        console.log('❌ checkAuth: token 不存在');
        this.clearAuthData();
        return false;
      }

      try {
        console.log('📡 checkAuth: 调用 /api/auth/me');
        const response = await authService.getCurrentUser();
        console.log('✅ checkAuth 响应:', response.data);

        if (response.data.user) {
          // 规范化用户数据，确保包含权限信息
          const userData = this.normalizeUserData(response.data.user);
          this.setAuthData(token, userData);
          console.log('🎉 checkAuth: 认证成功');
          console.log('🔑 用户权限:', this.user?.role?.permissions);
          return true;
        } else {
          console.log('❌ checkAuth: 服务器返回空用户');
          this.clearAuthData();
          return false;
        }
      } catch (error) {
        console.error('❌ checkAuth 失败:', error);
        this.clearAuthData();
        return false;
      }
    },

    // 规范化用户数据，确保包含权限结构
    normalizeUserData(userData) {
      if (!userData) return null;

      // 如果用户数据已经有正确的结构，直接返回
      if (userData.role && Array.isArray(userData.role.permissions)) {
        return userData;
      }

      // 如果没有 role 字段，创建默认结构
      if (!userData.role) {
        return {
          ...userData,
          role: {
            name: userData.roleName || 'user',
            permissions: userData.permissions || [] // 从用户数据的 permissions 字段获取
          }
        };
      }

      // 如果 role 没有 permissions 字段
      if (!userData.role.permissions) {
        return {
          ...userData,
          role: {
            ...userData.role,
            permissions: userData.permissions || [] // 从用户数据的 permissions 字段获取
          }
        };
      }

      return userData;
    },

    // 设置认证数据（store + localStorage）
    setAuthData(token, user) {
      // 验证数据有效性
      if (!token || !user) {
        console.error('❌ setAuthData: token 或 user 为空');
        return;
      }

      this.token = token;
      this.user = user;
      this.isAuthenticated = true;

      // 安全地存储到 localStorage
      try {
        localStorage.setItem('token', token);
        localStorage.setItem('user', JSON.stringify(user));
        console.log('💾 认证数据已保存到 localStorage');
      } catch (error) {
        console.error('❌ 保存到 localStorage 失败:', error);
      }
    },

    // 清除认证数据
    clearAuthData() {
      this.user = null;
      this.token = null;
      this.isAuthenticated = false;

      try {
        localStorage.removeItem('token')
        localStorage.removeItem('user')
        localStorage.removeItem('isLoggedIn')
        localStorage.removeItem('username')
        console.log('🧹 认证数据已从 localStorage 清除');
      } catch (error) {
        console.error('❌ 清除 localStorage 失败:', error);
      }
    },

    // 安全地获取 token
    getValidToken() {
      try {
        const token = localStorage.getItem('token');
        if (token && token !== 'undefined' && token !== 'null') {
          return token;
        }
        return null;
      } catch (error) {
        console.error('❌ 获取 token 失败:', error);
        return null;
      }
    },

    // 安全地获取用户数据
    getValidUserData() {
      try {
        const userData = localStorage.getItem('user');
        if (userData && userData !== 'undefined' && userData !== 'null') {
          const parsedUser = JSON.parse(userData);
          // 规范化存储的用户数据
          const normalizedUser = this.normalizeUserData(parsedUser);
          if (normalizedUser && typeof normalizedUser === 'object' && normalizedUser.id && normalizedUser.username) {
            return normalizedUser;
          }
        }
        return null;
      } catch (error) {
        console.error('❌ 解析用户数据失败:', error);
        return null;
      }
    },

    logout() {
      console.log('🚪 执行登出操作');
      this.clearAuthData();
    },

    // 初始化方法 - 从 localStorage 恢复状态
    initialize() {
      if (this.initialized) {
        console.log('🔄 认证状态已初始化，跳过');
        return;
      }

      console.log('🔄 开始初始化认证状态');

      const token = this.getValidToken();
      const userData = this.getValidUserData();

      console.log('📊 初始化检查:', {
        token: !!token,
        userData: !!userData
      });

      if (token && userData) {
        try {
          this.token = token;
          this.user = userData;
          this.isAuthenticated = true;
          console.log('✅ 从 localStorage 恢复认证状态成功');
          console.log('👤 恢复的用户:', this.user.username);
          console.log('🔑 用户权限:', this.user?.role?.permissions);
        } catch (e) {
          console.error('❌ 从 localStorage 恢复认证状态失败:', e);
          this.clearAuthData();
        }
      } else {
        console.log('ℹ️ localStorage 中无有效认证信息，清除可能存在的无效数据');
        this.clearAuthData();
      }

      this.initialized = true;
      console.log('🎯 认证状态初始化完成');
    },

    // 检查权限的便捷方法
    can(permission) {
      const permissions = this.user?.role?.permissions || [];
      return permissions.includes(permission);
    }
  }
});
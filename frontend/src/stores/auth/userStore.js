import { defineStore } from 'pinia';
import { userService } from '@/services/auth/userService';

export const useUserStore = defineStore('user', {
  state: () => ({
    users: [],
    currentUser: null,
    pagination: {
      currentPage: 1,
      total: 0,
      pageSize: 10
    },
    loading: false
  }),

  getters: {
    userList: (state) => state.users,
    paginationInfo: (state) => state.pagination
  },

  actions: {
    async fetchUsers(params = {}) {
      this.loading = true;
      try {
        const response = await userService.getUsers(params);
        this.users = response.data;
        this.pagination = {
          currentPage: response.current_page || params.page || this.pagination.currentPage,
          total: response.total || 0,
          pageSize: response.per_page || params.per_page || this.pagination.pageSize
        };
        return { success: true };
      } catch (error) {
        return {
          success: false,
          message: error.response?.data?.message || '获取用户列表失败'
        };
      } finally {
        this.loading = false;
      }
    },

    async fetchUserById(id) {
      try {
        const response = await userService.getUserById(id);
        console.log('用户详情-------:', response.data)
        this.currentUser = response.data.user;
        return response.data;
      } catch (error) {
        return {
          success: false,
          message: error.response?.data?.message || '获取用户信息失败'
        };
      }
    },

    async createUser(userData) {
      try {
        const response = await userService.createUser(userData);
        this.users.unshift(response.data.user);
        return { success: true, data: response.data };
      } catch (error) {
        return {
          success: false,
          message: error.response?.data?.message || '创建用户失败'
        };
      }
    },

    async updateUser(id, userData) {
      try {
        const response = await userService.updateUser(id, userData);
        const index = this.users.findIndex(user => user.id === id);
        if (index !== -1) {
          this.users[index] = response.data.user;
        }
        return { success: true, data: response.data };
      } catch (error) {
        return {
          success: false,
          message: error.response?.data?.message || '更新用户失败'
        };
      }
    },

    async deleteUser(id) {
      try {
        await userService.deleteUser(id);
        this.users = this.users.filter(user => user.id !== id);
        return { success: true };
      } catch (error) {
        return {
          success: false,
          message: error.response?.data?.message || '删除用户失败'
        };
      }
    }
  }
});
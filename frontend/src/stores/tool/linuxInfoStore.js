import { defineStore } from 'pinia';
import linuxInfoService from '@/services/tool/linuxInfoService';

export const useLinuxInfoStore = defineStore('linuxInfo', {
  state: () => ({
    servers: [],
    currentServer: null,
    commandResult: null,
    serverInfo: null,
    loading: false,
    error: null,
    pagination: {
      total: 0,
      page: 1,
      per_page: 10
    }
  }),

  actions: {
    async fetchServers({ page = 1, per_page = 10, server_name, host } = {}) {
      this.loading = true;
      this.error = null;
      try {
        const response = await linuxInfoService.getServers({ page, per_page, server_name, host });
        this.servers = response.data;
        this.pagination = {
          total: response.total,
          page: page,
          per_page: per_page
        };
      } catch (error) {
        this.error = error.message;
      } finally {
        this.loading = false;
      }
    },

    async fetchServer(serverId) {
      this.loading = true;
      this.error = null;
      try {
        const response = await linuxInfoService.getServer(serverId);
        if (response.success) {
          this.currentServer = response.data;
        } else {
          this.error = response.error;
        }
      } catch (error) {
        this.error = error.message;
      } finally {
        this.loading = false;
      }
    },

    async createServer(serverData) {
      this.loading = true;
      this.error = null;
      try {
        const response = await linuxInfoService.createServer(serverData);
        if (response.status == 201) {
          await this.fetchServers();
          return response.data;
        } else {
          this.error = response.error;
          return response;
        }
      } catch (error) {
        this.error = error.message;
        return error.response.data;
      } finally {
        this.loading = false;
      }
    },

    async updateServer(serverId, serverData) {
      this.loading = true;
      this.error = null;
      try {
        const response = await linuxInfoService.updateServer(serverId, serverData);
        if (response.status == 200) {
          await this.fetchServers();
          return response.data;
        } else {
          this.error = response.error;
          return null;
        }
      } catch (error) {
        this.error = error.message;
        return null;
      } finally {
        this.loading = false;
      }
    },

    async deleteServer(serverId) {
      this.loading = true;
      this.error = null;
      try {
        const response = await linuxInfoService.deleteServer(serverId);
        if (response.status == 200) {
          await this.fetchServers();
          return true;
        } else {
          this.error = response.error;
          return false;
        }
      } catch (error) {
        this.error = error.message;
        return false;
      } finally {
        this.loading = false;
      }
    },

    async executeCommand(serverId, command) {
      this.loading = true;
      this.error = null;
      try {
        const response = await linuxInfoService.executeCommand(serverId, command);
        this.commandResult = response.data;
        return this.commandResult;
      } catch (error) {
        this.error = error.message;
        return null;
      } finally {
        this.loading = false;
      }
    },

    async fetchServerInfo(serverId) {
      this.loading = true;
      this.error = null;
      try {
        const response = await linuxInfoService.getServerInfo(serverId);
        if (response.status == 200) {
          this.serverInfo = response.data;
        } else {
          this.error = response.error;
        }
      } catch (error) {
        this.error = error.message;
      } finally {
        this.loading = false;
      }
    },

    clearError() {
      this.error = null;
    },

    clearCurrentServer() {
      this.currentServer = null;
    },

    clearCommandResult() {
      this.commandResult = null;
    },

    clearServerInfo() {
      this.serverInfo = null;
    }
  },

  getters: {
    getServerById: (state) => (id) => {
      return state.servers.find(server => server.id === id);
    }
  }
});
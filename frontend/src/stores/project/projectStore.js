import { defineStore } from 'pinia'
import { projectService } from '@/services/project/projectService'

export const useProjectStore = defineStore('project', {
  state: () => ({
    projects: [],
    currentProject: null,
    pagination: {
      currentPage: 1,
      pageSize: 10,
      total: 0,
      totalPages: 1
    },
    loading: false,
    error: null,
    stats: null
  }),

  actions: {
    // 项目列表分页查询
    async fetchProjects(params = {}) {
      this.loading = true
      this.error = null
      try {
        const response = await projectService.getProjects({
          page: params.page || this.pagination.currentPage,
          per_page: params.pageSize || this.pagination.pageSize,
          name: params.name,
          status: params.status,
          sort: params.sort,
          order: params.order
        })

        this.projects = response.data
        this.pagination = {
          currentPage: response.currentPage || (params.page || this.pagination.currentPage),
          pageSize: params.pageSize || this.pagination.pageSize,
          total: response.total,
          totalPages: response.totalPages
        }
        return response.data
      } catch (error) {
        this.error = error.response?.data?.message || error.message || 'Failed to fetch projects'
        throw error
      } finally {
        this.loading = false
      }
    },

    // 获取项目详情
    async fetchProject(id) {
      this.loading = true
      this.error = null
      try {
        const response = await projectService.getProject(id)
        this.currentProject = response.data
        return response.data
      } catch (error) {
        this.error = error.response?.data?.message || error.message || 'Failed to fetch project'
        throw error
      } finally {
        this.loading = false
      }
    },

    // 创建项目
    async createProject(projectData) {
      this.loading = true
      this.error = null
      try {
        const response = await projectService.createProject(projectData)
        await this.fetchProjects({
          page: this.pagination.currentPage,
          pageSize: this.pagination.pageSize
        })
        return response.data
      } catch (error) {
        this.error = error.response?.data?.message || error.message || 'Failed to create project'
        throw error
      } finally {
        this.loading = false
      }
    },

    // 更新项目
    async updateProject(id, projectData) {
      this.loading = true
      this.error = null
      try {
        const response = await projectService.updateProject(id, projectData)
        this.currentProject = response.data
        await this.fetchProjects({
          page: this.pagination.currentPage,
          pageSize: this.pagination.pageSize
        })
        return response.data
      } catch (error) {
        this.error = error.response?.data?.message || error.message || 'Failed to update project'
        throw error
      } finally {
        this.loading = false
      }
    },

    // 删除项目
    async deleteProject(id) {
      this.loading = true
      this.error = null
      try {
        await projectService.deleteProject(id)
        
        if (this.currentProject?.id === id) {
          this.currentProject = null
        }
        
        await this.fetchProjects({
          page: this.projects.length === 1 && this.pagination.currentPage > 1
            ? this.pagination.currentPage - 1
            : this.pagination.currentPage,
          pageSize: this.pagination.pageSize
        })
      } catch (error) {
        this.error = error.response?.data?.message || error.message || 'Failed to delete project'
        throw error
      } finally {
        this.loading = false
      }
    },

    // 获取项目统计信息
    async fetchProjectStats(id) {
      this.loading = true
      this.error = null
      try {
        const response = await projectService.getProjectStats(id)
        this.stats = response.data
        return response.data
      } catch (error) {
        this.error = error.response?.data?.message || error.message || 'Failed to fetch project stats'
        throw error
      } finally {
        this.loading = false
      }
    },
  }
})
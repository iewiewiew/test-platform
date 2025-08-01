import { defineStore } from 'pinia'
import { imageService } from '@/services/tool/imageService'

export const useImageStore = defineStore('image', {
  state: () => ({
    images: [],
    currentImage: null,
    pagination: {
      currentPage: 1,
      pageSize: 20,
      total: 0,
      totalPages: 1
    },
    loading: false,
    error: null
  }),

  actions: {
    // 图片列表分页查询
    async fetchImages(params = {}) {
      this.loading = true
      this.error = null
      try {
        const response = await imageService.getImages({
          page: params.page || this.pagination.currentPage,
          per_page: params.pageSize || this.pagination.pageSize,
          filename: params.filename
        })

        const result = response.data.data || {}
        this.images = result.data || []

        // 处理分页数据
        this.pagination = {
          currentPage: result.page || params.page || this.pagination.currentPage,
          pageSize: result.per_page || params.pageSize || this.pagination.pageSize,
          total: result.total || 0,
          totalPages: result.pages || 1
        }
        
        return this.images
      } catch (error) {
        this.error = error.response?.data?.message || error.message || '获取图片列表失败'
        this.images = []
        throw error
      } finally {
        this.loading = false
      }
    },

    // 获取图片详情
    async fetchImage(id) {
      this.loading = true
      this.error = null
      try {
        const response = await imageService.getImage(id)
        this.currentImage = response?.data.data || null
        return this.currentImage
      } catch (error) {
        this.error = error.response?.data?.message || error.message || '获取图片详情失败'
        this.currentImage = null
        throw error
      } finally {
        this.loading = false
      }
    },

    // 上传图片
    async uploadImage(file, description = '') {
      this.loading = true
      this.error = null
      try {
        const response = await imageService.uploadImage(file, description)
        await this.fetchImages({
          page: this.pagination.currentPage,
          pageSize: this.pagination.pageSize
        })
        return response?.data
      } catch (error) {
        this.error = error.response?.data?.message || error.message || '上传图片失败'
        throw error
      } finally {
        this.loading = false
      }
    },

    // 更新图片信息
    async updateImage(id, imageData) {
      this.loading = true
      this.error = null
      try {
        const response = await imageService.updateImage(id, imageData)
        this.currentImage = response?.data.data || null
        await this.fetchImages({
          page: this.pagination.currentPage,
          pageSize: this.pagination.pageSize
        })
        return this.currentImage
      } catch (error) {
        this.error = error.response?.data?.message || error.message || '更新图片失败'
        throw error
      } finally {
        this.loading = false
      }
    },

    // 删除图片
    async deleteImage(id) {
      this.loading = true
      this.error = null
      try {
        await imageService.deleteImage(id)
        
        if (this.currentImage?.id === id) {
          this.currentImage = null
        }
        
        await this.fetchImages({
          page: this.images.length === 1 && this.pagination.currentPage > 1
            ? this.pagination.currentPage - 1
            : this.pagination.currentPage,
          pageSize: this.pagination.pageSize
        })
      } catch (error) {
        this.error = error.response?.data?.message || error.message || '删除图片失败'
        throw error
      } finally {
        this.loading = false
      }
    },

    // 批量删除图片
    async batchDeleteImages(ids) {
      this.loading = true
      this.error = null
      try {
        const response = await imageService.batchDeleteImages(ids)
        
        if (this.currentImage && ids.includes(this.currentImage.id)) {
          this.currentImage = null
        }
        
        const currentPageCount = this.images.length
        const deletedCount = response?.data?.data?.success_count || ids.length
        const shouldGoToPreviousPage = currentPageCount <= deletedCount && this.pagination.currentPage > 1
        
        await this.fetchImages({
          page: shouldGoToPreviousPage ? this.pagination.currentPage - 1 : this.pagination.currentPage,
          pageSize: this.pagination.pageSize
        })
        
        return response?.data
      } catch (error) {
        this.error = error.response?.data?.message || error.message || '批量删除图片失败'
        throw error
      } finally {
        this.loading = false
      }
    },

    // 搜索图片
    async searchImages(query) {
      return this.fetchImages({
        page: 1,
        filename: query
      })
    },

    // 改变页码
    async changePage(page) {
      return this.fetchImages({
        page: page,
        pageSize: this.pagination.pageSize
      })
    },

    // 改变每页大小
    async changePageSize(size) {
      return this.fetchImages({
        page: 1,
        pageSize: size
      })
    },

    // 清除错误
    clearError() {
      this.error = null
    },

    // 清除当前选中的图片
    clearCurrentImage() {
      this.currentImage = null
    }
  }
})


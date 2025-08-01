import { defineStore } from 'pinia'
import { ElMessage } from 'element-plus'
import { getProfile, updateProfile, changePassword, uploadAvatar } from '@/services/auth/profileService'

export const useProfileStore = defineStore('profile', {
  state: () => ({
    profile: { username: '', full_name: '', email: '', avatar_url: '' },
    loading: { profile: false, password: false, avatar: false }
  }),
  actions: {
    async fetchProfile() {
      try {
        const { data } = await getProfile()
        if (!data?.success) throw new Error(data?.message || '加载失败')
        this.profile = { ...(data.data || {}) }
        return true
      } catch (e) {
        ElMessage.error(e.message || '加载失败')
        return false
      }
    },

    async saveProfile(payload) {
      try {
        this.loading.profile = true
        const { data } = await updateProfile(payload)
        if (!data?.success) throw new Error(data?.message || '保存失败')
        ElMessage.success('资料保存成功')
        await this.fetchProfile()
        return true
      } catch (e) {
        ElMessage.error(e.message || '保存失败')
        return false
      } finally {
        this.loading.profile = false
      }
    },

    async updatePassword(old_password, new_password) {
      // 前置校验，避免无参直打 API 导致 400
      if (!old_password && !new_password) {
        ElMessage.warning('请输入原密码和新密码')
        return false
      }
      if (!old_password) {
        ElMessage.warning('请输入原密码')
        return false
      }
      if (!new_password) {
        ElMessage.warning('请输入新密码')
        return false
      }

      try {
        this.loading.password = true
        const res = await changePassword({ old_password, new_password })
        // 400 当作业务返回，不抛异常
        if (res.status === 400) {
          ElMessage.warning(res.data?.message || '原密码不正确')
          return false
        }
        const data = res.data
        if (!data?.success) {
          ElMessage.error(data?.message || '修改失败')
          return false
        }
        ElMessage.success('密码修改成功')
        return true
      } catch (e) {
        ElMessage.error(e.message || '修改失败')
        return false
      } finally {
        this.loading.password = false
      }
    },

    async uploadAvatarFile(file) {
      if (!file) {
        ElMessage.warning('请选择要上传的头像')
        return false
      }
      try {
        this.loading.avatar = true
        const fd = new FormData()
        fd.append('file', file)
        const { data } = await uploadAvatar(fd)
        if (!data?.success) throw new Error(data?.message || '上传失败')
        const url = data.data && data.data.avatar_url
        if (url) this.profile.avatar_url = url
        ElMessage.success('头像上传成功')
        return url || true
      } catch (e) {
        ElMessage.error(e.message || '上传失败')
        return false
      } finally {
        this.loading.avatar = false
      }
    }
  }
})



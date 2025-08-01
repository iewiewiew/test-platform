import apiClient from '@/utils/request'

export function getProfile() {
  return apiClient.get('/profile')
}

export function updateProfile(payload) {
  return apiClient.put('/profile', payload)
}

export function changePassword(payload) {
  // 接受 400 作为可处理的业务结果，避免被拦截器当作错误抛出
  return apiClient.put('/profile/password', payload, {
    validateStatus: (status) => [200, 400].includes(status)
  })
}

export function uploadAvatar(formData) {
  return apiClient.post('/profile/avatar', formData, { headers: { 'Content-Type': 'multipart/form-data' } })
}



<template>
  <div class="page-wrap">
    <el-card class="card-fill" shadow="hover">
      <el-row :gutter="16" class="row-fill">
        <el-col :xs="24" :sm="8" class="col-fill">
          <el-space direction="vertical" alignment="center" style="width:100%">
            <el-avatar :size="160" :src="avatarSrc" />
            <el-upload :show-file-list="false" accept="image/*" :http-request="uploadAvatar">
              <el-button type="primary" plain>上传头像</el-button>
            </el-upload>
          </el-space>
        </el-col>
        <el-col :xs="24" :sm="16" class="col-fill">
          <el-form :model="editForm" label-width="90px" class="form-fill">
            <el-form-item label="用户名">
              <el-input :model-value="profile.username" disabled />
            </el-form-item>
            <el-form-item label="昵称">
              <el-input v-model="editForm.full_name" placeholder="请输入昵称" clearable />
            </el-form-item>
            <el-form-item label="邮箱">
              <el-input v-model="editForm.email" placeholder="请输入邮箱" clearable />
            </el-form-item>
            <el-form-item label="原密码">
              <el-input v-model="pwdForm.old_password" type="password" show-password />
            </el-form-item>
            <el-form-item label="新密码">
              <el-input v-model="pwdForm.new_password" type="password" show-password />
            </el-form-item>
            <el-form-item>
              <el-button type="primary" :loading="loading.profile" @click="saveProfile">保存资料</el-button>
              <el-button :loading="loading.password" @click="changePassword">修改密码</el-button>
              <el-button @click="resetEdit">重置</el-button>
            </el-form-item>
          </el-form>
        </el-col>
      </el-row>
    </el-card>
  </div>
</template>

<script setup>
import { onMounted, reactive, ref, computed } from 'vue'
import { ElMessage } from 'element-plus'
import { useProfileStore } from '@/stores/auth/profileStore'
import apiClient from '@/utils/request'

const store = useProfileStore()
const profile = store.profile
const cacheBuster = ref(Date.now())

// 将后端静态资源基址拼上，以避免走前端 3000 端口
const API_ORIGIN = (apiClient.defaults.baseURL || '').replace(/\/?api\/?$/i, '')
const avatarSrc = computed(() => {
  if (!profile.avatar_url) return ''
  const base = API_ORIGIN || ''
  return `${base}${profile.avatar_url}?t=${cacheBuster.value}`
})
const editForm = reactive({ full_name: '', email: '' })
const pwdForm = reactive({ old_password: '', new_password: '' })
const loading = reactive({ profile: false, password: false })

async function refreshProfile() {
  try {
    await store.fetchProfile()
    const u = store.profile || {}
    profile.username = u.username || ''
    profile.full_name = u.full_name || ''
    profile.email = u.email || ''
    profile.avatar_url = u.avatar_url || ''
    editForm.full_name = profile.full_name
    editForm.email = profile.email
  } catch (e) {
    ElMessage.error(e.message || '加载失败')
  }
}

async function saveProfile() {
  try {
    loading.profile = true
    const ok = await store.saveProfile({ full_name: editForm.full_name, email: editForm.email })
    if (ok) await refreshProfile()
  } catch (e) {
    ElMessage.error(e.message || '保存失败')
  } finally { loading.profile = false }
}

function resetEdit() {
  editForm.full_name = profile.full_name
  editForm.email = profile.email
}

async function changePassword() {
  try {
    loading.password = true
    const ok = await store.updatePassword(pwdForm.old_password, pwdForm.new_password)
    if (ok) { pwdForm.old_password = ''; pwdForm.new_password = '' }
  } catch (e) {
    ElMessage.error(e.message || '修改失败')
  } finally { loading.password = false }
}

async function uploadAvatar({ file }) {
  try {
    const fd = new FormData()
    fd.append('file', file)
    const url = await store.uploadAvatarFile(file)
    if (url) { profile.avatar_url = url; cacheBuster.value = Date.now() }
  } catch (e) {
    ElMessage.error(e.message || '上传失败')
  }
}

onMounted(() => { refreshProfile() })
</script>

<style scoped>
.page-wrap { padding: 0; margin: 0; flex: 1; display: flex; min-height: 0; }
.card-fill { flex: 1; display: flex; flex-direction: column; min-height: 0; }
.card-fill :deep(.el-card__body) { flex: 1; display: flex; flex-direction: column; min-height: 0; }
.row-fill { flex: 1; min-height: 0; display: flex; flex-direction: row; }
.col-fill { display: flex; flex-direction: column; min-height: 0; }
.form-fill { flex: 1; display: flex; flex-direction: column; }
.card-header { display:flex; justify-content:space-between; align-items:center; }
</style>



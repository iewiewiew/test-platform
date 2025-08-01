<template>
  <div class="login-container">
    <el-card class="login-card">
      <h2 class="login-title">测试管理系统</h2>
      <el-form
        ref="loginFormRef"
        :model="loginForm"
        :rules="loginRules"
        @submit.prevent="handleLogin"
      >
        <el-form-item prop="username">
          <el-input
            v-model="loginForm.username"
            placeholder="用户名"
            size="large"
            :prefix-icon="User"
          />
        </el-form-item>
        
        <el-form-item prop="password">
          <el-input
            v-model="loginForm.password"
            type="password"
            placeholder="密码"
            size="large"
            :prefix-icon="Lock"
            show-password
            @keyup.enter="handleLogin"
          />
        </el-form-item>
        
        <el-form-item>
          <el-button
            type="primary"
            size="large"
            :loading="loading"
            @click="handleLogin"
            class="login-button"
          >
            {{ loading ? '登录中...' : '登录' }}
          </el-button>
        </el-form-item>
      </el-form>
    </el-card>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue';
import { useRouter, useRoute } from 'vue-router';
import { ElMessage } from 'element-plus';
import { User, Lock } from '@element-plus/icons-vue';
import { useAuthStore } from '@/stores/auth/authStore';

const router = useRouter();
const route = useRoute();
const authStore = useAuthStore();

const loginFormRef = ref();
const loading = ref(false);

const loginForm = reactive({
  username: 'admin',
  password: '123456',
});

const loginRules = {
  username: [
    { required: true, message: '请输入用户名', trigger: 'blur' },
    { min: 3, max: 20, message: '用户名长度为 3 到 20 个字符', trigger: 'blur' }
  ],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' },
    { min: 6, message: '密码长度至少为 6 个字符', trigger: 'blur' }
  ]
};

const handleLogin = async () => {
  if (!loginFormRef.value) return;
  
  try {
    const valid = await loginFormRef.value.validate();
    if (!valid) return;
    
    loading.value = true;
    
    const result = await authStore.login(loginForm);
    
    if (result.success) {
      ElMessage.success('登录成功');
      
      // 关键修复：正确处理返回URL
      const returnUrl = route.query.returnUrl;
      console.log('🔀 登录成功 - 返回URL:', returnUrl);
      
      if (returnUrl) {
        // 解码并跳转到原页面
        const targetPath = decodeURIComponent(returnUrl);
        console.log('🔀 登录成功 - 跳转到原页面:', targetPath);
        
        // 确保目标路径有效且不是登录页
        if (targetPath.startsWith('/') && targetPath !== '/login') {
          await router.push(targetPath);
        } else {
          await router.push('/dashboard');
        }
      } else {
        // 没有返回URL，跳转到默认页面
        console.log('🔀 登录成功 - 跳转到默认页面');
        await router.push('/dashboard');
      }
    } else {
      ElMessage.error(result.message || '登录失败');
    }
  } catch (error) {
    console.error('Login error:', error);
    ElMessage.error('登录过程中发生错误');
  } finally {
    loading.value = false;
  }
};

// 页面加载时检查是否已登录
onMounted(() => {
  const token = localStorage.getItem('token');
  if (token) {
    console.log('🔄 检测到已登录，自动跳转');
    
    // 关键修复：已登录用户访问登录页时也处理返回URL
    const returnUrl = route.query.returnUrl;
    
    if (returnUrl) {
      const targetPath = decodeURIComponent(returnUrl);
      if (targetPath.startsWith('/') && targetPath !== '/login') {
        router.push(targetPath);
        return;
      }
    }
    
    // 默认跳转
    router.push('/dashboard');
  }
});
</script>

<style scoped>
.login-container {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 100vh;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.login-card {
  width: 400px;
  padding: 40px;
}

.login-title {
  text-align: center;
  margin-bottom: 30px;
  color: #333;
  font-weight: 600;
}

.login-button {
  width: 100%;
  margin-top: 10px;
}
</style>
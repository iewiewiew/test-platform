<template>
  <router-view />
</template>

<script setup>
import { onMounted } from 'vue';
import { useAuthStore } from '@/stores/auth/authStore';

const authStore = useAuthStore();

onMounted(() => {
  console.log('🚀 App.vue 挂载，初始化认证状态');
  authStore.initialize();
});
</script>
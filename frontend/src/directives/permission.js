import { useAuthStore } from '@/stores/auth/authStore';

/**
 * 权限指令
 * 使用方式：v-permission="'user:read'"
 */
export const permissionDirective = {
  mounted(el, binding) {
    const { value } = binding; // 例如 'user:read'
    const authStore = useAuthStore();
    
    if (!value) {
      return;
    }
    
    const userPermissions = authStore.user?.role?.permissions || []; // 从认证存储中获取当前用户的权限列表

    if (!userPermissions.includes(value)) {
      el.parentNode?.removeChild(el); // 如果用户没有指定权限，就从 DOM 中移除该元素
    }
  }
};
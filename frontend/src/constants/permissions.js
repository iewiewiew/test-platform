/**
 * 权限常量定义
 */
export const PERMISSIONS = {
  USER_READ: 'user:read',
  USER_WRITE: 'user:write',
  USER_DELETE: 'user:delete',
  ROLE_READ: 'role:read',
  ROLE_WRITE: 'role:write',
};

/**
 * 权限显示名称映射
 */
export const PERMISSION_LABELS = {
  [PERMISSIONS.USER_READ]: '查看用户',
  [PERMISSIONS.USER_WRITE]: '管理用户',
  [PERMISSIONS.USER_DELETE]: '删除用户',
  [PERMISSIONS.ROLE_READ]: '查看角色',
  [PERMISSIONS.ROLE_WRITE]: '管理角色',
};

/**
 * 获取所有权限选项
 */
export const getAllPermissionOptions = () => {
  return Object.entries(PERMISSION_LABELS).map(([value, label]) => ({
    value,
    label,
  }));
};
#!/usr/bin/env python
# -*- coding:utf-8 -*-

"""
@author       weimenghua
@time         2025/10/27 15:17
@description
"""

from functools import wraps
from flask import request, jsonify
from ..services.auth.auth_service import AuthService


def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None

        if 'Authorization' in request.headers:
            auth_header = request.headers['Authorization']
            try:
                token = auth_header.split(" ")[1]
            except IndexError:
                return jsonify({'message': 'Token格式错误'}), 401

        if not token:
            return jsonify({'message': 'Token缺失'}), 401

        current_user = AuthService.get_current_user(token)
        if not current_user:
            return jsonify({'message': 'Token无效或已过期'}), 401

        return f(current_user, *args, **kwargs)

    return decorated


def permission_required(permission):
    def decorator(f):
        @wraps(f)
        def decorated(current_user, *args, **kwargs):
            # 管理员直接放行
            try:
                if hasattr(current_user, 'is_admin') and current_user.is_admin():
                    return f(current_user, *args, **kwargs)

                if not hasattr(current_user, 'role') or not current_user.role:
                    return jsonify({'message': '用户没有分配角色'}), 403

                # 使用模型方法获取权限列表，统一格式
                get_perms = getattr(current_user.role, 'get_permissions_list', None)
                permissions = get_perms() if callable(get_perms) else []

                if permission not in permissions:
                    return jsonify({'message': f'缺少权限: {permission}'}), 403

                return f(current_user, *args, **kwargs)
            except Exception as e:
                return jsonify({'message': str(e)}), 500

        return decorated

    return decorator
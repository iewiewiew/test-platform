#!/usr/bin/env python
# -*- coding:utf-8 -*-

"""
@author       weimenghua
@time         2025/10/27 15:16
@description
"""

from datetime import datetime, timedelta

import jwt
from flask import current_app

from sqlalchemy.orm import joinedload

from ...core.database import db
from ...models.auth.user_model import User, Role


class AuthService:
    @staticmethod
    def authenticate_user(username, password):
        """
        验证用户身份

        Args:
            username (str): 用户名
            password (str): 密码

        Returns:
            User or None: 验证成功返回用户对象，否则返回None
        """
        user = User.query.filter_by(username=username, is_active=True).first()
        if user and user.check_password(password):
            return user
        return None

    @staticmethod
    def generate_token(user):
        """
        生成JWT token

        Args:
            user (User): 用户对象

        Returns:
            str: JWT token字符串
        """
        payload = {
            'user_id': user.id,
            'username': user.username,
            'exp': datetime.now() + current_app.config['JWT_ACCESS_TOKEN_EXPIRES']
        }
        token = jwt.encode(payload, current_app.config['JWT_SECRET_KEY'], algorithm='HS256')
        return token

    @staticmethod
    def verify_token(token):
        """
        验证JWT token

        Args:
            token (str): JWT token字符串

        Returns:
            dict or None: token有效返回payload字典，否则返回None
        """
        try:
            payload = jwt.decode(token, current_app.config['JWT_SECRET_KEY'], algorithms=['HS256'])
            return payload
        except jwt.ExpiredSignatureError:
            return None
        except jwt.InvalidTokenError:
            return None

    @staticmethod
    def get_current_user(token):
        """
        获取当前用户（通过token）

        Args:
            token (str): JWT token

        Returns:
            User or None: 用户对象，如果token无效则返回None
        """
        payload = AuthService.verify_token(token)
        if payload:
            # 使用 joinedload 一次性加载角色和权限信息
            user = User.query.options(joinedload(User.role)).get(payload['user_id'])
            return user
        return None

    @staticmethod
    def get_current_user_with_permissions(token):
        """
        获取包含权限信息的当前用户数据
        """
        user = AuthService.get_current_user(token)
        if not user:
            return None

        # 使用新增的 to_full_dict 方法返回完整信息
        return user.to_full_dict()

    @staticmethod
    def get_current_user_simple(token):
        """
        获取简化版的当前用户信息（包含权限）
        """
        user = AuthService.get_current_user(token)
        if not user:
            return None

        return user.to_dict_with_permissions()
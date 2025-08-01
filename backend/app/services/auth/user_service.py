#!/usr/bin/env python
# -*- coding:utf-8 -*-

"""
@author       weimenghua
@time         2025/10/27 15:15
@description
"""

from sqlalchemy import or_

from ...core.database import db
from ...core.exceptions import APIException
from ...models.auth.user_model import User, Role


class UserService:
    @staticmethod
    def get_all_users(page=1, per_page=10, search=None):
        query = User.query

        if search:
            search_filter = or_(User.username.ilike(f'%{search}%'), User.email.ilike(f'%{search}%'),
                User.full_name.ilike(f'%{search}%'))
            query = query.filter(search_filter)

        pagination = query.order_by(User.id.desc()).paginate(page=page, per_page=per_page, error_out=False)

        return {
            'users': [user.to_dict() for user in pagination.items],
            'total': pagination.total,
            'pages': pagination.pages,
            'current_page': page,
            'per_page': per_page
        }

    @staticmethod
    def get_user_by_id(user_id):
        user = User.query.get_or_404(user_id)
        return user.to_dict()

    @staticmethod
    def create_user(user_data, current_user=None):
        """
        创建新用户

        Args:
            user_data (dict): 用户数据字典
            current_user (User): 当前登录用户，用于设置创建人

        Returns:
            User: 新创建的用户对象

        Raises:
            APIException: 当用户名或邮箱已存在时
        """

        # 检查用户名和邮箱是否已存在
        if User.query.filter_by(username=user_data['username']).first():
            raise APIException('用户名已存在', 409)

        if User.query.filter_by(email=user_data['email']).first():
            raise APIException('邮箱已存在', 409)

        user = User(username=user_data['username'], email=user_data['email'], full_name=user_data['full_name'],
            role_id=user_data.get('role_id'))
        user.set_password(user_data['password'])
        
        if current_user:
            user.created_by = current_user.id
            user.updated_by = current_user.id

        db.session.add(user)
        db.session.commit()

        return user

    @staticmethod
    def update_user(user_id, user_data, current_user=None):
        """
        更新用户信息

        Args:
            user_id (int): 用户ID
            user_data (dict): 要更新的用户数据
            current_user (User): 当前登录用户，用于设置更新人

        Returns:
            User: 更新后的用户对象

        Raises:
            APIException: 当用户不存在或用户名/邮箱冲突时
        """

        user = User.query.get(user_id)
        if not user:
            raise APIException('用户不存在', 404)

        # 检查用户名是否被其他用户使用
        if 'username' in user_data:
            existing_user = User.query.filter(User.username == user_data['username'], User.id != user_id).first()
            if existing_user:
                raise APIException('用户名已存在', 409)

        # 检查邮箱是否被其他用户使用
        if 'email' in user_data:
            existing_user = User.query.filter(User.email == user_data['email'], User.id != user_id).first()
            if existing_user:
                raise APIException('邮箱已存在', 409)

        # 更新字段
        for key, value in user_data.items():
            if key == 'password' and value:
                user.set_password(value)
            elif hasattr(user, key) and key not in ['created_by', 'updated_by', 'password']:
                setattr(user, key, value)
        
        if current_user:
            user.updated_by = current_user.id

        db.session.commit()
        return user

    @staticmethod
    def delete_user(user_id):
        """
        删除用户

        Args:
            user_id (int): 用户ID

        Returns:
            bool: 删除成功返回True

        Raises:
            APIException: 当用户不存在时
        """

        user = User.query.get(user_id)
        if not user:
            raise APIException('用户不存在', 404)

        db.session.delete(user)
        db.session.commit()

        return True


class RoleService:
    @staticmethod
    def get_all_roles():
        return Role.query.all()

    @staticmethod
    def get_role_by_id(role_id):
        return Role.query.get(role_id)

    @staticmethod
    def create_role(role_data, current_user=None):
        """
        创建新角色

        Args:
            role_data (dict): 角色数据字典
            current_user (User): 当前登录用户，用于设置创建人

        Returns:
            Role: 新创建的角色对象

        Raises:
            APIException: 当角色名已存在时
        """

        if Role.query.filter_by(name=role_data['name']).first():
            raise APIException('角色名已存在', 409)

        role = Role(name=role_data['name'], description=role_data.get('description', ''),
            permissions=role_data.get('permissions', '[]'))
        
        if current_user:
            role.created_by = current_user.id
            role.updated_by = current_user.id

        db.session.add(role)
        db.session.commit()

        return role

    @staticmethod
    def update_role(role_id, role_data, current_user=None):
        """
        更新角色信息

        Args:
            role_id (int): 角色ID
            role_data (dict): 要更新的角色数据
            current_user (User): 当前登录用户，用于设置更新人

        Returns:
            Role: 更新后的角色对象

        Raises:
            APIException: 当角色不存在或角色名冲突时
        """

        role = Role.query.get(role_id)
        if not role:
            raise APIException('角色不存在', 404)

        if 'name' in role_data:
            existing_role = Role.query.filter(Role.name == role_data['name'], Role.id != role_id).first()
            if existing_role:
                raise APIException('角色名已存在', 409)

        for key, value in role_data.items():
            if hasattr(role, key) and key not in ['created_by', 'updated_by']:
                setattr(role, key, value)
        
        if current_user:
            role.updated_by = current_user.id

        db.session.commit()
        return role

    @staticmethod
    def delete_role(role_id):
        """
        删除角色

        Args:
            role_id (int): 角色ID

        Returns:
            bool: 删除成功返回True

        Raises:
            APIException: 当角色不存在或角色下还有用户时
        """

        role = Role.query.get(role_id)
        if not role:
            raise APIException('角色不存在', 404)

        # 检查是否有用户使用该角色
        if role.users:
            raise APIException('该角色下还有用户，无法删除', 409)

        db.session.delete(role)
        db.session.commit()

        return True
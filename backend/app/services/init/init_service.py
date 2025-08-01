# !/usr/bin/env python
# -*- coding:utf-8 -*-

"""
@author       weimenghua
@time         2025/10/27 16:05
@description
"""

from ...core.database import db
from ...models.auth.user_model import User, Role, Permission

# 导入所有模型以确保表定义被注册到 SQLAlchemy
from ...models.example.example_model import Example
from ...models.project.project_model import Project
from ...models.environment.environment_model import Environment
from ...models.mock.mock_model import Mock
from ...models.database.sql_model import SQLTemplate
from ...models.database.database_conn_model import DatabaseConnection
from ...models.tool.linux_info_model import LinuxInfo
from ...models.tool.script_management_model import ScriptManagement
from ...models.api_docs.api_endpoint_model import ApiEndpoint
from ...models.api_docs.api_parameter_model import ApiParameter
from ...models.auth.operation_log_model import OperationLog
from ...models.auth.api_access_log_model import ApiAccessLog
from ...models.notification.notification_model import Notification


class InitService:
    @staticmethod
    def init_default_data():
        """
        初始化默认数据：角色和超管管理员
        """
        try:
            print("开始初始化默认数据...")
            
            # 确保所有表都已创建
            print("检查并创建数据库表...")
            db.create_all()
            print("✓ 数据库表检查完成")

            # 1. 创建或更新管理员角色
            admin_role = Role.query.filter_by(name='admin').first()
            if not admin_role:
                admin_role = Role(name='admin', description='系统超级管理员',
                    permissions=str(Permission.all_permissions()))
                db.session.add(admin_role)
                db.session.flush()  # 获取ID但不提交事务
                print("✓ 创建管理员角色成功")
            else:
                # 确保管理员角色拥有所有权限
                admin_role.permissions = str(Permission.all_permissions())
                print("✓ 更新管理员角色权限成功")

            # 2. 创建普通用户角色
            user_role = Role.query.filter_by(name='user').first()
            if not user_role:
                user_role = Role(name='user', description='普通用户', permissions=str([Permission.USER_READ]))
                db.session.add(user_role)
                db.session.flush()
                print("✓ 创建普通用户角色成功")

            # 3. 创建超管管理员账号
            admin_user = User.query.filter_by(username='admin').first()
            if not admin_user:
                admin_user = User(username='admin', email='admin@example.com', full_name='系统管理员',
                    role_id=admin_role.id, is_active=True)
                # 明确指定使用 pbkdf2:sha256 方法
                admin_user.set_password('123456')
                db.session.add(admin_user)
                print("✓ 创建超管管理员账号成功: admin/123456")
            else:
                # 如果管理员已存在，确保密码正确且角色正确
                admin_user.role_id = admin_role.id
                admin_user.is_active = True
                # 确保角色关系已刷新
                db.session.refresh(admin_user)
                print(f"✓ 超管管理员账号 admin 已存在，role_id={admin_user.role_id}, role_name={admin_user.role.name if admin_user.role else 'None'}")

            # 4. 创建默认普通用户 test/123456
            test_user = User.query.filter_by(username='test').first()
            if not test_user:
                test_user = User(username='test', email='test@example.com', full_name='测试用户',
                                  role_id=user_role.id, is_active=True)
                test_user.set_password('123456')
                db.session.add(test_user)
                print("✓ 创建默认普通用户成功: test/123456")
            else:
                # 确保角色正确
                test_user.role_id = user_role.id
                test_user.is_active = True
                print("✓ 默认普通用户 test 已存在")

            db.session.commit()
            print("✓ 数据提交成功")
            return True

        except Exception as e:
            db.session.rollback()
            print(f"✗ 初始化默认数据失败: {str(e)}")
            import traceback
            traceback.print_exc()  # 打印详细错误信息
            return False

    @staticmethod
    def check_admin_exists():
        """
        检查管理员账号是否存在
        """
        return User.query.filter_by(username='admin').first() is not None
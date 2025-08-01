# !/usr/bin/env python
# -*- coding:utf-8 -*-

"""
@author       weimenghua
@time         2025/10/27 16:05
@description
"""

from pathlib import Path

from flask_migrate import upgrade

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
from ...models.image.image_model import Image


class InitService:
    @staticmethod
    def run_migrations():
        """
        运行数据库迁移
        如果 migrations 目录不存在，使用 db.create_all() 作为备选方案
        """
        try:
            print("开始运行数据库迁移...")
            
            # 检查 migrations 目录是否存在
            backend_dir = Path(__file__).parent.parent.parent.parent
            migrations_dir = backend_dir / 'migrations'
            alembic_ini = migrations_dir / 'alembic.ini'
            
            # 如果 migrations 目录不存在或 alembic.ini 不存在，使用 db.create_all()
            if not migrations_dir.exists() or not alembic_ini.exists():
                print("⚠ migrations 目录未初始化，使用 db.create_all() 创建表...")
                try:
                    db.create_all()
                    print("✓ 使用 db.create_all() 创建表完成")
                    return True
                except Exception as e:
                    print(f"⚠ db.create_all() 失败: {str(e)}")
                    return False
            
            # 运行迁移
            upgrade()
            print("✓ 数据库迁移完成")
            return True
        except Exception as e:
            error_msg = str(e)
            # 检查是否是"Path doesn't exist"或 migrations 相关错误
            if "Path doesn't exist" in error_msg or "migrations" in error_msg.lower() or "alembic" in error_msg.lower():
                print(f"⚠ 迁移系统异常，尝试使用 db.create_all() 创建表...")
                try:
                    db.create_all()
                    print("✓ 使用 db.create_all() 创建表完成")
                    return True
                except Exception as e2:
                    print(f"⚠ db.create_all() 也失败: {str(e2)}")
                    return False
            else:
                print(f"⚠ 数据库迁移失败或无需迁移: {error_msg}")
                # 迁移失败不应该阻止应用启动，所以返回 True
                return True

    @staticmethod
    def init_default_data():
        """
        初始化默认数据：角色和超管管理员
        注意：表应该已经通过 run_migrations() 创建，这里只初始化数据
        """
        try:
            print("开始初始化默认数据...")
            
            # 确保所有表都已创建（如果迁移失败，这里作为备选方案）
            try:
                db.create_all()
                print("✓ 数据库表检查完成")
            except Exception as e:
                print(f"⚠ 数据库表检查失败（可能表已存在）: {str(e)}")

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
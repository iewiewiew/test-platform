#!/usr/bin/env python
# -*- coding:utf-8 -*-

"""
@author       weimenghua
@time         2025/7/30 17:47
@description  路由包初始化文件
"""

import os

from flask import Flask, redirect, url_for, request, jsonify, g
from flask_cors import CORS

from .api_docs import api_docs_bp, docs_bp
from .auth import auth_bp, user_bp, role_bp, profile_bp, api_access_log_bp, operation_log_bp
from .database import database_conn_bp, database_info_bp, sql_bp
from .environment import environment_bp
from .example import example_bp
from .mock import mock_bp, mock_data_bp
from .project import project_bp
from .test import test_case_bp, test_environment_bp, test_report_bp, pytest_executor_bp
from .tool import linux_info_bp, script_management_bp, tool_bp
from .notification import notification_bp
from .business import business_bp
from ..core.config import config
from ..core.database import db, migrate
from ..core.response_logger import ResponseLogger
from ..services.init import InitService
from ..services.tool import script_management_service
from ..services.auth import AuthService
from ..services.auth.api_access_log_service import ApiAccessLogService
from ..models.auth import User

# 导出所有蓝图，便于统一管理
__all__ = ['example_bp', 'api_docs_bp', 'mock_bp', 'mock_data_bp', 'project_bp', 'environment_bp', 'linux_info_bp',
    'sql_bp', 'role_bp', 'auth_bp', 'user_bp', 'database_conn_bp', 'database_info_bp', 'script_management_bp', 'tool_bp',
    'test_case_bp', 'test_report_bp', 'test_environment_bp', 'pytest_executor_bp', 'api_access_log_bp', 'operation_log_bp',
    'notification_bp', 'business_bp']


def create_app(config_name='default'):
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    app.config['JSON_AS_ASCII'] = False

    # 配置静态目录，确保可直接访问 /static 下的头像等资源
    try:
        app.static_folder = app.config.get('STATIC_FOLDER', app.static_folder)
        app.static_url_path = '/static'
        # 确保目录存在
        os.makedirs(app.config.get('AVATAR_UPLOAD_FOLDER', ''), exist_ok=True)
    except Exception:
        pass
    # 生产环境把 origins 设置为具体域名    
    if os.environ.get('FLASK_ENV') == 'production':
        CORS(app, resources={r"/api/*": {"origins": "http://example.com"}})
    else:
        CORS(app, resources={r"/api/*": {"origins": "*"}})

    db.init_app(app)
    migrate.init_app(app, db)

    with app.app_context():
        # 初始化默认数据
        if InitService.init_default_data():
            print("系统初始化完成")
        else:
            print("系统初始化失败")
        
        # 设置Flask应用实例到脚本管理服务（用于定时任务执行时创建应用上下文）
        script_management_service.set_app(app)
        
        # 加载已存在的定时任务
        try:
            script_management_service.load_existing_scheduled_tasks()
        except Exception as e:
            print(f"加载定时任务失败: {str(e)}")
            import traceback
            traceback.print_exc()

    # 注册响应日志记录
    ResponseLogger.init_app(example_bp)
    ResponseLogger.init_app(mock_bp)
    ResponseLogger.init_app(project_bp)
    ResponseLogger.init_app(environment_bp)
    ResponseLogger.init_app(api_docs_bp)
    ResponseLogger.init_app(mock_data_bp)
    ResponseLogger.init_app(linux_info_bp)
    ResponseLogger.init_app(sql_bp)
    ResponseLogger.init_app(auth_bp)
    ResponseLogger.init_app(role_bp)
    ResponseLogger.init_app(user_bp)
    ResponseLogger.init_app(database_conn_bp)
    ResponseLogger.init_app(database_info_bp)
    ResponseLogger.init_app(script_management_bp)
    ResponseLogger.init_app(tool_bp)
    ResponseLogger.init_app(profile_bp)
    ResponseLogger.init_app(docs_bp)
    ResponseLogger.init_app(test_case_bp)
    ResponseLogger.init_app(test_report_bp)
    ResponseLogger.init_app(test_environment_bp)
    ResponseLogger.init_app(pytest_executor_bp)
    ResponseLogger.init_app(api_access_log_bp)
    ResponseLogger.init_app(operation_log_bp)
    ResponseLogger.init_app(notification_bp)

    # 全局鉴权：所有 /api/* 接口要求携带有效 Token（登录与预检请求除外）
    @app.before_request
    def enforce_auth_for_all_api():
        try:
            # 允许通过配置快速关闭全局 Token 校验
            if not app.config.get('REQUIRE_GLOBAL_TOKEN', True):
                return None

            # 跳过非 API 路由
            if not request.path.startswith('/api/'):
                return None

            # 放行登录与预检
            if request.method == 'OPTIONS' or request.path == '/api/auth/login':
                return None
            
            # 放行Allure报告静态文件（允许公开访问测试报告）
            if request.path.startswith('/api/test-reports/') and '/allure/' in request.path:
                return None

            auth_header = request.headers.get('Authorization', '')
            token = auth_header.split(' ')[1] if auth_header.startswith('Bearer ') else None
            if not token:
                return jsonify({'message': 'Token缺失'}), 401

            current_user = AuthService.get_current_user(token)
            if not current_user:
                return jsonify({'message': 'Token无效或已过期'}), 401

            # 确保 role 关系已加载
            from sqlalchemy.orm import joinedload
            if not hasattr(current_user, 'role') or current_user.role is None:
                # 重新加载用户和角色关系
                current_user = User.query.options(joinedload(User.role)).get(current_user.id)
                if not current_user:
                    return jsonify({'message': '用户不存在'}), 404

            # 缓存到全局上下文，便于下游使用
            g.current_user = current_user
        except Exception as e:
            import traceback
            traceback.print_exc()
            return jsonify({'message': f'认证失败: {str(e)}'}), 500

    # 全局权限拦截：仅管理员可进行写操作，普通用户仅可读
    @app.before_request
    def enforce_admin_for_write_methods():
        try:
            # 允许通过配置快速关闭全局 Token 校验
            if not app.config.get('REQUIRE_GLOBAL_TOKEN', True):
                return None

            # 跳过非 API 路由
            if not request.path.startswith('/api/'):
                return None

            # 放行登录接口
            if request.path == '/api/auth/login':
                return None

            if request.method in ('POST', 'PUT', 'PATCH', 'DELETE'):
                # 放行个人资料自更新接口（允许已认证用户修改自己的资料）
                if request.path.startswith('/api/profile'):
                    return None

                # 复用上游鉴权结果
                current_user = getattr(g, 'current_user', None)
                if not current_user:
                    return jsonify({'message': '用户未认证', 'path': request.path}), 401
                
                # 确保 role 关系已加载
                from sqlalchemy.orm import joinedload
                if not hasattr(current_user, 'role') or current_user.role is None:
                    # 重新加载用户和角色关系
                    current_user = User.query.options(joinedload(User.role)).get(current_user.id)
                    if not current_user:
                        return jsonify({'message': '用户不存在'}), 404
                    g.current_user = current_user
                
                # 如果 role_id 存在但 role 关系仍为 None，尝试修复
                if current_user.role_id and current_user.role is None:
                    from ..models.auth import Role
                    role = Role.query.get(current_user.role_id)
                    if role:
                        current_user.role = role
                        db.session.commit()
                
                # 检查是否是管理员
                if not current_user.is_admin():
                    return jsonify({
                        'message': '仅管理员可进行写操作',
                        'debug': {
                            'user_id': current_user.id,
                            'username': current_user.username,
                            'role_id': current_user.role_id,
                            'role_name': current_user.role.name if current_user.role else None
                        }
                    }), 403
        except Exception as e:
            import traceback
            traceback.print_exc()
            return jsonify({'message': f'权限检查失败: {str(e)}'}), 500

    # 全局API访问日志记录
    @app.after_request
    def log_api_access(response):
        """
        记录所有API访问日志
        """
        try:
            # 只记录API路由
            if not request.path.startswith('/api/'):
                return response

            # 跳过OPTIONS预检请求
            if request.method == 'OPTIONS':
                return response

            # 跳过静态文件
            if request.path.startswith('/api/test-reports/') and '/allure/' in request.path:
                return response

            # 跳过登录接口（已有专门的登录日志）
            if request.path == '/api/auth/login':
                return response

            # 获取用户信息
            user_id = None
            username = None
            current_user = getattr(g, 'current_user', None)
            if current_user:
                user_id = current_user.id
                username = current_user.username

            # 获取客户端IP
            def get_client_ip():
                if request.headers.get('X-Forwarded-For'):
                    ip = request.headers.get('X-Forwarded-For').split(',')[0].strip()
                elif request.headers.get('X-Real-IP'):
                    ip = request.headers.get('X-Real-IP')
                else:
                    ip = request.remote_addr
                return ip

            # 获取请求参数
            query_params = None
            if request.args:
                query_params = request.args.to_dict()

            # 获取请求体（仅对POST/PUT/PATCH方法）
            request_body = None
            if request.method in ['POST', 'PUT', 'PATCH']:
                request_body = request.get_json(silent=True)

            # 计算响应时间
            response_time = None
            if hasattr(request, 'start_time'):
                import time
                response_time = time.time() - request.start_time

            # 记录API访问日志（异步记录，不阻塞响应）
            try:
                ApiAccessLogService.create_api_access_log(
                    user_id=user_id,
                    username=username,
                    access_ip=get_client_ip(),
                    user_agent=request.headers.get('User-Agent'),
                    api_path=request.path,
                    request_method=request.method,
                    endpoint=request.endpoint,
                    status_code=response.status_code,
                    response_time=response_time,
                    query_params=query_params,
                    request_body=request_body
                )
            except Exception as e:
                # 记录日志失败不影响主流程
                print(f"Failed to log API access: {e}")

        except Exception as e:
            # 记录日志失败不影响主流程
            print(f"Error in API access logging: {e}")

        return response

    # 记录请求开始时间
    @app.before_request
    def record_request_start_time():
        import time
        request.start_time = time.time()

    if os.environ.get('FLASK_APP') is None:
        os.environ['FLASK_APP'] = 'app.routes:create_app'

    app.register_blueprint(example_bp, url_prefix='/api')
    app.register_blueprint(mock_bp, url_prefix='/api')
    app.register_blueprint(project_bp, url_prefix='/api')
    app.register_blueprint(environment_bp, url_prefix='/api')
    app.register_blueprint(mock_data_bp, url_prefix='/api')
    app.register_blueprint(api_docs_bp, url_prefix='/api')
    app.register_blueprint(linux_info_bp, url_prefix='/api')
    app.register_blueprint(sql_bp, url_prefix='/api')
    app.register_blueprint(auth_bp, url_prefix='/api')
    app.register_blueprint(role_bp, url_prefix='/api')
    app.register_blueprint(user_bp, url_prefix='/api')
    app.register_blueprint(database_conn_bp, url_prefix='/api')
    app.register_blueprint(database_info_bp, url_prefix='/api')
    app.register_blueprint(script_management_bp, url_prefix='/api')
    app.register_blueprint(tool_bp, url_prefix='/api')
    app.register_blueprint(profile_bp, url_prefix='/api')
    app.register_blueprint(docs_bp, url_prefix='/api')
    app.register_blueprint(test_case_bp, url_prefix='/api')
    app.register_blueprint(test_report_bp, url_prefix='/api')
    app.register_blueprint(test_environment_bp, url_prefix='/api')
    app.register_blueprint(pytest_executor_bp, url_prefix='/api')
    app.register_blueprint(api_access_log_bp, url_prefix='/api')
    app.register_blueprint(operation_log_bp, url_prefix='/api')
    app.register_blueprint(notification_bp, url_prefix='/api')
    app.register_blueprint(business_bp, url_prefix='/api')

    return app

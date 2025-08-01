#!/usr/bin/env python
# -*- coding:utf-8 -*-

"""
@author       weimenghua
@time         2025/7/30 17:47
@description  路由包初始化文件
"""

import os
import sys
import time
import traceback
from pathlib import Path
from sqlalchemy.orm import joinedload

from flask import Flask, request, jsonify, g
from flask_cors import CORS

# 添加项目根目录到 Python 路径
backend_dir = Path(__file__).parent.parent.parent
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

from .api_docs import api_docs_bp, docs_bp
from .auth import auth_bp, user_bp, role_bp, profile_bp, api_access_log_bp, operation_log_bp
from .database import database_conn_bp, database_info_bp, sql_bp, redis_bp
from .environment import environment_bp
from .example import example_bp
from .mock import mock_bp, mock_data_bp
from .project import project_bp
from .test import test_case_bp, test_environment_bp, test_report_bp, pytest_executor_bp
from .tool import linux_info_bp, script_management_bp, tool_bp, mcp_bp
from .notification import notification_bp
from .business import business_bp
from .image import image_bp
from ..core.config import config, get_config_name
from ..core.database import db, migrate
from ..core.response_logger import ResponseLogger
from ..services.init import InitService
from ..services.tool import script_management_service
from ..services.auth import AuthService
from ..services.auth.api_access_log_service import ApiAccessLogService
from ..models.auth import User, Role

# 所有蓝图列表，用于统一注册和日志记录
ALL_BLUEPRINTS = [
    example_bp, mock_bp, mock_data_bp, project_bp, environment_bp,
    api_docs_bp, docs_bp, linux_info_bp, sql_bp, auth_bp, role_bp,
    user_bp, database_conn_bp, database_info_bp, redis_bp,
    script_management_bp, tool_bp, mcp_bp, profile_bp, test_case_bp,
    test_report_bp, test_environment_bp, pytest_executor_bp,
    api_access_log_bp, operation_log_bp, notification_bp, business_bp,
    image_bp
]


def create_app(config_name=None):
    """
    创建 Flask 应用
    
    Args:
        config_name: 配置名称，可选值：'development', 'testing', 'production'，如果为 None，则从环境变量 FLASK_ENV 获取
    
    Returns:
        Flask 应用实例
    """
    app = Flask(__name__)
    
    # 如果没有指定配置名称，从环境变量获取
    if config_name is None:
        config_name = get_config_name()
    
    # 验证配置名称
    if config_name not in config:
        raise ValueError(f"无效的配置名称: {config_name}，可选值: {list(config.keys())}")
    
    # 加载配置
    config_class = config[config_name]
    app.config.from_object(config_class)
    
    # 如果是生产环境，验证必需的配置项
    if config_name == 'production':
        config_class.validate()
    
    print(f"✓ 使用配置环境: {config_name}")
    app.config['JSON_AS_ASCII'] = False

    # 配置静态目录
    _setup_static_folder(app)
    
    # CORS 配置（根据环境配置）
    cors_origins = app.config.get('CORS_ORIGINS', ['*'])
    CORS(app, resources={r"/api/*": {"origins": cors_origins}})

    db.init_app(app)
    migrate.init_app(app, db)

    with app.app_context():
        _initialize_database(app)
        _initialize_scheduled_tasks(app)

    # 注册响应日志记录
    for bp in ALL_BLUEPRINTS:
        ResponseLogger.init_app(bp)

    # 注册全局中间件
    _register_middlewares(app)

    # 设置 Flask 应用环境变量
    if os.environ.get('FLASK_APP') is None:
        os.environ['FLASK_APP'] = 'app.routes:create_app'

    # 注册所有蓝图
    for bp in ALL_BLUEPRINTS:
        app.register_blueprint(bp, url_prefix='/api')


    return app


def _setup_static_folder(app):
    """配置静态文件目录"""
    try:
        app.static_folder = app.config.get('STATIC_FOLDER', app.static_folder)
        app.static_url_path = '/static'
        os.makedirs(app.config.get('AVATAR_UPLOAD_FOLDER', ''), exist_ok=True)
        os.makedirs(app.config.get('IMAGE_UPLOAD_FOLDER', ''), exist_ok=True)
    except Exception:
        pass


def _initialize_database(app):
    """初始化数据库"""
    auto_migrate = os.environ.get('AUTO_MIGRATE', 'true').lower() in ('true', '1', 'yes')
    if auto_migrate:
        InitService.run_migrations()
    
    if InitService.init_default_data():
        print("系统初始化完成")
    else:
        print("系统初始化失败")


def _initialize_scheduled_tasks(app):
    """初始化定时任务"""
    script_management_service.set_app(app)
    try:
        script_management_service.load_existing_scheduled_tasks()
    except Exception as e:
        print(f"加载定时任务失败: {str(e)}")
        traceback.print_exc()


def _should_skip_auth(path, method):
    """判断是否应该跳过认证"""
    # 跳过非 API 路由
    if not path.startswith('/api/'):
        return True
    # 跳过预检请求和登录接口
    if method == 'OPTIONS' or path == '/api/auth/login':
        return True
    # 跳过 Allure 报告静态文件
    if path.startswith('/api/test-reports/') and '/allure/' in path:
        return True
    # 跳过文档资源文件（图片等）
    if path.startswith('/api/docs/assets/'):
        return True
    # 跳过图片访问接口（GET请求）
    if path.startswith('/api/images/') and request.method == 'GET':
        # 检查是否是文件访问（包含文件扩展名）
        import os
        if os.path.splitext(path)[1] in ['.png', '.jpg', '.jpeg', '.gif', '.webp']:
            return True
    return False


def _load_user_with_role(user_id):
    """加载用户及其角色关系"""
    return User.query.options(joinedload(User.role)).get(user_id)


def _fix_user_role(current_user):
    """修复用户角色关系"""
    if current_user.role_id and current_user.role is None:
        role = Role.query.get(current_user.role_id)
        if role:
            current_user.role = role
            db.session.commit()


def _register_middlewares(app):
    """注册全局中间件"""
    
    @app.before_request
    def record_request_start_time():
        """记录请求开始时间"""
        request.start_time = time.time()
    
    @app.before_request
    def enforce_auth_for_all_api():
        """全局鉴权：所有 /api/* 接口要求携带有效 Token"""
        try:
            if not app.config.get('REQUIRE_GLOBAL_TOKEN', True):
                return None
            
            if _should_skip_auth(request.path, request.method):
                return None

            # 提取 Token
            auth_header = request.headers.get('Authorization', '')
            token = auth_header.split(' ')[1] if auth_header.startswith('Bearer ') else None
            if not token:
                return jsonify({'message': 'Token缺失'}), 401

            # 验证 Token
            current_user = AuthService.get_current_user(token)
            if not current_user:
                return jsonify({'message': 'Token无效或已过期'}), 401

            # 确保角色关系已加载
            if not hasattr(current_user, 'role') or current_user.role is None:
                current_user = _load_user_with_role(current_user.id)
                if not current_user:
                    return jsonify({'message': '用户不存在'}), 404

            g.current_user = current_user
        except Exception as e:
            traceback.print_exc()
            return jsonify({'message': f'认证失败: {str(e)}'}), 500

    @app.before_request
    def enforce_admin_for_write_methods():
        """全局权限拦截：仅管理员可进行写操作"""
        try:
            if not app.config.get('REQUIRE_GLOBAL_TOKEN', True):
                return None
            
            if _should_skip_auth(request.path, request.method):
                return None

            if request.method not in ('POST', 'PUT', 'PATCH', 'DELETE'):
                return None

            # 放行个人资料自更新接口
            if request.path.startswith('/api/profile'):
                return None

            # 获取当前用户
            current_user = getattr(g, 'current_user', None)
            if not current_user:
                return jsonify({'message': '用户未认证', 'path': request.path}), 401
            
            # 确保角色关系已加载
            if not hasattr(current_user, 'role') or current_user.role is None:
                current_user = _load_user_with_role(current_user.id)
                if not current_user:
                    return jsonify({'message': '用户不存在'}), 404
                g.current_user = current_user
            
            # 修复角色关系
            _fix_user_role(current_user)
            
            # 检查管理员权限
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
            traceback.print_exc()
            return jsonify({'message': f'权限检查失败: {str(e)}'}), 500

    @app.after_request
    def log_api_access(response):
        """记录所有API访问日志"""
        try:
            if _should_skip_auth(request.path, request.method):
                return response
            
            # 跳过登录接口（已有专门的登录日志）
            if request.path == '/api/auth/login':
                return response

            # 获取用户信息
            current_user = getattr(g, 'current_user', None)
            user_id = current_user.id if current_user else None
            username = current_user.username if current_user else None

            # 获取客户端IP
            def get_client_ip():
                if request.headers.get('X-Forwarded-For'):
                    return request.headers.get('X-Forwarded-For').split(',')[0].strip()
                elif request.headers.get('X-Real-IP'):
                    return request.headers.get('X-Real-IP')
                return request.remote_addr

            # 获取请求参数
            query_params = request.args.to_dict() if request.args else None
            request_body = request.get_json(silent=True) if request.method in ['POST', 'PUT', 'PATCH'] else None
            
            # 计算响应时间
            response_time = None
            if hasattr(request, 'start_time'):
                response_time = time.time() - request.start_time

            # 记录API访问日志
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
                print(f"Failed to log API access: {e}")

        except Exception as e:
            print(f"Error in API access logging: {e}")

        return response

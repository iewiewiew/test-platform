#!/usr/bin/env python
# -*- coding:utf-8 -*-

"""
@author       weimenghua
@time         2025/10/27 15:17
@description
"""

from flask import Blueprint, request, jsonify
from sqlalchemy.orm import joinedload

from ...services.auth.auth_service import AuthService
from ...services.auth.operation_log_service import OperationLogService
from ...models.auth.user_model import User

auth_bp = Blueprint('auth', __name__)


def get_client_ip():
    """获取客户端IP地址"""
    if request.headers.get('X-Forwarded-For'):
        ip = request.headers.get('X-Forwarded-For').split(',')[0].strip()
    elif request.headers.get('X-Real-IP'):
        ip = request.headers.get('X-Real-IP')
    else:
        ip = request.remote_addr
    return ip


@auth_bp.route('/auth/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username') if data else None

    if not data or not username or not data.get('password'):
        # 记录登录失败日志
        if username:
            try:
                OperationLogService.create_operation_log(
                    username=username,
                    operation_type=OperationLogService.OPERATION_LOGIN,
                    operation_module=OperationLogService.MODULE_AUTH,
                    operation_desc='用户登录',
                    request_ip=get_client_ip(),
                    user_agent=request.headers.get('User-Agent'),
                    api_path=request.path,
                    request_method=request.method,
                    operation_status='failed',
                    status_code=400,
                    failure_reason='用户名和密码不能为空'
                )
            except:
                pass
        return jsonify({'message': '用户名和密码不能为空'}), 400

    user = AuthService.authenticate_user(username, data['password'])
    if not user:
        # 记录登录失败日志
        try:
            OperationLogService.create_operation_log(
                username=username,
                operation_type=OperationLogService.OPERATION_LOGIN,
                operation_module=OperationLogService.MODULE_AUTH,
                operation_desc='用户登录',
                request_ip=get_client_ip(),
                user_agent=request.headers.get('User-Agent'),
                api_path=request.path,
                request_method=request.method,
                operation_status='failed',
                status_code=401,
                failure_reason='用户名或密码错误'
            )
        except:
            pass
        return jsonify({'message': '用户名或密码错误'}), 401

    # 确保 role 关系已加载
    if not hasattr(user, 'role') or user.role is None:
        user = User.query.options(joinedload(User.role)).get(user.id)
        if not user:
            return jsonify({'message': '用户数据异常'}), 500

    token = AuthService.generate_token(user)

    # 记录登录成功日志
    try:
        OperationLogService.create_operation_log(
            user_id=user.id,
            username=user.username,
            operation_type=OperationLogService.OPERATION_LOGIN,
            operation_module=OperationLogService.MODULE_AUTH,
            operation_desc='用户登录成功',
            request_ip=get_client_ip(),
            user_agent=request.headers.get('User-Agent'),
            api_path=request.path,
            request_method=request.method,
            operation_status='success',
            status_code=200,
            operation_data={'user_id': user.id, 'username': user.username}
        )
    except:
        pass  # 操作日志记录失败不影响登录流程

    return jsonify({'message': '登录成功', 'token': token, 'user': user.to_dict()}), 200


@auth_bp.route('/auth/me', methods=['GET'])
def get_current_user():
    token = None
    if 'Authorization' in request.headers:
        auth_header = request.headers['Authorization']
        try:
            token = auth_header.split(" ")[1]
        except IndexError:
            return jsonify({'message': 'Token格式错误'}), 401

    if not token:
        return jsonify({'message': 'Token缺失'}), 401

    user = AuthService.get_current_user(token)

    if not user:
        return jsonify({'message': 'Token无效或已过期'}), 401

    user_data = AuthService.get_current_user_with_permissions(token)
    if user_data:
        return jsonify({'user': user_data})

#!/usr/bin/env python
# -*- coding:utf-8 -*-

"""
@author       weimenghua
@time         2025/01/XX XX:XX
@description  操作日志路由
"""

from flask import Blueprint, request, jsonify
from datetime import datetime

from ...services.auth.operation_log_service import OperationLogService
from ...utils.decorators import token_required
from ...models.auth.user_model import Permission
from ...utils.decorators import permission_required
from ...core.exceptions import APIException

operation_log_bp = Blueprint('operation_logs', __name__)


@operation_log_bp.route('/operation-logs', methods=['GET'])
@token_required
@permission_required(Permission.USER_READ)
def get_operation_logs(current_user):
    """
    获取操作日志列表（分页）
    """
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    search = request.args.get('search', '')
    username = request.args.get('username', '')
    operation_type = request.args.get('operation_type', '')
    operation_module = request.args.get('operation_module', '')
    operation_status = request.args.get('operation_status', '')
    start_date = request.args.get('start_date', '')
    end_date = request.args.get('end_date', '')

    try:
        # 解析日期
        start_date_parsed = None
        end_date_parsed = None
        if start_date:
            try:
                start_date_parsed = datetime.fromisoformat(start_date.replace('Z', '+00:00'))
            except:
                pass
        if end_date:
            try:
                end_date_parsed = datetime.fromisoformat(end_date.replace('Z', '+00:00'))
            except:
                pass

        result = OperationLogService.get_all_operation_logs(
            page=page,
            per_page=per_page,
            search=search if search else None,
            username=username if username else None,
            operation_type=operation_type if operation_type else None,
            operation_module=operation_module if operation_module else None,
            operation_status=operation_status if operation_status else None,
            start_date=start_date_parsed,
            end_date=end_date_parsed
        )
        return jsonify(result), 200
    except APIException as e:
        return jsonify({'message': e.message, 'payload': e.payload}), e.status_code
    except Exception as e:
        return jsonify({'message': str(e)}), 500


@operation_log_bp.route('/operation-logs/<int:log_id>', methods=['GET'])
@token_required
@permission_required(Permission.USER_READ)
def get_operation_log(current_user, log_id):
    """
    获取单个操作日志详情
    """
    log = OperationLogService.get_operation_log_by_id(log_id)
    if not log:
        return jsonify({'message': '操作日志不存在'}), 404

    # 根据请求方法和接口路径推断操作类型的辅助函数
    def infer_operation_type(api_path, request_method):
        """根据接口路径和请求方法推断操作类型"""
        api_path_lower = api_path.lower() if api_path else ''
        method_upper = request_method.upper() if request_method else ''
        
        # 登录相关
        if '/login' in api_path_lower or '/auth/login' in api_path_lower:
            return 'login'
        # 登出相关
        if '/logout' in api_path_lower or '/auth/logout' in api_path_lower:
            return 'logout'
        # 根据请求方法推断
        if method_upper == 'POST':
            # POST 可能是创建或登录
            if '/create' in api_path_lower or '/add' in api_path_lower:
                return 'create'
            return 'create'  # 默认 POST 为创建
        elif method_upper == 'PUT' or method_upper == 'PATCH':
            return 'update'
        elif method_upper == 'DELETE':
            return 'delete'
        elif method_upper == 'GET':
            return 'query'
        else:
            return 'other'
    
    # 转换为 operation_log 格式
    api_dict = log.to_dict()
    inferred_type = infer_operation_type(api_dict['api_path'], api_dict['request_method'])
    converted_log = {
        'id': api_dict['id'],
        'user_id': api_dict['user_id'],
        'username': api_dict['username'],
        'operation_type': inferred_type,
        'operation_module': None,
        'operation_desc': f"API访问: {api_dict['api_path']}",
        'request_ip': api_dict['access_ip'],
        'user_agent': api_dict['user_agent'],
        'operation_time': api_dict['access_time'],
        'api_path': api_dict['api_path'],
        'request_method': api_dict['request_method'],
        'operation_status': 'success' if api_dict['status_code'] and api_dict['status_code'] < 400 else 'failed',
        'status_code': api_dict['status_code'],
        'failure_reason': None,
        'operation_data': None,
        'created_at': api_dict['created_at'],
        'updated_at': api_dict['updated_at']
    }

    return jsonify({'operation_log': converted_log}), 200


@operation_log_bp.route('/operation-logs/<int:log_id>', methods=['DELETE'])
@token_required
@permission_required(Permission.USER_DELETE)
def delete_operation_log(current_user, log_id):
    """
    删除操作日志
    """
    try:
        success = OperationLogService.delete_operation_log(log_id)
        if not success:
            return jsonify({'message': '操作日志不存在'}), 404
        return jsonify({'message': '删除成功'}), 200
    except APIException as e:
        return jsonify({'message': e.message, 'payload': e.payload}), e.status_code
    except Exception as e:
        return jsonify({'message': '删除失败'}), 500


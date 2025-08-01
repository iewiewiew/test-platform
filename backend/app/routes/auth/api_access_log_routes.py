#!/usr/bin/env python
# -*- coding:utf-8 -*-

"""
@author       weimenghua
@time         2025/01/XX XX:XX
@description  API访问日志路由
"""

from flask import Blueprint, request, jsonify
from datetime import datetime

from ...services.auth.api_access_log_service import ApiAccessLogService
from ...utils.decorators import token_required
from ...models.auth.user_model import Permission
from ...utils.decorators import permission_required
from ...core.exceptions import APIException

api_access_log_bp = Blueprint('api_access_logs', __name__)


@api_access_log_bp.route('/api-access-logs', methods=['GET'])
@token_required
@permission_required(Permission.USER_READ)
def get_api_access_logs(current_user):
    """
    获取API访问日志列表（分页）
    """
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    search = request.args.get('search', '')
    username = request.args.get('username', '')
    api_path = request.args.get('api_path', '')
    request_method = request.args.get('request_method', '')
    status_code = request.args.get('status_code', type=int)
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

        result = ApiAccessLogService.get_all_api_access_logs(
            page=page,
            per_page=per_page,
            search=search if search else None,
            username=username if username else None,
            api_path=api_path if api_path else None,
            request_method=request_method if request_method else None,
            status_code=status_code,
            start_date=start_date_parsed,
            end_date=end_date_parsed
        )
        return jsonify(result), 200
    except APIException as e:
        return jsonify({'message': e.message, 'payload': e.payload}), e.status_code
    except Exception as e:
        return jsonify({'message': str(e)}), 500


@api_access_log_bp.route('/api-access-logs/<int:log_id>', methods=['GET'])
@token_required
@permission_required(Permission.USER_READ)
def get_api_access_log(current_user, log_id):
    """
    获取单个API访问日志详情
    """
    log = ApiAccessLogService.get_api_access_log_by_id(log_id)
    if not log:
        return jsonify({'message': 'API访问日志不存在'}), 404

    return jsonify({'api_access_log': log.to_dict()}), 200


@api_access_log_bp.route('/api-access-logs/<int:log_id>', methods=['DELETE'])
@token_required
@permission_required(Permission.USER_DELETE)
def delete_api_access_log(current_user, log_id):
    """
    删除API访问日志
    """
    try:
        success = ApiAccessLogService.delete_api_access_log(log_id)
        if not success:
            return jsonify({'message': 'API访问日志不存在'}), 404
        return jsonify({'message': '删除成功'}), 200
    except APIException as e:
        return jsonify({'message': e.message, 'payload': e.payload}), e.status_code
    except Exception as e:
        return jsonify({'message': '删除失败'}), 500


@api_access_log_bp.route('/api-access-logs/user/<username>', methods=['GET'])
@token_required
@permission_required(Permission.USER_READ)
def get_user_api_access_logs(current_user, username):
    """
    获取指定用户的API访问日志
    """
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    
    try:
        result = ApiAccessLogService.get_all_api_access_logs(
            page=page,
            per_page=per_page,
            username=username
        )
        return jsonify(result), 200
    except APIException as e:
        return jsonify({'message': e.message, 'payload': e.payload}), e.status_code
    except Exception as e:
        return jsonify({'message': str(e)}), 500


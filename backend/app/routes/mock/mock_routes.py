#!/usr/bin/env python
# -*- coding:utf-8 -*-

"""
@author       weimenghua
@time         2025/10/1 19:15
@description  Mock API 管理与执行路由
"""

from flask import Blueprint, request, jsonify, g

from ...core.exceptions import APIException
from ...services.mock.mock_service import MockService

mock_bp = Blueprint('mock', __name__)


@mock_bp.route('/mock', methods=['GET'])
def get_all_mocks():
    """获取所有 Mock API（支持分页和搜索）"""

    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)

    # 获取查询参数
    name = request.args.get('name')
    path = request.args.get('path')
    method = request.args.get('method')
    project_id = request.args.get('project_id')

    try:
        result = MockService.get_all_mocks(page=page, per_page=per_page, name=name, path=path, method=method,
            project_id=project_id)
        return jsonify(result)
    except Exception as e:
        raise APIException('Server error', 500, {'details': str(e)})


@mock_bp.route('/mock/<int:mock_id>', methods=['GET'])
def get_mock_by_id(mock_id):
    """获取单个 Mock API 详情"""

    try:
        mock = MockService.get_mock_by_id(mock_id)
        return jsonify(mock)
    except Exception as e:
        raise APIException('Server error', 500, {'details': str(e)})


@mock_bp.route('/mock', methods=['POST'])
def create_mock():
    """创建 Mock API"""

    data = request.get_json()
    current_user = getattr(g, 'current_user', None)

    try:
        result = MockService.create_mock(data, current_user)
        return jsonify(result), 201
    except APIException as e:
        raise e
    except Exception as e:
        raise APIException('Server error', 500, {'details': str(e)})


@mock_bp.route('/mock/<int:mock_id>', methods=['PUT'])
def update_mock(mock_id):
    """更新 Mock API"""

    data = request.get_json()
    current_user = getattr(g, 'current_user', None)

    try:
        result = MockService.update_mock(mock_id, data, current_user)
        return jsonify(result)
    except Exception as e:
        raise APIException('Server error', 500, {'details': str(e)})


@mock_bp.route('/mock/<int:mock_id>', methods=['DELETE'])
def delete_mock(mock_id):
    """删除 Mock API"""

    try:
        result = MockService.delete_mock(mock_id)
        return jsonify(result)
    except Exception as e:
        raise APIException('Server error', 500, {'details': str(e)})


@mock_bp.route('/mock/execute/<path:api_path>', methods=['GET', 'POST', 'PUT', 'DELETE'])
def execute_mock(api_path):
    """执行 Mock API"""

    # 准备请求数据
    request_json = request.get_json(silent=True) or {}
    request_data = {'headers': dict(request.headers), 'args': request.args.to_dict(), 'json': request_json,
        'form': request.form.to_dict()}

    try:
        result, status_code = MockService.execute_mock(api_path, request.method, request_data)
        return jsonify(result), status_code
    except APIException as e:
        raise e
    except Exception as e:
        raise APIException('Server error', 500, {'details': str(e)})


@mock_bp.route('/mock/curl/<path:api_path>', methods=['GET'])
def generate_curl_command(api_path):
    """生成 Mock API 接口的 cURL 命令"""

    method = request.args.get('method') or request.args.get('method[params][method]') or 'GET'
    method = method.upper()

    try:
        result = MockService.generate_curl_command(api_path, method, request.host_url)
        return jsonify(result)
    except APIException as e:
        raise e
    except Exception as e:
        raise APIException('Server error', 500, {'details': str(e)})

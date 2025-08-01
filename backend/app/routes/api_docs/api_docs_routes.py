#!/usr/bin/env python
# -*- coding:utf-8 -*-

"""
@author       weimenghua
@time         2025/10/1 19:14
@description  API 文档管理路由
"""

from flask import Blueprint, request, jsonify, g

from ...services.api_docs.api_docs_service import ApiDocsService

api_docs_bp = Blueprint('api_docs', __name__)


@api_docs_bp.route('/api-docs/refresh', methods=['POST'])
def refresh_docs():
    """刷新API文档 - 从Gitee获取最新文档并更新数据库"""
    result = ApiDocsService.refresh_docs()
    return jsonify(result) if result['code'] == 0 else (jsonify(result), 500)


@api_docs_bp.route('/api-docs/endpoints', methods=['GET'])
def get_endpoints():
    """获取所有接口端点列表"""
    result = ApiDocsService.get_endpoints()
    return jsonify(result) if result['code'] == 0 else (jsonify(result), 500)


@api_docs_bp.route('/api-docs/endpoints/categories', methods=['GET'])
def get_endpoints_by_categories():
    """按分类获取接口端点（用于目录树）"""
    result = ApiDocsService.get_endpoints_by_categories()
    return jsonify(result) if result['code'] == 0 else (jsonify(result), 500)


@api_docs_bp.route('/api-docs/endpoints/<int:endpoint_id>', methods=['GET'])
def get_endpoint_detail(endpoint_id):
    """获取特定接口端点的详细信息"""
    result = ApiDocsService.get_endpoint_detail(endpoint_id)
    return jsonify(result) if result['code'] == 0 else (jsonify(result), 500)


@api_docs_bp.route('/api-docs/endpoints', methods=['POST'])
def create_endpoint():
    """创建新的接口端点"""
    data = request.get_json()
    current_user = getattr(g, 'current_user', None)
    result = ApiDocsService.create_endpoint(data, current_user)
    status_code = 201 if result['code'] == 0 else (409 if '已存在' in result['message'] else 500)
    return jsonify(result), status_code


@api_docs_bp.route('/api-docs/endpoints/<int:endpoint_id>', methods=['PUT'])
def update_endpoint(endpoint_id):
    """更新接口端点"""
    data = request.get_json()
    current_user = getattr(g, 'current_user', None)
    result = ApiDocsService.update_endpoint(endpoint_id, data, current_user)
    return jsonify(result) if result['code'] == 0 else (jsonify(result), 500)


@api_docs_bp.route('/api-docs/endpoints/<int:endpoint_id>', methods=['DELETE'])
def delete_endpoint(endpoint_id):
    """删除接口端点"""
    result = ApiDocsService.delete_endpoint(endpoint_id)
    return jsonify(result) if result['code'] == 0 else (jsonify(result), 500)


@api_docs_bp.route('/api-docs/endpoints/<int:endpoint_id>/parameters', methods=['GET'])
def get_endpoint_parameters(endpoint_id):
    """获取接口端点的所有参数"""
    result = ApiDocsService.get_endpoint_parameters(endpoint_id)
    return jsonify(result) if result['code'] == 0 else (jsonify(result), 500)


@api_docs_bp.route('/api-docs/endpoints/<int:endpoint_id>/test', methods=['POST'])
def test_endpoint(endpoint_id):
    """测试接口端点"""
    data = request.get_json() or {}
    result = ApiDocsService.test_endpoint(endpoint_id, data)
    return jsonify(result) if result['code'] == 0 else (jsonify(result), 500)

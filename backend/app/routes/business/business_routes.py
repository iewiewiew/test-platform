#!/usr/bin/env python
# -*- coding:utf-8 -*-

"""
@author       weimenghua
@time         2025/1/XX
@description  通用业务路由 - 场景化数据构造
"""

from flask import Blueprint, request, jsonify, g

from ...services.business.business_service import BusinessService
from ...core.exceptions import APIException

business_bp = Blueprint('business', __name__)


@business_bp.route('/business/create-repository', methods=['POST'])
def create_repository():
    """新建仓库"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'code': 1, 'message': '缺少请求参数'}), 400
        
        environment_id = data.get('environment_id')
        project_data = data.get('project_data')
        
        if not environment_id:
            return jsonify({'code': 1, 'message': '缺少environment_id参数'}), 400
        
        if not project_data:
            return jsonify({'code': 1, 'message': '缺少project_data参数'}), 400
        
        result = BusinessService.create_repository(environment_id, project_data)
        return jsonify(result) if result['code'] == 0 else (jsonify(result), 500)
    except APIException as e:
        return jsonify({'code': 1, 'message': e.message}), e.status_code
    except Exception as e:
        return jsonify({'code': 1, 'message': f'执行失败: {str(e)}'}), 500


@business_bp.route('/business/create-issue', methods=['POST'])
def create_issue():
    """新建工作项"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'code': 1, 'message': '缺少请求参数'}), 400
        
        environment_id = data.get('environment_id')
        issue_data = data.get('issue_data')
        
        if not environment_id:
            return jsonify({'code': 1, 'message': '缺少environment_id参数'}), 400
        
        if not issue_data:
            return jsonify({'code': 1, 'message': '缺少issue_data参数'}), 400
        
        result = BusinessService.create_issue(environment_id, issue_data)
        return jsonify(result) if result['code'] == 0 else (jsonify(result), 500)
    except APIException as e:
        return jsonify({'code': 1, 'message': e.message}), e.status_code
    except Exception as e:
        return jsonify({'code': 1, 'message': f'执行失败: {str(e)}'}), 500


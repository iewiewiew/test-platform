#!/usr/bin/env python
# -*- coding:utf-8 -*-

"""
@author       weimenghua
@time         2025/1/XX
@description  Pytest执行路由
"""

from flask import Blueprint, request, jsonify, g

from ...services.test.pytest_executor_service import PytestExecutorService
from ...core.exceptions import APIException

pytest_executor_bp = Blueprint('pytest_executor', __name__)


@pytest_executor_bp.route('/pytest-executor/execute', methods=['POST'])
def execute_pytest():
    """执行Pytest测试并生成Allure报告"""
    try:
        data = request.get_json() or {}
        module_name = data.get('module_name')
        environment_name = data.get('environment_name')
        component_name = data.get('component_name')
        current_user = g.get('current_user')
        
        if not environment_name:
            return jsonify({'error': '请选择测试环境'}), 400

        result = PytestExecutorService.execute_pytest(component_name, module_name, environment_name, current_user)
        return jsonify(result)
    except APIException as e:
        return jsonify({'error': e.message, 'payload': e.payload}), e.status_code
    except Exception as e:
        return jsonify({'error': str(e)}), 500


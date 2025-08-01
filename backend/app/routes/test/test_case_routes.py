#!/usr/bin/env python
# -*- coding:utf-8 -*-

"""
@author       weimenghua
@time         2025/1/XX
@description  测试用例路由
"""

from flask import Blueprint, request, jsonify, g

from ...services.test.test_case_service import TestCaseService
from ...core.exceptions import APIException

test_case_bp = Blueprint('test_case', __name__)


@test_case_bp.route('/test-cases/parse', methods=['POST'])
def parse_test_cases():
    """解析测试用例文件"""
    try:
        data = request.get_json() or {}
        directory_path = data.get('directory_path')
        current_user = g.get('current_user')
        result = TestCaseService.parse_test_cases_from_directory(directory_path, current_user)
        return jsonify(result)
    except APIException as e:
        return jsonify({'error': e.message, 'payload': e.payload}), e.status_code
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@test_case_bp.route('/test-cases', methods=['GET'])
def get_test_cases():
    """获取测试用例列表"""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        search = request.args.get('search')
        environment = request.args.get('environment')
        module_name = request.args.get('module_name')
        component_name = request.args.get('component_name')
        result = TestCaseService.get_test_cases(page, per_page, search, environment, module_name, component_name)
        return jsonify(result)
    except APIException as e:
        return jsonify({'error': e.message, 'payload': e.payload}), e.status_code
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@test_case_bp.route('/test-cases/module-names', methods=['GET'])
def get_module_names():
    """获取所有模块名称列表"""
    try:
        module_names = TestCaseService.get_module_names()
        return jsonify({'data': module_names})
    except APIException as e:
        return jsonify({'error': e.message, 'payload': e.payload}), e.status_code
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@test_case_bp.route('/test-cases/component-names', methods=['GET'])
def get_component_names():
    """获取所有组件名称列表"""
    try:
        component_names = TestCaseService.get_component_names()
        return jsonify({'data': component_names})
    except APIException as e:
        return jsonify({'error': e.message, 'payload': e.payload}), e.status_code
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@test_case_bp.route('/test-cases/<int:test_case_id>', methods=['GET'])
def get_test_case_by_id(test_case_id):
    """根据ID获取测试用例"""
    try:
        test_case = TestCaseService.get_test_case_by_id(test_case_id)
        return jsonify(test_case)
    except APIException as e:
        return jsonify({'error': e.message, 'payload': e.payload}), e.status_code
    except Exception as e:
        return jsonify({'error': str(e)}), 404


@test_case_bp.route('/test-cases/<int:test_case_id>/execute', methods=['POST'])
def execute_test_case(test_case_id):
    """执行测试用例"""
    try:
        data = request.get_json() or {}
        environment_name = data.get('environment_name')
        base_url = data.get('base_url')
        result = TestCaseService.execute_test_case(test_case_id, environment_name, base_url)
        return jsonify(result)
    except APIException as e:
        return jsonify({'error': e.message, 'payload': e.payload}), e.status_code
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@test_case_bp.route('/test-cases', methods=['POST'])
def create_test_case():
    """创建测试用例"""
    try:
        data = request.get_json() or {}
        current_user = g.get('current_user')
        result = TestCaseService.create_test_case(data, current_user)
        return jsonify(result), 201
    except APIException as e:
        return jsonify({'error': e.message, 'payload': e.payload}), e.status_code
    except Exception as e:
        import traceback
        print(f"Error creating test case: {e}")
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500


@test_case_bp.route('/test-cases/<int:test_case_id>', methods=['PUT'])
def update_test_case(test_case_id):
    """更新测试用例"""
    try:
        data = request.get_json() or {}
        current_user = g.get('current_user')
        result = TestCaseService.update_test_case(test_case_id, data, current_user)
        return jsonify(result)
    except APIException as e:
        return jsonify({'error': e.message, 'payload': e.payload}), e.status_code
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@test_case_bp.route('/test-cases/<int:test_case_id>', methods=['DELETE'])
def delete_test_case(test_case_id):
    """删除测试用例"""
    try:
        result = TestCaseService.delete_test_case(test_case_id)
        return jsonify(result)
    except APIException as e:
        return jsonify({'error': e.message, 'payload': e.payload}), e.status_code
    except Exception as e:
        return jsonify({'error': str(e)}), 404


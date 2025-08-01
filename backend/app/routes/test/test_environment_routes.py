#!/usr/bin/env python
# -*- coding:utf-8 -*-

"""
@author       weimenghua
@time         2025/1/XX
@description  测试环境路由
"""

from flask import Blueprint, request, jsonify, g, Response

from ...services.test.test_environment_service import TestEnvironmentService
from ...core.exceptions import APIException

test_environment_bp = Blueprint('test_environment', __name__)


@test_environment_bp.route('/test-environments/parse', methods=['POST'])
def parse_test_environments():
    """解析配置文件并初始化数据库"""
    try:
        data = request.get_json() or {}
        config_file = data.get('config_file')
        current_user = g.get('current_user')
        result = TestEnvironmentService.parse_config_file(config_file, current_user)
        return jsonify(result)
    except APIException as e:
        return jsonify({'error': e.message, 'payload': e.payload}), e.status_code
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@test_environment_bp.route('/test-environments', methods=['GET'])
def get_test_environments():
    """获取测试环境列表"""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        search = request.args.get('search')
        result = TestEnvironmentService.get_test_environments(page, per_page, search)
        return jsonify(result)
    except APIException as e:
        return jsonify({'error': e.message, 'payload': e.payload}), e.status_code
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@test_environment_bp.route('/test-environments/<int:env_id>', methods=['GET'])
def get_test_environment_by_id(env_id):
    """根据ID获取测试环境详情"""
    try:
        env = TestEnvironmentService.get_test_environment_by_id(env_id)
        return jsonify(env)
    except APIException as e:
        return jsonify({'error': e.message, 'payload': e.payload}), e.status_code
    except Exception as e:
        return jsonify({'error': str(e)}), 404


@test_environment_bp.route('/test-environments', methods=['POST'])
def create_test_environment():
    """创建测试环境"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'Missing required fields'}), 400

        current_user = getattr(g, 'current_user', None)
        env = TestEnvironmentService.create_test_environment(data, current_user)
        return jsonify(env), 201
    except APIException as e:
        return jsonify({'error': e.message, 'payload': e.payload}), e.status_code
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@test_environment_bp.route('/test-environments/<int:env_id>', methods=['PUT'])
def update_test_environment(env_id):
    """更新测试环境"""
    try:
        data = request.get_json()
        current_user = getattr(g, 'current_user', None)
        env = TestEnvironmentService.update_test_environment(env_id, data, current_user)
        return jsonify(env)
    except APIException as e:
        return jsonify({'error': e.message, 'payload': e.payload}), e.status_code
    except Exception as e:
        return jsonify({'error': str(e)}), 404


@test_environment_bp.route('/test-environments/<int:env_id>', methods=['DELETE'])
def delete_test_environment(env_id):
    """删除测试环境"""
    try:
        result = TestEnvironmentService.delete_test_environment(env_id)
        return jsonify(result)
    except APIException as e:
        return jsonify({'error': e.message, 'payload': e.payload}), e.status_code
    except Exception as e:
        return jsonify({'error': str(e)}), 404


@test_environment_bp.route('/test-environments/export', methods=['GET'])
def export_all_test_environments():
    """导出所有测试环境配置（支持 YAML 和 JSON 格式）"""
    try:
        # 获取导出格式参数，默认为 json
        export_format = request.args.get('format', 'json').lower()
        
        if export_format not in ['json', 'yaml']:
            return jsonify({'error': '不支持的导出格式，仅支持 json 或 yaml'}), 400
        
        # 调用服务层方法导出所有环境
        content, filename, mimetype = TestEnvironmentService.export_all_test_environments(export_format)
        
        # 返回文件下载响应
        response = Response(
            content,
            mimetype=mimetype,
            headers={
                'Content-Disposition': f'attachment; filename="{filename}"',
                'Content-Type': f'{mimetype}; charset=utf-8'
            }
        )
        return response
        
    except APIException as e:
        return jsonify({'error': e.message, 'payload': e.payload}), e.status_code
    except Exception as e:
        return jsonify({'error': str(e)}), 500


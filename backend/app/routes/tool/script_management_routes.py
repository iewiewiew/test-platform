#!/usr/bin/env python
# -*- coding:utf-8 -*-

"""
@author       weimenghua
@time         2025/01/26
@description  自动化脚本管理路由
"""

from flask import Blueprint, request, jsonify, g
from werkzeug.utils import secure_filename
import os

from ...core.exceptions import APIException
from ...services.tool.script_management_service import script_management_service

script_management_bp = Blueprint('script_management', __name__)


@script_management_bp.route('/script-management/scripts', methods=['GET'])
def get_scripts():
    """获取脚本列表（分页）"""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        name = request.args.get('name')
        script_type = request.args.get('script_type')
        
        result = script_management_service.get_all_scripts(page, per_page, name, script_type)
        return jsonify(result)
    except APIException as e:
        raise e
    except Exception as e:
        raise APIException('服务器错误', 500, {'details': str(e)})


@script_management_bp.route('/script-management/scripts/<int:script_id>', methods=['GET'])
def get_script_by_id(script_id):
    """根据ID获取脚本"""
    try:
        script = script_management_service.get_script_by_id(script_id)
        return jsonify(script)
    except APIException as e:
        raise e
    except Exception as e:
        raise APIException('服务器错误', 500, {'details': str(e)})


@script_management_bp.route('/script-management/scripts', methods=['POST'])
def create_script():
    """创建脚本"""
    try:
        data = request.get_json()
        if not data or 'name' not in data or 'script_content' not in data:
            raise APIException('缺少必要字段：name、script_content', 400)
        
        current_user = getattr(g, 'current_user', None)
        script = script_management_service.create_script(data, current_user)
        return jsonify(script), 201
    except APIException as e:
        raise e
    except Exception as e:
        raise APIException('服务器错误', 500, {'details': str(e)})


@script_management_bp.route('/script-management/scripts/<int:script_id>', methods=['PUT'])
def update_script(script_id):
    """更新脚本"""
    try:
        data = request.get_json()
        current_user = getattr(g, 'current_user', None)
        script = script_management_service.update_script(script_id, data, current_user)
        return jsonify(script)
    except APIException as e:
        raise e
    except Exception as e:
        raise APIException('服务器错误', 500, {'details': str(e)})


@script_management_bp.route('/script-management/scripts/<int:script_id>', methods=['DELETE'])
def delete_script(script_id):
    """删除脚本"""
    try:
        result = script_management_service.delete_script(script_id)
        return jsonify(result)
    except APIException as e:
        raise e
    except Exception as e:
        raise APIException('服务器错误', 500, {'details': str(e)})


@script_management_bp.route('/script-management/scripts/<int:script_id>/execute', methods=['POST'])
def execute_script(script_id):
    """手动执行脚本"""
    try:
        data = request.get_json() or {}
        triggered_by = data.get('triggered_by', 'manual')
        
        execution_id = script_management_service.execute_script(script_id, 'manual', triggered_by)
        return jsonify({
            'message': '脚本执行已启动',
            'execution_id': execution_id
        })
    except APIException as e:
        raise e
    except Exception as e:
        raise APIException('服务器错误', 500, {'details': str(e)})


@script_management_bp.route('/script-management/executions', methods=['GET'])
def get_execution_history():
    """获取执行记录（仅用于获取最新执行记录，用于查看功能）"""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 1, type=int)
        script_id = request.args.get('script_id', type=int)
        status = request.args.get('status')
        
        result = script_management_service.get_execution_history(script_id, page, per_page, status)
        return jsonify(result)
    except APIException as e:
        raise e
    except Exception as e:
        raise APIException('服务器错误', 500, {'details': str(e)})


@script_management_bp.route('/script-management/executions/<int:execution_id>', methods=['GET'])
def get_execution_by_id(execution_id):
    """获取执行记录详情"""
    try:
        execution = script_management_service.get_execution_by_id(execution_id)
        return jsonify(execution)
    except APIException as e:
        raise e
    except Exception as e:
        raise APIException('服务器错误', 500, {'details': str(e)})


@script_management_bp.route('/script-management/executions/<int:execution_id>/cancel', methods=['POST'])
def cancel_execution(execution_id):
    """取消正在执行的脚本"""
    try:
        result = script_management_service.cancel_execution(execution_id)
        return jsonify(result)
    except APIException as e:
        raise e
    except Exception as e:
        raise APIException('服务器错误', 500, {'details': str(e)})

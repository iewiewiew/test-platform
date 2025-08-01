#!/usr/bin/env python
# -*- coding:utf-8 -*-

"""
@author       weimenghua
@time         2025/01/26
@description  数据库连接管理路由
"""

from flask import Blueprint, request, jsonify, g

from ...core.exceptions import APIException
from ...services.database.database_conn_service import DatabaseConnService

database_conn_bp = Blueprint('database_conn', __name__)


@database_conn_bp.route('/database-connections', methods=['GET'])
def get_all_connections():
    """获取所有数据库连接（支持分页和搜索）"""
    
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    name = request.args.get('name')
    host = request.args.get('host')
    database = request.args.get('database')
    
    try:
        result = DatabaseConnService.get_all_connections(
            page=page, 
            per_page=per_page, 
            name=name,
            host=host,
            database=database
        )
        return jsonify(result)
    except Exception as e:
        raise APIException('服务器错误', 500, {'details': str(e)})


@database_conn_bp.route('/database-connections/select', methods=['GET'])
def get_all_connections_for_select():
    """获取所有数据库连接（用于下拉选择）"""
    
    try:
        result = DatabaseConnService.get_all_connections_for_select()
        return jsonify(result)
    except Exception as e:
        raise APIException('服务器错误', 500, {'details': str(e)})


@database_conn_bp.route('/database-connections/<int:connection_id>', methods=['GET'])
def get_connection_by_id(connection_id):
    """获取单个数据库连接详情"""
    
    try:
        connection = DatabaseConnService.get_connection_by_id(connection_id)
        return jsonify(connection)
    except APIException as e:
        raise e
    except Exception as e:
        raise APIException('服务器错误', 500, {'details': str(e)})


@database_conn_bp.route('/database-connections', methods=['POST'])
def create_connection():
    """创建数据库连接"""
    
    data = request.get_json()
    current_user = getattr(g, 'current_user', None)
    
    try:
        result = DatabaseConnService.create_connection(data, current_user)
        return jsonify(result), 201
    except APIException as e:
        raise e
    except Exception as e:
        raise APIException('服务器错误', 500, {'details': str(e)})


@database_conn_bp.route('/database-connections/<int:connection_id>', methods=['PUT'])
def update_connection(connection_id):
    """更新数据库连接"""
    
    data = request.get_json()
    current_user = getattr(g, 'current_user', None)
    
    try:
        result = DatabaseConnService.update_connection(connection_id, data, current_user)
        return jsonify(result)
    except APIException as e:
        raise e
    except Exception as e:
        raise APIException('服务器错误', 500, {'details': str(e)})


@database_conn_bp.route('/database-connections/<int:connection_id>', methods=['DELETE'])
def delete_connection(connection_id):
    """删除数据库连接"""
    
    try:
        result = DatabaseConnService.delete_connection(connection_id)
        return jsonify(result)
    except APIException as e:
        raise e
    except Exception as e:
        raise APIException('服务器错误', 500, {'details': str(e)})


@database_conn_bp.route('/database-connections/<int:connection_id>/test', methods=['POST'])
def test_connection(connection_id):
    """测试数据库连接"""
    
    try:
        result = DatabaseConnService.test_connection(connection_id)
        return jsonify(result)
    except APIException as e:
        raise e
    except Exception as e:
        raise APIException('服务器错误', 500, {'details': str(e)})


@database_conn_bp.route('/database-connections/test', methods=['POST'])
def test_connection_params():
    """测试数据库连接参数（不保存）"""
    
    data = request.get_json()
    
    if not data:
        raise APIException('测试数据不能为空', 400)
    
    try:
        result = DatabaseConnService.test_connection_params(data)
        return jsonify(result)
    except APIException as e:
        raise e
    except Exception as e:
        raise APIException('服务器错误', 500, {'details': str(e)})

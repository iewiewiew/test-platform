#!/usr/bin/env python
# -*- coding:utf-8 -*-

"""
@author       weimenghua
@time         2025/01/26
@description  Redis 数据库路由
"""

from flask import Blueprint, request, jsonify

from ...core.exceptions import APIException
from ...services.database.redis_service import RedisService

redis_bp = Blueprint('redis', __name__)


@redis_bp.route('/redis/<int:connection_id>/keys', methods=['GET'])
def get_keys(connection_id):
    """获取 Redis keys"""
    try:
        pattern = request.args.get('pattern', '*')
        cursor = request.args.get('cursor', 0, type=int)
        count = request.args.get('count', 100, type=int)
        
        result = RedisService().get_keys(connection_id, pattern, cursor, count)
        return jsonify(result)
    except APIException as e:
        raise e
    except Exception as e:
        raise APIException('服务器错误', 500, {'details': str(e)})


@redis_bp.route('/redis/<int:connection_id>/keys/<path:key>', methods=['GET'])
def get_key_info(connection_id, key):
    """获取 key 的详细信息"""
    try:
        result = RedisService().get_key_info(connection_id, key)
        return jsonify(result)
    except APIException as e:
        raise e
    except Exception as e:
        raise APIException('服务器错误', 500, {'details': str(e)})


@redis_bp.route('/redis/<int:connection_id>/keys/<path:key>', methods=['POST'])
def set_key_value(connection_id, key):
    """设置 key 的值"""
    try:
        data = request.get_json()
        value = data.get('value')
        key_type = data.get('type', 'string')
        ttl = data.get('ttl')
        
        if value is None:
            raise APIException('value 不能为空', 400)
        
        # 从 data 中移除已作为位置参数传递的键，避免重复传递
        kwargs = {k: v for k, v in data.items() if k not in ('value', 'type', 'ttl')}
        
        result = RedisService().set_key_value(connection_id, key, value, key_type, ttl, **kwargs)
        return jsonify(result)
    except APIException as e:
        raise e
    except Exception as e:
        raise APIException('服务器错误', 500, {'details': str(e)})


@redis_bp.route('/redis/<int:connection_id>/keys/<path:key>', methods=['PUT'])
def update_key_value(connection_id, key):
    """更新 key 的值"""
    try:
        data = request.get_json()
        value = data.get('value')
        key_type = data.get('type')
        ttl = data.get('ttl')
        
        if value is None:
            raise APIException('value 不能为空', 400)
        
        # 从 data 中移除已作为位置参数传递的键，避免重复传递
        kwargs = {k: v for k, v in data.items() if k not in ('value', 'type', 'ttl')}
        
        result = RedisService().update_key_value(connection_id, key, value, key_type, ttl, **kwargs)
        return jsonify(result)
    except APIException as e:
        raise e
    except Exception as e:
        raise APIException('服务器错误', 500, {'details': str(e)})


@redis_bp.route('/redis/<int:connection_id>/keys/<path:key>', methods=['DELETE'])
def delete_key(connection_id, key):
    """删除 key"""
    try:
        result = RedisService().delete_key(connection_id, key)
        return jsonify(result)
    except APIException as e:
        raise e
    except Exception as e:
        raise APIException('服务器错误', 500, {'details': str(e)})


@redis_bp.route('/redis/<int:connection_id>/keys/batch', methods=['DELETE'])
def delete_keys(connection_id):
    """批量删除 keys"""
    try:
        data = request.get_json()
        keys = data.get('keys', [])
        
        if not keys:
            raise APIException('请提供要删除的 keys', 400)
        
        result = RedisService().delete_keys(connection_id, keys)
        return jsonify(result)
    except APIException as e:
        raise e
    except Exception as e:
        raise APIException('服务器错误', 500, {'details': str(e)})


@redis_bp.route('/redis/<int:connection_id>/keys/count', methods=['GET'])
def get_key_count(connection_id):
    """获取 key 的数量"""
    try:
        pattern = request.args.get('pattern', '*')
        result = RedisService().get_key_count(connection_id, pattern)
        return jsonify(result)
    except APIException as e:
        raise e
    except Exception as e:
        raise APIException('服务器错误', 500, {'details': str(e)})


@redis_bp.route('/redis/<int:connection_id>/execute', methods=['POST'])
def execute_command(connection_id):
    """执行 Redis 命令"""
    try:
        data = request.get_json()
        command = data.get('command')
        
        if not command:
            raise APIException('命令不能为空', 400)
        
        result = RedisService().execute_command(connection_id, command)
        return jsonify(result)
    except APIException as e:
        raise e
    except Exception as e:
        raise APIException('服务器错误', 500, {'details': str(e)})


@redis_bp.route('/redis/<int:connection_id>/close', methods=['POST'])
def close_connection(connection_id):
    """关闭 Redis 连接"""
    try:
        result = RedisService().close_connection(connection_id)
        return jsonify(result)
    except APIException as e:
        raise e
    except Exception as e:
        raise APIException('服务器错误', 500, {'details': str(e)})


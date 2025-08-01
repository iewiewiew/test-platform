#!/usr/bin/env python
# -*- coding:utf-8 -*-

"""
@author       weimenghua
@time         2025/10/19 17:11
@description  Linux 服务器信息路由
"""

from flask import Blueprint, request, jsonify, g

from ...services.tool.linux_info_service import LinuxInfoService

linux_info_bp = Blueprint('linux_info', __name__)


@linux_info_bp.route('/servers', methods=['GET'])
def get_servers():
    try:
        # 获取分页参数
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        server_name = request.args.get('server_name', '').strip() or None
        host = request.args.get('host', '').strip() or None
        
        # 调用分页查询方法
        result = LinuxInfoService.get_all_servers(
            page=page,
            per_page=per_page,
            server_name=server_name,
            host=host
        )
        
        return jsonify({
            'success': True,
            'data': result['data'],
            'total': result['total'],
            'page': result['page'],
            'per_page': result['per_page']
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@linux_info_bp.route('/servers', methods=['POST'])
def create_server():
    try:
        data = request.get_json()
        required_fields = ['server_name', 'host', 'username']

        for field in required_fields:
            if field not in data or not data[field]:
                return jsonify({'success': False, 'error': f'Missing required field: {field}'}), 400

        current_user = getattr(g, 'current_user', None)
        server = LinuxInfoService.create_server(data, current_user)
        return jsonify({'success': True, 'data': server.to_dict()}), 201
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@linux_info_bp.route('/servers/<int:server_id>', methods=['GET'])
def get_server(server_id):
    try:
        server = LinuxInfoService.get_server_by_id(server_id)
        if server:
            return jsonify({'success': True, 'data': server.to_dict()})
        else:
            return jsonify({'success': False, 'error': 'Server not found'}), 404
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@linux_info_bp.route('/servers/<int:server_id>', methods=['PUT'])
def update_server(server_id):
    try:
        data = request.get_json()
        current_user = getattr(g, 'current_user', None)
        server = LinuxInfoService.update_server(server_id, data, current_user)
        if server:
            return jsonify({'success': True, 'data': server.to_dict()})
        else:
            return jsonify({'success': False, 'error': 'Server not found'}), 404
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@linux_info_bp.route('/servers/<int:server_id>', methods=['DELETE'])
def delete_server(server_id):
    try:
        success = LinuxInfoService.delete_server(server_id)
        if success:
            return jsonify({'success': True, 'message': 'Server deleted successfully'})
        else:
            return jsonify({'success': False, 'error': 'Server not found'}), 404
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@linux_info_bp.route('/servers/<int:server_id>/execute', methods=['POST'])
def execute_command(server_id):
    try:
        data = request.get_json()
        command = data.get('command')

        if not command:
            return jsonify({'success': False, 'error': 'Command is required'}), 400

        result = LinuxInfoService.execute_command(server_id, command)
        return jsonify(result)
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@linux_info_bp.route('/servers/<int:server_id>/info', methods=['GET'])
def get_server_info(server_id):
    try:
        info = LinuxInfoService.get_server_info(server_id)
        return jsonify({'success': True, 'data': info})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@linux_info_bp.route('/servers/<int:server_id>/metrics', methods=['GET'])
def get_server_metrics(server_id):
    """获取单台服务器资源使用指标"""
    try:
        data = LinuxInfoService.get_server_metrics(server_id)
        return jsonify({'success': True, 'data': data})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@linux_info_bp.route('/servers/metrics', methods=['GET'])
def get_all_servers_metrics():
    """获取所有服务器资源使用指标"""
    try:
        data = LinuxInfoService.get_all_server_metrics()
        return jsonify({'success': True, 'data': data})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

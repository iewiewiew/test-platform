#!/usr/bin/env python
# -*- coding:utf-8 -*-

"""
@author       weimenghua
@time         2025/10/27 15:18
@description  角色管理路由
"""

from flask import Blueprint, request, jsonify

from ...models.auth.user_model import Permission
from ...services.auth.user_service import RoleService
from ...utils.decorators import token_required, permission_required

role_bp = Blueprint('roles', __name__)


@role_bp.route('/roles', methods=['GET'])
@token_required
@permission_required(Permission.ROLE_READ)
def get_roles(current_user):
    try:
        roles = RoleService.get_all_roles()
        return jsonify({'roles': [role.to_dict() for role in roles], 'total': len(roles)}), 200
    except Exception as e:
        return jsonify({'message': str(e)}), 500


@role_bp.route('/roles/<int:role_id>', methods=['GET'])
@token_required
@permission_required(Permission.ROLE_READ)
def get_role(current_user, role_id):
    role = RoleService.get_role_by_id(role_id)
    if not role:
        return jsonify({'message': '角色不存在'}), 404

    return jsonify({'role': role.to_dict()}), 200


@role_bp.route('/roles', methods=['POST'])
@token_required
@permission_required(Permission.ROLE_WRITE)
def create_role(current_user):
    data = request.get_json()

    if not data.get('name'):
        return jsonify({'message': '角色名不能为空'}), 400

    try:
        role = RoleService.create_role(data, current_user)
        return jsonify({'message': '角色创建成功', 'role': role.to_dict()}), 201
    except ValueError as e:
        return jsonify({'message': str(e)}), 400
    except Exception as e:
        return jsonify({'message': '创建角色失败'}), 500


@role_bp.route('/roles/<int:role_id>', methods=['PUT'])
@token_required
@permission_required(Permission.ROLE_WRITE)
def update_role(current_user, role_id):
    data = request.get_json()

    try:
        role = RoleService.update_role(role_id, data, current_user)
        return jsonify({'message': '角色更新成功', 'role': role.to_dict()}), 200
    except ValueError as e:
        return jsonify({'message': str(e)}), 400
    except Exception as e:
        return jsonify({'message': '更新角色失败'}), 500


@role_bp.route('/roles/<int:role_id>', methods=['DELETE'])
@token_required
@permission_required(Permission.ROLE_WRITE)
def delete_role(current_user, role_id):
    try:
        RoleService.delete_role(role_id)
        return jsonify({'message': '角色删除成功'}), 200
    except ValueError as e:
        return jsonify({'message': str(e)}), 400
    except Exception as e:
        return jsonify({'message': '删除角色失败'}), 500

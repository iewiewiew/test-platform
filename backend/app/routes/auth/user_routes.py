#!/usr/bin/env python
# -*- coding:utf-8 -*-

"""
@author       weimenghua
@time         2025/10/27 15:17
@description  用户管理路由
"""

from flask import Blueprint, request, jsonify

from ...models.auth.user_model import Permission
from ...services.auth.user_service import UserService
from ...utils.decorators import token_required, permission_required
from ...core.exceptions import APIException

user_bp = Blueprint('users', __name__)


@user_bp.route('/users', methods=['GET'])
@token_required
@permission_required(Permission.USER_READ)
def get_users(current_user):
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    search = request.args.get('search', '')

    try:
        result = UserService.get_all_users(page=page, per_page=per_page, search=search)
        return jsonify(result), 200
    except APIException as e:
        return jsonify({'message': e.message, 'payload': e.payload}), e.status_code
    except Exception as e:
        return jsonify({'message': str(e)}), 500


@user_bp.route('/users/<int:user_id>', methods=['GET'])
@token_required
@permission_required(Permission.USER_READ)
def get_user(current_user, user_id):
    user = UserService.get_user_by_id(user_id)
    if not user:
        return jsonify({'message': '用户不存在'}), 404

    # UserService.get_user_by_id 已返回 dict，这里直接返回即可
    return jsonify({'user': user}), 200


@user_bp.route('/users', methods=['POST'])
@token_required
@permission_required(Permission.USER_WRITE)
def create_user(current_user):
    data = request.get_json()

    required_fields = ['username', 'email', 'password', 'full_name']
    for field in required_fields:
        if not data.get(field):
            return jsonify({'message': f'{field}不能为空'}), 400

    try:
        user = UserService.create_user(data, current_user)
        return jsonify({'message': '用户创建成功', 'user': user.to_dict()}), 201
    except APIException as e:
        return jsonify({'message': e.message, 'payload': e.payload}), e.status_code
    except Exception as e:
        import traceback
        print(f"Error creating user: {e}")
        traceback.print_exc()
        return jsonify({'message': f'创建用户失败: {str(e)}'}), 500


@user_bp.route('/users/<int:user_id>', methods=['PUT'])
@token_required
@permission_required(Permission.USER_WRITE)
def update_user(current_user, user_id):
    data = request.get_json()

    try:
        user = UserService.update_user(user_id, data, current_user)
        return jsonify({'message': '用户更新成功', 'user': user.to_dict()}), 200
    except APIException as e:
        return jsonify({'message': e.message, 'payload': e.payload}), e.status_code
    except Exception as e:
        import traceback
        print(f"Error updating user: {e}")
        traceback.print_exc()
        return jsonify({'message': f'更新用户失败: {str(e)}'}), 500


@user_bp.route('/users/<int:user_id>', methods=['DELETE'])
@token_required
@permission_required(Permission.USER_DELETE)
def delete_user(current_user, user_id):
    try:
        UserService.delete_user(user_id)
        return jsonify({'message': '用户删除成功'}), 200
    except APIException as e:
        return jsonify({'message': e.message, 'payload': e.payload}), e.status_code
    except Exception as e:
        import traceback
        print(f"Error deleting user: {e}")
        traceback.print_exc()
        return jsonify({'message': f'删除用户失败: {str(e)}'}), 500

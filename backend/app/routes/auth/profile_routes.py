#!/usr/bin/env python
# -*- coding:utf-8 -*-

"""
@author       weimenghua
@time         2025/11/03 00:00
@description  个人资料相关路由
"""

import os
import uuid
from werkzeug.utils import secure_filename
from flask import Blueprint, jsonify, g, request, current_app

from ...core.database import db
from ...utils.decorators import token_required
from ...services.auth.user_service import UserService

profile_bp = Blueprint('profile', __name__)


@profile_bp.route('/profile', methods=['GET'])
@token_required
def get_profile(current_user):
    # 返回当前用户的完整信息（包含角色与权限）
    user_dict = current_user.to_full_dict()
    return jsonify({'success': True, 'data': user_dict}), 200


# 注：根据全局策略，普通用户无写权限。以下接口将受全局拦截，仅管理员可调用。
@profile_bp.route('/profile', methods=['PUT'])
@token_required
def update_profile(current_user):
    data = request.get_json() or {}

    allowed_fields = {'full_name', 'email'}
    update_data = {k: v for k, v in data.items() if k in allowed_fields}

    if not update_data:
        return jsonify({'success': False, 'message': '无可更新的字段'}), 400

    user = UserService.update_user(current_user.id, update_data)
    return jsonify({'success': True, 'data': user.to_dict()}), 200


@profile_bp.route('/profile/password', methods=['PUT'])
@token_required
def change_password(current_user):
    data = request.get_json() or {}
    old_password = data.get('old_password')
    new_password = data.get('new_password')

    if not old_password or not new_password:
        return jsonify({'success': False, 'message': 'old_password/new_password 不能为空'}), 400

    if not current_user.check_password(old_password):
        return jsonify({'success': False, 'message': '原密码不正确'}), 400

    current_user.set_password(new_password)
    from ..core.database import db
    db.session.commit()
    return jsonify({'success': True, 'message': '密码修改成功'}), 200


def _allowed_image(filename):
    if '.' not in filename:
        return False
    ext = filename.rsplit('.', 1)[1].lower()
    return ext in current_app.config.get('ALLOWED_IMAGE_EXTENSIONS', set())


@profile_bp.route('/profile/avatar', methods=['POST'])
@token_required
def upload_avatar(current_user):
    if 'file' not in request.files:
        return jsonify({'success': False, 'message': '未找到文件字段 file'}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({'success': False, 'message': '未选择文件'}), 400

    if not _allowed_image(file.filename):
        return jsonify({'success': False, 'message': '不支持的图片格式'}), 400

    # 确保目录存在
    upload_dir = current_app.config['AVATAR_UPLOAD_FOLDER']
    os.makedirs(upload_dir, exist_ok=True)

    ext = file.filename.rsplit('.', 1)[1].lower()
    filename = secure_filename(f"{current_user.id}_{uuid.uuid4().hex}.{ext}")
    save_path = os.path.join(upload_dir, filename)
    file.save(save_path)

    # 生成可访问的 URL（使用 /static/avatars/<file>）
    subdir = current_app.config['AVATAR_SUBDIR']
    avatar_url = f"/static/{subdir}/{filename}"

    # 更新用户头像地址
    current_user.avatar_url = avatar_url
    db.session.commit()

    return jsonify({'success': True, 'data': {'avatar_url': avatar_url}}), 200



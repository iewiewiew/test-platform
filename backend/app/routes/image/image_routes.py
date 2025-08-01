#!/usr/bin/env python
# -*- coding:utf-8 -*-

"""
@author       weimenghua
@time         2025/12/22
@description  图片路由
"""

import os
from flask import Blueprint, request, jsonify, g, send_from_directory, current_app

from ...services.image.image_service import ImageService

image_bp = Blueprint('image', __name__)


@image_bp.route('/images', methods=['GET'])
def get_images():
    """获取图片列表"""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        filename = request.args.get('filename', '')

        result = ImageService.get_all_images(
            page=page,
            per_page=per_page,
            filename=filename if filename else None
        )

        return jsonify({'success': True, 'data': result})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500


@image_bp.route('/images/<int:image_id>', methods=['GET'])
def get_image(image_id):
    """获取单个图片信息"""
    try:
        image = ImageService.get_image_by_id(image_id)
        if not image:
            return jsonify({'success': False, 'message': '图片不存在'}), 404

        return jsonify({'success': True, 'data': image.to_dict()})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500


@image_bp.route('/images', methods=['POST'])
def upload_image():
    """上传图片"""
    try:
        if 'file' not in request.files:
            return jsonify({'success': False, 'message': '未选择文件'}), 400

        file = request.files['file']
        description = request.form.get('description', '')
        current_user = getattr(g, 'current_user', None)

        image = ImageService.upload_image(
            file=file,
            description=description if description else None,
            current_user=current_user
        )

        return jsonify({
            'success': True,
            'data': image.to_dict(),
            'message': '图片上传成功'
        }), 201
    except ValueError as e:
        return jsonify({'success': False, 'message': str(e)}), 400
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500


@image_bp.route('/images/<int:image_id>', methods=['PUT'])
def update_image(image_id):
    """更新图片信息（支持更新图片文件，但保留原有 UUID）"""
    try:
        current_user = getattr(g, 'current_user', None)
        
        # 检查是否有文件上传
        file = None
        if 'file' in request.files:
            file = request.files['file']
            if file.filename == '':
                file = None  # 空文件名表示没有实际上传文件
        
        # 获取表单数据或 JSON 数据
        if request.is_json:
            data = request.get_json() or {}
        else:
            # 从表单获取数据
            data = {
                'description': request.form.get('description', '')
            }
            # 如果值为空字符串，设置为 None（表示不更新）
            if data['description'] == '':
                data.pop('description')

        image = ImageService.update_image(image_id, data, file=file, current_user=current_user)
        if not image:
            return jsonify({'success': False, 'message': '图片不存在'}), 404

        message = '图片信息更新成功'
        if file:
            message = '图片文件和信息更新成功（UUID 保持不变）'

        return jsonify({
            'success': True,
            'data': image.to_dict(),
            'message': message
        })
    except ValueError as e:
        return jsonify({'success': False, 'message': str(e)}), 400
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500


@image_bp.route('/images/<int:image_id>', methods=['DELETE'])
def delete_image(image_id):
    """删除图片"""
    try:
        success = ImageService.delete_image(image_id)
        if not success:
            return jsonify({'success': False, 'message': '图片不存在'}), 404

        return jsonify({'success': True, 'message': '图片删除成功'})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500


@image_bp.route('/images/batch', methods=['DELETE'])
def batch_delete_images():
    """批量删除图片"""
    try:
        data = request.get_json()
        image_ids = data.get('ids', [])

        if not image_ids or not isinstance(image_ids, list):
            return jsonify({'success': False, 'message': 'IDs列表不能为空'}), 400

        result = ImageService.batch_delete_images(image_ids)

        if result['failed_count'] > 0:
            return jsonify({
                'success': True,
                'message': f'成功删除 {result["success_count"]} 张图片，{result["failed_count"]} 张失败',
                'data': result
            }), 200

        return jsonify({
            'success': True,
            'message': f'成功删除 {result["success_count"]} 张图片',
            'data': result
        })
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500


@image_bp.route('/images/<path:filename>', methods=['GET'])
def serve_image(filename):
    """直接访问图片文件 - 支持浏览器直接访问"""
    try:
        image_folder = current_app.config.get('IMAGE_UPLOAD_FOLDER')
        # 安全检查：确保文件名不包含路径分隔符（除了扩展名前的点）
        if filename.count('/') > 0 or '\\' in filename:
            return jsonify({'success': False, 'message': '无效的文件名'}), 400
        
        # 检查文件是否存在
        file_path = os.path.join(image_folder, filename)
        if not os.path.exists(file_path):
            return jsonify({'success': False, 'message': '图片不存在'}), 404
        
        # 设置正确的Content-Type，让浏览器可以直接显示图片
        return send_from_directory(image_folder, filename)
    except Exception as e:
        return jsonify({'success': False, 'message': f'图片访问失败: {str(e)}'}), 404


#!/usr/bin/env python
# -*- coding:utf-8 -*-

"""
@author       weimenghua
@time         2025/01/XX XX:XX
@description  常用文档路由
"""

import os
from pathlib import Path
from flask import Blueprint, request, jsonify, send_from_directory, abort

from ...services.api_docs.docs_service import DocsService

docs_bp = Blueprint('docs', __name__)


@docs_bp.route('/docs/<path:doc_path>', methods=['GET'])
def get_doc(doc_path):
    """获取指定路径的文档内容（支持子目录路径）"""
    try:
        result = DocsService.get_doc(doc_path)
        return jsonify(result) if result['code'] == 0 else (jsonify(result), 500)
    except Exception as e:
        return jsonify({'code': 1, 'message': f'获取文档失败: {str(e)}'}), 500


@docs_bp.route('/docs/list', methods=['GET'])
def get_docs_list():
    """获取所有可用文档列表"""
    try:
        result = DocsService.get_docs_list()
        return jsonify(result) if result['code'] == 0 else (jsonify(result), 500)
    except Exception as e:
        return jsonify({'code': 1, 'message': f'获取文档列表失败: {str(e)}'}), 500


@docs_bp.route('/docs', methods=['POST'])
def create_doc():
    """创建新文档（支持子目录路径）"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'code': 1, 'message': '请求数据不能为空'}), 400
        
        doc_path = data.get('path') or data.get('name', '')
        content = data.get('content', '')
        
        if not doc_path:
            return jsonify({'code': 1, 'message': '文档路径不能为空'}), 400
        
        result = DocsService.create_doc(doc_path, content)
        return jsonify(result) if result['code'] == 0 else (jsonify(result), 500)
    except Exception as e:
        return jsonify({'code': 1, 'message': f'创建文档失败: {str(e)}'}), 500


@docs_bp.route('/docs/<path:doc_path>', methods=['PUT'])
def update_doc(doc_path):
    """更新文档内容（支持子目录路径）"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'code': 1, 'message': '请求数据不能为空'}), 400
        
        content = data.get('content', '')
        
        result = DocsService.update_doc(doc_path, content)
        return jsonify(result) if result['code'] == 0 else (jsonify(result), 500)
    except Exception as e:
        return jsonify({'code': 1, 'message': f'更新文档失败: {str(e)}'}), 500


@docs_bp.route('/docs/<path:doc_path>', methods=['DELETE'])
def delete_doc(doc_path):
    """删除文档（支持子目录路径）"""
    try:
        result = DocsService.delete_doc(doc_path)
        return jsonify(result) if result['code'] == 0 else (jsonify(result), 500)
    except Exception as e:
        return jsonify({'code': 1, 'message': f'删除文档失败: {str(e)}'}), 500


@docs_bp.route('/docs/assets/<path:asset_path>', methods=['GET'])
def get_doc_asset(asset_path):
    """获取文档资源文件（图片等）"""
    try:
        docs_dir = DocsService.get_docs_dir()
        
        # Flask 的 <path:> 参数会自动进行 URL 解码，所以 asset_path 已经是解码后的路径
        print(f"[DEBUG] 请求图片资源: asset_path={asset_path}, docs_dir={docs_dir}")
        
        # 处理路径，确保安全（防止路径遍历攻击）
        # 注意：Flask 的 <path:> 参数会自动去掉开头的 /，所以不需要检查
        
        # 先检查是否包含路径遍历攻击（在 URL 解码后检查）
        if '..' in asset_path or asset_path.startswith('/'):
            print(f"[ERROR] 路径包含非法字符: {asset_path}")
            abort(400)
        
        # 构建文件路径
        file_path = docs_dir / asset_path
        print(f"[DEBUG] 构建的文件路径: {file_path}")
        
        # 确保文件在 docs 目录内（防止路径遍历）
        # 使用 resolve() 解析所有相对路径和符号链接，然后检查是否在 docs 目录内
        try:
            resolved_path = file_path.resolve()
            resolved_docs_dir = docs_dir.resolve()
            # 检查解析后的路径是否在 docs 目录内
            relative_path = resolved_path.relative_to(resolved_docs_dir)
            print(f"[DEBUG] 解析后的路径: {resolved_path}, 相对路径: {relative_path}")
        except ValueError as e:
            # 路径不在 docs 目录内，可能是路径遍历攻击
            print(f"[ERROR] 路径不在 docs 目录内: {asset_path}, 错误: {str(e)}")
            abort(400)
        
        # 检查文件是否存在
        if not file_path.exists():
            print(f"[ERROR] 文件不存在: {file_path}")
            abort(404)
        
        if not file_path.is_file():
            print(f"[ERROR] 路径不是文件: {file_path}")
            abort(404)
        
        # 检查文件扩展名，只允许图片文件
        allowed_extensions = {'.png', '.jpg', '.jpeg', '.gif', '.svg', '.webp', '.bmp', '.ico'}
        file_ext = file_path.suffix.lower()
        if file_ext not in allowed_extensions:
            print(f"[ERROR] 不允许的文件扩展名: {file_ext}")
            abort(400)
        
        print(f"[SUCCESS] 返回图片文件: {file_path}")
        # 返回文件，设置正确的 MIME 类型
        return send_from_directory(
            str(docs_dir),
            asset_path,
            as_attachment=False
        )
    except Exception as e:
        import traceback
        error_msg = f"获取资源文件失败: {str(e)}\n{traceback.format_exc()}"
        print(f"[ERROR] {error_msg}")
        return jsonify({'code': 1, 'message': f'获取资源文件失败: {str(e)}'}), 500


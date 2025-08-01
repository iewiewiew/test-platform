#!/usr/bin/env python
# -*- coding:utf-8 -*-

"""
@author       weimenghua
@time         2025/01/XX XX:XX
@description  常用文档路由
"""

from flask import Blueprint, request, jsonify

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


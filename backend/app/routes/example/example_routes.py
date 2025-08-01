#!/usr/bin/env python
# -*- coding:utf-8 -*-

"""
@author       weimenghua
@time         2025/10/21 10:05
@description  示例模块路由
"""

from flask import Blueprint, request, jsonify, g

from ...services.example.example_service import ExampleService

example_bp = Blueprint('example', __name__)


@example_bp.route('/examples', methods=['GET'])
def get_examples():
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        name = request.args.get('name', '')
        status = request.args.get('status', '')

        result = ExampleService.get_all_examples(page=page, per_page=per_page, name=name if name else None,
            status=status if status else None)

        return jsonify({'success': True, 'data': result})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500


@example_bp.route('/examples/<int:example_id>', methods=['GET'])
def get_example(example_id):
    try:
        example = ExampleService.get_example_by_id(example_id)
        if not example:
            return jsonify({'success': False, 'message': 'Example not found'}), 404

        return jsonify({'success': True, 'data': example.to_dict()})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500


@example_bp.route('/examples', methods=['POST'])
def create_example():
    try:
        data = request.get_json()

        if not data or not data.get('name'):
            return jsonify({'success': False, 'message': 'Name is required'}), 400

        current_user = getattr(g, 'current_user', None)
        example = ExampleService.create_example(data, current_user)
        return jsonify({'success': True, 'data': example.to_dict(), 'message': 'Example created successfully'}), 201
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500


@example_bp.route('/examples/<int:example_id>', methods=['PUT'])
def update_example(example_id):
    try:
        data = request.get_json()

        current_user = getattr(g, 'current_user', None)
        example = ExampleService.update_example(example_id, data, current_user)
        if not example:
            return jsonify({'success': False, 'message': 'Example not found'}), 404

        return jsonify({'success': True, 'data': example.to_dict(), 'message': 'Example updated successfully'})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500


@example_bp.route('/examples/<int:example_id>', methods=['DELETE'])
def delete_example(example_id):
    try:
        success = ExampleService.delete_example(example_id)
        if not success:
            return jsonify({'success': False, 'message': 'Example not found'}), 404

        return jsonify({'success': True, 'message': 'Example deleted successfully'})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500


@example_bp.route('/examples/batch', methods=['DELETE'])
def batch_delete_examples():
    """批量删除示例"""
    try:
        data = request.get_json()
        example_ids = data.get('ids', [])
        
        if not example_ids or not isinstance(example_ids, list):
            return jsonify({'success': False, 'message': 'IDs列表不能为空'}), 400
        
        result = ExampleService.batch_delete_examples(example_ids)
        
        if result['failed_count'] > 0:
            return jsonify({
                'success': True,
                'message': f'成功删除 {result["success_count"]} 条记录，{result["failed_count"]} 条失败',
                'data': result
            }), 200
        
        return jsonify({
            'success': True,
            'message': f'成功删除 {result["success_count"]} 条记录',
            'data': result
        })
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

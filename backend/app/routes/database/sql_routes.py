#!/usr/bin/env python
# -*- coding:utf-8 -*-

"""
@author       weimenghua
@time         2025/10/22 08:56
@description  SQL 工具箱路由
"""

from flask import Blueprint, request, jsonify, g

from ...services.database.sql_service import SQLService

sql_bp = Blueprint('sql', __name__)


@sql_bp.route('/sql/categories', methods=['GET'])
def get_categories():
    """获取所有分类 - 直接返回默认分类"""
    try:
        # 直接返回默认分类，不从数据库查询
        default_categories = ["示例模板SQL", "业务逻辑SQL"]

        return jsonify({'success': True, 'data': default_categories, 'total': len(default_categories)})

    except Exception as e:
        return jsonify({'success': False, 'error': str(e), 'data': []}), 500


@sql_bp.route('/sql/execute', methods=['POST'])
def execute_sql():
    """执行SQL查询"""
    data = request.get_json()
    sql_query = data.get('sql_query', '').strip()
    limit = data.get('limit', 1000)
    connection_id = data.get('connection_id')
    database_name = data.get('database_name')

    if not sql_query:
        return jsonify({'success': False, 'error': 'SQL查询不能为空'})

    # 转换connection_id为整数（如果提供）
    if connection_id is not None:
        try:
            connection_id = int(connection_id)
        except (ValueError, TypeError):
            return jsonify({'success': False, 'error': '连接ID格式错误'})

    current_user = getattr(g, 'current_user', None)
    result = SQLService.execute_sql(sql_query, limit, connection_id, database_name, current_user)
    return jsonify(result)


@sql_bp.route('/sql/templates', methods=['GET'])
def get_templates():
    """获取所有SQL模板"""
    templates = SQLService.get_all_templates()
    return jsonify({'success': True, 'data': [template.to_dict() for template in templates]})


@sql_bp.route('/sql/templates/<int:template_id>', methods=['GET'])
def get_template(template_id):
    """获取特定SQL模板"""
    template = SQLService.get_template_by_id(template_id)
    if template:
        return jsonify({'success': True, 'data': template.to_dict()})
    return jsonify({'success': False, 'error': '模板不存在'}), 404


@sql_bp.route('/sql/templates', methods=['POST'])
def create_template():
    """创建新的SQL模板"""
    data = request.get_json()

    required_fields = ['name', 'sql_content', 'category']
    for field in required_fields:
        if not data.get(field):
            return jsonify({'success': False, 'error': f'{field} 不能为空'}), 400

    current_user = getattr(g, 'current_user', None)
    template = SQLService.create_template(data, current_user)
    return jsonify({'success': True, 'data': template.to_dict()}), 201


@sql_bp.route('/sql/templates/<int:template_id>', methods=['PUT'])
def update_template(template_id):
    """更新SQL模板"""
    data = request.get_json()
    current_user = getattr(g, 'current_user', None)
    template = SQLService.update_template(template_id, data, current_user)

    if template:
        return jsonify({'success': True, 'data': template.to_dict()})
    return jsonify({'success': False, 'error': '模板不存在'}), 404


@sql_bp.route('/sql/templates/<int:template_id>', methods=['DELETE'])
def delete_template(template_id):
    """删除SQL模板"""
    success = SQLService.delete_template(template_id)
    if success:
        return jsonify({'success': True, 'message': '模板删除成功'})
    return jsonify({'success': False, 'error': '模板不存在'}), 404


@sql_bp.route('/sql/history', methods=['GET'])
def get_history():
    """获取查询历史"""
    limit = request.args.get('limit', 50, type=int)
    history = SQLService.get_query_history(limit)
    return jsonify({'success': True, 'data': [record.to_dict() for record in history]})

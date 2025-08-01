#!/usr/bin/env python
# -*- coding:utf-8 -*-

"""
@author       weimenghua
@time         2025/10/2 15:48
@description  模拟数据生成功能路由
"""

from flask import Blueprint, request, jsonify

from ...services.mock.mock_data_service import MockDataService

mock_data_bp = Blueprint('mock_data', __name__)


@mock_data_bp.route('/mock_data/generate', methods=['POST'])
def generate_mock_data():
    """
    生成模拟数据
    """
    try:
        data = request.get_json()

        # 验证必需参数
        if not data or 'fields' not in data:
            return jsonify({'error': '缺少必需参数: fields'}), 400

        fields = data.get('fields', [])
        count = data.get('count', 1)

        # 生成数据
        result = MockDataService.generate_mock_data(fields, count)

        return jsonify({'success': True, 'data': result, 'count': len(result)})

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@mock_data_bp.route('/mock_data/field-types', methods=['GET'])
def get_field_types():
    """
    获取支持的字段类型
    """
    field_types = MockDataService.get_supported_field_types()
    return jsonify({'success': True, 'data': field_types})

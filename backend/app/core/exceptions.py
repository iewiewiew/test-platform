# !/usr/bin/env python
# -*- coding:utf-8 -*-

"""
@author       weimenghua
@time         2025/9/28 16:22
@description  异常处理模块
"""

from flask import jsonify


class APIException(Exception):
    """API 异常基类"""

    def __init__(self, message, status_code=400, payload=None):
        super().__init__()
        self.message = message
        self.status_code = status_code
        self.payload = payload


def register_error_handlers(blueprint):
    """注册错误处理器到蓝图"""

    @blueprint.errorhandler(APIException)
    def handle_api_exception(error):
        response = jsonify({'error': error.message, 'payload': error.payload})
        response.status_code = error.status_code
        return response

    @blueprint.errorhandler(404)
    def handle_not_found(error):
        return jsonify({'error': 'Resource not found'}), 404

    @blueprint.errorhandler(500)
    def handle_internal_error(error):
        return jsonify({'error': 'Internal server error'}), 500

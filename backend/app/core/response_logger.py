#!/usr/bin/env python
# -*- coding:utf-8 -*-

"""
@author       weimenghua
@time         2025/9/28 16:46
@description  响应日志记录模块
"""

import json
import time

from flask import request

from ..utils.log_util import Logger

logger = Logger()


class ResponseLogger:
    """响应日志记录器"""

    @staticmethod
    def init_app(blueprint):
        """初始化响应日志记录"""

        @blueprint.after_request
        def after_request(response):
            ResponseLogger.log_request_response(request, response)
            return response

        @blueprint.before_request
        def before_request():
            request.start_time = time.time()

    @staticmethod
    def log_request_response(request, response):
        """记录请求和响应信息"""
        # 计算请求处理时间
        duration = time.time() - getattr(request, 'start_time', time.time())

        # 构建日志信息
        log_data = {'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'), 'method': request.method, 'path': request.path,
            'endpoint': request.endpoint or '', 'status_code': response.status_code, 'duration': f"{duration:.3f}s",
            'ip': request.remote_addr, 'user_agent': request.headers.get('User-Agent', '')}

        # 记录请求参数
        if request.args:
            log_data['query_params'] = request.args.to_dict()

        # 记录请求体（仅对 POST/PUT 方法）
        if request.method in ['POST', 'PUT', 'PATCH']:
            request_json = request.get_json(silent=True)
            if request_json:
                log_data['request_body'] = request_json

        # 记录响应数据
        if response.content_type == 'application/json':
            try:
                response_data = response.get_json()
                log_data['response_body'] = response_data
            except:
                log_data['response_body'] = 'Non-JSON response'

        # 格式化输出日志
        ResponseLogger._print_log(log_data)

    @staticmethod
    def _print_log(log_data):
        """格式化打印日志"""
        logger.info(f"{'=' * 90}")
        logger.info(
            f"时间: {log_data['timestamp']} 状态码: {log_data['status_code']} 耗时: {log_data['duration']} 客户端: {log_data['ip']}")
        logger.info(f"方法: {log_data['method']} 路径: {log_data['path']} 端点: {log_data['endpoint']}")

        if 'query_params' in log_data and log_data['query_params']:
            logger.info(f"查询参数: {json.dumps(log_data['query_params'], ensure_ascii=False)}")

        if 'request_body' in log_data:
            # logger.info(f"请求体: {json.dumps(log_data['request_body'], ensure_ascii=False, indent=2)}")  # indent=2 表示格式化
            logger.info(f"请求体: {json.dumps(log_data['request_body'], ensure_ascii=False)}")

        if 'response_body' in log_data:
            # logger.info(f"响应体: {json.dumps(log_data['response_body'], ensure_ascii=False, indent=2)}")  # indent=2 表示格式化
            logger.info(f"响应体: {json.dumps(log_data['response_body'], ensure_ascii=False)}")

        logger.info(f"{'=' * 90}\n")

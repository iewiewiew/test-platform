#!/usr/bin/env python
# -*- coding:utf-8 -*-

"""
@author       weimenghua
@time         2025/1/XX
@description  测试报告路由
"""

from flask import Blueprint, request, jsonify, send_from_directory, g
import os

from ...services.test.test_report_service import TestReportService
from ...core.exceptions import APIException
from ...models.test.test_report_model import TestReport
from ...utils.path_util import PathUtils

test_report_bp = Blueprint('test_report', __name__)


@test_report_bp.route('/test-reports/parse', methods=['POST'])
def parse_test_reports():
    """解析Pytest测试报告"""
    try:
        data = request.get_json() or {}
        report_dir = data.get('report_dir')
        current_user = g.get('current_user')
        result = TestReportService.parse_pytest_reports(report_dir, current_user)
        return jsonify(result)
    except APIException as e:
        return jsonify({'error': e.message, 'payload': e.payload}), e.status_code
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@test_report_bp.route('/test-reports', methods=['GET'])
def get_test_reports():
    """获取测试报告列表"""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        search = request.args.get('search')
        result = TestReportService.get_test_reports(page, per_page, search)
        return jsonify(result)
    except APIException as e:
        return jsonify({'error': e.message, 'payload': e.payload}), e.status_code
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@test_report_bp.route('/test-reports/<int:report_id>', methods=['GET'])
def get_test_report_by_id(report_id):
    """根据ID获取测试报告详情"""
    try:
        # 检查是否需要解析（通过query参数控制）
        auto_parse = request.args.get('parse', 'false').lower() == 'true'
        report = TestReportService.get_test_report_by_id(report_id, auto_parse=auto_parse)
        return jsonify(report)
    except APIException as e:
        return jsonify({'error': e.message, 'payload': e.payload}), e.status_code
    except Exception as e:
        return jsonify({'error': str(e)}), 404


@test_report_bp.route('/test-reports/<int:report_id>/parse', methods=['POST'])
def parse_test_report(report_id):
    """解析单个测试报告"""
    try:
        report = TestReportService.parse_and_update_report(report_id)
        return jsonify(report)
    except APIException as e:
        return jsonify({'error': e.message, 'payload': e.payload}), e.status_code
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@test_report_bp.route('/test-reports/<int:report_id>/logs', methods=['GET'])
def get_test_logs(report_id):
    """获取测试日志"""
    try:
        test_method = request.args.get('test_method')
        result = TestReportService.get_test_logs(report_id, test_method)
        return jsonify(result)
    except APIException as e:
        return jsonify({'error': e.message, 'payload': e.payload}), e.status_code
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@test_report_bp.route('/test-reports/<int:report_id>', methods=['DELETE'])
def delete_test_report(report_id):
    """删除测试报告"""
    try:
        result = TestReportService.delete_test_report(report_id)
        return jsonify(result)
    except APIException as e:
        return jsonify({'error': e.message, 'payload': e.payload}), e.status_code
    except Exception as e:
        return jsonify({'error': str(e)}), 404


@test_report_bp.route('/test-reports/<int:report_id>/allure', methods=['GET'])
def get_allure_report_url(report_id):
    """获取Allure报告访问URL"""
    try:
        report = TestReport.query.filter_by(id=report_id, is_active=True).first_or_404()
        
        # 获取报告目录
        report_dir = TestReportService._get_report_dir()
        
        # 从report_path中提取时间戳
        # report_path格式: backend/app/autotest/report/20251108143916/allure-results
        execution_timestamp = None
        if report.report_path:
            # 从report_path中提取时间戳目录名
            path_parts = report.report_path.split(os.sep)
            if 'allure-results' in path_parts:
                idx = path_parts.index('allure-results')
                if idx > 0:
                    execution_timestamp = path_parts[idx - 1]
        
        if not execution_timestamp:
            return jsonify({'error': '无法从报告路径中提取时间戳'}), 404
        
        # 根据时间戳确定allure报告目录
        timestamp_dir = os.path.join(report_dir, execution_timestamp)
        allure_report_dir = os.path.join(timestamp_dir, 'allure-report')
        
        # 检查Allure报告是否存在
        index_html = os.path.join(allure_report_dir, 'index.html')
        if os.path.exists(index_html):
            # 返回相对URL路径
            return jsonify({
                'url': f'/api/test-reports/{report_id}/allure/index.html'
            })
        else:
            return jsonify({'error': 'Allure报告不存在'}), 404
    except APIException as e:
        return jsonify({'error': e.message, 'payload': e.payload}), e.status_code
    except Exception as e:
        return jsonify({'error': str(e)}), 404


@test_report_bp.route('/test-reports/<int:report_id>/allure/<path:filename>', methods=['GET', 'OPTIONS'])
def serve_allure_report(report_id, filename):
    """提供Allure报告静态文件访问"""
    # 处理 CORS 预检请求
    if request.method == 'OPTIONS':
        response = jsonify({})
        response.headers['Access-Control-Allow-Origin'] = '*'
        response.headers['Access-Control-Allow-Methods'] = 'GET, OPTIONS'
        response.headers['Access-Control-Allow-Headers'] = 'Content-Type'
        return response
    
    try:
        report = TestReport.query.filter_by(id=report_id, is_active=True).first_or_404()
        
        # 获取报告目录
        report_dir = TestReportService._get_report_dir()
        
        # 从report_path中提取时间戳
        execution_timestamp = None
        if report.report_path:
            # 从report_path中提取时间戳目录名
            path_parts = report.report_path.split(os.sep)
            if 'allure-results' in path_parts:
                idx = path_parts.index('allure-results')
                if idx > 0:
                    execution_timestamp = path_parts[idx - 1]
        
        if not execution_timestamp:
            return jsonify({'error': '无法从报告路径中提取时间戳'}), 404
        
        # 根据时间戳确定allure报告目录
        timestamp_dir = os.path.join(report_dir, execution_timestamp)
        allure_report_dir = os.path.join(timestamp_dir, 'allure-report')
        
        # 安全检查：确保文件在报告目录内
        file_path = os.path.join(allure_report_dir, filename)
        if not os.path.abspath(file_path).startswith(os.path.abspath(allure_report_dir)):
            return jsonify({'error': '非法路径'}), 403
        
        if not os.path.exists(file_path):
            return jsonify({'error': '文件不存在'}), 404
        
        # 返回文件，设置正确的MIME类型
        response = send_from_directory(allure_report_dir, filename)
        
        # 根据文件扩展名设置MIME类型
        if filename.endswith('.html'):
            response.headers['Content-Type'] = 'text/html; charset=utf-8'
            # HTML 文件禁用缓存，确保总是获取最新内容
            response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
            response.headers['Pragma'] = 'no-cache'
            response.headers['Expires'] = '0'
        elif filename.endswith('.css'):
            response.headers['Content-Type'] = 'text/css; charset=utf-8'
            # CSS 文件可以缓存，但设置较短的过期时间
            response.headers['Cache-Control'] = 'public, max-age=3600'
        elif filename.endswith('.js'):
            response.headers['Content-Type'] = 'application/javascript; charset=utf-8'
            # JS 文件可以缓存，但设置较短的过期时间
            response.headers['Cache-Control'] = 'public, max-age=3600'
        elif filename.endswith('.json'):
            response.headers['Content-Type'] = 'application/json; charset=utf-8'
            # JSON 文件禁用缓存
            response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
            response.headers['Pragma'] = 'no-cache'
            response.headers['Expires'] = '0'
        elif filename.endswith('.png'):
            response.headers['Content-Type'] = 'image/png'
            response.headers['Cache-Control'] = 'public, max-age=86400'
        elif filename.endswith('.jpg') or filename.endswith('.jpeg'):
            response.headers['Content-Type'] = 'image/jpeg'
            response.headers['Cache-Control'] = 'public, max-age=86400'
        elif filename.endswith('.svg'):
            response.headers['Content-Type'] = 'image/svg+xml'
            response.headers['Cache-Control'] = 'public, max-age=86400'
        
        # 设置 CORS 头，允许跨域访问
        response.headers['Access-Control-Allow-Origin'] = '*'
        response.headers['Access-Control-Allow-Methods'] = 'GET, OPTIONS'
        response.headers['Access-Control-Allow-Headers'] = 'Content-Type'
        
        return response
    except APIException as e:
        return jsonify({'error': e.message, 'payload': e.payload}), e.status_code
    except Exception as e:
        return jsonify({'error': str(e)}), 404


#!/usr/bin/env python
# -*- coding:utf-8 -*-

"""
@author       weimenghua
@time         2025/10/1 19:12
@description
"""

import json

from sqlalchemy.exc import IntegrityError

from ...core.database import db
from ...core.exceptions import APIException
from ...models.mock.mock_model import Mock
from ...utils.dynamic_data_util import DynamicDataProcessor


class MockService:
    """Mock API 服务层"""

    @staticmethod
    def get_all_mocks(page=1, per_page=10, name=None, path=None, method=None, project_id=None):
        """获取所有 Mock API（支持分页和搜索）"""

        # 基础查询
        query = Mock.query

        # 添加模糊搜索条件
        if name:
            query = query.filter(Mock.name.ilike(f'%{name}%'))
        if path:
            query = query.filter(Mock.path.ilike(f'%{path}%'))
        if method:
            query = query.filter(Mock.method.ilike(f'%{method.upper()}%'))
        if project_id:
            query = query.filter(Mock.project_id == project_id)

        # 排序和分页
        pagination = query.order_by(Mock.id.desc()).paginate(page=page, per_page=per_page, error_out=False)

        return {'data': [mock.to_dict() for mock in pagination.items], 'total': pagination.total}

    @staticmethod
    def get_mock_by_id(mock_id):
        """获取单个 Mock API 详情"""

        mock = Mock.query.get_or_404(mock_id)
        return mock.to_dict()

    @staticmethod
    def create_mock(data, current_user=None):
        """创建 Mock API"""

        # 检查必填字段
        required_fields = ['name', 'path', 'method', 'response_status', 'response_body']
        if not all(field in data for field in required_fields):
            raise APIException('Missing required fields', 400)

        try:
            mock = Mock(name=data['name'], path=data['path'], project_id=data.get('project_id'),
                method=data['method'].upper(), response_status=data['response_status'],
                response_body=data['response_body'], response_delay=data.get('response_delay', 0),
                description=data.get('description', ''))
            if current_user:
                mock.created_by = current_user.id
                mock.updated_by = current_user.id

            db.session.add(mock)
            db.session.commit()

            return mock.to_dict()

        except IntegrityError as e:
            db.session.rollback()
            if 'uq_path_method' in str(e.orig):
                raise APIException(f"Path '{data['path']}' with method '{data['method']}' already exists", 409,
                    {'path': data['path'], 'method': data['method']})
            else:
                raise APIException('Database error', 500, {'details': str(e.orig)})

    @staticmethod
    def update_mock(mock_id, data, current_user=None):
        """更新 Mock API"""

        mock = Mock.query.get_or_404(mock_id)

        mock.name = data.get('name', mock.name)
        mock.path = data.get('path', mock.path)
        mock.project_id = data.get('project_id', mock.project_id)
        mock.method = data.get('method', mock.method).upper()
        mock.response_status = data.get('response_status', mock.response_status)
        mock.response_body = data.get('response_body', mock.response_body)
        mock.response_delay = data.get('response_delay', mock.response_delay)
        mock.description = data.get('description', mock.description)
        
        if current_user:
            mock.updated_by = current_user.id

        db.session.commit()

        return mock.to_dict()

    @staticmethod
    def delete_mock(mock_id):
        """删除 Mock API"""

        mock = Mock.query.get_or_404(mock_id)
        db.session.delete(mock)
        db.session.commit()

        return {'message': 'Mock API deleted successfully'}

    @staticmethod
    def execute_mock(api_path, http_method, request_data):
        """执行 Mock API"""

        # 查找Mock配置
        mock = Mock.query.filter_by(path=f'/{api_path.lstrip("/")}', method=http_method).first()

        if not mock:
            raise APIException('Mock API not found', 404, {'path': api_path, 'method': http_method})

        # 解析响应模板
        try:
            response_data = json.loads(mock.response_body)
            print(f"Mock API 原始响应: {response_data}")
        except json.JSONDecodeError as e:
            raise APIException('Invalid JSON template', 500, {'details': str(e), 'template': mock.response_body})

        # 处理模板
        processed_data = DynamicDataProcessor.process_template(response_data, request_data)

        print(f"Mock API 处理后的响应: {processed_data}")
        return processed_data, mock.response_status

    @staticmethod
    def generate_curl_command(api_path, method, host_url):
        """生成 Mock API 接口的 cURL 命令"""

        # 验证方法是否有效
        if method not in ['GET', 'POST', 'PUT', 'DELETE', 'PATCH']:
            raise APIException('Invalid HTTP method', 400)

        # 规范化路径
        normalized_path = f'/{api_path.lstrip("/")}'

        # 查询数据库获取Mock API配置
        mock = Mock.query.filter_by(path=normalized_path, method=method).first()
        if not mock:
            raise APIException('Mock API not found', 404, {'path': normalized_path, 'method': method})

        # 构建基础curl命令
        base_url = host_url.rstrip('/')
        execute_path = api_path.lstrip("/")
        if execute_path.startswith("mock/"):
            execute_path = execute_path[5:]  # 移除开头的mock/

        curl_command = f'curl -X {method} "{base_url}/api/mock/execute/{execute_path}"'

        # 处理请求头和请求体
        if method in ['POST', 'PUT', 'PATCH']:
            curl_command += ' \\\n  -H "Content-Type: application/json"'

            try:
                json_body = json.loads(mock.response_body)
                curl_command += f' \\\n  -d \'{json.dumps(json_body, ensure_ascii=False)}\''
            except (json.JSONDecodeError, TypeError):
                curl_command += f' \\\n  -d \'{mock.response_body}\''

        return {'curl_command': curl_command, 'api_details': mock.to_dict(), 'request_method': method,
            'api_path': normalized_path}

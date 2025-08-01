#!/usr/bin/env python
# -*- coding:utf-8 -*-

"""
@author       weimenghua
@time         2025/10/2 14:04
@description
"""

from urllib.parse import urlencode

import requests

from ...core.database import db
from ...models.api_docs.api_endpoint_model import ApiEndpoint
from ...models.api_docs.api_parameter_model import ApiParameter


class ApiDocsService:
    """API文档服务类"""

    @staticmethod
    def refresh_docs():
        """刷新API文档 - 从Gitee获取最新文档并更新数据库"""
        try:
            response = requests.get('https://gitee.com/api/v5/swagger_doc.json')
            response.raise_for_status()
            data = response.json()

            # 清空现有数据
            ApiParameter.query.delete()
            ApiEndpoint.query.delete()

            # 解析接口信息
            endpoints_created = 0
            parameters_created = 0

            # 文本清洗函数：去除 [EXTRA_INFO]...[/EXTRA_INFO]
            def _sanitize(text: str) -> str:
                if not isinstance(text, str):
                    return text
                import re
                return re.sub(r"\[EXTRA_INFO\][\s\S]*?\[/EXTRA_INFO\]", "", text).strip()

            basePath = data.get('basePath')
            for path, methods in data.get('paths', {}).items():
                for method, details in methods.items():
                    # 提取接口分类信息
                    tags = details.get('tags', ['default'])
                    category = tags[0] if tags else 'default'

                    path = basePath + path
                    endpoint = ApiEndpoint(
                        path=path,
                        method=method.upper(),
                        summary=_sanitize(details.get('summary', '')),
                        description=_sanitize(details.get('description', '')),
                        category=category,
                    )
                    db.session.add(endpoint)
                    db.session.flush()  # 获取ID
                    endpoints_created += 1

                    # 解析参数
                    for param in details.get('parameters', []):
                        api_param = ApiParameter(
                            endpoint_id=endpoint.id,
                            name=param['name'],
                            param_type=param.get('in', 'query'),
                            data_type=param.get('type', 'string'),
                            required=param.get('required', False),
                            description=_sanitize(param.get('description', '')),
                            example=param.get('example'),
                        )
                        db.session.add(api_param)
                        parameters_created += 1

            db.session.commit()

            return {'code': 0, 'message': '文档更新成功',
                'data': {'endpoints_created': endpoints_created, 'parameters_created': parameters_created}}

        except Exception as e:
            db.session.rollback()
            return {'code': 1, 'message': f'文档更新失败: {str(e)}'}

    @staticmethod
    def get_endpoints():
        """获取所有接口端点列表"""
        try:
            endpoints = ApiEndpoint.query.all()
            return {'code': 0, 'message': 'success', 'data': [endpoint.to_dict() for endpoint in endpoints]}
        except Exception as e:
            return {'code': 1, 'message': f'获取接口列表失败: {str(e)}'}

    @staticmethod
    def get_endpoints_by_categories():
        """按分类获取接口端点（用于目录树）"""
        try:
            endpoints = ApiEndpoint.query.all()

            # 按分类分组
            categories = {}
            for endpoint in endpoints:
                if endpoint.category not in categories:
                    categories[endpoint.category] = []

                categories[endpoint.category].append(
                    {'id': endpoint.id, 'path': endpoint.path, 'method': endpoint.method, 'summary': endpoint.summary,
                        'description': endpoint.description, 'parameters_count': len(endpoint.parameters)})

            return {'code': 0, 'message': 'success', 'data': categories}
        except Exception as e:
            return {'code': 1, 'message': f'获取分类接口失败: {str(e)}'}

    @staticmethod
    def get_endpoint_detail(endpoint_id):
        """获取特定接口端点的详细信息"""
        try:
            endpoint = ApiEndpoint.query.get(endpoint_id)
            if not endpoint:
                return {'code': 1, 'message': f'接口端点 {endpoint_id} 不存在'}

            parameters = ApiParameter.query.filter_by(endpoint_id=endpoint_id).all()

            return {'code': 0, 'message': 'success',
                'data': {'endpoint': endpoint.to_dict(), 'parameters': [param.to_dict() for param in parameters]}}
        except Exception as e:
            return {'code': 1, 'message': f'获取接口详情失败: {str(e)}'}

    @staticmethod
    def create_endpoint(data, current_user=None):
        """创建新的接口端点"""
        try:
            if not data or 'path' not in data or 'method' not in data:
                return {'code': 1, 'message': '缺少必要字段: path 和 method'}

            # 检查是否已存在
            existing = ApiEndpoint.query.filter_by(path=data['path'], method=data['method'].upper()).first()

            if existing:
                return {'code': 1, 'message': '接口端点已存在'}

            endpoint = ApiEndpoint(path=data['path'], method=data['method'].upper(), summary=data.get('summary', ''),
                description=data.get('description', ''), category=data.get('category', 'default'))
            if current_user:
                endpoint.created_by = current_user.id
                endpoint.updated_by = current_user.id

            db.session.add(endpoint)
            db.session.commit()

            return {'code': 0, 'message': '创建成功', 'data': endpoint.to_dict()}

        except Exception as e:
            db.session.rollback()
            return {'code': 1, 'message': f'创建失败: {str(e)}'}

    @staticmethod
    def update_endpoint(endpoint_id, data, current_user=None):
        """更新接口端点"""
        try:
            endpoint = ApiEndpoint.query.get(endpoint_id)
            if not endpoint:
                return {'code': 1, 'message': f'接口端点 {endpoint_id} 不存在'}

            if 'path' in data:
                endpoint.path = data['path']
            if 'method' in data:
                endpoint.method = data['method'].upper()
            if 'summary' in data:
                endpoint.summary = data['summary']
            if 'description' in data:
                endpoint.description = data['description']
            if 'category' in data:
                endpoint.category = data['category']
            
            if current_user:
                endpoint.updated_by = current_user.id

            db.session.commit()

            return {'code': 0, 'message': '更新成功', 'data': endpoint.to_dict()}

        except Exception as e:
            db.session.rollback()
            return {'code': 1, 'message': f'更新失败: {str(e)}'}

    @staticmethod
    def delete_endpoint(endpoint_id):
        """删除接口端点"""
        try:
            endpoint = ApiEndpoint.query.get(endpoint_id)
            if not endpoint:
                return {'code': 1, 'message': f'接口端点 {endpoint_id} 不存在'}

            db.session.delete(endpoint)
            db.session.commit()

            return {'code': 0, 'message': '删除成功'}

        except Exception as e:
            db.session.rollback()
            return {'code': 1, 'message': f'删除失败: {str(e)}'}

    @staticmethod
    def get_endpoint_parameters(endpoint_id):
        """获取接口端点的所有参数"""
        try:
            parameters = ApiParameter.query.filter_by(endpoint_id=endpoint_id).all()
            return {'code': 0, 'message': 'success', 'data': [param.to_dict() for param in parameters]}
        except Exception as e:
            return {'code': 1, 'message': f'获取参数失败: {str(e)}'}

    @staticmethod
    def test_endpoint(endpoint_id, data):
        """测试接口端点"""
        try:
            endpoint = ApiEndpoint.query.get(endpoint_id)
            if not endpoint:
                return {'code': 1, 'message': f'接口端点 {endpoint_id} 不存在'}

            # 获取环境信息（如果提供了environment_id）
            environment_id = data.get('environment_id')
            base_url = data.get('base_url', 'https://example.com')  # 默认base_url
            environment_params = {}

            if environment_id:
                from ...models.environment.environment_model import Environment, EnvironmentParameter
                environment = Environment.query.filter_by(id=environment_id, is_active=True).first()
                if environment:
                    base_url = environment.base_url
                    # 获取环境参数
                    params = EnvironmentParameter.query.filter_by(
                        environment_id=environment_id, is_active=True
                    ).all()
                    environment_params = {p.param_key: p.param_value for p in params}

            # 组织参数
            query_params = {}
            path_params = {}
            body_params = {}
            headers = {'Content-Type': 'application/json'}

            # 先应用环境参数（环境参数的优先级较低，会被表单参数覆盖）
            for param in endpoint.parameters:
                param_name = param.name
                # 优先使用表单传入的值，如果没有则使用环境参数
                value = data.get(param_name, environment_params.get(param_name, ''))
                
                if value:
                    if param.param_type == 'query':
                        query_params[param_name] = value
                    elif param.param_type == 'path':
                        path_params[param_name] = value
                    elif param.param_type == 'body':
                        body_params[param_name] = value
                    elif param.param_type == 'header':
                        headers[param_name] = value

            # 构建URL（替换路径参数）
            path = endpoint.path
            for key, value in path_params.items():
                path = path.replace(f'{{{key}}}', str(value))

            # 构建完整URL
            if not path.startswith('http'):
                # 确保base_url以/结尾，path不以/开头
                base_url = base_url.rstrip('/')
                # 如果 path 以 /api 开头，且 base_url 以 /api 结尾，去除 path 中的 /api 前缀避免重复
                if path.startswith('/api/') and base_url.endswith('/api'):
                    path = path[4:]  # 移除 '/api'，保留 '/v5/...'
                if path.startswith('/'):
                    full_url = base_url + path
                else:
                    full_url = base_url + '/' + path
            else:
                full_url = path

            # 添加查询参数
            if query_params:
                full_url += '?' + urlencode(query_params)

            # 发送请求
            if endpoint.method in ['POST', 'PUT', 'PATCH'] and body_params:
                response = requests.request(
                    method=endpoint.method,
                    url=full_url,
                    headers=headers,
                    json=body_params
                )
            else:
                response = requests.request(
                    method=endpoint.method,
                    url=full_url,
                    headers=headers
                )

            # 生成CURL命令
            curl_command = ApiDocsService._generate_curl_command(
                full_url, endpoint.method, headers, body_params
            )

            # 解析响应数据
            try:
                response_data = response.json() if response.content else None
            except:
                response_data = response.text if response.content else None

            return {'code': 0, 'message': '测试完成', 'data': {
                'request': {
                    'url': full_url,
                    'method': endpoint.method,
                    'headers': headers,
                    'body': body_params if body_params else None,
                    'curl': curl_command
                },
                'response': {
                    'status_code': response.status_code,
                    'headers': dict(response.headers),
                    'data': response_data,
                    'text': response.text if response.content else ''
                }}}

        except Exception as e:
            import traceback
            error_trace = traceback.format_exc()
            return {'code': 1, 'message': f'测试失败: {str(e)}', 'error': error_trace}

    @staticmethod
    def _generate_curl_command(url, method, headers, body_params):
        """生成CURL命令"""
        curl_parts = ['curl', '-X', method]
        
        # 添加headers
        for key, value in headers.items():
            curl_parts.append('-H')
            curl_parts.append(f'"{key}: {value}"')
        
        # 添加body（如果是POST/PUT/PATCH且有body）
        if method in ['POST', 'PUT', 'PATCH'] and body_params:
            import json
            body_json = json.dumps(body_params, ensure_ascii=False)
            curl_parts.append('-d')
            curl_parts.append(f"'{body_json}'")
        
        # 添加URL
        curl_parts.append(f"'{url}'")

        
        return ' '.join(curl_parts)

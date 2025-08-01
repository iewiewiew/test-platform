#!/usr/bin/env python
# -*- coding:utf-8 -*-

"""
@author       weimenghua
@time         2025/1/XX
@description  通用业务服务层 - 场景化数据构造
"""

import requests
import json
from urllib.parse import urlencode

from ...core.exceptions import APIException
from ...services.test.test_environment_service import TestEnvironmentService


class BusinessService:
    """通用业务服务类"""

    @staticmethod
    def _get_base_url(environment_id):
        """获取环境的基础URL"""
        if not environment_id:
            raise APIException('请选择测试环境', 400)
        
        env = TestEnvironmentService.get_test_environment_by_id(environment_id)
        if not env:
            raise APIException('测试环境不存在', 404)
        
        # 解析环境配置
        env_config = env.get('env_config', {})
        if isinstance(env_config, str):
            env_config = json.loads(env_config)
        
        # 获取base_url
        enterprise_info = env_config.get('enterprise_info', {})
        mix_info = env_config.get('mix_info', {})
        scheme = mix_info.get('scheme', 'https')
        host = enterprise_info.get('host', '')
        
        if not host:
            raise APIException('环境配置中缺少host信息', 400)
        
        return f'{scheme}://{host}'

    @staticmethod
    def create_repository(environment_id, project_data):
        """新建仓库"""
        try:
            base_url = BusinessService._get_base_url(environment_id)
            
            # 从环境配置中获取enterprise_id
            env = TestEnvironmentService.get_test_environment_by_id(environment_id)
            env_config = env.get('env_config', {})
            if isinstance(env_config, str):
                env_config = json.loads(env_config)
            
            enterprise_info = env_config.get('enterprise_info', {})
            enterprise_id = enterprise_info.get('enterprise_id', 127)  # 默认127
            
            # 构建完整URL
            url = f'{base_url}/enterprises/{enterprise_id}/projects'
            
            # 准备请求头
            headers = {
                'Accept': 'application/json, text/plain, */*',
                'Content-Type': 'application/json',
                'Set-Language': 'zh'
            }
            
            # 发送请求
            response = requests.post(
                url=url,
                headers=headers,
                json=project_data,
                timeout=30
            )
            
            # 解析响应
            try:
                response_data = response.json() if response.content else None
            except:
                response_data = response.text if response.content else None
            
            return {
                'code': 0 if response.status_code < 400 else 1,
                'message': '执行成功' if response.status_code < 400 else '执行失败',
                'data': {
                    'request': {
                        'url': url,
                        'method': 'POST',
                        'headers': headers,
                        'body': project_data
                    },
                    'response': {
                        'status_code': response.status_code,
                        'headers': dict(response.headers),
                        'data': response_data,
                        'text': response.text if response.content else ''
                    }
                }
            }
        except APIException as e:
            return {'code': 1, 'message': e.message}
        except Exception as e:
            import traceback
            error_trace = traceback.format_exc()
            return {'code': 1, 'message': f'执行失败: {str(e)}', 'error': error_trace}

    @staticmethod
    def create_issue(environment_id, issue_data):
        """新建工作项"""
        try:
            base_url = BusinessService._get_base_url(environment_id)
            
            # 从环境配置中获取enterprise_id
            env = TestEnvironmentService.get_test_environment_by_id(environment_id)
            env_config = env.get('env_config', {})
            if isinstance(env_config, str):
                env_config = json.loads(env_config)
            
            enterprise_info = env_config.get('enterprise_info', {})
            enterprise_id = enterprise_info.get('enterprise_id', 127)  # 默认127
            
            # 构建完整URL
            url = f'{base_url}/enterprises/{enterprise_id}/issues'
            
            # 准备请求头
            headers = {
                'Accept': 'application/json, text/plain, */*',
                'Content-Type': 'application/json',
                'Set-Language': 'zh'
            }
            
            # 发送请求
            response = requests.post(
                url=url,
                headers=headers,
                json=issue_data,
                timeout=30
            )
            
            # 解析响应
            try:
                response_data = response.json() if response.content else None
            except:
                response_data = response.text if response.content else None
            
            return {
                'code': 0 if response.status_code < 400 else 1,
                'message': '执行成功' if response.status_code < 400 else '执行失败',
                'data': {
                    'request': {
                        'url': url,
                        'method': 'POST',
                        'headers': headers,
                        'body': issue_data
                    },
                    'response': {
                        'status_code': response.status_code,
                        'headers': dict(response.headers),
                        'data': response_data,
                        'text': response.text if response.content else ''
                    }
                }
            }
        except APIException as e:
            return {'code': 1, 'message': e.message}
        except Exception as e:
            import traceback
            error_trace = traceback.format_exc()
            return {'code': 1, 'message': f'执行失败: {str(e)}', 'error': error_trace}

    @staticmethod
    def execute_business_api(api_path, method, environment_id, params=None, body=None):
        """执行业务API"""
        try:
            # 获取环境配置
            if not environment_id:
                raise APIException('请选择测试环境', 400)
            
            env = TestEnvironmentService.get_test_environment_by_id(environment_id)
            if not env:
                raise APIException('测试环境不存在', 404)
            
            # 解析环境配置
            env_config = env.get('env_config', {})
            if isinstance(env_config, str):
                env_config = json.loads(env_config)
            
            # 获取base_url
            enterprise_info = env_config.get('enterprise_info', {})
            mix_info = env_config.get('mix_info', {})
            scheme = mix_info.get('scheme', 'https')
            host = enterprise_info.get('host', '')
            
            if not host:
                raise APIException('环境配置中缺少host信息', 400)
            
            base_url = f'{scheme}://{host}'
            
            # 构建完整URL
            if api_path.startswith('http'):
                full_url = api_path
            else:
                base_url = base_url.rstrip('/')
                if api_path.startswith('/api/') and base_url.endswith('/api'):
                    api_path = api_path[4:]
                if api_path.startswith('/'):
                    full_url = base_url + api_path
                else:
                    full_url = base_url + '/' + api_path
            
            # 准备请求参数
            query_params = {}
            path_params = {}
            headers = {'Content-Type': 'application/json'}
            request_body = None
            
            # 处理参数
            if params:
                for key, value in params.items():
                    if value:
                        # 检查是否是路径参数（在path中包含{key}）
                        if f'{{{key}}}' in api_path:
                            path_params[key] = value
                        else:
                            query_params[key] = value
            
            # 替换路径参数
            final_path = api_path
            for key, value in path_params.items():
                final_path = final_path.replace(f'{{{key}}}', str(value))
            
            # 重新构建URL（如果路径参数改变了）
            if path_params:
                if final_path.startswith('http'):
                    full_url = final_path
                else:
                    base_url = base_url.rstrip('/')
                    if final_path.startswith('/api/') and base_url.endswith('/api'):
                        final_path = final_path[4:]
                    if final_path.startswith('/'):
                        full_url = base_url + final_path
                    else:
                        full_url = base_url + '/' + final_path
            
            # 添加查询参数
            if query_params:
                full_url += '?' + urlencode(query_params)
            
            # 处理请求体
            if body:
                if isinstance(body, str):
                    try:
                        request_body = json.loads(body)
                    except:
                        request_body = body
                else:
                    request_body = body
            
            # 发送请求
            if method.upper() in ['POST', 'PUT', 'PATCH']:
                response = requests.request(
                    method=method.upper(),
                    url=full_url,
                    headers=headers,
                    json=request_body,
                    timeout=30
                )
            else:
                response = requests.request(
                    method=method.upper(),
                    url=full_url,
                    headers=headers,
                    timeout=30
                )
            
            # 解析响应
            try:
                response_data = response.json() if response.content else None
            except:
                response_data = response.text if response.content else None
            
            return {
                'code': 0,
                'message': '执行成功',
                'data': {
                    'request': {
                        'url': full_url,
                        'method': method.upper(),
                        'headers': headers,
                        'params': query_params,
                        'path_params': path_params,
                        'body': request_body
                    },
                    'response': {
                        'status_code': response.status_code,
                        'headers': dict(response.headers),
                        'data': response_data,
                        'text': response.text if response.content else ''
                    }
                }
            }
        except APIException as e:
            return {'code': 1, 'message': e.message}
        except Exception as e:
            import traceback
            error_trace = traceback.format_exc()
            return {'code': 1, 'message': f'执行失败: {str(e)}', 'error': error_trace}


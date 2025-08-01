#!/usr/bin/env python
# -*- coding:utf-8 -*-

"""
@author       weimenghua
@time         2025/10/1 19:15
@description  环境管理路由
"""

from flask import Blueprint, request, jsonify, g
import requests
import time

from ...core.exceptions import APIException
from ...services.environment.environment_service import EnvironmentService

environment_bp = Blueprint('environments', __name__)


@environment_bp.route('/environments', methods=['GET'])
def get_all_environments():
    """获取所有环境（支持分页和搜索）"""

    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)

    # 获取查询参数
    search = request.args.get('search')
    project_id = request.args.get('project_id')

    try:
        result = EnvironmentService.get_all_environments(page=page, per_page=per_page, search=search,
            project_id=project_id)
        return jsonify(result)
    except Exception as e:
        raise APIException('服务器错误', 500, {'details': str(e)})


@environment_bp.route('/environments/<int:environment_id>', methods=['GET'])
def get_environment_by_id(environment_id):
    """获取单个环境详情"""

    try:
        environment = EnvironmentService.get_environment_by_id(environment_id)
        return jsonify(environment)
    except APIException as e:
        raise e
    except Exception as e:
        raise APIException('服务器错误', 500, {'details': str(e)})


@environment_bp.route('/environments', methods=['POST'])
def create_environment():
    """创建环境"""

    data = request.get_json()
    current_user = getattr(g, 'current_user', None)

    try:
        result = EnvironmentService.create_environment(data, current_user)
        return jsonify(result), 201
    except APIException as e:
        raise e
    except Exception as e:
        raise APIException('服务器错误', 500, {'details': str(e)})


@environment_bp.route('/environments/<int:environment_id>', methods=['PUT'])
def update_environment(environment_id):
    """更新环境"""

    data = request.get_json()
    current_user = getattr(g, 'current_user', None)

    try:
        result = EnvironmentService.update_environment(environment_id, data, current_user)
        return jsonify(result)
    except APIException as e:
        raise e
    except Exception as e:
        raise APIException('服务器错误', 500, {'details': str(e)})


@environment_bp.route('/environments/<int:environment_id>', methods=['DELETE'])
def delete_environment(environment_id):
    """删除环境"""

    try:
        result = EnvironmentService.delete_environment(environment_id)
        return jsonify(result)
    except APIException as e:
        raise e
    except Exception as e:
        raise APIException('服务器错误', 500, {'details': str(e)})


@environment_bp.route('/environments/<int:environment_id>/copy', methods=['POST'])
def copy_environment(environment_id):
    """复制环境"""

    data = request.get_json()
    new_name = data.get('new_name')
    current_user = getattr(g, 'current_user', None)

    if not new_name:
        raise APIException('新环境名称不能为空', 400)

    try:
        result = EnvironmentService.copy_environment(environment_id, new_name, current_user)
        return jsonify(result), 201
    except APIException as e:
        raise e
    except Exception as e:
        raise APIException('服务器错误', 500, {'details': str(e)})


@environment_bp.route('/environments/<int:environment_id>/stats', methods=['GET'])
def get_environment_stats(environment_id):
    """获取环境统计信息"""

    try:
        result = EnvironmentService.get_environment_stats(environment_id)
        return jsonify(result)
    except APIException as e:
        raise e
    except Exception as e:
        raise APIException('服务器错误', 500, {'details': str(e)})


@environment_bp.route('/environments/<int:environment_id>/parameters', methods=['GET'])
def get_environment_parameters(environment_id):
    """获取环境参数列表（支持分页和搜索）"""

    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    search = request.args.get('search')

    try:
        result = EnvironmentService.get_environment_parameters(environment_id, page=page, per_page=per_page,
            search=search)
        return jsonify(result)
    except APIException as e:
        raise e
    except Exception as e:
        raise APIException('服务器错误', 500, {'details': str(e)})


@environment_bp.route('/environments/<int:environment_id>/parameters', methods=['POST'])
def create_environment_parameter(environment_id):
    """创建环境参数"""

    data = request.get_json()
    current_user = getattr(g, 'current_user', None)

    try:
        result = EnvironmentService.create_environment_parameter(environment_id, data, current_user)
        return jsonify(result), 201
    except APIException as e:
        raise e
    except Exception as e:
        raise APIException('服务器错误', 500, {'details': str(e)})


@environment_bp.route('/parameters/<int:parameter_id>', methods=['PUT'])
def update_environment_parameter(parameter_id):
    """更新环境参数"""

    data = request.get_json()
    current_user = getattr(g, 'current_user', None)

    try:
        result = EnvironmentService.update_environment_parameter(parameter_id, data, current_user)
        return jsonify(result)
    except APIException as e:
        raise e
    except Exception as e:
        raise APIException('服务器错误', 500, {'details': str(e)})


@environment_bp.route('/parameters/<int:parameter_id>', methods=['DELETE'])
def delete_environment_parameter(parameter_id):
    """删除环境参数"""

    try:
        result = EnvironmentService.delete_environment_parameter(parameter_id)
        return jsonify(result)
    except APIException as e:
        raise e
    except Exception as e:
        raise APIException('服务器错误', 500, {'details': str(e)})


@environment_bp.route('/environments/batch', methods=['POST'])
def batch_operations():
    """批量操作环境"""

    data = request.get_json()
    operation = data.get('operation')
    environment_ids = data.get('environment_ids', [])

    if not operation or not environment_ids:
        raise APIException('操作类型和环境ID列表不能为空', 400)

    try:
        results = []
        for env_id in environment_ids:
            try:
                if operation == 'delete':
                    result = environment_service.delete_environment(env_id)
                    results.append({'environment_id': env_id, 'status': 'success', 'result': result})
                else:
                    results.append({'environment_id': env_id, 'status': 'error', 'error': f'不支持的操作: {operation}'})
            except Exception as e:
                results.append({'environment_id': env_id, 'status': 'error', 'error': str(e)})

        return jsonify({'results': results})
    except Exception as e:
        raise APIException('批量操作失败', 500, {'details': str(e)})


@environment_bp.route('/environments/export/<int:environment_id>', methods=['GET'])
def export_environment(environment_id):
    """导出环境配置"""

    try:
        # 获取环境详情
        environment = EnvironmentService.get_environment_by_id(environment_id)

        # 获取环境参数
        parameters_result = EnvironmentService.get_environment_parameters(environment_id, page=1, per_page=1000
            # 假设最多1000个参数
        )

        export_data = {'environment': environment, 'parameters': parameters_result['data'],
            'export_time': '2025-10-01T19:15:00Z',  # 实际应该使用当前时间
            'version': '1.0'}

        return jsonify(export_data)
    except APIException as e:
        raise e
    except Exception as e:
        raise APIException('导出失败', 500, {'details': str(e)})


@environment_bp.route('/environments/import', methods=['POST'])
def import_environment():
    """导入环境配置"""

    data = request.get_json()

    if not data or 'environment' not in data:
        raise APIException('导入数据格式错误', 400)

    try:
        environment_data = data['environment']
        parameters_data = data.get('parameters', [])

        # 创建环境
        environment = environment_service.create_environment(environment_data)

        # 创建参数
        for param_data in parameters_data:
            try:
                environment_service.create_environment_parameter(environment['id'], param_data)
            except Exception as param_error:
                # 记录参数导入错误，但不中断整个导入过程
                print(f"参数导入失败: {param_error}")

        return jsonify(
            {'message': '导入成功', 'environment': environment, 'imported_parameters_count': len(parameters_data)}), 201
    except APIException as e:
        raise e
    except Exception as e:
        raise APIException('导入失败', 500, {'details': str(e)})


@environment_bp.route('/environments/validate', methods=['POST'])
def validate_environment():
    """验证环境配置"""

    data = request.get_json()

    if not data:
        raise APIException('验证数据不能为空', 400)

    try:
        # 验证必填字段
        required_fields = ['name', 'base_url']
        missing_fields = [field for field in required_fields if field not in data]

        if missing_fields:
            return jsonify({'valid': False, 'errors': [f'缺少必填字段: {", ".join(missing_fields)}']})

        # 验证基础URL格式
        base_url = data.get('base_url', '')
        if not base_url.startswith(('http://', 'https://')):
            return jsonify({'valid': False, 'errors': ['基础URL必须以 http:// 或 https:// 开头']})

        # 验证名称长度
        name = data.get('name', '')
        if len(name) > 100:
            return jsonify({'valid': False, 'errors': ['环境名称长度不能超过100个字符']})

        return jsonify({'valid': True, 'message': '环境配置验证通过'})
    except Exception as e:
        raise APIException('验证失败', 500, {'details': str(e)})


@environment_bp.route('/environments/search', methods=['GET'])
def search_environments():
    """搜索环境（支持多种搜索条件）"""

    search_type = request.args.get('type', 'all')  # all, name, url, description
    keyword = request.args.get('keyword', '')
    project_id = request.args.get('project_id')
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)

    if not keyword:
        raise APIException('搜索关键词不能为空', 400)

    try:
        # 根据搜索类型构建不同的搜索条件
        if search_type == 'name':
            search_condition = keyword
        elif search_type == 'url':
            search_condition = keyword
        elif search_type == 'description':
            search_condition = keyword
        else:
            search_condition = keyword

        result = EnvironmentService.get_all_environments(page=page, per_page=per_page, search=search_condition,
            project_id=project_id)

        return jsonify({'search_type': search_type, 'keyword': keyword, 'results': result})
    except Exception as e:
        raise APIException('搜索失败', 500, {'details': str(e)})


@environment_bp.route('/environments/<int:environment_id>/health-check', methods=['POST'])
def health_check_environment(environment_id):
    """环境健康检查（后端代理，避免CORS问题）"""

    try:
        # 获取环境信息
        environment = EnvironmentService.get_environment_by_id(environment_id)
        base_url = environment.get('base_url')

        if not base_url:
            raise APIException('环境基础URL为空', 400)

        # 验证URL格式
        if not base_url.startswith(('http://', 'https://')):
            raise APIException('URL格式错误，必须以 http:// 或 https:// 开头', 400)

        # 执行健康检查
        start_time = time.time()
        status_code = None
        error_message = None
        health_status = 'unhealthy'

        try:
            # 先尝试HEAD请求（减少数据传输）
            try:
                response = requests.head(
                    base_url,
                    timeout=10,
                    allow_redirects=True,
                    verify=False  # 忽略SSL证书验证（可选）
                )
                status_code = response.status_code
            except requests.exceptions.RequestException:
                # HEAD失败，尝试GET请求
                response = requests.get(
                    base_url,
                    timeout=10,
                    allow_redirects=True,
                    verify=False
                )
                status_code = response.status_code
        except requests.exceptions.Timeout:
            error_message = '请求超时（10秒）'
            response_time = int((time.time() - start_time) * 1000)
        except requests.exceptions.ConnectionError as e:
            error_message = f'连接错误: {str(e)}'
            response_time = int((time.time() - start_time) * 1000)
        except requests.exceptions.RequestException as e:
            error_message = f'请求失败: {str(e)}'
            response_time = int((time.time() - start_time) * 1000)
        else:
            # 请求成功
            response_time = int((time.time() - start_time) * 1000)

            # 根据HTTP状态码判断健康状态
            if status_code >= 200 and status_code < 300:
                # 2xx 成功
                health_status = 'healthy' if response_time < 1000 else ('warning' if response_time < 3000 else 'unhealthy')
            elif status_code >= 300 and status_code < 400:
                # 3xx 重定向
                health_status = 'warning'
            else:
                # 4xx/5xx 错误
                health_status = 'unhealthy'

        result = {
            'environment_id': environment_id,
            'environment_name': environment.get('name'),
            'base_url': base_url,
            'health_status': health_status,
            'status_code': status_code,
            'response_time': response_time,
            'error_message': error_message,
            'scanned_at': time.strftime('%Y-%m-%dT%H:%M:%S', time.localtime())
        }

        return jsonify(result)

    except APIException as e:
        raise e
    except Exception as e:
        raise APIException('健康检查失败', 500, {'details': str(e)})

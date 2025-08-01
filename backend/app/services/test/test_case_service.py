#!/usr/bin/env python
# -*- coding:utf-8 -*-

"""
@author       weimenghua
@time         2025/1/XX
@description  测试用例服务层
"""

import os
import csv
import json
import requests
from urllib.parse import urljoin, urlparse
from sqlalchemy import or_

from ...core.database import db
from ...core.exceptions import APIException
from ...models.test.test_case_model import TestCase
from ...utils.path_util import PathUtils


class TestCaseService:
    """测试用例服务类"""

    @staticmethod
    def _get_testdata_dir():
        """获取testdata目录路径"""
        # 使用基于当前文件位置的路径计算，避免依赖项目名称
        current_file = os.path.abspath(__file__)
        app_dir = os.path.dirname(os.path.dirname(os.path.dirname(current_file)))  # 获取 app 目录
        return os.path.join(app_dir, 'autotest', 'testdata')
    

    @staticmethod
    def parse_test_cases_from_directory(directory_path=None, current_user=None):
        """解析测试用例目录下的所有CSV文件并插入数据库（支持根据用例名称更新）"""
        if directory_path is None:
            directory_path = TestCaseService._get_testdata_dir()

        if not os.path.exists(directory_path):
            raise APIException(f'测试用例目录不存在: {directory_path}', 404)

        total_created = 0
        total_updated = 0
        errors = []

        # 遍历目录下的所有CSV文件
        for root, dirs, files in os.walk(directory_path):
            for file in files:
                if file.endswith('.csv') and file.startswith('test_data_'):
                    file_path = os.path.join(root, file)
                    try:
                        result = TestCaseService._parse_csv_file(file_path, current_user)
                        total_created += result.get('created', 0)
                        total_updated += result.get('updated', 0)
                    except Exception as e:
                        errors.append(f'解析文件 {file_path} 失败: {str(e)}')

        total_count = total_created + total_updated
        message = f'成功处理 {total_count} 条测试用例'
        if total_created > 0 and total_updated > 0:
            message += f'（新增 {total_created} 条，更新 {total_updated} 条）'
        elif total_created > 0:
            message += f'（新增 {total_created} 条）'
        elif total_updated > 0:
            message += f'（更新 {total_updated} 条）'

        return {
            'created_count': total_created,
            'updated_count': total_updated,
            'total_count': total_count,
            'errors': errors,
            'message': message
        }

    @staticmethod
    def _parse_csv_file(file_path, current_user=None):
        """解析单个CSV文件"""
        created_count = 0
        updated_count = 0
        
        # 从文件路径中提取组件名称（testdata下的目录名）
        component_name = None
        try:
            testdata_dir = TestCaseService._get_testdata_dir()
            if os.path.isabs(file_path):
                # 如果是绝对路径，计算相对于testdata的路径
                if file_path.startswith(testdata_dir):
                    relative_path = os.path.relpath(file_path, testdata_dir)
                    # 获取第一级目录名作为组件名称
                    path_parts = relative_path.split(os.sep)
                    if len(path_parts) > 1:
                        component_name = path_parts[0]
        except:
            pass
        
        with open(file_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                test_case_name = row.get('test_case_name', '')
                if not test_case_name:
                    continue
                
                # 根据用例名称检查是否已存在
                existing = TestCase.query.filter_by(
                    test_case_name=test_case_name,
                    is_active=True
                ).first()

                if existing:
                    # 如果存在，更新测试用例
                    existing.test_case_id = row.get('test_case_id', existing.test_case_id)
                    existing.test_module_name = row.get('test_module_name', existing.test_module_name)
                    existing.component_name = component_name or existing.component_name
                    existing.request_method = row.get('request_method', existing.request_method).upper()
                    existing.path = row.get('path', existing.path)
                    existing.request_body = row.get('request_body', existing.request_body)
                    existing.request_param = row.get('request_param', existing.request_param)
                    existing.response_body = row.get('response_body', existing.response_body)
                    existing.assert_status = row.get('assert_status', existing.assert_status)
                    existing.assert_value = row.get('assert_value', existing.assert_value)
                    existing.pytest_annotation = row.get('pytest_annotation', existing.pytest_annotation)
                    existing.is_skip = row.get('is_skip', existing.is_skip)
                    existing.file_path = file_path
                    # 更新更新人
                    if current_user:
                        existing.updated_by = current_user.id
                    updated_count += 1
                else:
                    # 如果不存在，创建新测试用例
                    test_case = TestCase(
                        test_case_id=row.get('test_case_id', ''),
                        test_module_name=row.get('test_module_name', ''),
                        test_case_name=test_case_name,
                        component_name=component_name,
                        request_method=row.get('request_method', '').upper(),
                        path=row.get('path', ''),
                        request_body=row.get('request_body', ''),
                        request_param=row.get('request_param', ''),
                        response_body=row.get('response_body', ''),
                        assert_status=row.get('assert_status', ''),
                        assert_value=row.get('assert_value', ''),
                        pytest_annotation=row.get('pytest_annotation', ''),
                        is_skip=row.get('is_skip', 'no'),
                        file_path=file_path,
                        created_by=current_user.id if current_user else None,
                        updated_by=current_user.id if current_user else None
                    )
                    db.session.add(test_case)
                    created_count += 1

        db.session.commit()
        return {
            'created': created_count,
            'updated': updated_count,
            'total': created_count + updated_count
        }

    @staticmethod
    def get_test_cases(page=1, per_page=10, search=None, environment=None, module_name=None, component_name=None):
        """获取测试用例列表（支持分页和搜索）"""
        from sqlalchemy.orm import joinedload
        
        query = TestCase.query.options(joinedload(TestCase.creator)).filter_by(is_active=True)

        # 添加搜索条件（测试用例名称、用例ID）
        if search:
            query = query.filter(
                or_(
                    TestCase.test_case_name.ilike(f'%{search}%'),
                    TestCase.test_case_id.ilike(f'%{search}%')
                )
            )

        # 模块名称筛选（支持模糊搜索）
        if module_name:
            query = query.filter(TestCase.test_module_name.ilike(f'%{module_name}%'))
        
        # 组件名称筛选
        if component_name:
            query = query.filter(TestCase.component_name == component_name)

        # 环境筛选（暂时保留，后续可以根据环境筛选）
        # if environment:
        #     # 可以根据环境筛选测试用例
        #     pass

        # 排序和分页
        pagination = query.order_by(TestCase.id.desc()).paginate(
            page=page, per_page=per_page, error_out=False
        )

        return {
            'data': [test_case.to_dict() for test_case in pagination.items],
            'total': pagination.total,
            'page': page,
            'per_page': per_page
        }

    @staticmethod
    def get_module_names():
        """获取所有模块名称列表（用于下拉筛选）"""
        module_names = db.session.query(TestCase.test_module_name).filter_by(
            is_active=True
        ).distinct().order_by(TestCase.test_module_name).all()
        return [name[0] for name in module_names if name[0]]

    @staticmethod
    def get_component_names():
        """获取所有组件名称列表（用于下拉筛选）"""
        # 优先从testdata目录下获取所有目录名作为组件名称
        component_names = []
        try:
            testdata_dir = TestCaseService._get_testdata_dir()
            if os.path.exists(testdata_dir):
                for item in os.listdir(testdata_dir):
                    item_path = os.path.join(testdata_dir, item)
                    if os.path.isdir(item_path) and not item.startswith('.'):
                        component_names.append(item)
                component_names.sort()
        except Exception as e:
            pass
        
        # 如果从目录获取失败或为空，从数据库中获取已存在的组件名称作为补充
        if not component_names:
            try:
                db_component_names = db.session.query(TestCase.component_name).filter(
                    TestCase.component_name.isnot(None),
                    TestCase.is_active == True
                ).distinct().order_by(TestCase.component_name).all()
                component_names = [name[0] for name in db_component_names if name[0]]
            except:
                pass
        
        return component_names

    @staticmethod
    def get_test_case_by_id(test_case_id):
        """根据ID获取测试用例"""
        test_case = TestCase.query.filter_by(id=test_case_id, is_active=True).first_or_404()
        return test_case.to_dict()

    @staticmethod
    def execute_test_case(test_case_id, environment_name=None, base_url=None):
        """执行测试用例（发起HTTP请求）"""
        test_case = TestCase.query.filter_by(id=test_case_id, is_active=True).first_or_404()

        # 获取环境配置
        if environment_name:
            from .test_environment_service import TestEnvironmentService
            env_config = TestEnvironmentService.get_environment_config(environment_name)
            if env_config and 'enterprise_info' in env_config:
                enterprise_info = env_config['enterprise_info']
                scheme = env_config.get('mix_info', {}).get('scheme', 'https')
                host = enterprise_info.get('host', '')
                if host:
                    base_url = f'{scheme}://{host}'
        elif not base_url:
            raise APIException('请提供环境名称或基础URL', 400)

        # 构建完整URL
        full_url = urljoin(base_url.rstrip('/') + '/', test_case.path.lstrip('/'))

        # 解析请求参数
        headers = {'Content-Type': 'application/json'}
        params = None
        body = None

        if test_case.request_param:
            try:
                params = json.loads(test_case.request_param) if test_case.request_param else None
            except:
                # 如果不是JSON，尝试解析为查询参数
                pass

        if test_case.request_body and test_case.request_body != 'None':
            try:
                body = json.loads(test_case.request_body) if test_case.request_body else None
            except:
                body = test_case.request_body

        # 发送HTTP请求
        try:
            method = test_case.request_method.upper()
            if method in ['POST', 'PUT', 'PATCH']:
                response = requests.request(
                    method=method,
                    url=full_url,
                    headers=headers,
                    params=params,
                    json=body,
                    timeout=30
                )
            else:
                response = requests.request(
                    method=method,
                    url=full_url,
                    headers=headers,
                    params=params,
                    timeout=30
                )

            # 解析响应
            try:
                response_data = response.json() if response.content else None
            except:
                response_data = response.text if response.content else None

            # 验证断言
            assert_result = None
            if test_case.assert_status:
                expected_statuses = [int(s.strip()) for s in test_case.assert_status.split(',')]
                assert_result = {
                    'status_assert': response.status_code in expected_statuses,
                    'expected_status': test_case.assert_status,
                    'actual_status': response.status_code
                }

            return {
                'code': 0,
                'message': '测试执行完成',
                'data': {
                    'test_case': test_case.to_dict(),
                    'request': {
                        'url': full_url,
                        'method': method,
                        'headers': headers,
                        'params': params,
                        'body': body
                    },
                    'response': {
                        'status_code': response.status_code,
                        'headers': dict(response.headers),
                        'data': response_data,
                        'text': response.text if response.content else ''
                    },
                    'assert_result': assert_result
                }
            }

        except requests.exceptions.RequestException as e:
            return {
                'code': 1,
                'message': f'请求失败: {str(e)}',
                'error': str(e)
            }
        except Exception as e:
            import traceback
            error_trace = traceback.format_exc()
            return {
                'code': 1,
                'message': f'执行失败: {str(e)}',
                'error': error_trace
            }

    @staticmethod
    def create_test_case(data, current_user=None):
        """创建测试用例"""
        # 检查必填字段
        if not data.get('test_case_name'):
            raise APIException('测试用例名称不能为空', 400)
        if not data.get('test_module_name'):
            raise APIException('模块名称不能为空', 400)
        if not data.get('request_method'):
            raise APIException('请求方法不能为空', 400)
        if not data.get('path'):
            raise APIException('请求路径不能为空', 400)
        
        # 检查用例名称是否已存在
        existing = TestCase.query.filter_by(
            test_case_name=data['test_case_name'],
            is_active=True
        ).first()
        if existing:
            raise APIException('测试用例名称已存在', 409)
        
        # 创建测试用例
        test_case = TestCase(
            test_case_id=data.get('test_case_id', ''),
            test_module_name=data['test_module_name'],
            test_case_name=data['test_case_name'],
            component_name=data.get('component_name'),
            request_method=data['request_method'].upper() if data.get('request_method') else None,
            path=data['path'],
            request_body=data.get('request_body', ''),
            request_param=data.get('request_param', ''),
            response_body=data.get('response_body', ''),
            assert_status=data.get('assert_status', ''),
            assert_value=data.get('assert_value', ''),
            pytest_annotation=data.get('pytest_annotation', ''),
            is_skip=data.get('is_skip', 'no'),
            file_path=data.get('file_path', ''),
            created_by=current_user.id if current_user else None,
            updated_by=current_user.id if current_user else None
        )
        
        db.session.add(test_case)
        db.session.commit()
        
        return {
            'code': 0,
            'message': '测试用例创建成功',
            'data': test_case.to_dict()
        }

    @staticmethod
    def update_test_case(test_case_id, data, current_user=None):
        """更新测试用例"""
        test_case = TestCase.query.filter_by(id=test_case_id, is_active=True).first_or_404()
        
        # 更新字段
        if 'test_case_id' in data:
            test_case.test_case_id = data['test_case_id']
        if 'test_module_name' in data:
            test_case.test_module_name = data['test_module_name']
        if 'test_case_name' in data:
            test_case.test_case_name = data['test_case_name']
        if 'component_name' in data:
            test_case.component_name = data['component_name']
        if 'request_method' in data:
            test_case.request_method = data['request_method'].upper() if data['request_method'] else None
        if 'path' in data:
            test_case.path = data['path']
        if 'request_body' in data:
            test_case.request_body = data['request_body']
        if 'request_param' in data:
            test_case.request_param = data['request_param']
        if 'response_body' in data:
            test_case.response_body = data['response_body']
        if 'assert_status' in data:
            test_case.assert_status = data['assert_status']
        if 'assert_value' in data:
            test_case.assert_value = data['assert_value']
        if 'pytest_annotation' in data:
            test_case.pytest_annotation = data['pytest_annotation']
        if 'is_skip' in data:
            test_case.is_skip = data['is_skip']
        if 'file_path' in data:
            test_case.file_path = data['file_path']
        
        # 更新更新人
        if current_user:
            test_case.updated_by = current_user.id
        
        db.session.commit()
        return {
            'code': 0,
            'message': '测试用例更新成功',
            'data': test_case.to_dict()
        }

    @staticmethod
    def delete_test_case(test_case_id):
        """删除测试用例（软删除）"""
        test_case = TestCase.query.filter_by(id=test_case_id, is_active=True).first_or_404()
        test_case.is_active = False
        db.session.commit()
        return {'message': '测试用例删除成功'}


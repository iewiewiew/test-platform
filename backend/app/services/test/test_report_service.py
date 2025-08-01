#!/usr/bin/env python
# -*- coding:utf-8 -*-

"""
@author       weimenghua
@time         2025/1/XX
@description  测试报告服务层
"""

import os
import json
from datetime import datetime
from urllib.parse import urljoin

from ...core.database import db
from ...core.exceptions import APIException
from ...models.test.test_report_model import TestReport
from ...models.test.test_case_model import TestCase
from ...utils.path_util import PathUtils


class TestReportService:
    """测试报告服务类"""

    @staticmethod
    def _get_report_dir():
        """获取报告目录路径"""
        # 使用基于当前文件位置的路径计算，避免依赖项目名称
        current_file = os.path.abspath(__file__)
        app_dir = os.path.dirname(os.path.dirname(current_file))  # 获取 app 目录
        return os.path.join(app_dir, 'autotest', 'report')

    @staticmethod
    def parse_pytest_reports(report_dir=None, current_user=None):
        """解析Pytest测试报告 - 按执行批次聚合"""
        if report_dir is None:
            report_dir = TestReportService._get_report_dir()

        if not os.path.exists(report_dir):
            raise APIException(f'测试报告目录不存在: {report_dir}', 404)

        parsed_count = 0
        errors = []

        # 按suite（执行批次）聚合测试用例
        suite_groups = {}
        
        # 遍历所有时间戳目录，解析每个时间戳下的allure-results
        for item in os.listdir(report_dir):
            timestamp_dir = os.path.join(report_dir, item)
            # 跳过非目录项
            if not os.path.isdir(timestamp_dir):
                continue
            
            # 检查是否是时间戳目录（包含allure-results子目录）
            allure_results_dir = os.path.join(timestamp_dir, 'allure-results')
            if not os.path.exists(allure_results_dir):
                continue
            
            # 解析allure-results目录下的JSON文件
            for file in os.listdir(allure_results_dir):
                if file.endswith('-result.json'):
                    file_path = os.path.join(allure_results_dir, file)
                    try:
                        case_data = TestReportService._parse_result_json(file_path)
                        if case_data:
                            # 从labels中提取suite信息作为分组key
                            suite_name = None
                            for label in case_data.get('labels', []):
                                if label.get('name') == 'suite':
                                    suite_name = label.get('value', '')
                                    break
                            
                            if not suite_name:
                                suite_name = 'unknown_suite'
                            
                            # 按suite分组
                            if suite_name not in suite_groups:
                                suite_groups[suite_name] = {
                                    'cases': [],
                                    'module': None,
                                    'environment': None
                                }
                            
                            suite_groups[suite_name]['cases'].append(case_data)
                            
                            # 提取模块和环境信息（从第一个用例中提取）
                            if suite_groups[suite_name]['module'] is None:
                                for label in case_data.get('labels', []):
                                    if label.get('name') == 'story':
                                        suite_groups[suite_name]['module'] = label.get('value', '')
                                    elif label.get('name') == 'suite':
                                        suite_value = label.get('value', '')
                                        # 从suite名称中提取环境信息（格式：test_auto_时间戳_模块_环境）
                                        parts = suite_value.split('_')
                                        if len(parts) >= 2:
                                            suite_groups[suite_name]['environment'] = parts[-1]
                    except Exception as e:
                        errors.append(f'解析文件 {file} 失败: {str(e)}')

        # 为每个suite创建测试报告
        for suite_name, suite_info in suite_groups.items():
            try:
                cases = suite_info['cases']
                if not cases:
                    continue
                
                # 聚合统计信息
                total = len(cases)
                passed = sum(1 for c in cases if c.get('status') == 'passed')
                failed = sum(1 for c in cases if c.get('status') == 'failed')
                skipped = sum(1 for c in cases if c.get('status') == 'skipped')
                error = sum(1 for c in cases if c.get('status') in ['broken', 'error'])
                
                # 计算总时长
                durations = [c.get('duration', 0) for c in cases if c.get('duration', 0) > 0]
                total_duration = sum(durations) if durations else 0.0
                
                # 生成报告名称
                module = suite_info.get('module', '所有模块')
                environment = suite_info.get('environment', '未知环境')
                report_name = f'{module}_{environment}_{datetime.now().strftime("%Y%m%d%H%M%S")}'
                
                # 构建报告数据（包含所有用例详情）
                report_data = {
                    'suite_name': suite_name,
                    'module': module,
                    'environment': environment,
                    'cases': cases,
                    'summary': {
                        'total': total,
                        'passed': passed,
                        'failed': failed,
                        'skipped': skipped,
                        'error': error,
                        'duration': total_duration
                    }
                }
                
                # 检查是否已存在相同的报告（基于suite_name）
                existing_report = TestReport.query.filter_by(
                    report_name=report_name,
                    is_active=True
                ).first()
                
                if existing_report:
                    # 更新现有报告
                    existing_report.execution_module = module
                    existing_report.execution_environment = environment
                    existing_report.total_tests = total
                    existing_report.passed_tests = passed
                    existing_report.failed_tests = failed
                    existing_report.skipped_tests = skipped
                    existing_report.error_tests = error
                    existing_report.duration = total_duration
                    existing_report.report_data = json.dumps(report_data, ensure_ascii=False)
                    existing_report.status = 'success' if failed == 0 and error == 0 else 'failed'
                    # 更新更新人
                    if current_user:
                        existing_report.updated_by = current_user.id
                else:
                    # 创建新报告
                    test_report = TestReport(
                        report_name=report_name,
                        report_path=allure_results_dir,
                        report_type='pytest',
                        execution_module=module,
                        execution_environment=environment,
                        total_tests=total,
                        passed_tests=passed,
                        failed_tests=failed,
                        skipped_tests=skipped,
                        error_tests=error,
                        duration=total_duration,
                        report_data=json.dumps(report_data, ensure_ascii=False),
                        status='success' if failed == 0 and error == 0 else 'failed',
                        created_by=current_user.id if current_user else None,
                        updated_by=current_user.id if current_user else None
                    )
                    db.session.add(test_report)
                
                parsed_count += 1
            except Exception as e:
                errors.append(f'处理suite {suite_name} 失败: {str(e)}')

        db.session.commit()

        return {
            'parsed_count': parsed_count,
            'errors': errors,
            'message': f'成功解析 {parsed_count} 个测试报告'
        }

    @staticmethod
    def _parse_result_json(file_path):
        """解析单个result JSON文件"""
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            
            # 解析测试结果
            status = data.get('status', 'unknown')
            passed = 1 if status == 'passed' else 0
            failed = 1 if status == 'failed' else 0
            skipped = 1 if status == 'skipped' else 0
            error = 1 if status == 'broken' or status == 'error' else 0

            return {
                'uuid': data.get('uuid', ''),
                'name': data.get('name', ''),
                'full_name': data.get('fullName', ''),
                'status': status,
                'total': 1,
                'passed': passed,
                'failed': failed,
                'skipped': skipped,
                'error': error,
                'duration': data.get('stop', 0) - data.get('start', 0) if 'stop' in data and 'start' in data else 0,
                'start_time': data.get('start', 0),
                'stop_time': data.get('stop', 0),
                'description': data.get('description', ''),
                'steps': data.get('steps', []),
                'attachments': data.get('attachments', []),
                'labels': data.get('labels', []),
                'parameters': data.get('parameters', [])
            }

    @staticmethod
    def get_test_reports(page=1, per_page=10, search=None):
        """获取测试报告列表（支持分页和搜索）"""
        query = TestReport.query.filter_by(is_active=True)

        # 添加搜索条件
        if search:
            query = query.filter(
                TestReport.report_name.ilike(f'%{search}%')
            )

        # 排序和分页
        pagination = query.order_by(TestReport.id.desc()).paginate(
            page=page, per_page=per_page, error_out=False
        )

        return {
            'data': [report.to_dict() for report in pagination.items],
            'total': pagination.total,
            'page': page,
            'per_page': per_page
        }

    @staticmethod
    def parse_and_update_report(report_id):
        """解析并更新单个测试报告"""
        report = TestReport.query.filter_by(id=report_id, is_active=True).first_or_404()
        
        # 如果报告已经解析过（有report_data且状态不是pending），直接返回
        if report.report_data and report.status != 'pending':
            return report.to_dict()
        
        # 检查报告路径是否存在
        # report_path可能是相对路径，需要转换为绝对路径
        allure_results_dir = report.report_path
        if not os.path.isabs(allure_results_dir):
            # 如果是相对路径，需要基于app目录构建绝对路径
            # 使用基于当前文件位置的路径计算
            current_file = os.path.abspath(__file__)
            app_dir = os.path.dirname(os.path.dirname(current_file))  # 获取 app 目录
            allure_results_dir = os.path.join(app_dir, allure_results_dir)
        
        if not os.path.exists(allure_results_dir):
            raise APIException(f'测试报告目录不存在: {allure_results_dir}', 404)
        
        # 解析allure-results目录下的JSON文件
        suite_groups = {}
        for file in os.listdir(allure_results_dir):
            if file.endswith('-result.json'):
                file_path = os.path.join(allure_results_dir, file)
                try:
                    case_data = TestReportService._parse_result_json(file_path)
                    if case_data:
                        # 从labels中提取suite信息作为分组key
                        suite_name = None
                        for label in case_data.get('labels', []):
                            if label.get('name') == 'suite':
                                suite_name = label.get('value', '')
                                break
                        
                        if not suite_name:
                            suite_name = 'unknown_suite'
                        
                        # 按suite分组
                        if suite_name not in suite_groups:
                            suite_groups[suite_name] = {
                                'cases': [],
                                'module': None,
                                'environment': None
                            }
                        
                        suite_groups[suite_name]['cases'].append(case_data)
                        
                        # 提取模块和环境信息
                        if suite_groups[suite_name]['module'] is None:
                            for label in case_data.get('labels', []):
                                if label.get('name') == 'story':
                                    suite_groups[suite_name]['module'] = label.get('value', '')
                                elif label.get('name') == 'suite':
                                    suite_value = label.get('value', '')
                                    parts = suite_value.split('_')
                                    if len(parts) >= 2:
                                        suite_groups[suite_name]['environment'] = parts[-1]
                except Exception as e:
                    continue
        
        # 更新报告数据（使用第一个suite的数据，或者合并所有suite）
        if suite_groups:
            # 合并所有suite的数据
            all_cases = []
            total_passed = 0
            total_failed = 0
            total_skipped = 0
            total_error = 0
            total_duration = 0.0
            module = report.execution_module or ''
            environment = report.execution_environment or ''
            
            for suite_name, suite_info in suite_groups.items():
                cases = suite_info['cases']
                if cases:
                    all_cases.extend(cases)
                    if not module and suite_info.get('module'):
                        module = suite_info['module']
                    if not environment and suite_info.get('environment'):
                        environment = suite_info['environment']
            
            # 统计信息
            total = len(all_cases)
            total_passed = sum(1 for c in all_cases if c.get('status') == 'passed')
            total_failed = sum(1 for c in all_cases if c.get('status') == 'failed')
            total_skipped = sum(1 for c in all_cases if c.get('status') == 'skipped')
            total_error = sum(1 for c in all_cases if c.get('status') in ['broken', 'error'])
            durations = [c.get('duration', 0) for c in all_cases if c.get('duration', 0) > 0]
            total_duration = sum(durations) if durations else 0.0
            
            # 构建报告数据
            report_data = {
                'suite_name': list(suite_groups.keys())[0] if suite_groups else '',
                'module': module,
                'environment': environment,
                'cases': all_cases,
                'summary': {
                    'total': total,
                    'passed': total_passed,
                    'failed': total_failed,
                    'skipped': total_skipped,
                    'error': total_error,
                    'duration': total_duration
                }
            }
            
            # 更新报告
            report.execution_module = module
            report.execution_environment = environment
            report.total_tests = total
            report.passed_tests = total_passed
            report.failed_tests = total_failed
            report.skipped_tests = total_skipped
            report.error_tests = total_error
            report.duration = total_duration
            report.report_data = json.dumps(report_data, ensure_ascii=False)
            report.status = 'success' if total_failed == 0 and total_error == 0 else 'failed'
            
            db.session.commit()
        
        # 解析完成后，调用 get_test_report_by_id 获取完整的报告数据（包含 case_tree）
        return TestReportService.get_test_report_by_id(report_id, auto_parse=False)

    @staticmethod
    def get_test_report_by_id(report_id, auto_parse=False):
        """根据ID获取测试报告详情"""
        report = TestReport.query.filter_by(id=report_id, is_active=True).first_or_404()
        
        # 如果状态为pending且auto_parse为True，自动解析报告
        if auto_parse and (report.status == 'pending' or not report.report_data):
            try:
                return TestReportService.parse_and_update_report(report_id)
            except Exception as e:
                # 解析失败不影响获取报告，记录错误
                print(f'自动解析报告失败: {str(e)}')
        
        result = report.to_dict()
        
        # 解析pytest执行结果
        if report.pytest_result:
            try:
                result['pytest_result'] = json.loads(report.pytest_result)
            except:
                result['pytest_result'] = None
        else:
            result['pytest_result'] = None
        
        # 解析报告数据
        if report.report_data:
            try:
                report_data = json.loads(report.report_data)
                result['report_data'] = report_data
                
                # 构建用例树形结构
                cases = report_data.get('cases', [])
                case_tree = []
                
                for case in cases:
                    case_info = {
                        'id': case.get('uuid', ''),
                        'name': case.get('name', ''),
                        'full_name': case.get('full_name', ''),
                        'status': case.get('status', 'unknown'),
                        'duration': case.get('duration', 0),
                        'description': case.get('description', ''),
                        'request': None,
                        'response': None,
                        'steps': []
                    }
                    
                    # 从测试用例数据库中获取请求信息
                    case_name = case.get('name', '')
                    if case_name:
                        # 尝试从数据库查找测试用例
                        # 如果报告有执行组件信息，优先按组件名称查找
                        query = TestCase.query.filter_by(
                            test_case_name=case_name,
                            is_active=True
                        )
                        if report.execution_component:
                            query = query.filter_by(component_name=report.execution_component)
                        test_case = query.first()
                        
                        # 如果按组件名称没找到，且报告有执行模块信息，尝试按模块名称查找
                        if not test_case and report.execution_module:
                            query = TestCase.query.filter_by(
                                test_case_name=case_name,
                                is_active=True
                            ).filter(TestCase.test_module_name.ilike(f'%{report.execution_module}%'))
                            if report.execution_component:
                                query = query.filter_by(component_name=report.execution_component)
                            test_case = query.first()
                        
                        # 如果还是没找到，使用原来的逻辑（不限制组件）
                        if not test_case:
                            test_case = TestCase.query.filter_by(
                                test_case_name=case_name,
                                is_active=True
                            ).first()
                        
                        if test_case:
                            # 获取环境信息，构建完整URL
                            environment = report_data.get('environment', '')
                            base_url = ''
                            if environment:
                                # 尝试从环境配置中获取base_url
                                try:
                                    from .test_environment_service import TestEnvironmentService
                                    env_config = TestEnvironmentService.get_environment_config(environment)
                                    if env_config:
                                        enterprise_info = env_config.get('enterprise_info', {})
                                        scheme = env_config.get('mix_info', {}).get('scheme', 'https')
                                        host = enterprise_info.get('host', '')
                                        if host:
                                            base_url = f'{scheme}://{host}'
                                except:
                                    pass
                            
                            # 构建请求信息
                            full_url = urljoin(base_url.rstrip('/') + '/', test_case.path.lstrip('/')) if base_url else test_case.path
                            case_info['request'] = {
                                'method': test_case.request_method,
                                'path': test_case.path,
                                'url': full_url,
                                'headers': {'Content-Type': 'application/json'},
                                'body': None,
                                'params': None
                            }
                            
                            # 解析请求体
                            if test_case.request_body and test_case.request_body != 'None':
                                try:
                                    case_info['request']['body'] = json.loads(test_case.request_body)
                                except:
                                    case_info['request']['body'] = test_case.request_body
                            
                            # 解析请求参数
                            if test_case.request_param:
                                try:
                                    case_info['request']['params'] = json.loads(test_case.request_param)
                                except:
                                    case_info['request']['params'] = test_case.request_param
                            
                            # 从日志文件中获取响应信息
                            # 从fullName中提取测试方法名，例如：test_get_enterprises_enterprise_id_projects
                            full_name = case.get('full_name', '')
                            test_method = None
                            if full_name and '#' in full_name:
                                test_method = full_name.split('#')[-1] if '#' in full_name else None
                            
                            # 使用报告的创建时间来确定日志目录
                            report_date = report.created_at.strftime('%Y%m%d') if hasattr(report, 'created_at') and report.created_at else datetime.now().strftime('%Y%m%d')
                            
                            response_data = TestReportService._get_response_from_log(
                                test_case.test_case_name,
                                test_method,
                                environment,
                                report_date
                            )
                            if response_data:
                                case_info['response'] = {
                                    'status_code': response_data.get('status_code'),
                                    'headers': response_data.get('headers', {}),
                                    'body': response_data.get('body')
                                }
                    
                    # 从steps中提取请求和响应信息（作为补充）
                    steps = case.get('steps', [])
                    for step in steps:
                        step_name = step.get('name', '')
                        step_status = step.get('status', 'unknown')
                        step_attachments = step.get('attachments', [])
                        step_parameters = step.get('parameters', [])
                        
                        # 如果还没有请求信息，尝试从step parameters中提取
                        if not case_info['request'] and step_parameters:
                            for param in step_parameters:
                                param_name = param.get('name', '').lower()
                                param_value = param.get('value', '')
                                
                                if 'method' in param_name or 'http' in param_name:
                                    if not case_info['request']:
                                        case_info['request'] = {}
                                    case_info['request']['method'] = param_value
                                elif 'url' in param_name or 'path' in param_name:
                                    if not case_info['request']:
                                        case_info['request'] = {}
                                    case_info['request']['url'] = param_value
                        
                        # 如果还没有响应信息，尝试从step parameters中提取
                        if not case_info['response'] and step_parameters:
                            for param in step_parameters:
                                param_name = param.get('name', '').lower()
                                param_value = param.get('value', '')
                                
                                if 'status' in param_name or 'code' in param_name:
                                    if not case_info['response']:
                                        case_info['response'] = {}
                                    case_info['response']['status_code'] = param_value
                        
                        # 从attachments中查找请求和响应信息
                        for att in step_attachments:
                            att_name = att.get('name', '').lower()
                            att_source = att.get('source', '')
                            
                            if 'request' in att_name and not case_info['request']:
                                case_info['request'] = {
                                    'attachment': {
                                        'name': att.get('name', ''),
                                        'source': att_source,
                                        'type': att.get('type', '')
                                    }
                                }
                            elif 'response' in att_name and not case_info['response']:
                                case_info['response'] = {
                                    'attachment': {
                                        'name': att.get('name', ''),
                                        'source': att_source,
                                        'type': att.get('type', '')
                                    }
                                }
                        
                        # 保存步骤信息
                        case_info['steps'].append({
                            'name': step_name,
                            'status': step_status,
                            'duration': step.get('stop', 0) - step.get('start', 0) if 'stop' in step and 'start' in step else 0,
                            'attachments': step_attachments,
                            'parameters': step_parameters
                        })
                    
                    # 如果没有从steps中找到，尝试从case的attachments中查找
                    if not case_info['request'] or not case_info['response']:
                        attachments = case.get('attachments', [])
                        for att in attachments:
                            att_name = att.get('name', '').lower()
                            att_source = att.get('source', '')
                            
                            if 'request' in att_name and not case_info['request']:
                                case_info['request'] = {
                                    'attachment': {
                                        'name': att.get('name', ''),
                                        'source': att_source,
                                        'type': att.get('type', '')
                                    }
                                }
                            elif 'response' in att_name and not case_info['response']:
                                case_info['response'] = {
                                    'attachment': {
                                        'name': att.get('name', ''),
                                        'source': att_source,
                                        'type': att.get('type', '')
                                    }
                                }
                    
                    case_tree.append(case_info)
                
                result['case_tree'] = case_tree
            except Exception as e:
                result['case_tree'] = []
                result['parse_error'] = str(e)

        return result

    @staticmethod
    def _get_response_from_log(test_case_name, test_method=None, environment=None, report_date=None):
        """从日志文件中获取响应信息"""
        try:
            # 使用基于当前文件位置的路径计算，避免依赖项目名称
            current_file = os.path.abspath(__file__)
            app_dir = os.path.dirname(os.path.dirname(current_file))  # 获取 app 目录
            # 使用报告日期，如果没有则使用今天
            date_str = report_date if report_date else datetime.now().strftime('%Y%m%d')
            # 日志目录在 app/autotest/report/log 下
            log_dir = os.path.join(app_dir, 'autotest', 'report', 'log', date_str)
            
            if not os.path.exists(log_dir):
                return None
            
            # 构建日志文件名
            # 优先使用test_method（从fullName中提取），格式：TestAPI.test_get_enterprises_enterprise_id_projects
            # 如果没有test_method，则使用test_case_name
            if test_method:
                # 从test_method构建文件名，例如：TestAPI.test_get_enterprises_enterprise_id_projects
                log_file_json = os.path.join(log_dir, f'TestAPI.{test_method}_response.json')
                log_file_txt = os.path.join(log_dir, f'TestAPI.{test_method}_response.txt')
            else:
                # 使用测试用例名称
                method_name = test_case_name.replace(' ', '_').replace('-', '_')
                log_file_json = os.path.join(log_dir, f'{method_name}_response.json')
                log_file_txt = os.path.join(log_dir, f'{method_name}_response.txt')
            
            # 优先读取JSON文件
            if os.path.exists(log_file_json):
                with open(log_file_json, 'r', encoding='utf-8') as f:
                    response_body = json.load(f)
                    return {
                        'status_code': 200,  # 从文件名无法确定状态码，默认200
                        'headers': {},
                        'body': response_body
                    }
            elif os.path.exists(log_file_txt):
                with open(log_file_txt, 'r', encoding='utf-8') as f:
                    response_body = f.read()
                    return {
                        'status_code': 200,
                        'headers': {},
                        'body': response_body
                    }
            
            # 如果精确匹配失败，尝试模糊匹配（查找所有包含test_method的文件）
            if test_method:
                import glob
                pattern_json = os.path.join(log_dir, f'*{test_method}*response.json')
                pattern_txt = os.path.join(log_dir, f'*{test_method}*response.txt')
                
                matching_files = glob.glob(pattern_json) + glob.glob(pattern_txt)
                if matching_files:
                    # 使用第一个匹配的文件
                    log_file = matching_files[0]
                    if log_file.endswith('.json'):
                        with open(log_file, 'r', encoding='utf-8') as f:
                            response_body = json.load(f)
                            return {
                                'status_code': 200,
                                'headers': {},
                                'body': response_body
                            }
                    else:
                        with open(log_file, 'r', encoding='utf-8') as f:
                            response_body = f.read()
                            return {
                                'status_code': 200,
                                'headers': {},
                                'body': response_body
                            }
            
            return None
        except Exception as e:
            # 静默失败，不影响主流程
            return None

    @staticmethod
    def get_test_logs(report_id, test_method=None):
        """获取测试日志（请求和响应）"""
        report = TestReport.query.filter_by(id=report_id, is_active=True).first_or_404()
        
        # 使用报告的创建时间来确定日志目录
        report_date = report.created_at.strftime('%Y%m%d') if hasattr(report, 'created_at') and report.created_at else datetime.now().strftime('%Y%m%d')
        environment = report.execution_environment or ''
        
        logs = []
        
        try:
            # 使用基于当前文件位置的路径计算，避免依赖项目名称
            current_file = os.path.abspath(__file__)
            app_dir = os.path.dirname(os.path.dirname(current_file))  # 获取 app 目录
            # 日志目录在 app/autotest/report/log 下
            log_dir = os.path.join(app_dir, 'autotest', 'report', 'log', report_date)
            
            if not os.path.exists(log_dir):
                return {'logs': []}
            
            # 如果指定了test_method，只读取该方法的日志
            if test_method:
                log_files = []
                # 查找匹配的日志文件
                for file in os.listdir(log_dir):
                    if test_method in file and (file.endswith('_response.json') or file.endswith('_response.txt')):
                        log_files.append(os.path.join(log_dir, file))
                
                for log_file in log_files:
                    try:
                        with open(log_file, 'r', encoding='utf-8') as f:
                            if log_file.endswith('.json'):
                                content = json.load(f)
                            else:
                                content = f.read()
                            logs.append({
                                'file': os.path.basename(log_file),
                                'content': content,
                                'type': 'response'
                            })
                    except Exception as e:
                        continue
            else:
                # 读取所有日志文件
                for file in sorted(os.listdir(log_dir)):
                    if file.endswith('_response.json') or file.endswith('_response.txt'):
                        file_path = os.path.join(log_dir, file)
                        try:
                            with open(file_path, 'r', encoding='utf-8') as f:
                                if file.endswith('.json'):
                                    content = json.load(f)
                                else:
                                    content = f.read()
                                logs.append({
                                    'file': file,
                                    'content': content,
                                    'type': 'response'
                                })
                        except Exception as e:
                            continue
        except Exception as e:
            pass
        
        return {'logs': logs}

    @staticmethod
    def delete_test_report(report_id):
        """删除测试报告（软删除）"""
        report = TestReport.query.filter_by(id=report_id, is_active=True).first_or_404()
        report.is_active = False
        db.session.commit()
        return {'message': '测试报告删除成功'}


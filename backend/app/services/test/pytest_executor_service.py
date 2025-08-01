#!/usr/bin/env python
# -*- coding:utf-8 -*-

"""
@author       weimenghua
@time         2025/1/XX
@description  Pytest执行服务层
"""

import os
import sys
import subprocess
import json
import yaml
from datetime import datetime
from sqlalchemy import or_

from ...core.database import db
from ...core.exceptions import APIException
from ...autotest.test_case_generator import generate_pytest_code_from_test_cases
from ...models.test.test_case_model import TestCase
from .test_environment_service import TestEnvironmentService
from .test_report_service import TestReportService
from ...utils.path_util import PathUtils
from ...services.notification.notification_sender import NotificationSender


class PytestExecutorService:
    """Pytest执行服务类"""

    @staticmethod
    def _get_autotest_dir():
        """获取autotest目录路径"""
        # 使用基于当前文件位置的路径计算，避免依赖项目名称
        current_file = os.path.abspath(__file__)
        app_dir = os.path.dirname(os.path.dirname(current_file))  # 获取 app 目录
        return os.path.join(app_dir, 'autotest')
    
    @staticmethod
    def _get_testcase_dir():
        """获取testcase目录路径"""
        # 使用基于当前文件位置的路径计算，避免依赖项目名称
        current_file = os.path.abspath(__file__)
        app_dir = os.path.dirname(os.path.dirname(current_file))  # 获取 app 目录
        return os.path.join(app_dir, 'autotest', 'testcase')
    
    @staticmethod
    def _get_report_dir():
        """获取报告目录路径"""
        # 使用基于当前文件位置的路径计算，避免依赖项目名称
        current_file = os.path.abspath(__file__)
        app_dir = os.path.dirname(os.path.dirname(current_file))  # 获取 app 目录
        return os.path.join(app_dir, 'autotest', 'report')
    
    @staticmethod
    def _get_config_file():
        """获取配置文件路径"""
        # 使用基于当前文件位置的路径计算，避免依赖项目名称
        current_file = os.path.abspath(__file__)
        app_dir = os.path.dirname(os.path.dirname(current_file))  # 获取 app 目录
        return os.path.join(app_dir, 'autotest', 'config', 'config.yaml')

    @staticmethod
    def execute_pytest(component_name=None, module_name=None, environment_name=None, current_user=None):
        """执行Pytest测试并生成Allure报告"""
        try:
            # 生成执行时间戳，用于区分不同的测试执行
            execution_timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
            
            # 1. 筛选测试用例
            print(f'开始筛选测试用例 - component_name: {component_name}, module_name: {module_name}, environment_name: {environment_name}')
            test_cases = PytestExecutorService._get_test_cases_by_filter(component_name, module_name, environment_name)
            if not test_cases:
                error_msg = f'没有找到符合条件的测试用例。筛选条件：'
                if component_name:
                    error_msg += f' 组件名称={component_name}'
                if module_name:
                    error_msg += f' 模块名称={module_name}'
                if environment_name:
                    error_msg += f' 环境名称={environment_name}'
                raise APIException(error_msg, 400)

            # 2. 生成测试代码
            test_file_path = PytestExecutorService._generate_test_code(test_cases, component_name, module_name, environment_name)

            # 3. 执行pytest，使用时间戳创建独立的allure结果目录
            result = PytestExecutorService._run_pytest(test_file_path, environment_name, execution_timestamp)

            # 4. 生成allure报告，使用时间戳创建独立的报告目录
            allure_report_path = PytestExecutorService._generate_allure_report(execution_timestamp)

            # 5. 立即创建测试报告记录（不解析详细数据）
            report_id = None
            # 将test_file_path转换为相对路径（相对于app目录）
            # 使用基于当前文件位置的路径计算
            current_file = os.path.abspath(__file__)
            app_dir = os.path.dirname(os.path.dirname(current_file))  # 获取 app 目录
            relative_test_file_path = test_file_path
            if os.path.isabs(test_file_path) and test_file_path.startswith(app_dir):
                relative_test_file_path = os.path.relpath(test_file_path, app_dir)
            
            try:
                from ...models.test.test_report_model import TestReport
                report_dir = PytestExecutorService._get_report_dir()
                # 使用时间戳创建独立的报告目录，下面包含 allure-results 和 allure-report
                timestamp_dir = os.path.join(report_dir, execution_timestamp)
                allure_results_dir = os.path.join(timestamp_dir, 'allure-results')
                # 将allure_results_dir转换为相对路径（相对于app目录）用于存储
                relative_allure_results_dir = allure_results_dir
                if os.path.isabs(allure_results_dir) and allure_results_dir.startswith(app_dir):
                    relative_allure_results_dir = os.path.relpath(allure_results_dir, app_dir)
                
                # 生成报告名称，使用执行时间戳
                component_part = f'{component_name}_' if component_name else ''
                report_name = f'{component_part}{module_name or "所有模块"}_{environment_name or "未知环境"}_{execution_timestamp}'
                
                # 保存pytest执行结果（只保存关键信息，不保存完整的stdout/stderr，避免数据过长）
                pytest_result_json = None
                if result:
                    try:
                        # 只保存关键信息：成功状态、返回码、测试用例数量
                        simplified_result = {
                            'success': result.get('success', False),
                            'returncode': result.get('returncode', -1),
                            'test_cases_count': len(test_cases)
                        }
                        pytest_result_json = json.dumps(simplified_result, ensure_ascii=False)
                    except:
                        pass
                
                # 创建测试报告记录（状态为pending，等待解析）
                test_report = TestReport(
                    report_name=report_name,
                    report_path=relative_allure_results_dir,
                    report_type='pytest',
                    execution_module=module_name or '',
                    execution_component=component_name or '',
                    execution_environment=environment_name or '',
                    total_tests=len(test_cases),
                    passed_tests=0,
                    failed_tests=0,
                    skipped_tests=0,
                    error_tests=0,
                    duration=0.0,
                    report_data=None,  # 暂不解析详细数据
                    pytest_result=pytest_result_json,  # 保存Pytest执行结果
                    status='pending',  # 状态为pending，等待解析
                    test_file_path=relative_test_file_path,
                    test_file_name=os.path.basename(test_file_path),
                    created_by=current_user.id if current_user else None,
                    updated_by=current_user.id if current_user else None
                )
                db.session.add(test_report)
                db.session.commit()
                report_id = test_report.id
                print(f'成功创建测试报告记录，report_id: {report_id}, report_name: {report_name}')
            except Exception as e:
                # 创建报告失败应该抛出异常，让前端知道有问题
                import traceback
                error_trace = traceback.format_exc()
                error_msg = f'创建测试报告记录失败: {str(e)}'
                print(f'{error_msg}\n{error_trace}')
                db.session.rollback()
                raise APIException(error_msg, 500, {'error': error_trace})

            # 6. 发送测试结果通知（异步发送，不阻塞主流程）
            try:
                # 解析测试结果，获取通过/失败数量
                passed_tests = 0
                failed_tests = 0
                skipped_tests = 0
                total_tests = len(test_cases)
                
                # 从pytest结果中解析（如果可能）
                if result and result.get('stdout'):
                    stdout = result.get('stdout', '')
                    # 尝试从stdout中解析测试结果
                    # pytest输出格式示例: "3 passed, 1 failed, 1 skipped"
                    import re
                    passed_match = re.search(r'(\d+)\s+passed', stdout)
                    failed_match = re.search(r'(\d+)\s+failed', stdout)
                    skipped_match = re.search(r'(\d+)\s+skipped', stdout)
                    
                    if passed_match:
                        passed_tests = int(passed_match.group(1))
                    if failed_match:
                        failed_tests = int(failed_match.group(1))
                    if skipped_match:
                        skipped_tests = int(skipped_match.group(1))
                
                # 构建测试结果数据
                test_result_data = {
                    'title': 'Pytest测试执行完成',
                    'component_name': component_name or '',
                    'module_name': module_name or '',
                    'environment_name': environment_name or '',
                    'total_tests': total_tests,
                    'passed_tests': passed_tests,
                    'failed_tests': failed_tests,
                    'skipped_tests': skipped_tests,
                    'error_tests': 0,
                    'duration': 0.0,  # 可以从报告中解析
                    'success': result.get('success', False) if result else False,
                    'report_id': report_id,
                    'report_url': f'/api/test-reports/{report_id}/allure/index.html' if report_id else ''
                }
                
                # 发送通知到所有启用的通知配置
                notification_result = NotificationSender.send_to_all_enabled(test_result_data)
                print(f'通知发送结果: 总数={notification_result.get("total", 0)}, 成功={notification_result.get("success", 0)}, 失败={notification_result.get("failed", 0)}')
            except Exception as e:
                # 通知发送失败不影响主流程
                import traceback
                error_trace = traceback.format_exc()
                print(f'发送测试结果通知失败: {str(e)}\n{error_trace}')

            return {
                'code': 0,
                'message': '测试执行完成',
                'data': {
                    'test_cases_count': len(test_cases),
                    'test_file_path': relative_test_file_path,
                    'pytest_result': result,
                    'allure_report_path': allure_report_path,
                    'report_id': report_id
                }
            }

        except APIException:
            raise
        except Exception as e:
            import traceback
            error_trace = traceback.format_exc()
            raise APIException(f'执行失败: {str(e)}', 500, {'error': error_trace})

    @staticmethod
    def _get_test_cases_by_filter(component_name=None, module_name=None, environment_name=None):
        """根据模块名称、组件名称和环境筛选测试用例"""
        query = TestCase.query.filter_by(is_active=True)

        # 只有当module_name不为空且不是空字符串时才添加筛选条件
        if module_name and str(module_name).strip():
            module_filter = str(module_name).strip()
            query = query.filter(TestCase.test_module_name.ilike(f'%{module_filter}%'))
            print(f'添加模块筛选条件: {module_filter}')
        
        # 只有当component_name不为空且不是空字符串时才添加筛选条件
        if component_name and str(component_name).strip():
            component_filter = str(component_name).strip()
            query = query.filter(TestCase.component_name == component_filter)
            print(f'添加组件筛选条件: {component_filter}')

        # 环境筛选暂时通过环境名称来标识，实际执行时会使用环境配置
        # 这里先返回所有符合条件的测试用例

        test_cases = query.all()
        # 添加调试日志
        print(f'筛选测试用例 - component_name: {component_name}, module_name: {module_name}, environment_name: {environment_name}, 找到 {len(test_cases)} 条用例')
        if test_cases:
            print(f'找到的测试用例示例: {[tc.test_case_name for tc in test_cases[:3]]}')
        return test_cases

    @staticmethod
    def _generate_test_code(test_cases, component_name, module_name, environment_name):
        """生成Pytest测试代码"""
        # 确保testcase目录存在
        testcase_dir = PytestExecutorService._get_testcase_dir()
        os.makedirs(testcase_dir, exist_ok=True)

        # 获取环境配置
        env_config = None
        if environment_name:
            env_config = TestEnvironmentService.get_environment_config(environment_name)

        # 调用 test_case_generator 生成测试代码
        test_file_path = generate_pytest_code_from_test_cases(
            test_cases=test_cases,
            component_name=component_name or '',
            module_name=module_name or '',
            environment_name=environment_name or '',
            env_config=env_config or {},
            output_dir=testcase_dir
        )

        return test_file_path

    @staticmethod
    def _run_pytest(test_file_path, environment_name, execution_timestamp):
        """执行Pytest测试"""
        autotest_dir = PytestExecutorService._get_autotest_dir()
        testcase_dir = PytestExecutorService._get_testcase_dir()
        # 测试报告写到 backend/app/autotest/report 目录下
        report_dir = PytestExecutorService._get_report_dir()
        # 使用时间戳创建独立的报告目录，下面包含 allure-results
        timestamp_dir = os.path.join(report_dir, execution_timestamp)
        allure_results_dir = os.path.join(timestamp_dir, 'allure-results')
        os.makedirs(allure_results_dir, exist_ok=True)

        # 执行pytest - 使用当前test-platform项目的Python解释器（sys.executable）
        python_cmd = sys.executable
        
        # 验证Python解释器是否可用
        try:
            # 检查Python版本
            version_result = subprocess.run(
                [python_cmd, '--version'],
                capture_output=True,
                text=True,
                timeout=5
            )
            if version_result.returncode != 0:
                raise FileNotFoundError(f'Python解释器不可用: {python_cmd}')
        except FileNotFoundError as e:
            raise APIException(f'未找到可用的Python解释器: {str(e)}', 500)
        
        # 确保测试文件路径是绝对路径
        if not os.path.isabs(test_file_path):
            test_file_path = os.path.join(testcase_dir, test_file_path)
        
        pytest_ini_path = os.path.join(autotest_dir, 'pytest.ini')
        if not os.path.exists(pytest_ini_path):
            # 如果不存在，创建一个配置文件，指定 testpaths 为 testcase 目录
            with open(pytest_ini_path, 'w', encoding='utf-8') as f:
                f.write('[pytest]\n')
                f.write('testpaths = testcase\n')
                f.write('python_files = test_*.py\n')
                f.write('python_classes = Test*\n')
                f.write('python_functions = test_*\n')
        
        # 检测是否在 Docker 环境中
        is_docker = autotest_dir.startswith('/app')
        
        # 在 Docker 环境中，需要特殊处理以避免模块导入问题
        if is_docker:
            
            # 构建 pytest 命令，使用 importlib 模式避免模块路径问题
            pytest_cmd = [
                python_cmd,
                '-m',
                'pytest',
                test_file_path,
                f'--rootdir={autotest_dir}',  # 明确指定根目录
                '--import-mode=importlib',  # 使用 importlib 模式，避免路径冲突
                '-c', pytest_ini_path,  # 明确指定配置文件
                f'--alluredir={allure_results_dir}',
                '--clean-alluredir',
                '-v',
                '-s'
            ]
            
            # 设置 PYTHONPATH，确保 /app 在最前面
            env = dict(os.environ, PYTEST_CURRENT_TEST='')
            pythonpath = env.get('PYTHONPATH', '')
            if pythonpath:
                env['PYTHONPATH'] = f'/app:{pythonpath}'
            else:
                env['PYTHONPATH'] = '/app'
            
            # 在 /app 目录下执行，而不是在 /app/app/autotest 目录下
            cwd = '/app'
        else:
            # 本地环境：保持原有逻辑
            pytest_cmd = [
                python_cmd,
                '-m',
                'pytest',
                test_file_path,
                f'--rootdir={autotest_dir}',
                '-c', pytest_ini_path,
                f'--alluredir={allure_results_dir}',
                '--clean-alluredir',
                '-v',
                '-s'
            ]
            env = dict(os.environ, PYTEST_CURRENT_TEST='')
            cwd = autotest_dir

        try:
            result = subprocess.run(
                pytest_cmd,
                cwd=cwd,
                capture_output=True,
                text=True,
                timeout=3600,  # 1小时超时
                env=env  # 使用配置好的环境变量
            )

            return {
                'returncode': result.returncode,
                'stdout': result.stdout,
                'stderr': result.stderr,
                'success': result.returncode == 0
            }
        except subprocess.TimeoutExpired:
            return {
                'returncode': -1,
                'stdout': '',
                'stderr': '测试执行超时',
                'success': False
            }
        except Exception as e:
            return {
                'returncode': -1,
                'stdout': '',
                'stderr': str(e),
                'success': False
            }

    @staticmethod
    def _generate_allure_report(execution_timestamp):
        """生成Allure报告"""
        autotest_dir = PytestExecutorService._get_autotest_dir()
        # 测试报告写到 backend/app/autotest/report 目录下
        report_dir = PytestExecutorService._get_report_dir()
        # 使用时间戳创建独立的报告目录，下面包含 allure-results 和 allure-report
        timestamp_dir = os.path.join(report_dir, execution_timestamp)
        allure_results_dir = os.path.join(timestamp_dir, 'allure-results')
        allure_report_dir = os.path.join(timestamp_dir, 'allure-report')

        # 确保目录存在
        os.makedirs(allure_results_dir, exist_ok=True)
        os.makedirs(allure_report_dir, exist_ok=True)

        # 生成allure报告
        try:
            result = subprocess.run(
                ['allure', 'generate', allure_results_dir, '-o', allure_report_dir, '--clean'],
                cwd=autotest_dir,
                capture_output=True,
                text=True,
                timeout=300  # 5分钟超时
            )

            if result.returncode == 0:
                # 返回相对路径（相对于app目录）
                # 使用基于当前文件位置的路径计算
                current_file = os.path.abspath(__file__)
                app_dir = os.path.dirname(os.path.dirname(current_file))  # 获取 app 目录
                if allure_report_dir.startswith(app_dir):
                    relative_path = os.path.relpath(allure_report_dir, app_dir)
                    return relative_path
                # 如果无法计算相对路径，返回绝对路径
                return allure_report_dir
            else:
                raise APIException(f'生成Allure报告失败: {result.stderr}', 500)
        except subprocess.TimeoutExpired:
            raise APIException('生成Allure报告超时', 500)
        except FileNotFoundError:
            raise APIException('未找到allure命令，请确保已安装Allure', 500)


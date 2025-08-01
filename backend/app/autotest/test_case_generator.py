#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
@author       weimenghua
@time         2025/05/10 19:38
@description  测试用例生成器：读取 CSV 测试用例转换为 Pytest 测试用例
"""

import csv
import json
import os
import re
import urllib.parse
from datetime import datetime
from glob import glob
from pathlib import Path
from typing import List, Dict, Optional, Tuple

from ..utils.log_util import Logger
from ..utils.path_util import PathUtils

logger = Logger()

# 常量定义
TEST_DATA_PREFIX = 'test_data_'
TEST_API_PREFIX = 'test_api_'
CSV_EXTENSION = '.csv'
PYTHON_EXTENSION = '.py'
UNKNOWN_MODULE = 'Unknown Module'
SKIP_NO = "no"
ASYNC_MARKER = "(asyncio)"
DOWNLOAD_MARKER = "(download)"
UPLOAD_MARKER = "(upload)"

# 特殊字段映射
SPECIAL_FIELD_MAPPING = {
    '{owner}': '{self.enterprise_path}',
    '{repo}': '{self.project_path}',
}

# 特殊文件名处理
SPECIAL_DOWNLOAD_FILES = {
    '导出企业文档为PDF(download)': '/ent_wiki.pdf'
}


def _read_csv_test_cases(testdata_file: str) -> List[Dict[str, str]]:
    """读取 CSV 文件中的测试用例数据"""
    with open(testdata_file, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        return list(reader)


def _generate_output_file_path(testdata_file: str, testdata_base_dir: str, 
                                testcase_base_dir: str) -> Tuple[str, str]:
    """
    生成输出文件路径
    返回: (output_file, output_dir)
    """
    # 从文件名生成输出文件名
    testdata_filename = os.path.basename(testdata_file)
    output_filename = (testdata_filename
                       .replace(TEST_DATA_PREFIX, TEST_API_PREFIX)
                       .replace(CSV_EXTENSION, PYTHON_EXTENSION))

    # 保持目录结构：获取相对于testdata_base_dir的路径
    relative_path = os.path.dirname(os.path.relpath(testdata_file, testdata_base_dir))
    if relative_path == '.':
        output_dir = testcase_base_dir
    else:
        output_dir = os.path.join(testcase_base_dir, relative_path)
        os.makedirs(output_dir, exist_ok=True)

    output_file = os.path.join(output_dir, output_filename)
    return output_file, output_dir


def _generate_test_class_header(env: str, test_module_name: str) -> str:
    """生成测试类的头部代码"""
    current_time = datetime.now().strftime("%Y/%m/%d %H:%M")
    return f'''#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
@author       weimenghua
@time         {current_time}
@description  API 接口测试
"""

import os
import sys
import allure
import pytest
import asyncio
from datetime import datetime, timedelta
from pathlib import Path

# 添加项目根目录到 Python 路径，确保可以导入 utils 和 config 模块
# 检测是否在 Docker 环境中（路径以 /app 开头）
current_file = Path(__file__).resolve()
current_path = current_file.parent
is_docker = str(current_path).startswith('/app')

if is_docker:
    # Docker 环境：/app 就是项目根目录（backend 目录被挂载到 /app）
    project_root = '/app'
    # 确保 /app 在 sys.path 的最前面，并且移除可能干扰的路径
    if project_root in sys.path:
        sys.path.remove(project_root)
    sys.path.insert(0, project_root)
    # 移除当前目录（/app/app/autotest/testcase）避免干扰模块搜索
    current_dir = str(current_path)
    if current_dir in sys.path:
        sys.path.remove(current_dir)
    # Docker 环境中，使用 app.xxx 导入（不带 backend 前缀）
    from app.utils.log_util import Logger
    from app.utils.path_util import PathUtils
    from app.utils.http_client_util import HttpClient
    from app.utils.response_util import APIResponse
    from app.autotest.config.config_util import ConfigUtils
else:
    # 本地开发环境：向上查找包含 backend/ 目录的项目根目录
    project_root = None
    for parent in current_path.parents:
        backend_dir = parent / 'backend'
        if backend_dir.exists() and backend_dir.is_dir():
            project_root = parent
            break
    
    # 如果没找到，使用默认路径（从 testcase/ 向上 4 级）
    if project_root is None:
        project_root = current_path.parent.parent.parent.parent
    
    # 将项目根目录添加到 sys.path，这样可以使用 backend.app.xxx 导入
    if project_root and str(project_root) not in sys.path:
        sys.path.insert(0, str(project_root))
    
    # 本地环境中，使用 backend.app.xxx 导入
    from backend.app.utils.log_util import Logger
    from backend.app.utils.path_util import PathUtils
    from backend.app.utils.http_client_util import HttpClient
    from backend.app.utils.response_util import APIResponse
    from backend.app.autotest.config.config_util import ConfigUtils

env = '{env}'

@allure.story("{test_module_name}")
class TestAPI:
    @classmethod
    def setup_class(cls):
        """测试类初始化"""
        cls.logger = Logger()
        cls.time = datetime.now().strftime('%Y%m%d%H%M%S')
        cls.current_year = datetime.now().strftime('%Y')
        cls.current_week = (datetime.now() - timedelta(weeks=1)).isocalendar()[1]
        cls.base_path = PathUtils.get_project_root_path('test-platform')
        # 根据环境自动设置 config_path
        # Docker 环境：/app/app/autotest/config/config.yaml
        # 本地环境：项目根目录/backend/app/autotest/config/config.yaml
        if str(cls.base_path).startswith('/app'):
            cls.config_path = os.path.join(cls.base_path, 'app', 'autotest', 'config', 'config.yaml')
        else:
            cls.config_path = os.path.join(cls.base_path, 'backend', 'app', 'autotest', 'config', 'config.yaml')

        cls.env = '{env}'
        cls.data = ConfigUtils(cls.env, cls.config_path)
        cls.host = cls.data.host
        cls.user_id = cls.data.user_id
        cls.username = cls.data.username
        cls.password = cls.data.password
        cls.headers = cls.data.headers
        cls.access_token = cls.data.access_token
        cls.enterprise_id = cls.data.enterprise_id
        cls.enterprise_path = cls.data.enterprise_path
        cls.project_id = cls.data.project_id
        cls.project_path = cls.data.project_path
        cls.program_id = cls.data.program_id
        cls.team_id = cls.data.team_id
        cls.file_path = cls.data.file_path
        cls.docker_responsitory = cls.data.docker_responsitory
        cls.docker_username = cls.data.docker_username
        cls.docker_password = cls.data.docker_password
        cls.client = HttpClient(cls.host)
'''


def _generate_test_name(case: Dict[str, str], test_name_counts: Dict[str, int]) -> str:
    """生成测试方法名称，处理重复名称"""
    # 处理方法名称, 去掉 ? 后面的内容
    path = urllib.parse.unquote(case['path'].split('?')[0])
    base_name = (f"test_{case['request_method']}"
                 f"{path.replace('/', '_').replace('{', '').replace('}', '').replace('-', '_').replace('.', '_')}")

    # 检查名称是否已存在并处理重复
    if base_name in test_name_counts:
        test_name_counts[base_name] += 1
        return f"{base_name}_{test_name_counts[base_name]}"
    else:
        test_name_counts[base_name] = 1
        return base_name


def _normalize_path(path: str) -> str:
    """处理路径参数，替换变量引用"""
    # 处理特殊字段映射
    for original, replacement in SPECIAL_FIELD_MAPPING.items():
        path = path.replace(original, replacement)
    
    # 自动替换所有 {variable} 为 {self.variable}
    path = re.sub(r'\{(\w+)\}', r'{self.\1}', path)
    return path


def _normalize_request_body(request_body: str) -> str:
    """处理请求体参数，替换变量引用"""
    if not request_body:
        return request_body
    
    # 1. 先处理普通f-string中的变量（如 f"仓库组仓库_{time}" → f"仓库组仓库_{self.time}"）
    request_body = re.sub(
        r'f([\'"])(.*?)\{(\w+)\}(.*?)\1',
        lambda m: f'f{m.group(1)}{m.group(2)}{{self.{m.group(3)}}}{m.group(4)}{m.group(1)}',
        request_body
    )
    
    # 2. 处理带引号的变量（如 "{time}" 或 '{time}' → self.time）
    request_body = re.sub(r'([\'"])\{(\w+)\}\1', r'self.\2', request_body)
    
    # 3. 处理不带引号的变量（如 {time} → self.time）
    request_body = re.sub(r'\{\s*(\w+)\s*\}', r'self.\1', request_body)
    
    return request_body


def _write_test_method_decorator(f, case: Dict[str, str]):
    """写入测试方法的装饰器"""
    f.write(f"    @allure.title('{case['test_case_id']}-{case['test_case_name']}')\n")
    
    if case.get('pytest_annotation'):
        f.write(f"    {case['pytest_annotation']}\n")
    
    if case.get('request_param'):
        f.write(f"    @pytest.mark.parametrize({case['request_param']})\n")


def _write_test_method_signature(f, case: Dict[str, str], test_name: str):
    """写入测试方法签名"""
    if case.get('request_param'):
        f.write(f"    def {test_name}(self):\n")
        f.write(f"        \"\"\"{case['test_case_name']}\"\"\"\n")
    elif ASYNC_MARKER in case['test_case_name']:
        f.write(f"    async def {test_name}(self):\n")
    else:
        f.write(f"    def {test_name}(self):\n")
        f.write(f"        \"\"\"{case['test_case_name']}\"\"\"\n")


def _write_request_code(f, case: Dict[str, str]):
    """写入请求代码"""
    test_case_name = case['test_case_name']
    request_method = case['request_method'].lower()
    
    if request_method == 'get':
        if DOWNLOAD_MARKER in test_case_name:
            if test_case_name in SPECIAL_DOWNLOAD_FILES:
                file_path = f"self.file_path + '{SPECIAL_DOWNLOAD_FILES[test_case_name]}'"
            else:
                file_path = "self.file_path"
            f.write(f"        self.client.download_file(path, {file_path}, self.headers)\n\n")
        else:
            f.write(f"        response = APIResponse(self.client.send_get_request(path, self.headers))\n")
    else:
        if UPLOAD_MARKER in test_case_name:
            f.write(f"        response = APIResponse(self.client.upload_file(path, self.file_path + '/tmp.txt', body, self.headers))\n\n")
        else:
            f.write(f"        response = APIResponse(self.client.send_{request_method}_request(path, body, self.headers))\n")


def _write_response_handler(f, case: Dict[str, str]):
    """写入响应处理代码"""
    # 获取响应结果提供给依赖用例
    if case.get('response_body'):
        formatted_response = case['response_body'].replace('\\n', '\n')
        indented_response = '\n        '.join(formatted_response.splitlines())
        f.write(f"        {indented_response}\n")
    
    # 状态码断言（排除下载类型）
    download_pattern = re.compile(r'.*(?:导出|下载).*\(download\)$')
    if not download_pattern.match(case['test_case_name']):
        assert_status = case['assert_status']
        f.write(f"        response.assert_status(({assert_status}), '{case['test_case_name']}状态码验证')\n\n")
    
    # 异步等待
    if ASYNC_MARKER in case['test_case_name']:
        f.write(f"        await asyncio.sleep(3)\n\n")
    
    # 值断言
    if case.get('assert_value'):
        assert_value = case['assert_value']
        f.write(f"        response.assert_value({assert_value})\n\n")


def _write_test_footer(f, output_file: str, env: str, module: str):
    """写入测试文件尾部代码"""
    filename = os.path.splitext(os.path.basename(output_file))[0]
    f.write(f"""
if __name__ == '__main__':
    # pytest testcase/gitee/{filename}.py --env={env} --module={module} --alluredir=report/allure-results --clean-alluredir && allure serve report/allure-results -p 8899
    base_path = PathUtils.get_project_root_path('test-platform')
    allure_results_dir = f'{{base_path}}/report/allure-results'
    allure_report_dir = f'{{base_path}}/report/allure-report'
    os.makedirs(allure_results_dir, exist_ok=True)
    os.makedirs(allure_report_dir, exist_ok=True)
    pytest.main([f'{filename}.py', '--env={env}', '--module={module}', f'--alluredir={{allure_results_dir}}'])
    os.system(f'allure generate {{allure_results_dir}} -o {{allure_report_dir}} --clean')
    os.system(f'allure serve {{allure_results_dir}} -p 8899')
""")


def generate_test_cases_from_csv(testdata_base_dir: str, testdata_file: str, 
                                  testcase_base_dir: str, env: str, module: str):
    """
    从 CSV 文件生成测试用例
    :param testdata_base_dir: 测试数据基础目录
    :param testdata_file: CSV 文件路径
    :param testcase_base_dir: 测试用例基础目录
    :param env: 测试环境
    :param module: 测试模块
    """
    # 读取测试用例
    test_cases = _read_csv_test_cases(testdata_file)
    if not test_cases:
        logger.warning(f"CSV 文件 {testdata_file} 中没有测试用例数据")
        return

    # 获取模块名
    test_module_name = test_cases[0].get('test_module_name', UNKNOWN_MODULE)
    
    # 生成输出文件路径
    output_file, output_dir = _generate_output_file_path(
        testdata_file, testdata_base_dir, testcase_base_dir
    )

    # 生成测试文件
    path = Path(output_file)
    with path.open('w', encoding='utf-8') as f:
        # 写入文件头部
        f.write(_generate_test_class_header(env, test_module_name))
        f.write("\n")

        # 生成测试方法
        test_name_counts = {}  # 用于记录每个测试名称出现的次数
        
        for case in test_cases:
            # 跳过不需要执行的用例
            if case.get('is_skip') != SKIP_NO:
                continue

            # 生成测试方法名称
            test_name = _generate_test_name(case, test_name_counts)
            
            # 写入装饰器
            _write_test_method_decorator(f, case)
            
            # 写入方法签名
            _write_test_method_signature(f, case, test_name)
            
            # 处理路径参数
            normalized_path = _normalize_path(case['path'])
            f.write(f"        path = f\"{normalized_path}\"\n")
            
            # 处理请求体参数
            normalized_body = _normalize_request_body(case['request_body'])
            f.write(f"        body = {normalized_body}\n")
            
            # 写入请求代码
            _write_request_code(f, case)
            
            # 写入响应处理代码
            _write_response_handler(f, case)

        # 写入文件尾部
        _write_test_footer(f, output_file, env, module)


def _calculate_output_path(testdata_file: str, testdata_dir: str, testcase_dir: str) -> Path:
    """计算输出文件路径"""
    relative_path = os.path.dirname(os.path.relpath(testdata_file, testdata_dir))
    output_filename = (os.path.basename(testdata_file)
                       .replace(TEST_DATA_PREFIX, TEST_API_PREFIX)
                       .replace(CSV_EXTENSION, PYTHON_EXTENSION))
    
    if relative_path == '.':
        return Path(testcase_dir) / output_filename
    else:
        return Path(testcase_dir) / relative_path / output_filename


def process_testdata_directory(testdata_dir: str, testcase_dir: str, 
                                env: str, module: Optional[str] = None):
    """
    处理整个测试数据目录，包括所有子目录
    :param testdata_dir: 测试数据目录
    :param testcase_dir: 测试用例目录
    :param env: 测试环境
    :param module: 测试模块（可选）
    """
    # 确保输出目录存在
    os.makedirs(testcase_dir, exist_ok=True)

    # 递归查找所有 test_data_*.csv 文件
    if module:
        csv_pattern = str(Path(testdata_dir) / module / f'{TEST_DATA_PREFIX}*{CSV_EXTENSION}')
    else:
        csv_pattern = str(Path(testdata_dir) / '**' / f'{TEST_DATA_PREFIX}*{CSV_EXTENSION}')
    
    testdata_files = glob(csv_pattern, recursive=True)

    if not testdata_files:
        logger.warning(f"在目录 {testdata_dir} 中没有找到任何 {TEST_DATA_PREFIX}*{CSV_EXTENSION} 文件")
        return

    for testdata_file in testdata_files:
        generate_test_cases_from_csv(
            testdata_base_dir=testdata_dir,
            testdata_file=testdata_file,
            testcase_base_dir=testcase_dir,
            env=env,
            module=module
        )

        # 计算并输出日志
        output_path = _calculate_output_path(testdata_file, testdata_dir, testcase_dir)
        logger.info(f"生成 testcase: {output_path}")


def _generate_test_class_header_from_config(env: str, test_module_name: str, env_config: Dict) -> str:
    """从环境配置生成测试类的头部代码"""
    current_time = datetime.now().strftime("%Y/%m/%d %H:%M")
    
    # 不再从 env_config 中硬编码配置，改为使用 ConfigUtils 从 config.yaml 获取
    
    return f'''#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
@author       Auto Generated
@time         {current_time}
@description  API 接口测试 - 模块: {test_module_name}, 环境: {env}
"""

import os
import sys
import allure
import pytest
import asyncio
from datetime import datetime, timedelta
from pathlib import Path

# 添加项目根目录到 Python 路径，确保可以导入 utils 和 config 模块
# 检测是否在 Docker 环境中（路径以 /app 开头）
current_file = Path(__file__).resolve()
current_path = current_file.parent
is_docker = str(current_path).startswith('/app')

if is_docker:
    # Docker 环境：/app 就是项目根目录（backend 目录被挂载到 /app）
    project_root = '/app'
    # 确保 /app 在 sys.path 的最前面，并且移除可能干扰的路径
    if project_root in sys.path:
        sys.path.remove(project_root)
    sys.path.insert(0, project_root)
    # 移除当前目录（/app/app/autotest/testcase）避免干扰模块搜索
    current_dir = str(current_path)
    if current_dir in sys.path:
        sys.path.remove(current_dir)
    # Docker 环境中，使用 app.xxx 导入（不带 backend 前缀）
    from app.utils.log_util import Logger
    from app.utils.path_util import PathUtils
    from app.utils.http_client_util import HttpClient
    from app.utils.response_util import APIResponse
    from app.autotest.config.config_util import ConfigUtils
else:
    # 本地开发环境：向上查找包含 backend/ 目录的项目根目录
    project_root = None
    for parent in current_path.parents:
        backend_dir = parent / 'backend'
        if backend_dir.exists() and backend_dir.is_dir():
            project_root = parent
            break
    
    # 如果没找到，使用默认路径（从 testcase/ 向上 4 级）
    if project_root is None:
        project_root = current_path.parent.parent.parent.parent
    
    # 将项目根目录添加到 sys.path，这样可以使用 backend.app.xxx 导入
    if project_root and str(project_root) not in sys.path:
        sys.path.insert(0, str(project_root))
    
    # 本地环境中，使用 backend.app.xxx 导入
    from backend.app.utils.log_util import Logger
    from backend.app.utils.path_util import PathUtils
    from backend.app.utils.http_client_util import HttpClient
    from backend.app.utils.response_util import APIResponse
    from backend.app.autotest.config.config_util import ConfigUtils

env = '{env}'

@allure.story("{test_module_name}")
class TestAPI:
    @classmethod
    def setup_class(cls):
        """测试类初始化"""
        cls.logger = Logger()
        cls.time = datetime.now().strftime('%Y%m%d%H%M%S')
        cls.current_year = datetime.now().strftime('%Y')
        cls.current_week = (datetime.now() - timedelta(weeks=1)).isocalendar()[1]
        cls.base_path = PathUtils.get_project_root_path('test-platform')
        # 根据环境自动设置 config_path
        # Docker 环境：/app/app/autotest/config/config.yaml
        # 本地环境：项目根目录/backend/app/autotest/config/config.yaml
        if str(cls.base_path).startswith('/app'):
            cls.config_path = os.path.join(cls.base_path, 'app', 'autotest', 'config', 'config.yaml')
        else:
            cls.config_path = os.path.join(cls.base_path, 'backend', 'app', 'autotest', 'config', 'config.yaml')

        cls.env = '{env}'
        cls.data = ConfigUtils(cls.env, cls.config_path)
        cls.host = cls.data.host
        cls.user_id = cls.data.user_id
        cls.username = cls.data.username
        cls.password = cls.data.password
        cls.headers = cls.data.headers
        cls.access_token = cls.data.access_token
        cls.enterprise_id = cls.data.enterprise_id
        cls.enterprise_path = cls.data.enterprise_path
        cls.project_id = cls.data.project_id
        cls.project_path = cls.data.project_path
        cls.program_id = cls.data.program_id
        cls.team_id = cls.data.team_id
        cls.file_path = cls.data.file_path
        cls.docker_responsitory = cls.data.docker_responsitory
        cls.docker_username = cls.data.docker_username
        cls.docker_password = cls.data.docker_password
        cls.client = HttpClient(cls.host)
'''


def generate_pytest_code_from_test_cases(test_cases: List, component_name: str, 
                                          module_name: str, environment_name: str, env_config: Dict,
                                          output_dir: str) -> str:
    """
    从数据库的测试用例对象生成 pytest 测试代码
    
    :param test_cases: 测试用例对象列表（TestCase 模型实例）
    :param component_name: 组件名称
    :param module_name: 模块名称
    :param environment_name: 环境名称
    :param env_config: 环境配置字典
    :param output_dir: 输出目录
    :return: 生成的测试文件路径
    """
    # 确保输出目录存在
    os.makedirs(output_dir, exist_ok=True)
    
    # 生成文件名
    timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
    module_suffix = f"_{module_name.replace(' ', '_').replace('/', '_')}" if module_name else ""
    env_suffix = f"_{environment_name}" if environment_name else ""
    component_suffix = f"_{component_name.replace(' ', '_').replace('/', '_')}" if component_name else ""
    test_file_name = f"test_auto_{timestamp}{component_suffix}{module_suffix}{env_suffix}.py"
    test_file_path = os.path.join(output_dir, test_file_name)
    
    # 获取模块名（从第一个测试用例获取，如果没有则使用传入的模块名）
    test_module_name = module_name or '自动化测试'
    if test_cases and hasattr(test_cases[0], 'test_module_name') and test_cases[0].test_module_name:
        test_module_name = test_cases[0].test_module_name
    
    # 生成测试文件
    with open(test_file_path, 'w', encoding='utf-8') as f:
        # 写入文件头部
        f.write(_generate_test_class_header_from_config(environment_name or 'default', test_module_name, env_config))
        f.write("\n")
        
        # 生成测试方法
        test_name_counts = {}  # 用于记录每个测试名称出现的次数
        
        for case in test_cases:
            # 跳过不需要执行的用例
            if hasattr(case, 'is_skip') and case.is_skip and case.is_skip.lower() != SKIP_NO:
                continue
            
            # 生成测试方法名称
            if hasattr(case, 'path') and hasattr(case, 'request_method'):
                path = urllib.parse.unquote(case.path.split('?')[0])
                base_name = (f"test_{case.request_method.lower()}"
                             f"{path.replace('/', '_').replace('{', '').replace('}', '').replace('-', '_').replace('.', '_')}")
                
                if base_name in test_name_counts:
                    test_name_counts[base_name] += 1
                    test_name = f"{base_name}_{test_name_counts[base_name]}"
                else:
                    test_name_counts[base_name] = 1
                    test_name = base_name
            else:
                # 如果没有 path 和 request_method，使用 test_case_id
                test_name = f"test_{case.test_case_id.lower().replace('-', '_')}" if hasattr(case, 'test_case_id') else f"test_case_{len(test_name_counts) + 1}"
            
            # 写入装饰器
            if hasattr(case, 'test_case_id') and hasattr(case, 'test_case_name'):
                f.write(f"    @allure.title('{case.test_case_id}-{case.test_case_name}')\n")
            
            # 添加pytest注解
            if hasattr(case, 'pytest_annotation') and case.pytest_annotation:
                f.write(f"    {case.pytest_annotation}\n")
            
            # 写入方法签名
            if hasattr(case, 'test_case_name') and ASYNC_MARKER in case.test_case_name:
                f.write(f"    async def {test_name}(self):\n")
            else:
                f.write(f"    def {test_name}(self):\n")
            
            if hasattr(case, 'test_case_name'):
                f.write(f"        \"\"\"{case.test_case_name}\"\"\"\n")
            
            # 处理路径参数
            if hasattr(case, 'path'):
                normalized_path = _normalize_path(case.path)
                f.write(f"        path = f\"{normalized_path}\"\n")
            
            # 处理请求体参数
            if hasattr(case, 'request_body') and case.request_body and case.request_body != 'None':
                normalized_body = _normalize_request_body(case.request_body)
                f.write(f"        body = {normalized_body}\n")
            else:
                f.write("        body = None\n")
            
            # 写入请求代码
            if hasattr(case, 'request_method') and hasattr(case, 'test_case_name'):
                request_method = case.request_method.lower() if case.request_method else 'get'
                test_case_name = case.test_case_name if hasattr(case, 'test_case_name') else ''
                
                if request_method == 'get':
                    if DOWNLOAD_MARKER in test_case_name:
                        if test_case_name in SPECIAL_DOWNLOAD_FILES:
                            file_path = f"self.file_path + '{SPECIAL_DOWNLOAD_FILES[test_case_name]}'"
                        else:
                            file_path = "self.file_path"
                        f.write(f"        self.client.download_file(path, {file_path}, self.headers)\n\n")
                    else:
                        f.write(f"        response = APIResponse(self.client.send_get_request(path, self.headers))\n")
                else:
                    if UPLOAD_MARKER in test_case_name:
                        f.write(f"        response = APIResponse(self.client.upload_file(path, self.file_path + '/tmp.txt', body, self.headers))\n\n")
                    else:
                        f.write(f"        response = APIResponse(self.client.send_{request_method}_request(path, body, self.headers))\n")
            else:
                # 默认使用 GET 请求
                f.write(f"        response = APIResponse(self.client.send_get_request(path, self.headers))\n")
            
            # 写入响应处理代码
            # 获取响应结果提供给依赖用例
            if hasattr(case, 'response_body') and case.response_body:
                formatted_response = case.response_body.replace('\\n', '\n')
                indented_response = '\n        '.join(formatted_response.splitlines())
                f.write(f"        {indented_response}\n")
            
            # 状态码断言（排除下载类型）
            if hasattr(case, 'test_case_name') and hasattr(case, 'assert_status'):
                download_pattern = re.compile(r'.*(?:导出|下载).*\(download\)$')
                if not download_pattern.match(case.test_case_name):
                    assert_status = case.assert_status
                    test_case_name = case.test_case_name if hasattr(case, 'test_case_name') else '状态码验证'
                    f.write(f"        response.assert_status(({assert_status}), '{test_case_name}状态码验证')\n\n")
            
            # 异步等待
            if hasattr(case, 'test_case_name') and ASYNC_MARKER in case.test_case_name:
                f.write(f"        await asyncio.sleep(3)\n\n")
            
            # 值断言
            if hasattr(case, 'assert_value') and case.assert_value:
                assert_value = case.assert_value
                f.write(f"        response.assert_value({assert_value})\n\n")
    
    logger.info(f"生成测试用例文件: {test_file_path}")
    return test_file_path


if __name__ == '__main__':
    env = 'premium_k8s'

    base_path = PathUtils.get_project_root_path('test-platform')
    testdata_dir = Path(base_path) / 'testdata'
    testcase_dir = Path(base_path) / 'testcase'

    # 处理整个测试数据目录
    process_testdata_directory(testdata_dir, testcase_dir, env, 'example')
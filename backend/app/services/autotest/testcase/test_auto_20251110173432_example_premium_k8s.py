#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
@author       Auto Generated
@time         2025/11/10 17:34
@description  API 接口测试 - 模块: 示例模块, 环境: premium_k8s
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

env = 'premium_k8s'

@allure.story("示例模块")
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

        cls.env = 'premium_k8s'
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

    @allure.title('TC002-查看仓库')
    def test_get_enterprises_enterprise_id_projects(self):
        """查看仓库"""
        path = f"/enterprises/{self.enterprise_id}/projects?page=1&per_page=20&offset=0"
        body = None
        response = APIResponse(self.client.send_get_request(path, self.headers))
        response.assert_status((200,201,204), '查看仓库状态码验证')

        response.assert_value(response.data['total_count'] > 0,"仓库总数应该大于0")


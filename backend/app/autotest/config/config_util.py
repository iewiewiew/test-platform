#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
@author       weimenghua
@time         2024/8/2 17:46
@description  读取配置文件
"""

import json
import sys
from pathlib import Path
from typing import Dict, List, Optional, Union

import yaml

from ...utils.http_client_util import HttpClient
from ...utils.log_util import Logger
from ...utils.path_util import PathUtils

logger = Logger()


class ConfigUtils:
    """通用配置读取工具类，支持YAML和JSON格式"""

    # 类常量定义默认路径
    DEFAULT_CONFIG_DIR = "config"
    DEFAULT_YAML_CONFIG = "config.yaml"
    DEFAULT_JSON_CONFIG = "config_pipeline_info.json"

    def __init__(self, config_key: str = None, config_path: str = None, config_type: str = "yaml"):
        """
        初始化配置工具
        :param config_key: 配置键名（YAML需要）
        :param config_path: 配置文件路径（可选）
        :param config_type: 配置类型，yaml或json
        """
        self.config_path = self._resolve_config_path(config_path, config_type)
        self.config_type = config_type.lower()
        self.config_key = config_key
        self.data = self._load_config()

        # 初始化通用配置
        self._init_common_config()

    def _resolve_config_path(self, config_path: str, config_type: str) -> str:
        """解析配置文件路径"""
        if config_path:
            return config_path

        # 获取项目根目录
        project_root = Path(sys.path[0]).parent
        config_dir = project_root / self.DEFAULT_CONFIG_DIR

        # 根据类型返回默认路径
        if config_type == "yaml":
            return str(config_dir / self.DEFAULT_YAML_CONFIG)
        return str(config_dir / self.DEFAULT_JSON_CONFIG)

    def _load_config(self) -> Dict:
        """加载配置文件"""
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                if self.config_type == "yaml":
                    config = yaml.safe_load(f)
                    return config.get(self.config_key, {}) if self.config_key else config
                else:
                    return json.load(f)
        except FileNotFoundError:
            logger.error(f"Config file not found: {self.config_path}")
            return {}
        except (yaml.YAMLError, json.JSONDecodeError) as e:
            logger.error(f"Invalid config format: {str(e)}")
            return {}
        except Exception as e:
            logger.error(f"Failed to load config: {str(e)}")
            return {}

    def _init_common_config(self):
        """初始化通用配置项"""
        # 企业信息
        enterprise_info = self.data.get('enterprise_info', {})
        self.host = enterprise_info.get('host')
        self.enterprise_id = enterprise_info.get('enterprise_id')
        self.enterprise_path = enterprise_info.get('enterprise_path')
        self.access_token = enterprise_info.get('access_token')
        self.session_cookie = enterprise_info.get('session_cookie')
        self.user_id = enterprise_info.get('user_id')
        self.username = enterprise_info.get('username')
        self.password = enterprise_info.get('password')

        # 仓库信息
        self.project_id = self.data.get('project_info', {}).get('project_id')
        self.project_path = self.data.get('project_info', {}).get('project_path')
        self.project_list = self.data.get('project_info', {}).get('project_list')

        # 其它信息
        self.scheme = self.data.get('mix_info', {}).get('scheme')
        self.team_id = self.data.get('mix_info', {}).get('team_id')
        self.program_id = self.data.get('mix_info', {}).get('program_id')
        self.file_path = self.data.get('mix_info', {}).get('file_path')

        # 数据库信息
        self.dbhost = self.data.get('dbhost')
        self.port = self.data.get('port')
        self.user = self.data.get('user')
        self.dbpassword = self.data.get('dbpassword')
        self.database = self.data.get('database')

        # 邮件信息
        self.sender_mail = self.data.get('sender_mail')
        self.auth_code = self.data.get('auth_code')
        self.receiver_mail = self.data.get('receiver_mail')

        # Git 信息
        self.ssh_url = self.data.get('git', {}).get('ssh_url')
        self.http_url = self.data.get('git', {}).get('http_url')

        # GiteeGo 信息
        self.repo_username = self.data.get('giteego', {}).get('repo_username')
        self.repo_password = self.data.get('giteego', {}).get('repo_password')
        self.repo_artifact_url = self.data.get('giteego', {}).get('repo_artifact_url')
        self.artifact_repository = self.data.get('giteego', {}).get('artifact_repository')
        self.docker_responsitory = self.data.get('giteego', {}).get('docker_responsitory')
        self.docker_username = self.data.get('giteego', {}).get('docker_username')
        self.docker_password = self.data.get('giteego', {}).get('docker_password')
        self.docker_images_tag = self.data.get('giteego', {}).get('docker_images_tag')
        self.sleep_time = self.data.get('giteego', {}).get('sleep_time')
        self.is_run_pipeline = self.data.get('giteego', {}).get('is_run_pipeline')

        # HTTP客户端
        self.headers = {
            'Accept': 'application/json, text/plain, */*',
            'Cookie': f'{self.session_cookie}' if self.session_cookie else '',
            'Content-Type': 'application/json;charset=UTF-8',
            'Xly_Enterprise': f'{self.enterprise_path}',
            'Xly_Enterprise_ID': f'{self.enterprise_id}',
            'xly_repo_id': f'{self.project_id}'
        }
        self.client = HttpClient(self.host) if self.host else None

    def get_value(self, key_path: str, default=None) -> Union[Dict, List, str, int, None]:
        """
        安全获取嵌套配置值
        :param key_path: 点分隔的键路径，如 'enterprise_info.host'
        :param default: 默认值
        :return: 配置值或默认值
        """
        keys = key_path.split('.')
        value = self.data
        try:
            for key in keys:
                value = value[key]
            return value
        except (KeyError, TypeError):
            return default

    @property
    def is_valid(self) -> bool:
        """检查配置是否有效"""
        return bool(self.data)


class PipelineConfigReader(ConfigUtils):
    """专门用于读取流水线配置的工具类"""

    def __init__(self, config_path: str = None):
        """
        初始化流水线配置读取器
        :param config_path: JSON配置文件路径（可选）
        """
        super().__init__(config_path=config_path, config_type="json")
        self.pipeline_displayname_list = self.data.get('pipeline_displayname_list', [])
        self.repo_list = self.data.get('repo_list', [])
        self.pipeline_methods = self.data.get('pipeline_methods', {})

    def get_display_names(self) -> List[str]:
        """获取所有流水线显示名称列表"""
        return self.pipeline_displayname_list

    def get_repo_list(self) -> List[str]:
        """获取所有仓库名称列表"""
        return self.repo_list

    def get_pipeline_methods(self, repo_name: str) -> Optional[List[str]]:
        """获取指定仓库的流水线方法列表"""
        return self.pipeline_methods.get(repo_name)

    def get_all_pipeline_methods(self) -> Dict[str, List[str]]:
        """获取所有流水线方法映射"""
        return self.pipeline_methods

    @property
    def is_valid(self) -> bool:
        """检查流水线配置是否有效"""
        return super().is_valid and all([
            self.pipeline_displayname_list,
            self.repo_list,
            self.pipeline_methods
        ])


if __name__ == '__main__':
    # 使用示例 - YAML配置
    import os
    # 获取当前文件所在目录的父目录（autotest目录）
    base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    config_path = os.path.join(base_path, 'config', 'config.yaml')

    yaml_config = ConfigUtils(config_key='example_env', config_path=config_path)
    logger.debug(f"host from YAML: {yaml_config.host}")
    logger.debug(f"username from YAML: {yaml_config.username}")
    logger.debug(f"username from YAML: {yaml_config.ssh_url}")

    # 使用示例 - JSON流水线配置
    pipeline_config = PipelineConfigReader()
    if pipeline_config.is_valid:
        logger.debug(pipeline_config.get_display_names())
        logger.debug(pipeline_config.get_repo_list())
        logger.debug(pipeline_config.get_all_pipeline_methods())
        logger.debug(pipeline_config.get_pipeline_methods('java-maven-example'))
    else:
        logger.error("Invalid pipeline configuration")

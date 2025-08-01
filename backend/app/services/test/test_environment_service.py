#!/usr/bin/env python
# -*- coding:utf-8 -*-

"""
@author       weimenghua
@time         2025/1/XX
@description  测试环境服务层
"""

import os
import yaml
import json
from sqlalchemy import or_

from ...core.database import db
from ...core.exceptions import APIException
from ...models.test.test_environment_model import TestEnvironment
from ...utils.path_util import PathUtils


class TestEnvironmentService:
    """测试环境服务类"""

    @staticmethod
    def _get_config_file():
        """获取配置文件路径"""
        # 使用基于当前文件位置的路径计算，避免依赖项目名称
        current_file = os.path.abspath(__file__)
        app_dir = os.path.dirname(os.path.dirname(os.path.dirname(current_file)))  # 获取 app 目录
        return os.path.join(app_dir, 'autotest', 'config', 'config.yaml')

    @staticmethod
    def parse_config_file(config_file=None, current_user=None):
        """解析配置文件并初始化数据库"""
        if config_file is None:
            config_file = TestEnvironmentService._get_config_file()

        if not os.path.exists(config_file):
            raise APIException(f'配置文件不存在: {config_file}', 404)

        with open(config_file, 'r', encoding='utf-8') as f:
            config_data = yaml.safe_load(f)

        parsed_count = 0
        errors = []

        # 解析每个环境配置
        for env_name, env_config in config_data.items():
            # 跳过非环境配置的键（如database, email等）
            if not isinstance(env_config, dict) or 'enterprise_info' not in env_config:
                continue

            try:
                # 检查是否已存在
                existing = TestEnvironment.query.filter_by(env_name=env_name).first()
                
                if existing:
                    # 更新现有环境
                    existing.env_config = json.dumps(env_config, ensure_ascii=False)
                    existing.description = ''
                    # 更新更新人
                    if current_user:
                        existing.updated_by = current_user.id
                else:
                    # 创建新环境
                    test_env = TestEnvironment(
                        env_name=env_name,
                        env_config=json.dumps(env_config, ensure_ascii=False),
                        description='',
                        created_by=current_user.id if current_user else None,
                        updated_by=current_user.id if current_user else None
                    )
                    db.session.add(test_env)
                    parsed_count += 1
            except Exception as e:
                errors.append(f'解析环境 {env_name} 失败: {str(e)}')

        db.session.commit()

        return {
            'parsed_count': parsed_count,
            'updated_count': len(config_data) - parsed_count,
            'errors': errors,
            'message': f'成功解析 {parsed_count} 个新环境，更新 {len(config_data) - parsed_count} 个现有环境'
        }

    @staticmethod
    def get_test_environments(page=1, per_page=10, search=None):
        """获取测试环境列表（支持分页和搜索）"""
        from sqlalchemy.orm import joinedload
        
        query = TestEnvironment.query.options(
            joinedload(TestEnvironment.creator),
            joinedload(TestEnvironment.updater)
        ).filter_by(is_active=True)

        # 添加搜索条件
        if search:
            query = query.filter(
                TestEnvironment.env_name.ilike(f'%{search}%')
            )

        # 排序和分页
        pagination = query.order_by(TestEnvironment.id.desc()).paginate(
            page=page, per_page=per_page, error_out=False
        )

        results = []
        for env in pagination.items:
            env_dict = env.to_dict()
            # 解析配置（只显示基本信息，不显示完整配置）
            try:
                config = json.loads(env.env_config)
                if 'enterprise_info' in config:
                    enterprise_info = config['enterprise_info']
                    env_dict['host'] = enterprise_info.get('host', '')
                    env_dict['enterprise_id'] = enterprise_info.get('enterprise_id', '')
            except:
                pass
            results.append(env_dict)

        return {
            'data': results,
            'total': pagination.total,
            'page': page,
            'per_page': per_page
        }

    @staticmethod
    def get_test_environment_by_id(env_id):
        """根据ID获取测试环境详情"""
        env = TestEnvironment.query.filter_by(id=env_id, is_active=True).first_or_404()
        result = env.to_dict()
        
        # 解析配置
        try:
            result['env_config'] = json.loads(env.env_config)
        except:
            result['env_config'] = env.env_config

        return result

    @staticmethod
    def get_environment_config(env_name):
        """根据环境名称获取环境配置"""
        env = TestEnvironment.query.filter_by(env_name=env_name, is_active=True).first()
        if not env:
            return None
        
        try:
            return json.loads(env.env_config)
        except:
            return None

    @staticmethod
    def create_test_environment(data, current_user=None):
        """创建测试环境"""
        required_fields = ['env_name', 'env_config']
        if not all(field in data for field in required_fields):
            raise APIException('环境名称和配置不能为空', 400)

        # 检查环境名称是否已存在
        existing = TestEnvironment.query.filter_by(env_name=data['env_name']).first()
        if existing:
            raise APIException(f'环境名称 {data["env_name"]} 已存在', 409)

        try:
            # 如果env_config是字典，转换为JSON字符串
            if isinstance(data['env_config'], dict):
                env_config_str = json.dumps(data['env_config'], ensure_ascii=False)
            else:
                env_config_str = data['env_config']

            test_env = TestEnvironment(
                env_name=data['env_name'],
                env_config=env_config_str,
                description=data.get('description', ''),
                created_by=current_user.id if current_user else None,
                updated_by=current_user.id if current_user else None
            )

            db.session.add(test_env)
            db.session.commit()

            # 更新YAML文件
            TestEnvironmentService._update_yaml_file(data['env_name'], data['env_config'])

            return test_env.to_dict()

        except Exception as e:
            db.session.rollback()
            raise APIException(f'创建失败: {str(e)}', 500)

    @staticmethod
    def update_test_environment(env_id, data, current_user=None):
        """更新测试环境"""
        env = TestEnvironment.query.filter_by(id=env_id, is_active=True).first_or_404()

        try:
            if 'env_name' in data:
                # 检查新名称是否与其他环境冲突
                existing = TestEnvironment.query.filter(
                    TestEnvironment.env_name == data['env_name'],
                    TestEnvironment.id != env_id
                ).first()
                if existing:
                    raise APIException(f'环境名称 {data["env_name"]} 已存在', 409)
                env.env_name = data['env_name']

            if 'env_config' in data:
                # 如果env_config是字典，转换为JSON字符串
                if isinstance(data['env_config'], dict):
                    env_config_str = json.dumps(data['env_config'], ensure_ascii=False)
                else:
                    env_config_str = data['env_config']
                env.env_config = env_config_str

            if 'description' in data:
                env.description = data['description']

            if current_user:
                env.updated_by = current_user.id

            db.session.commit()

            # 更新YAML文件
            if 'env_config' in data:
                TestEnvironmentService._update_yaml_file(env.env_name, data['env_config'])

            return env.to_dict()

        except APIException:
            raise
        except Exception as e:
            db.session.rollback()
            raise APIException(f'更新失败: {str(e)}', 500)

    @staticmethod
    def _update_yaml_file(env_name, env_config):
        """更新YAML配置文件"""
        config_file = TestEnvironmentService._get_config_file()

        # 读取现有配置
        if os.path.exists(config_file):
            with open(config_file, 'r', encoding='utf-8') as f:
                config_data = yaml.safe_load(f) or {}
        else:
            config_data = {}

        # 如果env_config是字符串，尝试解析为字典
        if isinstance(env_config, str):
            try:
                env_config = json.loads(env_config)
            except:
                pass

        # 更新或添加环境配置
        config_data[env_name] = env_config

        # 写入YAML文件
        with open(config_file, 'w', encoding='utf-8') as f:
            yaml.dump(config_data, f, allow_unicode=True, default_flow_style=False, sort_keys=False)

    @staticmethod
    def delete_test_environment(env_id):
        """删除测试环境（软删除）"""
        env = TestEnvironment.query.filter_by(id=env_id, is_active=True).first_or_404()
        env.is_active = False
        db.session.commit()
        return {'message': '测试环境删除成功'}

    @staticmethod
    def export_all_test_environments(format='json'):
        """
        导出所有测试环境配置，格式与 config.yaml 保持一致
        
        Args:
            format: 导出格式，支持 'json' 或 'yaml'
            
        Returns:
            tuple: (文件内容, 文件名, MIME类型)
        """
        from datetime import datetime
        
        # 获取所有活跃的测试环境
        environments = TestEnvironment.query.filter_by(is_active=True).order_by(TestEnvironment.id).all()
        
        # 构建导出数据，格式与 config.yaml 保持一致
        # 顶层键是环境名称，值是环境配置对象
        export_data = {}
        
        # 遍历所有环境，构建配置字典
        for env in environments:
            # 解析环境配置
            if isinstance(env.env_config, str):
                env_config = json.loads(env.env_config)
            else:
                env_config = env.env_config
            
            # 以环境名称为键，配置对象为值
            export_data[env.env_name] = env_config
        
        # 根据格式生成文件内容
        if format.lower() == 'yaml':
            content = yaml.dump(export_data, allow_unicode=True, default_flow_style=False, sort_keys=False)
            filename = f"config_{datetime.now().strftime('%Y%m%d_%H%M%S')}.yaml"
            mimetype = 'application/x-yaml'
        else:  # 默认 JSON
            content = json.dumps(export_data, ensure_ascii=False, indent=2)
            filename = f"config_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            mimetype = 'application/json'
        
        return content, filename, mimetype


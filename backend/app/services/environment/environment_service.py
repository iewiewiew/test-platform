#!/usr/bin/env python
# -*- coding:utf-8 -*-

"""
@author       weimenghua
@time         2025/10/1 19:12
@description  环境管理服务层
"""

from sqlalchemy import or_
from sqlalchemy.exc import IntegrityError

from ...core.database import db
from ...core.exceptions import APIException
from ...models.environment.environment_model import Environment, EnvironmentParameter


class EnvironmentService:
    @staticmethod
    def get_all_environments(page=1, per_page=10, search=None, project_id=None):
        """获取所有环境（支持分页和搜索）"""

        # 基础查询
        query = Environment.query.filter_by(is_active=True)

        # 添加搜索条件
        if search:
            query = query.filter(or_(Environment.name.ilike(f'%{search}%'), Environment.base_url.ilike(f'%{search}%'),
                Environment.description.ilike(f'%{search}%')))

        # 项目筛选
        if project_id:
            query = query.filter(Environment.project_id == project_id)

        # 排序和分页，同时加载服务器信息
        from sqlalchemy.orm import joinedload
        query = query.options(joinedload(Environment.server))
        pagination = query.order_by(Environment.id.desc()).paginate(page=page, per_page=per_page,
            error_out=False)

        return {'data': [environment.to_dict() for environment in pagination.items], 'total': pagination.total,
            'page': page, 'per_page': per_page}

    @staticmethod
    def get_environment_by_id(environment_id):
        """获取单个环境详情"""

        environment = Environment.query.filter_by(id=environment_id, is_active=True).first_or_404()

        return environment.to_dict()

    @staticmethod
    def create_environment(data, current_user=None):
        """创建环境"""

        # 检查必填字段
        required_fields = ['name', 'base_url']
        if not all(field in data for field in required_fields):
            raise APIException('环境名称和基础URL不能为空', 400)

        try:
            environment = Environment(name=data['name'], base_url=data['base_url'],
                username=data.get('username', ''),
                password=data.get('password', ''),
                description=data.get('description', ''),
                server_id=data.get('server_id'))
            if current_user:
                environment.created_by = current_user.id
                environment.updated_by = current_user.id

            db.session.add(environment)
            db.session.commit()

            return environment.to_dict()

        except IntegrityError as e:
            db.session.rollback()
            if 'uq_environment_name' in str(e.orig):
                raise APIException(f"环境名称 '{data['name']}' 已存在", 409, {'name': data['name']})
            else:
                raise APIException('数据库错误', 500, {'details': str(e.orig)})

    @staticmethod
    def update_environment(environment_id, data, current_user=None):
        """更新环境"""

        environment = Environment.query.filter_by(id=environment_id, is_active=True).first_or_404()

        try:
            # 更新字段
            if 'name' in data:
                environment.name = data['name']
            if 'base_url' in data:
                environment.base_url = data['base_url']
            if 'username' in data:
                environment.username = data['username']
            if 'password' in data:
                environment.password = data['password']
            if 'description' in data:
                environment.description = data['description']
            if 'project_id' in data:
                environment.project_id = data['project_id']
            if 'server_id' in data:
                environment.server_id = data['server_id']
            
            if current_user:
                environment.updated_by = current_user.id

            db.session.commit()

            return environment.to_dict()

        except IntegrityError as e:
            db.session.rollback()
            if 'uq_environment_name' in str(e.orig):
                raise APIException(f"环境名称 '{data.get('name', environment.name)}' 已存在", 409,
                    {'name': data.get('name', environment.name)})
            else:
                raise APIException('数据库错误', 500, {'details': str(e.orig)})

    @staticmethod
    def delete_environment(environment_id):
        """删除环境（软删除）"""

        environment = Environment.query.filter_by(id=environment_id, is_active=True).first_or_404()

        try:
            # 软删除环境
            environment.is_active = False

            # 同时软删除关联的所有参数
            EnvironmentParameter.query.filter_by(environment_id=environment_id).update({'is_active': False})

            db.session.commit()

            return {'message': '环境删除成功'}

        except Exception as e:
            db.session.rollback()
            raise APIException('删除失败', 500, {'details': str(e)})

    @staticmethod
    def get_environment_parameters(environment_id, page=1, per_page=10, search=None):
        """获取环境参数列表（支持分页和搜索）"""

        # 验证环境存在
        environment = Environment.query.filter_by(id=environment_id, is_active=True).first_or_404()

        # 基础查询
        query = EnvironmentParameter.query.filter_by(environment_id=environment_id, is_active=True)

        # 添加搜索条件
        if search:
            query = query.filter(or_(EnvironmentParameter.param_key.ilike(f'%{search}%'),
                EnvironmentParameter.description.ilike(f'%{search}%')))

        # 排序和分页
        pagination = query.order_by(EnvironmentParameter.id.desc()).paginate(page=page, per_page=per_page,
            error_out=False)

        return {'data': [parameter.to_dict() for parameter in pagination.items], 'total': pagination.total,
            'page': page, 'per_page': per_page, 'environment': environment.to_dict()}

    @staticmethod
    def create_environment_parameter(environment_id, data, current_user=None):
        """创建环境参数"""

        # 验证环境存在
        environment = Environment.query.filter_by(id=environment_id, is_active=True).first_or_404()

        # 检查必填字段
        required_fields = ['param_key', 'param_value']
        if not all(field in data for field in required_fields):
            raise APIException('参数键和参数值不能为空', 400)

        try:
            parameter = EnvironmentParameter(environment_id=environment_id, param_key=data['param_key'],
                param_value=data['param_value'], description=data.get('description', ''))
            if current_user:
                parameter.created_by = current_user.id
                parameter.updated_by = current_user.id

            db.session.add(parameter)

            # 更新环境的参数计数
            EnvironmentService._update_environment_parameter_count(environment_id)

            db.session.commit()

            return parameter.to_dict()

        except IntegrityError as e:
            db.session.rollback()
            if 'uq_environment_param_key' in str(e.orig):
                raise APIException(f"参数键 '{data['param_key']}' 在该环境中已存在", 409,
                    {'param_key': data['param_key'], 'environment_id': environment_id})
            else:
                raise APIException('数据库错误', 500, {'details': str(e.orig)})

    @staticmethod
    def update_environment_parameter(parameter_id, data, current_user=None):
        """更新环境参数"""

        parameter = EnvironmentParameter.query.filter_by(id=parameter_id, is_active=True).first_or_404()

        try:
            # 更新字段
            if 'param_key' in data:
                parameter.param_key = data['param_key']
            if 'param_value' in data:
                parameter.param_value = data['param_value']
            if 'description' in data:
                parameter.description = data['description']
            
            if current_user:
                parameter.updated_by = current_user.id

            db.session.commit()

            return parameter.to_dict()

        except IntegrityError as e:
            db.session.rollback()
            if 'uq_environment_param_key' in str(e.orig):
                raise APIException(f"参数键 '{data.get('param_key', parameter.param_key)}' 在该环境中已存在", 409,
                    {'param_key': data.get('param_key', parameter.param_key),
                        'environment_id': parameter.environment_id})
            else:
                raise APIException('数据库错误', 500, {'details': str(e.orig)})

    @staticmethod
    def delete_environment_parameter(parameter_id):
        """删除环境参数（软删除）"""

        parameter = EnvironmentParameter.query.filter_by(id=parameter_id, is_active=True).first_or_404()

        try:
            environment_id = parameter.environment_id
            parameter.is_active = False

            # 更新环境的参数计数
            EnvironmentService._update_environment_parameter_count(environment_id)

            db.session.commit()

            return {'message': '参数删除成功'}

        except Exception as e:
            db.session.rollback()
            raise APIException('删除失败', 500, {'details': str(e)})

    @staticmethod
    def _update_environment_parameter_count(environment_id):
        """更新环境的参数计数"""

        parameter_count = EnvironmentParameter.query.filter_by(environment_id=environment_id, is_active=True).count()

        environment = Environment.query.get(environment_id)
        environment.parameter_count = parameter_count

    @staticmethod
    def get_environment_stats(environment_id):
        """获取环境统计信息"""

        environment = Environment.query.filter_by(id=environment_id, is_active=True).first_or_404()

        # 获取参数分类统计
        parameter_stats = db.session.query(EnvironmentParameter.param_key,
            db.func.count(EnvironmentParameter.id)).filter_by(environment_id=environment_id, is_active=True).group_by(
            EnvironmentParameter.param_key).all()

        return {'environment': environment.to_dict(),
            'parameter_stats': [{'param_key': key, 'count': count} for key, count in parameter_stats],
            'total_parameters': environment.parameter_count}

    @staticmethod
    def copy_environment(environment_id, new_name, current_user=None):
        """复制环境及其参数"""

        source_environment = Environment.query.filter_by(id=environment_id, is_active=True).first_or_404()

        try:
            # 创建新环境
            new_environment = Environment(name=new_name, base_url=source_environment.base_url,
                username=source_environment.username or '',
                password=source_environment.password or '',
                description=f"复制自: {source_environment.name}", project_id=source_environment.project_id)
            if current_user:
                new_environment.created_by = current_user.id
                new_environment.updated_by = current_user.id

            db.session.add(new_environment)
            db.session.flush()  # 获取新环境的ID

            # 复制参数
            source_parameters = EnvironmentParameter.query.filter_by(environment_id=environment_id,
                is_active=True).all()

            for param in source_parameters:
                new_param = EnvironmentParameter(environment_id=new_environment.id, param_key=param.param_key,
                    param_value=param.param_value, description=param.description)
                if current_user:
                    new_param.created_by = current_user.id
                    new_param.updated_by = current_user.id
                db.session.add(new_param)

            # 更新参数计数
            EnvironmentService._update_environment_parameter_count(new_environment.id)

            db.session.commit()

            return new_environment.to_dict()

        except IntegrityError as e:
            db.session.rollback()
            if 'uq_environment_name' in str(e.orig):
                raise APIException(f"环境名称 '{new_name}' 已存在", 409, {'name': new_name})
            else:
                raise APIException('复制失败', 500, {'details': str(e.orig)})

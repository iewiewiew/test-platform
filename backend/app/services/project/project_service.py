#!/usr/bin/env python
# -*- coding:utf-8 -*-

"""
@author       weimenghua
@time         2025/10/1 19:12
@description
"""

from ...core.database import db
from ...core.exceptions import APIException
from ...models.mock.mock_model import Mock
from ...models.project.project_model import Project


class ProjectService:
    """项目服务层"""

    @staticmethod
    def get_all_projects():
        """获取所有项目"""
        projects = Project.query.all()
        return [{'id': p.id, 'name': p.name, 'description': p.description, 'mock_api_count': len(p.mock_apis),
            'created_at': p.created_at.isoformat(), 'updated_at': p.updated_at.isoformat()} for p in projects]

    @staticmethod
    def get_projects_by_pages(page, per_page, name):
        """分页获取项目列表"""
        query = Project.query
        if name:
            query = query.filter(Project.name.like(f'%{name}%'))

        pagination = query.order_by(Project.id.desc()).paginate(page=page, per_page=per_page)
        return {'data': [p.to_dict() for p in pagination.items], 'total': pagination.total}

    @staticmethod
    def get_project_by_id(project_id):
        """根据 ID 获取项目"""
        project = Project.query.get_or_404(project_id)
        return project.to_dict()

    @staticmethod
    def create_project(data, current_user=None):
        """创建项目"""
        # 检查项目名称是否已存在
        if Project.query.filter_by(name=data['name']).first():
            raise APIException('项目名称已存在', 409)

        project = Project(name=data['name'], description=data.get('description', ''))
        if current_user:
            project.created_by = current_user.id
            project.updated_by = current_user.id
        db.session.add(project)
        db.session.commit()

        return project.to_dict()

    @staticmethod
    def update_project(project_id, data, current_user=None):
        """更新项目"""
        project = Project.query.get_or_404(project_id)

        from ..core.exceptions import APIException
        # 检查项目名称是否与其他项目冲突
        if 'name' in data and data['name'] != project.name:
            if Project.query.filter(Project.name == data['name'], Project.id != project_id).first():
                raise APIException('项目名称已存在', 409)
            project.name = data['name']

        if 'description' in data:
            project.description = data['description']
        
        if current_user:
            project.updated_by = current_user.id

        db.session.commit()
        return project.to_dict()

    @staticmethod
    def delete_project(project_id):
        """删除项目"""
        project = Project.query.get_or_404(project_id)
        db.session.delete(project)
        db.session.commit()

    @staticmethod
    def get_project_mock_apis(project_id):
        """获取项目的 Mock API 列表"""
        # 验证项目是否存在
        Project.query.get_or_404(project_id)
        mock_apis = Mock.query.filter_by(project_id=project_id).all()
        return [api.to_dict() for api in mock_apis]

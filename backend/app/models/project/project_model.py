#!/usr/bin/env python
# -*- coding:utf-8 -*-

"""
@author       weimenghua
@time         2025/7/30 17:47
@description  项目实体类
"""

from ...core.database import db
from ...models.base.base_model import BaseModel


class Project(BaseModel):
    """项目模型"""
    __tablename__ = 'projects'

    name = db.Column(db.String(100), nullable=False, unique=True, comment='项目名称')
    description = db.Column(db.Text, comment='项目描述')

    # 与Mock的关联关系
    mock = db.relationship('Mock', backref='projects', lazy=True, cascade='all, delete-orphan')

    def to_dict(self):
        """
        将项目对象转换为字典

        Returns:
            dict: 项目数据的字典表示
        """
        result = super().to_dict()
        result['mock_count'] = len(self.mock)
        return result

    def __repr__(self):
        return f'<Project {self.name}>'

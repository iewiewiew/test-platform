#!/usr/bin/env python
# -*- coding:utf-8 -*-

"""
@author       weimenghua
@time         2025/7/30 17:47
@description  Mock实体类
"""

from sqlalchemy import UniqueConstraint

from ...core.database import db
from ...models.base.base_model import BaseModel


class Mock(BaseModel):
    """Mock模型"""
    __tablename__ = 'mocks'

    __table_args__ = (UniqueConstraint('path', 'method', name='uq_path_method'),)

    name = db.Column(db.String(100), nullable=False, comment='Mock名称')
    path = db.Column(db.String(200), unique=False, nullable=False, comment='路径')
    method = db.Column(db.String(10), nullable=False, comment='HTTP方法：GET, POST, PUT, DELETE')
    response_status = db.Column(db.Integer, nullable=False, comment='响应状态码')
    response_body = db.Column(db.Text, nullable=False, comment='响应体')
    response_delay = db.Column(db.Integer, default=0, comment='响应延迟（毫秒）')
    description = db.Column(db.Text, comment='描述')
    project_id = db.Column(db.Integer, db.ForeignKey('projects.id'), nullable=True, comment='项目ID')

    def to_dict(self):
        """
        将Mock对象转换为字典

        Returns:
            dict: Mock数据的字典表示
        """
        result = super().to_dict()
        result['project_name'] = self.projects.name if self.projects else None
        return result

    def __repr__(self):
        return f'<Mock {self.method} {self.path}>'

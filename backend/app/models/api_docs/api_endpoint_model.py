#!/usr/bin/env python
# -*- coding:utf-8 -*-

"""
@author       weimenghua
@time         2025/8/5 10:27
@description  API端点模型实体类
"""

from ...core.database import db
from ...models.base.base_model import BaseModel


class ApiEndpoint(BaseModel):
    """API端点模型"""
    __tablename__ = 'api_endpoints'

    path = db.Column(db.String(255), nullable=False, comment='API路径')
    method = db.Column(db.String(10), nullable=False, comment='HTTP方法')
    summary = db.Column(db.Text, comment='摘要')
    description = db.Column(db.Text, comment='描述')
    category = db.Column(db.String(100), nullable=False, default='default', comment='分类')
    parent_id = db.Column(db.Integer, db.ForeignKey('api_endpoints.id'), comment='父节点ID')
    
    # 关系
    parameters = db.relationship('ApiParameter', backref='endpoint', lazy=True, cascade='all, delete-orphan')

    def to_dict(self):
        """
        将API端点对象转换为字典

        Returns:
            dict: API端点数据的字典表示
        """
        result = super().to_dict()
        result['parameters_count'] = len(self.parameters)
        return result

    def __repr__(self):
        return f'<ApiEndpoint {self.method} {self.path}>'

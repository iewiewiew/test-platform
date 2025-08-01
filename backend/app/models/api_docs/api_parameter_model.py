#!/usr/bin/env python
# -*- coding:utf-8 -*-

"""
@author       weimenghua
@time         2025/8/5 10:27
@description  API参数模型实体类
"""

from ...core.database import db
from ...models.base.base_model import BaseModel


class ApiParameter(BaseModel):
    """API参数模型"""
    __tablename__ = 'api_parameters'

    endpoint_id = db.Column(db.Integer, db.ForeignKey('api_endpoints.id'), nullable=False, comment='端点ID')
    name = db.Column(db.String(100), nullable=False, comment='参数名称')
    param_type = db.Column(db.String(50), nullable=False, comment='参数类型：query/path/body/header')
    data_type = db.Column(db.String(50), nullable=False, default='string', comment='数据类型')
    required = db.Column(db.Boolean, default=False, comment='是否必填')
    description = db.Column(db.Text, comment='描述')
    example = db.Column(db.String(255), comment='示例值')

    def to_dict(self):
        """
        将API参数对象转换为字典

        Returns:
            dict: API参数数据的字典表示
        """
        # ApiParameter 不需要 created_by/updated_by，只保留基础字段
        result = super().to_dict(exclude_fields=['created_by', 'updated_by', 'is_active'])
        result.pop('creator_name', None)
        result.pop('updater_name', None)
        return result

    def __repr__(self):
        return f'<ApiParameter {self.name} ({self.param_type})>'

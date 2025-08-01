#!/usr/bin/env python
# -*- coding:utf-8 -*-

"""
@author       weimenghua
@time         2025/10/21 10:04
@description  示例实体类
"""

from ...core.database import db
from ...models.base.base_model import BaseModel


class Example(BaseModel):
    """示例模型"""
    __tablename__ = 'examples'

    name = db.Column(db.String(100), nullable=False, comment='名称')
    description = db.Column(db.Text, comment='描述')
    status = db.Column(db.String(20), default='active', comment='状态')

    def to_dict(self):
        """
        将示例对象转换为字典

        Returns:
            dict: 示例数据的字典表示
        """
        result = super().to_dict()
        result['status'] = self.status
        return result

    def __repr__(self):
        return f'<Example {self.name}>'

#!/usr/bin/env python
# -*- coding:utf-8 -*-

"""
@author       weimenghua
@time         2025/1/XX
@description  测试环境实体类
"""

from ...core.database import db
from ...models.base.base_model import BaseModel


class TestEnvironment(BaseModel):
    """测试环境模型"""
    __tablename__ = 'test_environments'

    env_name = db.Column(db.String(100), nullable=False, unique=True, comment='环境名称')
    env_config = db.Column(db.Text, nullable=False, comment='环境配置(JSON格式)')
    description = db.Column(db.Text, comment='描述')

    def to_dict(self):
        """
        将测试环境对象转换为字典

        Returns:
            dict: 测试环境数据的字典表示
        """
        result = super().to_dict()
        return result

    def __repr__(self):
        return f'<TestEnvironment {self.env_name}>'


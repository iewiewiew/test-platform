#!/usr/bin/env python
# -*- coding:utf-8 -*-

"""
@author       weimenghua
@time         2025/1/XX
@description  测试用例实体类
"""

from ...core.database import db
from ...models.base.base_model import BaseModel


class TestCase(BaseModel):
    """测试用例模型"""
    __tablename__ = 'test_cases'

    test_case_id = db.Column(db.String(100), nullable=False, comment='测试用例ID')
    test_module_name = db.Column(db.String(200), nullable=False, comment='测试模块名称')
    test_case_name = db.Column(db.String(200), nullable=False, comment='测试用例名称')
    component_name = db.Column(db.String(200), comment='组件名称')
    request_method = db.Column(db.String(10), nullable=False, comment='请求方法')
    path = db.Column(db.String(500), nullable=False, comment='请求路径')
    request_body = db.Column(db.Text, comment='请求体')
    request_param = db.Column(db.Text, comment='请求参数')
    response_body = db.Column(db.Text, comment='响应体')
    assert_status = db.Column(db.String(100), comment='断言状态码')
    assert_value = db.Column(db.Text, comment='断言值')
    pytest_annotation = db.Column(db.Text, comment='Pytest注解')
    is_skip = db.Column(db.String(10), default='no', comment='是否跳过')
    file_path = db.Column(db.String(500), comment='文件路径')

    def to_dict(self):
        """
        将测试用例对象转换为字典

        Returns:
            dict: 测试用例数据的字典表示
        """
        result = super().to_dict()
        return result

    def __repr__(self):
        return f'<TestCase {self.test_case_id}: {self.test_case_name}>'


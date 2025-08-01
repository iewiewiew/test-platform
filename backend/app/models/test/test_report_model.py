#!/usr/bin/env python
# -*- coding:utf-8 -*-

"""
@author       weimenghua
@time         2025/1/XX
@description  测试报告实体类
"""

from ...core.database import db
from ...models.base.base_model import BaseModel


class TestReport(BaseModel):
    """测试报告模型"""
    __tablename__ = 'test_reports'

    report_name = db.Column(db.String(200), nullable=False, comment='报告名称')
    report_path = db.Column(db.String(500), nullable=False, comment='报告路径')
    report_type = db.Column(db.String(50), default='pytest', comment='报告类型')
    execution_module = db.Column(db.String(100), comment='执行模块')
    execution_component = db.Column(db.String(100), comment='执行组件')
    execution_environment = db.Column(db.String(100), comment='执行环境')
    total_tests = db.Column(db.Integer, default=0, comment='总测试数')
    passed_tests = db.Column(db.Integer, default=0, comment='通过测试数')
    failed_tests = db.Column(db.Integer, default=0, comment='失败测试数')
    skipped_tests = db.Column(db.Integer, default=0, comment='跳过测试数')
    error_tests = db.Column(db.Integer, default=0, comment='错误测试数')
    duration = db.Column(db.Float, default=0.0, comment='执行时长(秒)')
    report_data = db.Column(db.Text, comment='报告数据(JSON格式)')
    pytest_result = db.Column(db.Text, comment='Pytest执行结果(JSON格式，包含stdout和stderr)')
    test_file_path = db.Column(db.String(500), comment='测试文件路径')
    test_file_name = db.Column(db.String(200), comment='测试文件名称')
    status = db.Column(db.String(20), default='pending', comment='状态: pending, success, failed')

    def to_dict(self):
        """
        将测试报告对象转换为字典

        Returns:
            dict: 测试报告数据的字典表示
        """
        result = super().to_dict()
        # 计算成功率
        if self.total_tests > 0:
            result['success_rate'] = round((self.passed_tests / self.total_tests) * 100, 2)
        else:
            result['success_rate'] = 0.0
        return result

    def __repr__(self):
        return f'<TestReport {self.report_name}>'


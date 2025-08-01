#!/usr/bin/env python
# -*- coding:utf-8 -*-

"""
@author       weimenghua
@time         2025/10/22 08:54
@description  SQL模板和查询历史实体类
"""

from ...core.database import db
from ...models.base.base_model import BaseModel


class SQLTemplate(BaseModel):
    """SQL模板模型"""
    __tablename__ = 'sql_templates'

    name = db.Column(db.String(100), nullable=False, comment='模板名称')
    description = db.Column(db.Text, comment='描述')
    sql_content = db.Column(db.Text, nullable=False, comment='SQL内容')
    category = db.Column(db.String(50), nullable=False, comment='分类')

    def __repr__(self):
        return f'<SQLTemplate {self.name}>'


class QueryHistory(BaseModel):
    """查询历史模型"""
    __tablename__ = 'query_histories'

    sql_query = db.Column(db.Text, nullable=False, comment='SQL查询语句')
    execution_time = db.Column(db.Float, comment='执行时间（秒）')
    success = db.Column(db.Boolean, default=True, comment='是否成功')
    error_message = db.Column(db.Text, comment='错误信息')
    connection_id = db.Column(db.Integer, db.ForeignKey('database_connections.id'), nullable=True, comment='连接ID')

    def to_dict(self):
        """
        将查询历史对象转换为字典

        Returns:
            dict: 查询历史数据的字典表示
        """
        result = super().to_dict()
        # QueryHistory 不需要 updated_at 和 updated_by，只保留 created_at
        result.pop('updated_at', None)
        result.pop('updated_by', None)
        result.pop('updater_name', None)
        return result

    def __repr__(self):
        return f'<QueryHistory {self.id}>'

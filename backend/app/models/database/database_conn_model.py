#!/usr/bin/env python
# -*- coding:utf-8 -*-

"""
@author       weimenghua
@time         2025/01/26
@description  数据库连接实体类
"""

from ...core.database import db
from ...models.base.base_model import BaseModel


class DatabaseConnection(BaseModel):
    """数据库连接模型"""
    __tablename__ = 'database_connections'

    name = db.Column(db.String(100), nullable=False, comment='连接名称')
    host = db.Column(db.String(255), nullable=False, comment='数据库主机')
    port = db.Column(db.Integer, nullable=False, default=3306, comment='数据库端口（MySQL默认3306，Redis默认6379）')
    database = db.Column(db.String(100), nullable=True, comment='数据库名称（Redis 不需要）')
    username = db.Column(db.String(100), nullable=True, comment='用户名（Redis 可能不需要）')
    password = db.Column(db.String(255), nullable=True, comment='密码（Redis 可能不需要）')
    driver = db.Column(db.String(50), nullable=False, default='mysql', comment='数据库驱动')
    charset = db.Column(db.String(50), default='utf8mb4', comment='字符集')
    description = db.Column(db.Text, comment='描述')

    def to_dict(self, exclude_password=True, exclude_fields=None):
        """转换为字典，默认隐藏密码"""
        if exclude_fields is None:
            exclude_fields = []
        if exclude_password:
            exclude_fields.append('password')
        
        result = super().to_dict(exclude_fields=exclude_fields)
        
        # 格式化时间为字符串，去掉时区信息，直接显示本地时间
        if 'created_at' in result and result['created_at']:
            result['created_at'] = result['created_at'].replace('T', ' ').split('.')[0]
        if 'updated_at' in result and result['updated_at']:
            result['updated_at'] = result['updated_at'].replace('T', ' ').split('.')[0]
        
        if exclude_password and 'password' not in result:
            result['password'] = '******'
        
        return result

    def get_connection_string(self):
        """获取数据库连接字符串"""
        driver = (self.driver or 'mysql').lower()
        if driver == 'redis':
            # Redis 连接字符串格式: redis://[:password@]host:port[/db]
            if self.password:
                return f"redis://:{self.password}@{self.host}:{self.port}/{self.database or 0}"
            else:
                return f"redis://{self.host}:{self.port}/{self.database or 0}"
        elif driver in ('mysql', 'pymysql'):
            dialect = 'mysql+pymysql'
        elif driver in ('mysqlconnector', 'mysql+mysqlconnector'):
            dialect = 'mysql+mysqlconnector'
        elif driver in ('postgresql', 'postgres'):
            dialect = 'postgresql'
        else:
            # 默认回退到 PyMySQL 以避免 MySQLdb 依赖
            dialect = 'mysql+pymysql'

        return f"{dialect}://{self.username}:{self.password}@{self.host}:{self.port}/{self.database}?charset={self.charset}"

    def __repr__(self):
        return f'<DatabaseConnection {self.name}>'

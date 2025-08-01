#!/usr/bin/env python
# -*- coding:utf-8 -*-

"""
@author       weimenghua
@time         2025/10/19 17:10
@description  服务器信息实体类
"""

from ...core.database import db
from ...models.base.base_model import BaseModel


class LinuxInfo(BaseModel):
    """服务器信息模型"""
    __tablename__ = 'linux_servers'

    server_name = db.Column(db.String(100), nullable=False, comment='服务器名称')
    host = db.Column(db.String(100), nullable=False, comment='主机地址')
    port = db.Column(db.Integer, default=22, comment='端口号')
    username = db.Column(db.String(50), nullable=False, comment='用户名')
    password = db.Column(db.String(200), comment='密码')
    private_key = db.Column(db.Text, comment='私钥')
    description = db.Column(db.Text, comment='描述')

    def __repr__(self):
        return f'<LinuxInfo {self.server_name}>'

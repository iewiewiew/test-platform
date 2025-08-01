#!/usr/bin/env python
# -*- coding:utf-8 -*-

"""
@author       weimenghua
@time         2025/01/XX XX:XX
@description  操作日志模型
"""

from sqlalchemy import or_
from ...core.database import db, datetime, tz_beijing
from ...models.base.base_model import BaseModel


class OperationLog(BaseModel):
    __tablename__ = 'operation_logs'

    # 用户信息
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True, comment='用户ID')
    username = db.Column(db.String(80), nullable=False, index=True, comment='用户名')
    
    # 操作信息
    operation_type = db.Column(db.String(50), nullable=False, index=True, comment='操作类型: login/create/update/delete/query等')
    operation_module = db.Column(db.String(50), nullable=True, comment='操作模块: user/role/project等')
    operation_desc = db.Column(db.String(255), nullable=True, comment='操作描述')
    
    # 请求信息
    request_ip = db.Column(db.String(50), nullable=True, comment='请求IP')
    user_agent = db.Column(db.String(500), nullable=True, comment='用户代理')
    operation_time = db.Column(db.DateTime, default=lambda: datetime.now(tz_beijing), nullable=False, comment='操作时间')
    
    # 接口信息
    api_path = db.Column(db.String(255), nullable=True, comment='访问接口路径')
    request_method = db.Column(db.String(10), nullable=True, comment='请求方法')
    
    # 操作结果
    operation_status = db.Column(db.String(20), nullable=False, default='success', comment='操作状态: success/failed')
    status_code = db.Column(db.Integer, nullable=True, comment='响应状态码')
    failure_reason = db.Column(db.String(500), nullable=True, comment='失败原因')
    
    # 操作详情（JSON格式存储）
    operation_data = db.Column(db.Text, nullable=True, comment='操作数据详情')
    
    # 关联关系
    user = db.relationship('User', foreign_keys=[user_id], lazy='select', uselist=False)

    def to_dict(self):
        """
        转换为字典格式，用于JSON序列化
        """
        import json
        operation_data_dict = None
        
        if self.operation_data:
            try:
                operation_data_dict = json.loads(self.operation_data)
            except:
                operation_data_dict = self.operation_data
        
        return {
            'id': self.id,
            'user_id': self.user_id,
            'username': self.username,
            'operation_type': self.operation_type,
            'operation_module': self.operation_module,
            'operation_desc': self.operation_desc,
            'request_ip': self.request_ip,
            'user_agent': self.user_agent,
            'operation_time': self.operation_time.isoformat() if self.operation_time else None,
            'api_path': self.api_path,
            'request_method': self.request_method,
            'operation_status': self.operation_status,
            'status_code': self.status_code,
            'failure_reason': self.failure_reason,
            'operation_data': operation_data_dict,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }

    def __repr__(self):
        return f'<OperationLog {self.username} {self.operation_type} {self.operation_time}>'


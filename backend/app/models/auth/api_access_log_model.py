#!/usr/bin/env python
# -*- coding:utf-8 -*-

"""
@author       weimenghua
@time         2025/01/XX XX:XX
@description  API访问日志模型
"""

from sqlalchemy import or_
from ...core.database import db, datetime, tz_beijing
from ...models.base.base_model import BaseModel


class ApiAccessLog(BaseModel):
    __tablename__ = 'api_access_logs'

    # 用户信息
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True, comment='用户ID')
    username = db.Column(db.String(80), nullable=True, index=True, comment='用户名')
    
    # 访问信息
    access_ip = db.Column(db.String(50), nullable=True, comment='访问IP')
    user_agent = db.Column(db.String(500), nullable=True, comment='用户代理')
    access_time = db.Column(db.DateTime, default=lambda: datetime.now(tz_beijing), nullable=False, comment='访问时间')
    
    # 接口信息
    api_path = db.Column(db.String(255), nullable=False, index=True, comment='访问接口路径')
    request_method = db.Column(db.String(10), nullable=False, comment='请求方法')
    endpoint = db.Column(db.String(255), nullable=True, comment='端点名称')
    
    # 响应信息
    status_code = db.Column(db.Integer, nullable=True, comment='响应状态码')
    response_time = db.Column(db.Float, nullable=True, comment='响应时间(秒)')
    
    # 请求参数（JSON格式存储）
    query_params = db.Column(db.Text, nullable=True, comment='查询参数')
    request_body = db.Column(db.Text, nullable=True, comment='请求体')
    
    # 关联关系
    user = db.relationship('User', foreign_keys=[user_id], lazy='select', uselist=False)

    def to_dict(self):
        """
        转换为字典格式，用于JSON序列化
        """
        import json
        query_params_dict = None
        request_body_dict = None
        
        if self.query_params:
            try:
                query_params_dict = json.loads(self.query_params)
            except:
                query_params_dict = self.query_params
        
        if self.request_body:
            try:
                request_body_dict = json.loads(self.request_body)
            except:
                request_body_dict = self.request_body
        
        return {
            'id': self.id,
            'user_id': self.user_id,
            'username': self.username,
            'access_ip': self.access_ip,
            'user_agent': self.user_agent,
            'access_time': self.access_time.isoformat() if self.access_time else None,
            'api_path': self.api_path,
            'request_method': self.request_method,
            'endpoint': self.endpoint,
            'status_code': self.status_code,
            'response_time': self.response_time,
            'query_params': query_params_dict,
            'request_body': request_body_dict,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }

    def __repr__(self):
        return f'<ApiAccessLog {self.username} {self.api_path} {self.access_time}>'


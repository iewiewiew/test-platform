#!/usr/bin/env python
# -*- coding:utf-8 -*-

"""
@author       weimenghua
@time         2025/7/30 17:47
@description  环境配置实体类
"""

from ...core.database import db
from ...models.base.base_model import BaseModel


class Environment(BaseModel):
    """环境配置模型"""
    __tablename__ = 'environments'

    name = db.Column(db.String(100), nullable=False, comment='环境名称')
    base_url = db.Column(db.String(500), nullable=False, comment='基础URL')
    username = db.Column(db.String(100), comment='用户名')
    password = db.Column(db.String(500), comment='密码')
    description = db.Column(db.Text, comment='描述')
    parameter_count = db.Column(db.Integer, default=0, comment='参数数量')
    server_id = db.Column(db.Integer, db.ForeignKey('linux_servers.id'), nullable=True, comment='关联服务器ID')
    
    # 关联关系
    parameters = db.relationship('EnvironmentParameter', backref='environments', lazy=True)
    server = db.relationship('LinuxInfo', foreign_keys=[server_id], lazy=True)

    def to_dict(self):
        """
        将环境对象转换为字典

        Returns:
            dict: 环境数据的字典表示
        """
        result = super().to_dict()
        server_info = None
        if self.server:
            server_info = {
                'id': self.server.id,
                'server_name': self.server.server_name,
                'host': self.server.host
            }
        
        result['username'] = self.username or ''
        result['password'] = self.password or ''
        result['description'] = self.description or ''
        result['server'] = server_info
        return result

    def delete(self, soft_delete=True):
        """
        删除实例

        Args:
            soft_delete: 是否软删除（默认True）
        """
        try:
            if soft_delete:
                self.is_active = False
                db.session.commit()
            else:
                db.session.delete(self)
                db.session.commit()
            return True
        except Exception as e:
            db.session.rollback()
            print(f"删除失败: {e}")
            return False

    def __repr__(self):
        return f'<Environment {self.name}>'


class EnvironmentParameter(BaseModel):
    """环境参数模型"""
    __tablename__ = 'environment_parameters'

    environment_id = db.Column(db.Integer, db.ForeignKey('environments.id'), nullable=False, comment='环境ID')
    param_key = db.Column(db.String(100), nullable=False, comment='参数键')
    param_value = db.Column(db.Text, nullable=False, comment='参数值')
    description = db.Column(db.String(200), comment='描述')

    def to_dict(self):
        """
        将环境参数对象转换为字典

        Returns:
            dict: 环境参数数据的字典表示
        """
        result = super().to_dict()
        result['description'] = self.description or ''
        return result

    def delete(self, soft_delete=True):
        """
        删除实例

        Args:
            soft_delete: 是否软删除（默认True）
        """
        try:
            if soft_delete:
                self.is_active = False
                db.session.commit()
            else:
                db.session.delete(self)
                db.session.commit()
            return True
        except Exception as e:
            db.session.rollback()
            print(f"删除失败: {e}")
            return False

    def __repr__(self):
        return f'<EnvironmentParameter {self.param_key}>'

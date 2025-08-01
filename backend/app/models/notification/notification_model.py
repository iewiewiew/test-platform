#!/usr/bin/env python
# -*- coding:utf-8 -*-

"""
@author       weimenghua
@time         2025/1/XX
@description  消息通知实体类
"""

from ...core.database import db
from ...models.base.base_model import BaseModel


class Notification(BaseModel):
    """消息通知模型"""
    __tablename__ = 'notifications'

    name = db.Column(db.String(100), nullable=False, comment='通知名称')
    notification_type = db.Column(db.String(50), nullable=False, comment='通知类型: feishu, dingtalk, wechat_work, custom')
    webhook_url = db.Column(db.String(500), nullable=False, comment='Webhook URL')
    secret = db.Column(db.String(200), nullable=True, comment='密钥（用于签名验证）')
    description = db.Column(db.Text, comment='描述')
    is_enabled = db.Column(db.Boolean, default=True, nullable=False, comment='是否启用')
    config = db.Column(db.JSON, nullable=True, comment='额外配置（JSON格式）')

    def to_dict(self):
        """
        将通知对象转换为字典

        Returns:
            dict: 通知数据的字典表示
        """
        result = super().to_dict()
        return result

    def __repr__(self):
        return f'<Notification {self.name}>'


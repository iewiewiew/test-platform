#!/usr/bin/env python
# -*- coding:utf-8 -*-

"""
@author       weimenghua
@time         2025/1/XX
@description  消息通知服务层
"""

from ...core.database import db
from ...core.exceptions import APIException
from ...models.notification.notification_model import Notification


class NotificationService:
    """消息通知服务层"""

    @staticmethod
    def get_all_notifications():
        """获取所有通知配置"""
        notifications = Notification.query.filter_by(is_active=True).all()
        return [n.to_dict() for n in notifications]

    @staticmethod
    def get_notifications_by_pages(page, per_page, name=None, notification_type=None):
        """分页获取通知列表"""
        query = Notification.query.filter_by(is_active=True)
        
        if name:
            query = query.filter(Notification.name.like(f'%{name}%'))
        
        if notification_type:
            query = query.filter(Notification.notification_type == notification_type)

        pagination = query.order_by(Notification.id.desc()).paginate(page=page, per_page=per_page, error_out=False)
        return {
            'data': [n.to_dict() for n in pagination.items],
            'total': pagination.total,
            'current_page': pagination.page,
            'per_page': pagination.per_page
        }

    @staticmethod
    def get_notification_by_id(notification_id):
        """根据 ID 获取通知配置"""
        notification = Notification.query.get_or_404(notification_id)
        return notification.to_dict()

    @staticmethod
    def create_notification(data, current_user=None):
        """创建通知配置"""
        # 检查通知名称是否已存在
        if Notification.query.filter_by(name=data['name'], is_active=True).first():
            raise APIException('通知名称已存在', 409)

        # 验证通知类型
        valid_types = ['feishu', 'dingtalk', 'wechat_work', 'custom']
        if data.get('notification_type') not in valid_types:
            raise APIException(f'通知类型必须是: {", ".join(valid_types)}', 400)

        notification = Notification(
            name=data['name'],
            notification_type=data['notification_type'],
            webhook_url=data['webhook_url'],
            secret=data.get('secret'),
            description=data.get('description', ''),
            is_enabled=data.get('is_enabled', True),
            config=data.get('config')
        )
        
        if current_user:
            notification.created_by = current_user.id
            notification.updated_by = current_user.id
        
        db.session.add(notification)
        db.session.commit()

        return notification.to_dict()

    @staticmethod
    def update_notification(notification_id, data, current_user=None):
        """更新通知配置"""
        notification = Notification.query.get_or_404(notification_id)

        # 检查通知名称是否与其他通知冲突
        if 'name' in data and data['name'] != notification.name:
            if Notification.query.filter(
                Notification.name == data['name'],
                Notification.id != notification_id,
                Notification.is_active == True
            ).first():
                raise APIException('通知名称已存在', 409)
            notification.name = data['name']

        if 'notification_type' in data:
            valid_types = ['feishu', 'dingtalk', 'wechat_work', 'custom']
            if data['notification_type'] not in valid_types:
                raise APIException(f'通知类型必须是: {", ".join(valid_types)}', 400)
            notification.notification_type = data['notification_type']

        if 'webhook_url' in data:
            notification.webhook_url = data['webhook_url']
        
        if 'secret' in data:
            notification.secret = data['secret']
        
        if 'description' in data:
            notification.description = data['description']
        
        if 'is_enabled' in data:
            notification.is_enabled = data['is_enabled']
        
        if 'config' in data:
            notification.config = data['config']
        
        if current_user:
            notification.updated_by = current_user.id

        db.session.commit()
        return notification.to_dict()

    @staticmethod
    def delete_notification(notification_id):
        """删除通知配置（软删除）"""
        notification = Notification.query.get_or_404(notification_id)
        notification.is_active = False
        db.session.commit()

    @staticmethod
    def get_enabled_notifications():
        """获取所有启用的通知配置"""
        notifications = Notification.query.filter_by(is_active=True, is_enabled=True).all()
        return [n.to_dict() for n in notifications]


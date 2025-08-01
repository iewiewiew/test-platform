#!/usr/bin/env python
# -*- coding:utf-8 -*-

"""
@author       weimenghua
@time         2025/1/XX
@description  消息通知路由
"""

from flask import Blueprint, request, jsonify, g

from ...services.notification.notification_service import NotificationService
from ...services.notification.notification_sender import NotificationSender
from ...core.exceptions import APIException

notification_bp = Blueprint('notification', __name__)


@notification_bp.route('/notifications', methods=['GET'])
def get_notifications():
    """分页获取通知列表"""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        name = request.args.get('name')
        notification_type = request.args.get('notification_type')
        
        result = NotificationService.get_notifications_by_pages(page, per_page, name, notification_type)
        return jsonify(result)
    except APIException as e:
        return jsonify({'error': e.message, 'payload': e.payload}), e.status_code
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@notification_bp.route('/notifications/all', methods=['GET'])
def get_all_notifications():
    """获取所有通知配置"""
    try:
        notifications = NotificationService.get_all_notifications()
        return jsonify(notifications)
    except APIException as e:
        return jsonify({'error': e.message, 'payload': e.payload}), e.status_code
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@notification_bp.route('/notifications/<int:notification_id>', methods=['GET'])
def get_notification_by_id(notification_id):
    """根据 ID 获取通知配置"""
    try:
        notification = NotificationService.get_notification_by_id(notification_id)
        return jsonify(notification)
    except APIException as e:
        return jsonify({'error': e.message, 'payload': e.payload}), e.status_code
    except Exception as e:
        return jsonify({'error': str(e)}), 404


@notification_bp.route('/notifications', methods=['POST'])
def create_notification():
    """创建通知配置"""
    try:
        data = request.get_json()
        if not data or 'name' not in data or 'notification_type' not in data or 'webhook_url' not in data:
            return jsonify({'error': 'Missing required fields: name, notification_type, webhook_url'}), 400

        current_user = getattr(g, 'current_user', None)
        notification = NotificationService.create_notification(data, current_user)
        return jsonify(notification), 201
    except APIException as e:
        return jsonify({'error': e.message, 'payload': e.payload}), e.status_code
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@notification_bp.route('/notifications/<int:notification_id>', methods=['PUT'])
def update_notification(notification_id):
    """更新通知配置"""
    try:
        data = request.get_json()
        current_user = getattr(g, 'current_user', None)
        notification = NotificationService.update_notification(notification_id, data, current_user)
        return jsonify(notification)
    except APIException as e:
        return jsonify({'error': e.message, 'payload': e.payload}), e.status_code
    except Exception as e:
        return jsonify({'error': str(e)}), 404


@notification_bp.route('/notifications/<int:notification_id>', methods=['DELETE'])
def delete_notification(notification_id):
    """删除通知配置"""
    try:
        NotificationService.delete_notification(notification_id)
        return jsonify({'message': 'Notification deleted'})
    except APIException as e:
        return jsonify({'error': e.message, 'payload': e.payload}), e.status_code
    except Exception as e:
        return jsonify({'error': str(e)}), 404


@notification_bp.route('/notifications/<int:notification_id>/test', methods=['POST'])
def test_notification(notification_id):
    """测试通知配置"""
    try:
        data = request.get_json() or {}
        message = data.get('message', '这是一条测试消息')
        
        result = NotificationSender.send_test_notification(notification_id, message)
        return jsonify(result)
    except APIException as e:
        return jsonify({'error': e.message, 'payload': e.payload}), e.status_code
    except Exception as e:
        return jsonify({'error': str(e)}), 500


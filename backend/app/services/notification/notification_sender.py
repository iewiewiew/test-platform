#!/usr/bin/env python
# -*- coding:utf-8 -*-

"""
@author       weimenghua
@time         2025/1/XX
@description  消息通知发送工具类
"""

import json
import hmac
import hashlib
import base64
import time
import requests
from datetime import datetime
from typing import Dict, Any, Optional

from ...models.notification.notification_model import Notification


class NotificationSender:
    """消息通知发送器"""

    @staticmethod
    def send_test_notification(notification_id: int, message: str) -> Dict[str, Any]:
        """
        发送测试通知
        
        Args:
            notification_id: 通知配置ID
            message: 测试消息内容
            
        Returns:
            dict: 发送结果
        """
        notification = Notification.query.get(notification_id)
        if not notification:
            return {'success': False, 'error': '通知配置不存在'}
        
        if not notification.is_enabled or not notification.is_active:
            return {'success': False, 'error': '通知配置未启用'}
        
        test_data = {
            'title': '测试通知',
            'content': message,
            'timestamp': datetime.now().isoformat()
        }
        
        return NotificationSender.send_notification(notification, test_data)

    @staticmethod
    def send_pytest_result(notification_id: int, test_result: Dict[str, Any]) -> Dict[str, Any]:
        """
        发送Pytest测试结果通知
        
        Args:
            notification_id: 通知配置ID
            test_result: 测试结果数据
            
        Returns:
            dict: 发送结果
        """
        notification = Notification.query.get(notification_id)
        if not notification:
            return {'success': False, 'error': '通知配置不存在'}
        
        if not notification.is_enabled or not notification.is_active:
            return {'success': False, 'error': '通知配置未启用'}
        
        # 构建测试结果消息
        message_data = NotificationSender._build_pytest_message(test_result)
        
        return NotificationSender.send_notification(notification, message_data)

    @staticmethod
    def send_notification(notification: Notification, message_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        发送通知
        
        Args:
            notification: 通知配置对象
            message_data: 消息数据
            
        Returns:
            dict: 发送结果
        """
        try:
            if notification.notification_type == 'feishu':
                return NotificationSender._send_feishu(notification, message_data)
            elif notification.notification_type == 'dingtalk':
                return NotificationSender._send_dingtalk(notification, message_data)
            elif notification.notification_type == 'wechat_work':
                return NotificationSender._send_wechat_work(notification, message_data)
            elif notification.notification_type == 'custom':
                return NotificationSender._send_custom(notification, message_data)
            else:
                return {'success': False, 'error': f'不支持的通知类型: {notification.notification_type}'}
        except Exception as e:
            return {'success': False, 'error': str(e)}

    @staticmethod
    def _build_pytest_message(test_result: Dict[str, Any]) -> Dict[str, Any]:
        """构建Pytest测试结果消息"""
        title = test_result.get('title', 'Pytest测试执行完成')
        component = test_result.get('component_name', '')
        module = test_result.get('module_name', '')
        environment = test_result.get('environment_name', '')
        total = test_result.get('total_tests', 0)
        passed = test_result.get('passed_tests', 0)
        failed = test_result.get('failed_tests', 0)
        skipped = test_result.get('skipped_tests', 0)
        duration = test_result.get('duration', 0)
        success = test_result.get('success', False)
        report_url = test_result.get('report_url', '')
        
        # 构建消息内容
        status_emoji = '✅' if success else '❌'
        status_text = '成功' if success else '失败'
        
        content = f"""
**{title}**

**执行信息：**
- 组件：{component or '全部'}
- 模块：{module or '全部'}
- 环境：{environment or '未知'}

**测试结果：**
- 总用例数：{total}
- 通过：{passed} ✅
- 失败：{failed} ❌
- 跳过：{skipped} ⏭️
- 执行时长：{duration:.2f}秒

**状态：** {status_emoji} {status_text}
"""
        
        if report_url:
            content += f"\n**报告链接：** {report_url}"
        
        return {
            'title': title,
            'content': content.strip(),
            'timestamp': datetime.now().isoformat(),
            'success': success,
            'total': total,
            'passed': passed,
            'failed': failed,
            'skipped': skipped,
            'duration': duration,
            'report_url': report_url
        }

    @staticmethod
    def _send_feishu(notification: Notification, message_data: Dict[str, Any]) -> Dict[str, Any]:
        """发送飞书通知"""
        webhook_url = notification.webhook_url
        
        # 构建飞书消息格式
        content = message_data.get('content', '')
        title = message_data.get('title', '通知')
        
        # 飞书支持Markdown格式
        payload = {
            "msg_type": "interactive",
            "card": {
                "config": {
                    "wide_screen_mode": True
                },
                "header": {
                    "title": {
                        "tag": "plain_text",
                        "content": title
                    },
                    "template": "blue" if message_data.get('success', True) else "red"
                },
                "elements": [
                    {
                        "tag": "div",
                        "text": {
                            "tag": "lark_md",
                            "content": content
                        }
                    }
                ]
            }
        }
        
        # 如果有签名密钥，需要添加签名
        if notification.secret:
            timestamp = str(int(time.time()))
            string_to_sign = f'{timestamp}\n{notification.secret}'
            sign = base64.b64encode(
                hmac.new(
                    string_to_sign.encode('utf-8'),
                    notification.secret.encode('utf-8'),
                    digestmod=hashlib.sha256
                ).digest()
            ).decode('utf-8')
            payload['timestamp'] = timestamp
            payload['sign'] = sign
        
        try:
            response = requests.post(webhook_url, json=payload, timeout=10)
            response.raise_for_status()
            result = response.json()
            if result.get('code') == 0:
                return {'success': True, 'message': '发送成功'}
            else:
                return {'success': False, 'error': result.get('msg', '发送失败')}
        except requests.exceptions.RequestException as e:
            return {'success': False, 'error': f'请求失败: {str(e)}'}

    @staticmethod
    def _send_dingtalk(notification: Notification, message_data: Dict[str, Any]) -> Dict[str, Any]:
        """发送钉钉通知"""
        webhook_url = notification.webhook_url
        
        # 构建钉钉消息格式
        content = message_data.get('content', '')
        title = message_data.get('title', '通知')
        
        payload = {
            "msgtype": "markdown",
            "markdown": {
                "title": title,
                "text": f"## {title}\n\n{content}"
            }
        }
        
        # 如果有签名密钥，需要添加签名
        if notification.secret:
            timestamp = str(round(time.time() * 1000))
            string_to_sign = f'{timestamp}\n{notification.secret}'
            sign = base64.b64encode(
                hmac.new(
                    notification.secret.encode('utf-8'),
                    string_to_sign.encode('utf-8'),
                    digestmod=hashlib.sha256
                ).digest()
            ).decode('utf-8')
            webhook_url = f"{webhook_url}&timestamp={timestamp}&sign={sign}"
        
        try:
            response = requests.post(webhook_url, json=payload, timeout=10)
            response.raise_for_status()
            result = response.json()
            if result.get('errcode') == 0:
                return {'success': True, 'message': '发送成功'}
            else:
                return {'success': False, 'error': result.get('errmsg', '发送失败')}
        except requests.exceptions.RequestException as e:
            return {'success': False, 'error': f'请求失败: {str(e)}'}

    @staticmethod
    def _send_wechat_work(notification: Notification, message_data: Dict[str, Any]) -> Dict[str, Any]:
        """发送企业微信通知"""
        webhook_url = notification.webhook_url
        
        # 构建企业微信消息格式
        content = message_data.get('content', '')
        title = message_data.get('title', '通知')
        
        payload = {
            "msgtype": "markdown",
            "markdown": {
                "content": f"# {title}\n{content}"
            }
        }
        
        try:
            response = requests.post(webhook_url, json=payload, timeout=10)
            response.raise_for_status()
            result = response.json()
            if result.get('errcode') == 0:
                return {'success': True, 'message': '发送成功'}
            else:
                return {'success': False, 'error': result.get('errmsg', '发送失败')}
        except requests.exceptions.RequestException as e:
            return {'success': False, 'error': f'请求失败: {str(e)}'}

    @staticmethod
    def _send_custom(notification: Notification, message_data: Dict[str, Any]) -> Dict[str, Any]:
        """发送自定义通知"""
        webhook_url = notification.webhook_url
        
        # 使用配置中的自定义格式，如果没有则使用默认格式
        config = notification.config or {}
        payload_format = config.get('payload_format', 'default')
        
        if payload_format == 'default':
            payload = {
                'title': message_data.get('title', '通知'),
                'content': message_data.get('content', ''),
                'timestamp': message_data.get('timestamp', datetime.now().isoformat()),
                'data': message_data
            }
        else:
            # 使用自定义格式
            payload = message_data
        
        # 如果有自定义headers
        headers = config.get('headers', {})
        if not isinstance(headers, dict):
            headers = {}
        
        try:
            response = requests.post(
                webhook_url,
                json=payload,
                headers=headers,
                timeout=config.get('timeout', 10)
            )
            response.raise_for_status()
            return {'success': True, 'message': '发送成功', 'response': response.text}
        except requests.exceptions.RequestException as e:
            return {'success': False, 'error': f'请求失败: {str(e)}'}

    @staticmethod
    def send_to_all_enabled(test_result: Dict[str, Any]) -> Dict[str, Any]:
        """
        向所有启用的通知配置发送消息
        
        Args:
            test_result: 测试结果数据
            
        Returns:
            dict: 发送结果汇总
        """
        from .notification_service import NotificationService
        
        notifications = NotificationService.get_enabled_notifications()
        results = []
        
        for notification_data in notifications:
            notification = Notification.query.get(notification_data['id'])
            if notification:
                message_data = NotificationSender._build_pytest_message(test_result)
                result = NotificationSender.send_notification(notification, message_data)
                results.append({
                    'notification_id': notification_data['id'],
                    'notification_name': notification_data['name'],
                    'notification_type': notification_data['notification_type'],
                    'success': result.get('success', False),
                    'error': result.get('error'),
                    'message': result.get('message')
                })
        
        success_count = sum(1 for r in results if r.get('success'))
        total_count = len(results)
        
        return {
            'total': total_count,
            'success': success_count,
            'failed': total_count - success_count,
            'results': results
        }


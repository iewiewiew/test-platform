#!/usr/bin/env python
# -*- coding:utf-8 -*-

"""
@author       weimenghua
@time         2025/01/XX XX:XX
@description  操作日志工具函数
"""

from flask import request, g

from ..services.auth.operation_log_service import OperationLogService


def get_client_ip():
    """获取客户端IP地址"""
    if request.headers.get('X-Forwarded-For'):
        ip = request.headers.get('X-Forwarded-For').split(',')[0].strip()
    elif request.headers.get('X-Real-IP'):
        ip = request.headers.get('X-Real-IP')
    else:
        ip = request.remote_addr
    return ip


def log_operation(operation_type, operation_module, operation_desc, 
                 operation_status='success', status_code=200, 
                 failure_reason=None, operation_data=None):
    """
    记录操作日志的通用函数
    
    Args:
        operation_type: 操作类型 (create/update/delete等)
        operation_module: 操作模块 (user/role/project等)
        operation_desc: 操作描述
        operation_status: 操作状态 (success/failed)
        status_code: HTTP状态码
        failure_reason: 失败原因
        operation_data: 操作数据详情
    """
    try:
        current_user = getattr(g, 'current_user', None)
        user_id = current_user.id if current_user else None
        username = current_user.username if current_user else 'anonymous'
        
        OperationLogService.create_operation_log(
            user_id=user_id,
            username=username,
            operation_type=operation_type,
            operation_module=operation_module,
            operation_desc=operation_desc,
            request_ip=get_client_ip(),
            user_agent=request.headers.get('User-Agent'),
            api_path=request.path,
            request_method=request.method,
            operation_status=operation_status,
            status_code=status_code,
            failure_reason=failure_reason,
            operation_data=operation_data
        )
    except Exception as e:
        # 记录日志失败不影响主流程，但需要打印详细错误以便调试
        import traceback
        print(f"Failed to log operation: {e}")
        print(f"Traceback: {traceback.format_exc()}")


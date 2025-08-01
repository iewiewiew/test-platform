#!/usr/bin/env python
# -*- coding:utf-8 -*-

"""
@author       weimenghua
@time         2025/01/XX XX:XX
@description  操作日志服务
"""

import json
from sqlalchemy import or_, desc
from ...core.database import db, datetime, tz_beijing
from ...models.auth.operation_log_model import OperationLog


class OperationLogService:
    # 操作类型常量
    OPERATION_LOGIN = 'login'
    OPERATION_LOGOUT = 'logout'
    OPERATION_CREATE = 'create'
    OPERATION_UPDATE = 'update'
    OPERATION_DELETE = 'delete'
    OPERATION_QUERY = 'query'
    OPERATION_EXPORT = 'export'
    OPERATION_IMPORT = 'import'
    OPERATION_OTHER = 'other'
    
    # 操作模块常量
    MODULE_USER = 'user'
    MODULE_ROLE = 'role'
    MODULE_PROJECT = 'project'
    MODULE_ENVIRONMENT = 'environment'
    MODULE_TEST = 'test'
    MODULE_MOCK = 'mock'
    MODULE_DATABASE = 'database'
    MODULE_AUTH = 'auth'
    MODULE_OTHER = 'other'

    @staticmethod
    def create_operation_log(user_id=None, username=None, operation_type=None, 
                            operation_module=None, operation_desc=None,
                            request_ip=None, user_agent=None, api_path=None, 
                            request_method=None, operation_status='success',
                            status_code=None, failure_reason=None, operation_data=None):
        """
        创建操作日志

        Args:
            user_id: 用户ID
            username: 用户名
            operation_type: 操作类型
            operation_module: 操作模块
            operation_desc: 操作描述
            request_ip: 请求IP
            user_agent: 用户代理
            api_path: 访问接口路径
            request_method: 请求方法
            operation_status: 操作状态 (success/failed)
            status_code: 响应状态码
            failure_reason: 失败原因
            operation_data: 操作数据详情（字典）

        Returns:
            OperationLog: 创建的操作日志对象
        """
        # 将操作数据转换为JSON字符串
        operation_data_str = None
        if operation_data:
            try:
                operation_data_str = json.dumps(operation_data, ensure_ascii=False)
            except:
                operation_data_str = str(operation_data)
        
        operation_log = OperationLog(
            user_id=user_id,
            username=username or 'anonymous',
            operation_type=operation_type or OperationLogService.OPERATION_OTHER,
            operation_module=operation_module,
            operation_desc=operation_desc,
            request_ip=request_ip,
            user_agent=user_agent,
            api_path=api_path,
            request_method=request_method,
            operation_status=operation_status,
            status_code=status_code,
            failure_reason=failure_reason,
            operation_data=operation_data_str,
            operation_time=datetime.now(tz_beijing)
        )
        
        try:
            db.session.add(operation_log)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            # 记录日志失败不影响主流程，但需要打印详细错误以便调试
            import traceback
            print(f"Failed to create operation log: {e}")
            print(f"Traceback: {traceback.format_exc()}")
        
        return operation_log

    @staticmethod
    def get_all_operation_logs(page=1, per_page=10, search=None, username=None, 
                              operation_type=None, operation_module=None,
                              operation_status=None, start_date=None, end_date=None):
        """
        获取所有操作日志（分页），从 api_access_logs 表获取

        Args:
            page: 页码
            per_page: 每页数量
            search: 搜索关键词（用户名、IP、接口路径）
            username: 用户名筛选
            operation_type: 操作类型筛选（暂不支持，保留接口兼容性）
            operation_module: 操作模块筛选（暂不支持，保留接口兼容性）
            operation_status: 操作状态筛选（根据状态码判断）
            start_date: 开始日期
            end_date: 结束日期

        Returns:
            dict: 包含操作日志列表和分页信息的字典
        """
        from ...models.auth.api_access_log_model import ApiAccessLog
        
        # 查询 api_access_logs
        query = ApiAccessLog.query
        
        # 搜索条件
        if search:
            search_filter = or_(
                ApiAccessLog.username.ilike(f'%{search}%'),
                ApiAccessLog.access_ip.ilike(f'%{search}%'),
                ApiAccessLog.api_path.ilike(f'%{search}%')
            )
            query = query.filter(search_filter)

        # 用户名筛选
        if username:
            query = query.filter(ApiAccessLog.username == username)

        # 操作状态筛选（根据状态码判断）
        if operation_status:
            if operation_status == 'success':
                query = query.filter(ApiAccessLog.status_code < 400)
            elif operation_status == 'failed':
                query = query.filter(ApiAccessLog.status_code >= 400)

        # 日期范围筛选
        if start_date:
            query = query.filter(ApiAccessLog.access_time >= start_date)
        if end_date:
            query = query.filter(ApiAccessLog.access_time <= end_date)

        # 按访问时间倒序排列并分页
        pagination = query.order_by(desc(ApiAccessLog.access_time)).paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        # 根据请求方法和接口路径推断操作类型的辅助函数
        def infer_operation_type(api_path, request_method):
            """根据接口路径和请求方法推断操作类型"""
            api_path_lower = api_path.lower() if api_path else ''
            method_upper = request_method.upper() if request_method else ''
            
            # 登录相关
            if '/login' in api_path_lower or '/auth/login' in api_path_lower:
                return 'login'
            # 登出相关
            if '/logout' in api_path_lower or '/auth/logout' in api_path_lower:
                return 'logout'
            # 根据请求方法推断
            if method_upper == 'POST':
                # POST 可能是创建或登录
                if '/create' in api_path_lower or '/add' in api_path_lower:
                    return 'create'
                return 'create'  # 默认 POST 为创建
            elif method_upper == 'PUT' or method_upper == 'PATCH':
                return 'update'
            elif method_upper == 'DELETE':
                return 'delete'
            elif method_upper == 'GET':
                return 'query'
            else:
                return 'other'
        
        # 将 api_access_logs 转换为与 operation_logs 兼容的格式
        converted_logs = []
        for api_log in pagination.items:
            api_dict = api_log.to_dict()
            # 推断操作类型
            inferred_type = infer_operation_type(api_dict['api_path'], api_dict['request_method'])
            
            # 转换为 operation_log 格式
            converted_log = {
                'id': api_dict['id'],
                'user_id': api_dict['user_id'],
                'username': api_dict['username'],
                'operation_type': inferred_type,
                'operation_module': None,
                'operation_desc': f"API访问: {api_dict['api_path']}",
                'request_ip': api_dict['access_ip'],
                'user_agent': api_dict['user_agent'],
                'operation_time': api_dict['access_time'],  # 使用 access_time
                'api_path': api_dict['api_path'],
                'request_method': api_dict['request_method'],
                'operation_status': 'success' if api_dict['status_code'] and api_dict['status_code'] < 400 else 'failed',
                'status_code': api_dict['status_code'],
                'failure_reason': None,
                'operation_data': None,
                'created_at': api_dict['created_at'],
                'updated_at': api_dict['updated_at']
            }
            converted_logs.append(converted_log)
        
        # 如果指定了操作类型筛选，在转换后的数据中筛选
        if operation_type:
            converted_logs = [log for log in converted_logs if log['operation_type'] == operation_type]
            # 重新计算分页信息
            total = len(converted_logs)
            start = (page - 1) * per_page
            end = start + per_page
            paginated_logs = converted_logs[start:end]
            pages = (total + per_page - 1) // per_page if total > 0 else 0
            
            return {
                'operation_logs': paginated_logs,
                'total': total,
                'pages': pages,
                'current_page': page,
                'per_page': per_page
            }

        return {
            'operation_logs': converted_logs,
            'total': pagination.total,
            'pages': pagination.pages,
            'current_page': page,
            'per_page': per_page
        }

    @staticmethod
    def get_operation_log_by_id(log_id):
        """
        根据ID获取操作日志（从 api_access_logs 表）

        Args:
            log_id: 日志ID

        Returns:
            ApiAccessLog: 操作日志对象，不存在返回None
        """
        from ...models.auth.api_access_log_model import ApiAccessLog
        return ApiAccessLog.query.get(log_id)

    @staticmethod
    def delete_operation_log(log_id):
        """
        删除操作日志（从 api_access_logs 表）

        Args:
            log_id: 日志ID

        Returns:
            bool: 删除成功返回True
        """
        from ...models.auth.api_access_log_model import ApiAccessLog
        log = ApiAccessLog.query.get(log_id)
        if not log:
            return False

        db.session.delete(log)
        db.session.commit()
        return True

    @staticmethod
    def delete_old_logs(days=90):
        """
        删除指定天数之前的旧日志

        Args:
            days: 保留天数，默认90天

        Returns:
            int: 删除的记录数
        """
        from datetime import timedelta
        cutoff_date = datetime.now(tz_beijing) - timedelta(days=days)
        
        deleted_count = OperationLog.query.filter(OperationLog.operation_time < cutoff_date).delete()
        db.session.commit()
        
        return deleted_count


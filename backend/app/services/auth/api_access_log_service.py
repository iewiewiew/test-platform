#!/usr/bin/env python
# -*- coding:utf-8 -*-

"""
@author       weimenghua
@time         2025/01/XX XX:XX
@description  API访问日志服务
"""

import json
from sqlalchemy import or_, desc
from ...core.database import db, datetime, tz_beijing
from ...models.auth.api_access_log_model import ApiAccessLog


class ApiAccessLogService:
    @staticmethod
    def create_api_access_log(user_id=None, username=None, access_ip=None, user_agent=None, 
                             api_path=None, request_method=None, endpoint=None,
                             status_code=None, response_time=None, query_params=None, 
                             request_body=None):
        """
        创建API访问日志

        Args:
            user_id: 用户ID
            username: 用户名
            access_ip: 访问IP
            user_agent: 用户代理
            api_path: 访问接口路径
            request_method: 请求方法
            endpoint: 端点名称
            status_code: 响应状态码
            response_time: 响应时间(秒)
            query_params: 查询参数
            request_body: 请求体

        Returns:
            ApiAccessLog: 创建的API访问日志对象
        """
        # 将字典转换为JSON字符串
        query_params_str = None
        if query_params:
            try:
                query_params_str = json.dumps(query_params, ensure_ascii=False)
            except:
                query_params_str = str(query_params)
        
        request_body_str = None
        if request_body:
            try:
                request_body_str = json.dumps(request_body, ensure_ascii=False)
            except:
                request_body_str = str(request_body)
        
        api_log = ApiAccessLog(
            user_id=user_id,
            username=username or 'anonymous',
            access_ip=access_ip,
            user_agent=user_agent,
            api_path=api_path,
            request_method=request_method,
            endpoint=endpoint,
            status_code=status_code,
            response_time=response_time,
            query_params=query_params_str,
            request_body=request_body_str,
            access_time=datetime.now(tz_beijing)
        )
        
        try:
            db.session.add(api_log)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            # 记录日志失败不影响主流程，只打印错误
            print(f"Failed to create API access log: {e}")
        
        return api_log

    @staticmethod
    def get_all_api_access_logs(page=1, per_page=10, search=None, username=None, 
                                api_path=None, request_method=None, status_code=None,
                                start_date=None, end_date=None):
        """
        获取所有API访问日志（分页）

        Args:
            page: 页码
            per_page: 每页数量
            search: 搜索关键词（用户名、IP、接口路径）
            username: 用户名筛选
            api_path: 接口路径筛选
            request_method: 请求方法筛选
            status_code: 状态码筛选
            start_date: 开始日期
            end_date: 结束日期

        Returns:
            dict: 包含API访问日志列表和分页信息的字典
        """
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

        # 接口路径筛选
        if api_path:
            query = query.filter(ApiAccessLog.api_path.ilike(f'%{api_path}%'))

        # 请求方法筛选
        if request_method:
            query = query.filter(ApiAccessLog.request_method == request_method)

        # 状态码筛选
        if status_code:
            query = query.filter(ApiAccessLog.status_code == status_code)

        # 日期范围筛选
        if start_date:
            query = query.filter(ApiAccessLog.access_time >= start_date)
        if end_date:
            query = query.filter(ApiAccessLog.access_time <= end_date)

        # 按访问时间倒序排列
        pagination = query.order_by(desc(ApiAccessLog.access_time)).paginate(
            page=page, per_page=per_page, error_out=False
        )

        return {
            'api_access_logs': [log.to_dict() for log in pagination.items],
            'total': pagination.total,
            'pages': pagination.pages,
            'current_page': page,
            'per_page': per_page
        }

    @staticmethod
    def get_api_access_log_by_id(log_id):
        """
        根据ID获取API访问日志

        Args:
            log_id: 日志ID

        Returns:
            ApiAccessLog: API访问日志对象，不存在返回None
        """
        return ApiAccessLog.query.get(log_id)

    @staticmethod
    def delete_api_access_log(log_id):
        """
        删除API访问日志

        Args:
            log_id: 日志ID

        Returns:
            bool: 删除成功返回True
        """
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
        
        deleted_count = ApiAccessLog.query.filter(ApiAccessLog.access_time < cutoff_date).delete()
        db.session.commit()
        
        return deleted_count


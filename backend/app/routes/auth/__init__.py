#!/usr/bin/env python
# -*- coding:utf-8 -*-

"""
@author       weimenghua
@time         2025/7/30 17:47
@description  认证授权路由模块
"""

from .auth_routes import auth_bp
from .user_routes import user_bp
from .role_routes import role_bp
from .profile_routes import profile_bp
from .api_access_log_routes import api_access_log_bp
from .operation_log_routes import operation_log_bp

__all__ = ['auth_bp', 'user_bp', 'role_bp', 'profile_bp', 'api_access_log_bp', 'operation_log_bp']



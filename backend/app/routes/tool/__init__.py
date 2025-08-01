#!/usr/bin/env python
# -*- coding:utf-8 -*-

"""
@author       weimenghua
@time         2025/7/30 17:47
@description  工具路由模块
"""

from .linux_info_routes import linux_info_bp
from .script_management_routes import script_management_bp
from .tool_routes import tool_bp
from .mcp_routes import mcp_bp

__all__ = ['linux_info_bp', 'script_management_bp', 'tool_bp', 'mcp_bp']



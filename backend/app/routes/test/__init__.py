#!/usr/bin/env python
# -*- coding:utf-8 -*-

"""
@author       weimenghua
@time         2025/7/30 17:47
@description  测试路由模块
"""

from .test_case_routes import test_case_bp
from .test_environment_routes import test_environment_bp
from .test_report_routes import test_report_bp
from .pytest_executor_routes import pytest_executor_bp

__all__ = ['test_case_bp', 'test_environment_bp', 'test_report_bp', 'pytest_executor_bp']



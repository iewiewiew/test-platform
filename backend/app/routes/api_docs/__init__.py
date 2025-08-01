#!/usr/bin/env python
# -*- coding:utf-8 -*-

"""
@author       weimenghua
@time         2025/7/30 17:47
@description  API文档路由模块
"""

from .api_docs_routes import api_docs_bp
from .docs_routes import docs_bp

__all__ = ['api_docs_bp', 'docs_bp']



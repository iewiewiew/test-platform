# !/usr/bin/env python
# -*- coding:utf-8 -*-

"""
@author       weimenghua
@time         2025/7/30 17:45
@description  配置文件
"""

import os
from datetime import timedelta
from dotenv import load_dotenv

load_dotenv()


class Config:
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-key')
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', 'mysql+mysqlconnector://root:123456@localhost/test_platform?charset=utf8mb4')
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # JWT 配置
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY') or 'jwt-secret-key-change-in-production'
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=24)  # Token 过期时间
    JWT_ALGORITHM = 'HS256'

    # 全局鉴权开关：设置为 False 可快速关闭全局 Token 校验
    REQUIRE_GLOBAL_TOKEN = os.getenv('REQUIRE_GLOBAL_TOKEN', 'true').lower() in ('1', 'true', 'yes')

    # 静态与上传配置
    BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))  # 指向 backend 目录
    STATIC_FOLDER = os.path.join(BASE_DIR, 'static')
    AVATAR_SUBDIR = 'avatars'
    AVATAR_UPLOAD_FOLDER = os.path.join(STATIC_FOLDER, AVATAR_SUBDIR)
    MAX_CONTENT_LENGTH = int(os.getenv('MAX_CONTENT_LENGTH', 5 * 1024 * 1024))  # 5MB
    ALLOWED_IMAGE_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}


class DevelopmentConfig(Config):
    DEBUG = True


class ProductionConfig(Config):
    DEBUG = False


config = {'development': DevelopmentConfig, 'production': ProductionConfig, 'default': DevelopmentConfig}

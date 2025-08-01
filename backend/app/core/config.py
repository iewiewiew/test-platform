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
    """基础配置类"""
    # 应用基础配置
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-key-change-in-production')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # 数据库配置
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', 'mysql+mysqlconnector://root:123456@localhost/test_platform?charset=utf8mb4')
    SQLALCHEMY_ECHO = False  # 是否打印 SQL 语句
    
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
    IMAGE_SUBDIR = 'images'
    IMAGE_UPLOAD_FOLDER = os.path.join(STATIC_FOLDER, IMAGE_SUBDIR)
    MAX_CONTENT_LENGTH = int(os.getenv('MAX_CONTENT_LENGTH', 5 * 1024 * 1024))  # 5MB
    ALLOWED_IMAGE_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}
    
    # 日志配置
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
    
    # 自动迁移配置
    AUTO_MIGRATE = os.getenv('AUTO_MIGRATE', 'true').lower() in ('1', 'true', 'yes')
    
    # CORS 配置
    CORS_ORIGINS = os.getenv('CORS_ORIGINS', '*').split(',')


class DevelopmentConfig(Config):
    """开发环境配置"""
    DEBUG = True
    SQLALCHEMY_ECHO = True  # 开发环境打印 SQL
    LOG_LEVEL = 'DEBUG'
    REQUIRE_GLOBAL_TOKEN = os.getenv('REQUIRE_GLOBAL_TOKEN', 'false').lower() in ('1', 'true', 'yes')  # 开发环境默认关闭
    CORS_ORIGINS = ['*']  # 开发环境允许所有来源


class TestingConfig(Config):
    """测试环境配置"""
    DEBUG = True
    TESTING = True
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', 'mysql+mysqlconnector://root:123456@localhost/test_platform_test?charset=utf8mb4')
    SQLALCHEMY_ECHO = False
    LOG_LEVEL = 'INFO'
    REQUIRE_GLOBAL_TOKEN = True
    # 测试环境可以使用内存数据库或独立的测试数据库
    WTF_CSRF_ENABLED = False  # 测试环境禁用 CSRF


class ProductionConfig(Config):
    """生产环境配置"""
    DEBUG = False
    SQLALCHEMY_ECHO = False
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'WARNING')
    REQUIRE_GLOBAL_TOKEN = True
    # 生产环境必须设置强密钥（在应用启动时检查，而不是类定义时）
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-key-change-in-production')
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY', 'jwt-secret-key-change-in-production')
    # 生产环境限制 CORS 来源
    CORS_ORIGINS = os.getenv('CORS_ORIGINS', '').split(',') if os.getenv('CORS_ORIGINS') else []
    
    @staticmethod
    def validate():
        """验证生产环境必需的配置项"""
        secret_key = os.getenv('SECRET_KEY')
        jwt_secret_key = os.getenv('JWT_SECRET_KEY')
        
        if not secret_key or secret_key == 'dev-key-change-in-production':
            raise ValueError('生产环境必须设置 SECRET_KEY 环境变量')
        if not jwt_secret_key or jwt_secret_key == 'jwt-secret-key-change-in-production':
            raise ValueError('生产环境必须设置 JWT_SECRET_KEY 环境变量')


# 配置字典
config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}


def get_config_name():
    """
    获取配置名称
    从 FLASK_ENV 环境变量获取，如果未设置或无效，默认使用 development
    """
    env = os.getenv('FLASK_ENV', 'development').lower()
    
    # 验证环境名称是否有效
    if env in config:
        return env
    
    # 如果环境变量无效，返回默认值
    return 'development'

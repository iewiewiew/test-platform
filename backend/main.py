# !/usr/bin/env python
# -*- coding:utf-8 -*-

"""
@author       weimenghua
@time         2025/7/30 17:47
@description  启动项目

环境配置说明：
- 开发环境: FLASK_ENV=development
- 测试环境: FLASK_ENV=testing
- 生产环境: FLASK_ENV=production

启动方式：
1. 开发环境: python main.py 或 flask run --host=0.0.0.0 --port=5001
2. 生产环境: gunicorn -w 4 -b 0.0.0.0:5001 main:app
"""

import os
from app.routes import create_app
from app.core.config import get_config_name

# 获取配置环境
config_name = get_config_name()

# 创建应用
app = create_app(config_name)

if __name__ == '__main__':
    # 从环境变量获取端口，默认 5001
    port = int(os.getenv('PORT', 5001))
    host = os.getenv('HOST', '0.0.0.0')
    
    # 根据环境决定是否开启 debug 模式
    debug = app.config.get('DEBUG', False)
    
    print(f"=" * 60)
    print(f"启动 Flask 应用")
    print(f"环境: {config_name}")
    print(f"地址: http://{host}:{port}")
    print(f"Debug: {debug}")
    print(f"=" * 60)
    
    # 启动应用
    # 生产环境建议使用: gunicorn -w 4 -b 0.0.0.0:5001 main:app
    app.run(host=host, port=port, debug=debug)




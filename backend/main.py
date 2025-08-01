# !/usr/bin/env python
# -*- coding:utf-8 -*-

"""
@author       weimenghua
@time         2025/7/30 17:47
@description  启动项目
"""

from app.routes import create_app

app = create_app()

if __name__ == '__main__':
    # 生产环境命令行执行: gunicorn -w 4 -b 0.0.0.0:5001 main:app
    # 开发环境命令行执行: flask run --host=0.0.0.0 --port=5001 --debug
    app.run(host='0.0.0.0', port=5001, debug=False )




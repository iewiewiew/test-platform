#!/bin/bash

# 删除空镜像资源 需优化
docker system prune -f

# 删除服务
# lsof -i:5001 | awk 'NR!=1 {print $2}' | xargs kill -9
# docker-compos stop test_platform_db
# docker-compos rm -f test_platform_db
docker-compose stop test_platform_backend test_platform_frontend
docker-compose rm -f test_platform_backend test_platform_frontend

# 启动服务
docker-compose up --build -d test_platform_backend test_platform_frontend

echo "服务地址: http://114.67.240.27:8899/"
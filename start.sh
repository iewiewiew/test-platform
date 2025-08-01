#!/bin/bash

# 删除空镜像资源 需优化
docker system prune -f

# 删除服务
# lsof -i:5001 | awk 'NR!=1 {print $2}' | xargs kill -9
# docker-compos stop test_platform_db
# docker-compos rm -f test_platform_db
docker-compose stop test_platform_backend test_platform_frontend
docker-compose rm -f test_platform_backend test_platform_frontend

# 删除镜像
docker rmi -f test-platform-test_platform_backend test-platform-test_platform_frontend

# 根据参数决定是否重新构建镜像
if [ "$1" == "build" ] || [ "$1" == "b" ]; then
    echo "正在重新构建镜像..."
    docker-compose up --build -d test_platform_backend test_platform_frontend
else
    echo "使用现有镜像启动服务（如需重建请使用: ./start.sh build 或者 ./start.sh b）"
    docker-compose up -d test_platform_backend test_platform_frontend
fi

echo "服务启动完成！"
echo "服务地址: http://114.67.240.27:8899"

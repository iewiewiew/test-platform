#!/bin/bash
# 数据库初始化和应用启动脚本

set -e

echo "等待 MySQL 数据库就绪..."
# 等待数据库可用
TIMEOUT=60
until mysqladmin ping -h db -P 3306 -uroot -p123456 --silent 2>/dev/null; do
  echo "等待 MySQL 在 db:3306 就绪..."
  sleep 2
  TIMEOUT=$((TIMEOUT - 2))
  if [ $TIMEOUT -le 0 ]; then
    echo "超时：MySQL 未在指定时间内启动" >&2
    exit 1
  fi
done

echo "MySQL 已就绪，开始数据库初始化..."

# 创建数据库（如果不存在）
echo "创建数据库 test_platform（如果不存在）..."
mysql -h db -P 3306 -uroot -p123456 << EOF || true
CREATE DATABASE IF NOT EXISTS test_platform CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
EOF

# 设置 Flask 应用
export FLASK_APP=app.routes:create_app

echo "数据库迁移完成，执行初始化SQL..."
# 执行初始化SQL文件（临时禁用 set -e，确保即使失败也继续启动应用）
set +e
if [ -f "/app/docker/db-init/init.sql" ]; then
    echo "执行 init.sql 初始化数据..."
    if mysql -h db -P 3306 -uroot -p123456 test_platform < /app/docker/db-init/init.sql 2>&1; then
        echo "✓ 初始化SQL执行成功"
    else
        echo "警告: 执行 init.sql 时出现错误（可能是数据已存在），继续启动应用..."
    fi
else
    echo "警告: init.sql 文件不存在，跳过初始化数据步骤"
fi
set -e

echo "启动应用..."
# 启动 Flask 应用
exec flask run --host=0.0.0.0 --port=5001


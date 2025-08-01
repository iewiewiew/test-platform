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

# 设置环境（如果没有设置，默认使用 development）
export FLASK_ENV=${FLASK_ENV:-development}
echo "使用环境: $FLASK_ENV"

# 运行数据库迁移
echo "开始运行数据库迁移..."
set +e
migration_success=false
if flask db upgrade 2>&1; then
    echo "✓ 数据库迁移成功"
    migration_success=true
else
    echo "警告: 数据库迁移失败或无需迁移（migrations 目录可能未初始化）"
    echo "提示: 应用启动时会自动创建表并初始化数据"
fi
set -e

# 执行初始化SQL文件（仅在迁移成功且文件存在时执行）
# 注意：如果 migrations 未初始化，应用启动时会自动创建表并初始化数据
set +e
if [ "$migration_success" = true ] && [ -f "/app/docker/db-init/init.sql" ]; then
    echo "执行 init.sql 初始化数据..."
    if mysql -h db -P 3306 -uroot -p123456 test_platform < /app/docker/db-init/init.sql 2>&1; then
        echo "✓ 初始化SQL执行成功"
    else
        echo "警告: 执行 init.sql 时出现错误（可能是数据已存在），继续启动应用..."
    fi
elif [ ! -f "/app/docker/db-init/init.sql" ]; then
    echo "提示: init.sql 文件不存在，应用启动时会自动执行 backend/sql/init_tmp.sql"
fi
set -e

echo "启动应用..."
# 启动 Flask 应用
exec flask run --host=0.0.0.0 --port=5001


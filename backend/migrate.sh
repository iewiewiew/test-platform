#!/bin/bash

# 清空数据库再初始化: drop database if exists test_platform;

export FLASK_APP=app.routes:create_app

mysql -h127.0.0.1 -uroot -p123456 << EOF
drop database if exists test_platform;
CREATE DATABASE IF NOT EXISTS test_platform CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
EOF

rm -rf migrations/
flask db init
flask db migrate -m "Initial migration"
flask db upgrade

mysql -h127.0.0.1 -uroot -p123456 < sql/init_tmp.sql

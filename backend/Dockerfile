# 基础镜像 https://docker.aityp.com/s/docker.io
# FROM swr.cn-north-4.myhuaweicloud.com/ddn-k8s/docker.io/python:3.9
FROM test-platfrom-python-base:latest

WORKDIR /app

# 复制应用代码
COPY . .

# 设置环境变量
ENV FLASK_APP=app.routes:create_app
ENV FLASK_ENV=development
ENV PORT=5001
ENV HOST=0.0.0.0

# 数据库初始化脚本
COPY ./docker/db-init/wait-for-it.sh /wait-for-it.sh
COPY ./docker/db-init/start.sh /start.sh
RUN chmod +x /wait-for-it.sh /start.sh

# 暴露端口
EXPOSE 5001

# 启动命令（等待数据库就绪后执行迁移并启动应用）
CMD ["/start.sh"]
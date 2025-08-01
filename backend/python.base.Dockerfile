# 基础镜像 https://docker.aityp.com/s/docker.io
# docker build --no-cache -t test-platfrom-python-base:latest -f python.base.Dockerfile .
FROM swr.cn-north-4.myhuaweicloud.com/ddn-k8s/docker.io/python:3.9

# 安装系统依赖（MySQL客户端等）
RUN rm -f /etc/apt/sources.list /etc/apt/sources.list.d/* && \
    echo "deb http://mirrors.aliyun.com/debian/ bookworm main non-free contrib" > /etc/apt/sources.list && \
    echo "deb http://mirrors.aliyun.com/debian-security/ bookworm-security main" >> /etc/apt/sources.list && \
    echo "deb http://mirrors.aliyun.com/debian/ bookworm-updates main non-free contrib" >> /etc/apt/sources.list && \
    apt-get update -o Acquire::Check-Valid-Until=false -o Acquire::AllowInsecureRepositories=true && \
    apt-get install -y build-essential python3-dev libffi-dev default-libmysqlclient-dev default-mysql-client openjdk-17-jre tzdata && \
    ln -sf /usr/share/zoneinfo/Asia/Shanghai /etc/localtime && \
    echo "Asia/Shanghai" > /etc/timezone && \
    rm -rf /var/lib/apt/lists/*

# allure 下载：wget https://github.com/allure-framework/allure2/releases/download/2.22.1/allure-2.22.1.zip
COPY allure-2.22.1.zip allure-2.22.1.zip
# 安装 Allure
RUN unzip allure-2.22.1.zip -d /opt/ && \
    ln -s /opt/allure-2.22.1/bin/allure /usr/local/bin/allure && \
    allure --version

# 复制依赖文件并安装
COPY requirements.txt .
RUN pip config set global.index-url https://mirrors.aliyun.com/pypi/simple/ && \
    pip config set global.trusted-host mirrors.aliyun.com && \
    pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt
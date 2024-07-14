FROM python:3.9-slim-buster as Base
WORKDIR /backend
COPY ./backend/requirements.txt requirements.txt

ARG PIP_INDEX_URL="https://pypi.org/simple"
# 安装依赖，尽量减少镜像层并在安装后清理
RUN sed -i 's/deb.debian.org/mirrors.aliyun.com/g' /etc/apt/sources.list && \
    sed -i 's|security.debian.org/debian-security|mirrors.aliyun.com/debian-security|g' /etc/apt/sources.list && \
    apt-get update && \
    apt-get install -y --no-install-recommends default-libmysqlclient-dev build-essential libpcre3-dev && \
    pip install --no-cache-dir -r requirements.txt -i ${PIP_INDEX_URL} && \
    apt-get remove -y python3-dev build-essential libpcre3-dev && \
    apt-get autoremove -y && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# 第二阶段开始
FROM python:3.9-slim-buster

# 设置时区
RUN sed -i 's/deb.debian.org/mirrors.aliyun.com/g' /etc/apt/sources.list && \
    sed -i 's|security.debian.org/debian-security|mirrors.aliyun.com/debian-security|g' /etc/apt/sources.list && \
    apt-get update && \
    apt-get install -y default-libmysqlclient-dev tzdata && \
    echo "Asia/Shanghai" > /etc/timezone && \
    ln -snf /usr/share/zoneinfo/Asia/Shanghai /etc/localtime && \
    dpkg-reconfigure -f noninteractive tzdata && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# 从构建阶段复制安装的包
COPY --from=Base /usr/local/lib/python3.9/site-packages /usr/local/lib/python3.9/site-packages
COPY --from=Base /usr/local/bin /usr/local/bin

# 复制应用代码
WORKDIR /backend
COPY ./backend .
COPY ./backend/conf/docker.py conf/env.py

CMD ["celery", "-A", "backend", "worker", "-B", "--loglevel=info"]
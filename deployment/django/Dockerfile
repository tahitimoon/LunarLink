FROM python:3.9-buster as Base
WORKDIR /backend
COPY ./backend/requirements.txt requirements.txt
ARG DEBIAN_REPO="deb.debian.org"
ARG PIP_INDEX_URL="https://pypi.tuna.tsinghua.edu.cn/simple"
RUN echo "deb https://$DEBIAN_REPO/debian/ buster main contrib non-free" > /etc/apt/sources.list && \
    echo "deb-src https://$DEBIAN_REPO/debian/ buster main contrib non-free" >> /etc/apt/sources.list && \
    echo "deb https://$DEBIAN_REPO/debian-security buster/updates main contrib non-free" >> /etc/apt/sources.list && \
    echo "deb-src https://$DEBIAN_REPO/debian-security buster/updates main contrib non-free" >> /etc/apt/sources.list && \
    echo "deb https://$DEBIAN_REPO/debian/ buster-updates main contrib non-free" >> /etc/apt/sources.list && \
    echo "deb-src https://$DEBIAN_REPO/debian/ buster-updates main contrib non-free" >> /etc/apt/sources.list
RUN apt-get update && \
    apt-get install -y default-libmysqlclient-dev python3-dev build-essential netcat-openbsd libpcre3-dev && \
    pip install setuptools==57.5.0 -i ${PIP_INDEX_URL} && \
    pip install -r requirements.txt -i ${PIP_INDEX_URL} && \
    apt-get remove -y python3-dev build-essential libpcre3-dev && \
    apt-get autoremove -y && \
    rm -rf /var/lib/apt/lists/*

FROM python:3.9-buster
ARG DEBIAN_REPO="deb.debian.org"
RUN echo "deb https://$DEBIAN_REPO/debian/ buster main contrib non-free" > /etc/apt/sources.list && \
    echo "deb-src https://$DEBIAN_REPO/debian/ buster main contrib non-free" >> /etc/apt/sources.list && \
    echo "deb https://$DEBIAN_REPO/debian-security buster/updates main contrib non-free" >> /etc/apt/sources.list && \
    echo "deb-src https://$DEBIAN_REPO/debian-security buster/updates main contrib non-free" >> /etc/apt/sources.list && \
    echo "deb https://$DEBIAN_REPO/debian/ buster-updates main contrib non-free" >> /etc/apt/sources.list && \
    echo "deb-src https://$DEBIAN_REPO/debian/ buster-updates main contrib non-free" >> /etc/apt/sources.list

RUN apt-get update && \
    apt-get install -y default-libmysqlclient-dev tzdata && \
    echo "Asia/Shanghai" > /etc/timezone && \
    ln -snf /usr/share/zoneinfo/Asia/Shanghai /etc/localtime && \
    dpkg-reconfigure -f noninteractive tzdata && \
    rm -rf /var/lib/apt/lists/*

COPY --from=Base /usr/local/lib/python3.9/site-packages /usr/local/lib/python3.9/site-packages
COPY --from=Base /usr/local/bin /usr/local/bin
WORKDIR /backend
COPY ./backend .
COPY ./backend/conf/docker.py conf/env.py

CMD ["gunicorn", "--config", "gunicorn_conf.py", "backend.wsgi:application"]

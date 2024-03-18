# Docker构建

仅本地快速部署体验之用，如果本地开发还是参照`LunarLink`目录下的说明，搭建开发环境

## 修改配置

```sh
cd LunarLink/backend/conf
# 将docker_example.py内容复制到docker.py中
cd LunarLink/deployment/web
# 将nginx_example.conf内容复制到nginx.conf中
```

## docker compose

在`LunarLink`目录下，执行`docker-compose up -d`

## 创建数据库

连接数据库，如使用`Navicat Premium`建立连接，创建`fast_dev`库，字符集为`utf8mb4`，排序规则为`utf8mb4_unicode_ci`

## 第一次运行

进入django容器初始化数据库`docker exec -it faster-runner-django /bin/bash`

```bash
# 执行迁移命令：
python3 manage.py makemigrations
python3 manage.py migrate
# 创建管理员用户
python3 manage.py createsuperuser
```

## 访问项目

```
浏览器打开:
http://localhost:8080
用户/密码:管理员用户/密码
```

## 服务端口

- web: 8080
- api: 8000
- mysql: 3306
- rabbitmq: 5672
- redis: 6379

## MySQL存储

为了不污染本地开发环境，mysql、rabbitmq、redis使用docker的Volume进行存储。

- mysql: mysql:/var/lib/mysql
- rabbitmq: rabbitmq:/var/lib/rabbitmq
- redis: redis:/data
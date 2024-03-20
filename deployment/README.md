# Docker构建

仅本地快速部署体验之用，如果本地开发还是参照`LunarLink`目录下的说明，搭建开发环境

## docker compose

```bash
# 进入项目根目录
cd LunarLink

# 执行如下命令即可启动所有服务
docker-compose up -d
```

## 第一次运行

进入django容器初始化数据库`docker exec -it lunar-link-django /bin/bash`

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
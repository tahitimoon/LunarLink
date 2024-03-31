# Docker构建

本地快速部署或线上单机部署参照如下说明

如果本地开发还是参照`LunarLink`目录下的说明，搭建开发环境

## 修改配置

```bash
# 进入项目根目录
cd LunarLink

# 将.env.example文件重命名为.env 并配置相关参数
mv .env.example .env
```

## docker compose

```bash
# 在根目录，执行如下命令
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

```bash
# 登录管理后台，设置账号姓名
http://localhost:8081/admin/

浏览器打开:
http://localhost:8081
用户/密码:管理员用户/密码
```

## 服务端口

- web: 8081
- api: 8000
- mysql: 3306
- rabbitmq: 5672
- redis: 6379

## MySQL存储

为了不污染本地开发环境，mysql、rabbitmq、redis使用docker的Volume进行存储。

- mysql: mysql:/var/lib/mysql
- rabbitmq: rabbitmq:/var/lib/rabbitmq
- redis: redis:/data
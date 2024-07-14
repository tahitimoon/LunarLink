# gunicorn配置文件
import multiprocessing

# 并行工作进程数, int，cpu数量*2+1 推荐进程数
workers = multiprocessing.cpu_count() * 2 + 1
# 指定每个进程开启的线程数
threads = 2

# 绑定ip和端口号
bind = "0.0.0.0:8000"

# 使用gevent工作进程类型来处理请求
worker_class = "gevent"

forwarded_allow_ips = "*"
x_forwarded_for_header = "X-FORWARDED-FOR"

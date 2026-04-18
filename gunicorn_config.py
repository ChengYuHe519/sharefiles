#!/usr/bin/env python3
# Gunicorn 生产服务器配置

import multiprocessing

# 服务器绑定
bind = "0.0.0.0:5000"

# 工作进程数
workers = multiprocessing.cpu_count() * 2 + 1

# 工作进程类型
worker_class = "sync"

# 超时设置
timeout = 30
keepalive = 2

# 日志配置
accesslog = "-"  # 输出到标准输出
errorlog = "-"   # 输出到标准错误
loglevel = "info"

# 进程名称
proc_name = "sharefiles"

# 最大请求数（防止内存泄漏）
max_requests = 1000
max_requests_jitter = 50

# 优雅重启
graceful_timeout = 30

# 防止DDoS攻击
limit_request_line = 4094
limit_request_fields = 100
limit_request_field_size = 8190

print(f"Gunicorn配置加载: {workers}个工作进程，绑定到{bind}")
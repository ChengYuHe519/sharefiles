#!/usr/bin/env python3
# Gunicorn 生产服务器配置

import multiprocessing

# 服务器绑定
bind = "0.0.0.0:5000"

# 工作进程数（根据服务器规模调整）
cpu_count = multiprocessing.cpu_count()

# 生产环境建议配置
if cpu_count <= 2:          # 小型服务器（1-2核）
    workers = 3
elif cpu_count <= 4:        # 中型服务器（3-4核）
    workers = cpu_count * 2
elif cpu_count <= 8:        # 标准服务器（5-8核）
    workers = cpu_count + 2
elif cpu_count <= 16:       # 大型服务器（9-16核）
    workers = cpu_count
else:                       # 超大型服务器（16+核）
    workers = 16            # 限制最大工作进程数

print(f"CPU核心数: {cpu_count}, 设置工作进程数: {workers}")

# 工作进程类型
worker_class = "gthread"
threads = 4

# 超时设置
timeout = 600
keepalive = 2

# 日志配置
import os
accesslog = "-"  # 输出到标准输出
errorlog = "-"   # 输出到标准错误
loglevel = os.getenv('LOG_LEVEL', 'info').lower()

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
# 📁 ShareFiles - 轻量级文件共享平台

[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.8+-green.svg)](https://python.org)
[![Docker](https://img.shields.io/badge/docker-✓-blue.svg)](https://docker.com)
[![Status](https://img.shields.io/badge/status-stable-brightgreen.svg)]()

> 🔐 一个安全、快速、易部署的自托管文件共享服务，支持上传、管理、分享文件，适合个人或小团队使用。

---

## 📑 目录

- [✨ 功能特性](#-功能特性)
- [🖼️ 界面预览](#️-界面预览)
- [🏗️ 技术架构](#️-技术架构)
- [📦 项目结构](#-项目结构)
- [🚀 快速开始](#-快速开始)
- [⚙️ 配置详解](#️-配置详解)
- [🔐 安全最佳实践](#-安全最佳实践)
- [🔧 运维监控](#-运维监控)
- [🐛 故障排除](#-故障排除)
- [🔄 升级迁移](#-升级迁移)
- [🤝 贡献指南](#-贡献指南)
- [📜 许可证](#-许可证)

---

## ✨ 功能特性

### 🔹 核心功能

- ✅ **文件上传**：支持拖拽上传、多文件批量上传、上传进度显示
- ✅ **文件管理**：列表/网格视图切换、文件名搜索、按时间/大小排序
- ✅ **分享链接**：生成可分享的下载链接，支持设置有效期和访问密码
- ✅ **权限控制**：管理员后台，支持用户认证和操作日志

### 🔹 部署友好

- ✅ **多模式运行**：支持本地开发、Gunicorn 生产、Docker 容器化部署
- ✅ **Nginx 反向代理**：内置配置，支持静态资源缓存和 HTTPS 终止
- ✅ **环境变量配置**：敏感信息隔离，便于不同环境切换

### 🔹 安全可靠

- ✅ **密码哈希**：使用 PBKDF2 算法存储管理员密码
- ✅ **文件校验**：上传文件 MD5 校验，防止损坏和重复
- ✅ **CORS 控制**：可配置跨域策略，防止未授权访问

### 🔹 扩展性强

- ✅ **模块化设计**：代码结构清晰，便于二次开发和功能扩展
- ✅ **日志系统**：结构化日志输出，便于问题追踪和审计

---

## 🏗️ 技术架构

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│   Client    │────▶│   Nginx     │────▶│  Gunicorn   │
│  (Browser)  │     │(Reverse Proxy)│  │(WSGI Server)│
└─────────────┘     └─────────────┘     └──────┬──────┘
                                               │
                    ┌─────────────┐     ┌──────▼──────┐
                    │  File System│     │  Flask App  │
                    │  (uploads/) │     │  (app.py)   │
                    └─────────────┘     └─────────────┘
```

**技术栈：**
| 组件 | 技术选型 | 说明 |
|------|----------|------|
| 后端框架 | Flask | 轻量级 Python Web 框架 |
| WSGI 服务器 | Gunicorn | 生产级 Python WSGI HTTP Server |
| 反向代理 | Nginx | 静态资源缓存、HTTPS 终止、负载均衡 |
| 容器化 | Docker + Docker Compose | 一键部署，环境隔离 |
| 密码加密 | PBKDF2 (hashlib) | 安全的密码哈希存储 |
| 日志管理 | Python logging | 结构化日志，支持文件输出 |

---

## 🚀 快速开始

### 方式一：本地开发运行（推荐调试使用）

```bash
# 1. 克隆项目
git clone https://github.com/ChengYuHe519/sharefiles.git
cd sharefiles

# 2. 创建虚拟环境（可选但推荐）
python -m venv .venv
source .venv/bin/activate  # Linux/macOS
# .venv\Scripts\activate   # Windows

# 3. 设置环境变量
export ADMIN_PASSWORD="your_secure_password_here"
export SESSION_SECRET=$(openssl rand -hex 32)
export UPLOAD_FOLDER="uploads"
export MAX_FILE_SIZE_GB=2

# 4. 安装依赖
pip install -r requirements.txt

# 5. 创建上传目录并赋权
mkdir -p uploads logs
chmod 755 uploads logs

# 6. 运行开发服务器
python app.py
# 访问 http://localhost:5000
```

### 方式二：Gunicorn 生产运行

```bash
# 安装 Gunicorn（如未安装）
pip install gunicorn

# 使用配置文件启动
gunicorn --config gunicorn_config.py app:app
# 默认监听 127.0.0.1:8000，建议配合 Nginx 使用
```

### 方式三：Docker 单容器部署

```bash
# 1. 构建镜像
docker build -t sharefiles .

# 2. 运行容器
docker run -d \
  -p 5000:5000 \
  -e ADMIN_PASSWORD="your_secure_password_here" \
  -e SESSION_SECRET=$(openssl rand -hex 32) \
  -e MAX_FILE_SIZE_GB=2 \
  -v $(pwd)/files:/app/files \
  -v $(pwd)/logs:/app/logs \
  --name sharefiles \
  --restart unless-stopped \
  sharefiles
```

### 方式四：Docker Compose 完整部署（✅ 推荐生产环境）

```bash
# 1. 创建 .env 文件（复制模板并修改）
cp .env.example .env
# 编辑 .env 填写你的配置

# 2. 启动服务（Nginx + App + 日志卷）
docker-compose up -d

# 3. 查看服务状态
docker-compose ps
docker-compose logs -f app  # 查看应用日志

# 访问：http://your-server-ip
# Nginx 默认监听 80/443 端口
```

---

## ⚙️ 配置详解

### 环境变量参考表

| 变量名               | 必填    | 默认值    | 说明                                       | 示例                      |
| -------------------- | ------- | --------- | ------------------------------------------ | ------------------------- |
| `ADMIN_PASSWORD`     | ✅ 是   | 无        | 管理员登录密码（≥8字符），首次运行自动哈希 | `MyS3cur3P@ss`            |
| `SESSION_SECRET`     | ⚠️ 建议 | 自动生成  | Flask Session 加密密钥（≥32字符）          | `$(openssl rand -hex 32)` |
| `UPLOAD_FOLDER`      | ❌ 否   | `uploads` | 文件存储相对路径                           | `data/files`              |
| `MAX_FILE_SIZE_GB`   | ❌ 否   | `2`       | 单文件上传上限（单位：GB）                 | `5`                       |
| `ALLOWED_EXTENSIONS` | ❌ 否   | 常见格式  | 允许上传的文件扩展名（逗号分隔）           | `pdf,docx,jpg,png,zip`    |
| `LOG_LEVEL`          | ❌ 否   | `INFO`    | 日志级别：DEBUG/INFO/WARNING/ERROR         | `DEBUG`                   |

> 💡 **提示**：`SESSION_SECRET` 建议每次部署时重新生成，避免会话劫持。

### Gunicorn 配置要点（`gunicorn_config.py`）

```python
# 工作进程数：建议 = (2 × CPU核心数) + 1
workers = 4

# 绑定地址：生产环境建议绑定 127.0.0.1，由 Nginx 代理
bind = "127.0.0.1:8000"

# 日志配置
accesslog = "logs/access.log"
errorlog = "logs/error.log"
loglevel = "info"
```

### Nginx 关键配置（`nginx.conf`）

```nginx
# 限制上传大小（与 MAX_FILE_SIZE_GB 保持一致）
client_max_body_size 2G;

# 静态文件缓存
location /static {
    expires 30d;
    add_header Cache-Control "public, immutable";
}

# 反向代理到 Gunicorn
location / {
    proxy_pass http://127.0.0.1:8000;
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
}
```

---

## 🔐 安全最佳实践

### 1️⃣ 密码与认证安全

- ✅ 首次部署后，建议将明文密码替换为哈希值：
    ```python
    # 生成 PBKDF2 哈希（一次性脚本）
    import hashlib, os
    password = "your_password"
    salt = os.urandom(16).hex()
    key = hashlib.pbkdf2_hmac('sha256', password.encode(), salt.encode(), 100000).hex()
    print(f"{salt}:100000:{key}")  # 将此值设为 ADMIN_PASSWORD
    ```
- ✅ 定期更换管理员密码
- ✅ 避免在代码或日志中打印敏感信息

### 2️⃣ 网络与传输安全

- 🔒 **必须启用 HTTPS**（生产环境）：
    ```bash
    # 使用 Let's Encrypt 免费证书（推荐）
    # 或生成自签名证书（仅测试）
    mkdir -p ssl
    openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
      -keyout ssl/key.pem -out ssl/cert.pem \
      -subj "/C=CN/ST=Beijing/L=Beijing/O=YourOrg/CN=your-domain.com"
    ```
- 🔒 配置 Nginx 强制 HTTPS 跳转：
    ```nginx
    server {
        listen 80;
        server_name your-domain.com;
        return 301 https://$server_name$request_uri;
    }
    ```

### 3️⃣ 系统级防护

```bash
# 1. 防火墙配置（Ubuntu/Debian）
ufw allow 22/tcp    # SSH
ufw allow 80/tcp    # HTTP（可选，用于证书申请）
ufw allow 443/tcp   # HTTPS
ufw enable

# 2. 限制上传目录权限
chmod 750 uploads
chown www-data:www-data uploads  # 根据实际运行用户调整

# 3. 定期更新依赖
pip audit  # 检查已知漏洞
pip install --upgrade -r requirements.txt
```

---

## 🔧 运维监控

### 📊 日志查看

```bash
# Docker 部署
docker-compose logs -f app      # 应用日志
docker-compose logs -f nginx    # Nginx 访问日志

# 直接运行
tail -f logs/app.log
tail -f logs/gunicorn.log

# 实时跟踪错误
grep -i "error" logs/*.log | tail -20
```

### ❤️ 健康检查

```bash
# 基础连通性
curl -f http://localhost:5000/ && echo "✓ Service OK"

# 详细状态（可集成到监控系统）
curl -s http://localhost:5000/health | jq

# Docker 健康状态（需在 docker-compose.yml 中配置 healthcheck）
docker inspect --format='{{.State.Health.Status}}' sharefiles
```

### 💾 备份与恢复

```bash
# 全量备份（文件 + 配置）
BACKUP_DIR="backup_$(date +%Y%m%d_%H%M)"
mkdir -p $BACKUP_DIR
cp -r files/ $BACKUP_DIR/
cp .env $BACKUP_DIR/
tar -czf ${BACKUP_DIR}.tar.gz $BACKUP_DIR
rm -rf $BACKUP_DIR

# 恢复备份
tar -xzf backup_20240101_1200.tar.gz
cp backup_*/.env ./
cp -r backup_*/files/* ./files/
docker-compose restart
```

### 📈 性能监控建议

| 指标       | 监控方式                    | 阈值建议          |
| ---------- | --------------------------- | ----------------- |
| CPU 使用率 | `top` / `htop` / Prometheus | >80% 告警         |
| 内存占用   | `free -h` / Docker stats    | >90% 告警         |
| 磁盘空间   | `df -h`                     | <10% 剩余空间告警 |
| 上传速率   | Nginx access log 分析       | 异常突增需排查    |

---

## 🐛 故障排除

### ❌ 问题 1：文件上传失败 / 413 错误

```bash
# 可能原因及解决方案：
# 1. 超过大小限制 → 检查 MAX_FILE_SIZE_GB 和 nginx client_max_body_size
# 2. 目录无写权限 → chmod 755 uploads && chown -R www-data:www-data uploads
# 3. 磁盘空间不足 → df -h 检查剩余空间
# 4. 临时目录满 → 清理 /tmp 或配置 UPLOAD_FOLDER 到独立分区
```

### ❌ 问题 2：服务启动失败 / 端口占用

```bash
# 检查端口占用
lsof -i :5000      # Linux/macOS
netstat -ano | findstr :5000  # Windows

# 杀死占用进程（谨慎操作）
kill -9 <PID>

# 或修改配置更换端口
# gunicorn_config.py: bind = "127.0.0.1:8001"
```

### ❌ 问题 3：管理员登录失败

```bash
# 1. 检查 ADMIN_PASSWORD 是否设置正确
# 2. 首次运行后密码已哈希，需用哈希值登录
# 3. 查看日志确认错误类型：
docker-compose logs app | grep -i "auth\|login\|error"

# 4. 重置密码（临时方案）：
#    - 停止服务
#    - 修改 .env 中 ADMIN_PASSWORD 为新明文
#    - 重启服务（会自动重新哈希）
```

### ❌ 问题 4：Docker 容器反复重启

```bash
# 1. 查看退出原因
docker inspect sharefiles --format='{{.State.ExitCode}} {{.State.Error}}'

# 2. 检查应用日志
docker-compose logs --tail=50 app

# 常见原因：
# - 环境变量缺失 → 检查 .env 文件
# - 依赖安装失败 → 重建镜像：docker-compose build --no-cache
# - 端口冲突 → 修改 docker-compose.yml 中的端口映射
```

---

## 🔄 升级迁移

### 版本升级流程

```bash
# 1. 备份（务必！）
./scripts/backup.sh  # 或手动执行备份命令

# 2. 拉取新代码
git pull origin main

# 3. 更新依赖（如 requirements.txt 有变更）
docker-compose build --no-cache

# 4. 重启服务
docker-compose up -d

# 5. 验证
curl -f http://localhost/ && echo "✓ Upgrade successful"
```

### 数据迁移（跨服务器）

```bash
# 源服务器导出
tar -czf sharefiles-backup.tar.gz files/ .env docker-compose.yml

# 传输到新服务器
scp sharefiles-backup.tar.gz user@new-server:/opt/

# 新服务器恢复
cd /opt/sharefiles
tar -xzf ../sharefiles-backup.tar.gz
docker-compose up -d
```

---

## 🤝 贡献指南

欢迎提交 Issue 和 Pull Request！🎉

### 开发流程

```bash
# 1. Fork 仓库并克隆
git clone https://github.com/ChengYuHe519/sharefiles.git

# 2. 创建功能分支
git checkout -b feature/your-feature-name

# 3. 开发并测试
#    - 保持代码风格一致（PEP 8）
#    - 添加必要的注释和日志
#    - 本地测试通过后再提交

# 4. 提交变更
git add .
git commit -m "feat: add xxx feature"  # 使用约定式提交

# 5. 推送并创建 PR
git push origin feature/your-feature-name
```

### 提交规范

```
feat:     新功能
fix:      修复问题
docs:     文档更新
style:    代码格式调整（不影响逻辑）
refactor: 重构（无功能变更）
test:     测试相关
chore:    构建/工具链变更
```

---

## 📜 许可证

本项目采用 [MIT License](LICENSE) 开源协议。

```
MIT License

Copyright (c) 2024 CTT

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.
```

---

**✨ 祝你部署顺利！如有问题，欢迎提 Issue 交流~**

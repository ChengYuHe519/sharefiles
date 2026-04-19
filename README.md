# 📦 ShareFiles - 简单文件共享系统

一个基于 **Flask + Gunicorn + Nginx + Docker Compose** 的轻量级文件共享服务，适用于：

- 局域网文件共享
- 临时文件中转
- 私有云简易替代方案

------

## ✨ 特性

- 📤 文件上传 / 📥 下载
- 🔐 管理员登录与后台管理
- 🗑 文件删除
- 🛡 CSRF 防护
- 🔑 PBKDF2 密码加密
- 🚦 登录限流（防爆破）
- 🌐 支持反向代理与真实 IP 获取
- 🐳 Docker 一键部署
- ⚡ 支持大文件（GB 级）传输

------

## 🖼 界面说明

| 页面     | 路径     | 说明             |
| -------- | -------- | ---------------- |
| 首页     | `/`      | 上传 + 文件列表  |
| 管理后台 | `/admin` | 登录后可删除文件 |

------

## 📁 项目结构

```bash
.
├── app.py                 # Flask 主程序
├── docker-compose.yml     # 容器编排
├── Dockerfile             # 镜像构建
├── gunicorn_config.py     # Gunicorn 配置
├── nginx.conf             # Nginx 反向代理
├── requirements.txt
├── templates              # 前端页面
│   ├── index.html
│   ├── admin_login.html
│   └── admin_panel.html
```

------

## 🚀 快速开始

### 方式一：Docker（推荐）

#### 1. 创建 `.env`

```env
ADMIN_PASSWORD=your_password_here
SESSION_SECRET=your_very_long_random_string_at_least_32_chars
MAX_FILE_SIZE_GB=2
```

#### 2. 修改 `docker-compose.yml`

替换以下占位：

```yaml
- /your-file-path:/app/files
- your-host-port:5000
- /your-ssl-path:/etc/nginx/ssl
```

#### 3. 启动

```bash
docker compose up -d --build
```

#### 4. 访问

```
https://<your-ip>:<port>
```

------

### 方式二：本地运行（开发）

```bash
pip install -r requirements.txt

export ADMIN_PASSWORD='your_password'
export SESSION_SECRET='your_secret_key_32+'

python app.py
```

访问：

```
http://localhost:5000
```

------

## ⚙️ 配置说明

### 环境变量

| 变量               | 必填 | 说明                     |
| ------------------ | ---- | ------------------------ |
| `ADMIN_PASSWORD`   | ✅    | 管理员密码（≥8位）       |
| `SESSION_SECRET`   | ✅    | Session 密钥（≥32位）    |
| `UPLOAD_FOLDER`    | ❌    | 文件目录（默认 uploads） |
| `MAX_FILE_SIZE_GB` | ❌    | 最大上传大小（默认 2GB） |
| `DEBUG_IP`         | ❌    | 打印真实 IP 调试         |
| `LOG_LEVEL`        | ❌    | Gunicorn 日志等级        |

------

## 🔒 安全设计

- ✅ PBKDF2-SHA256 密码哈希
- ✅ CSRF Token 校验
- ✅ 登录失败限流（5次/5分钟）
- ✅ 文件名安全过滤（防路径穿越）
- ✅ ProxyFix + 自定义真实 IP 获取
- ✅ Nginx 安全响应头

------

## 📦 文件处理规则

- 自动重命名避免覆盖

  ```
  file.txt → file_1.txt → file_2.txt
  ```

- 文件名清洗（去除非法字符）

- 支持中文文件名

------

## 🧱 架构说明

```text
Client
  ↓
Nginx (HTTPS + 反代 + 大文件优化)
  ↓
Gunicorn
  ↓
Flask App
  ↓
文件存储 (Volume)
```

------

## ⚡ 性能与大文件优化

已优化：

- Nginx 关闭缓冲（避免临时文件爆炸）
- Gunicorn 多 worker + 线程
- Flask 限制上传大小
- 支持流式下载

------

## ⚠️ 注意事项

- ❗ 必须设置 `ADMIN_PASSWORD`
- ❗ `SESSION_SECRET` 建议固定（否则重启失效）
- ❗ 确保磁盘空间足够
- ❗ 修改 Nginx 端口和证书路径

------

## 🛠 常见问题

### 1. 上传失败？

检查：

- Flask `MAX_CONTENT_LENGTH`
- Nginx `client_max_body_size`

------

### 2. 无法获取真实 IP？

确保：

- 已通过 `Nginx` 访问
- 已设置 `ProxyFix`

------

### 3. 登录被限制？

等待 5 分钟或更换 IP

------

## 📄 License

本项目采用 [MIT License](LICENSE) 开源协议。

------

## ⭐ Star 支持

如果这个项目对你有帮助，可以点个 ⭐ 支持一下 😄

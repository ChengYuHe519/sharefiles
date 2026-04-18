from flask import Flask, request, send_from_directory, render_template, redirect, url_for, session, g
import os
import time
import hashlib
import hmac
import secrets
from werkzeug.utils import secure_filename
import urllib.parse
from collections import defaultdict
from datetime import datetime, timedelta
from functools import wraps

app = Flask(__name__)

# 添加自定义模板过滤器
@app.template_filter('urlencode')
def urlencode_filter(s):
    return urllib.parse.quote(s)

# 添加ProxyFix中间件（必须在路由定义之前）
from werkzeug.middleware.proxy_fix import ProxyFix

# 信任代理链（x_for=1表示信任1层代理）
# 在Docker Compose中：客户端 → Nginx → Flask
# 所以需要信任1层代理
app.wsgi_app = ProxyFix(
    app.wsgi_app,
    x_for=1,      # 信任X-Forwarded-For头
    x_proto=1,    # 信任X-Forwarded-Proto头
    x_host=1,     # 信任X-Forwarded-Host头
    x_port=0,     # 不信任X-Forwarded-Port（不需要）
    x_prefix=0    # 不信任X-Forwarded-Prefix（不需要）
)

# 密码哈希函数（需要在配置之前定义）
def hash_password(password, salt=None):
    """使用PBKDF2哈希密码"""
    if salt is None:
        salt = secrets.token_bytes(16)

    # 使用PBKDF2进行密码哈希
    iterations = 100000
    key = hashlib.pbkdf2_hmac(
        'sha256',
        password.encode('utf-8'),
        salt,
        iterations
    )

    # 返回格式: salt:iterations:key
    return f"{salt.hex()}:{iterations}:{key.hex()}"

def verify_password(stored_password, provided_password):
    """验证密码"""
    try:
        salt_hex, iterations_hex, key_hex = stored_password.split(':')
        salt = bytes.fromhex(salt_hex)
        iterations = int(iterations_hex)
        stored_key = bytes.fromhex(key_hex)

        # 计算提供的密码的哈希
        provided_key = hashlib.pbkdf2_hmac(
            'sha256',
            provided_password.encode('utf-8'),
            salt,
            iterations
        )

        # 使用恒定时间比较防止时序攻击
        return hmac.compare_digest(stored_key, provided_key)
    except (ValueError, AttributeError):
        return False

# ============== 配置区（支持 Docker 环境变量）==============
import secrets

# 环境变量默认值
UPLOAD_FOLDER = os.getenv('UPLOAD_FOLDER', 'uploads')
ADMIN_PASSWORD = os.getenv('ADMIN_PASSWORD')
SESSION_SECRET = os.getenv('SESSION_SECRET', secrets.token_hex(32))
MAX_FILE_SIZE_GB = int(os.getenv('MAX_FILE_SIZE_GB', '2'))

# 配置校验
if not ADMIN_PASSWORD:
    raise ValueError("ADMIN_PASSWORD 环境变量必须设置")

# 将明文密码转换为哈希存储
if not ADMIN_PASSWORD.startswith(':'):  # 简单判断是否为哈希格式
    if len(ADMIN_PASSWORD) < 8:
        raise ValueError("ADMIN_PASSWORD 至少需要8个字符")
    # 如果是明文密码，转换为哈希并打印提示
    hashed_password = hash_password(ADMIN_PASSWORD)
    print(f"注意: 明文密码已自动哈希。下次部署时建议直接使用哈希值: {hashed_password}")
    ADMIN_PASSWORD_HASH = hashed_password
else:
    ADMIN_PASSWORD_HASH = ADMIN_PASSWORD
if len(SESSION_SECRET) < 32:
    raise ValueError("SESSION_SECRET 至少需要32个字符")
if MAX_FILE_SIZE_GB <= 0 or MAX_FILE_SIZE_GB > 100:
    raise ValueError("MAX_FILE_SIZE_GB 必须在1-100之间")

print(f"配置加载成功: UPLOAD_FOLDER={UPLOAD_FOLDER}, MAX_FILE_SIZE_GB={MAX_FILE_SIZE_GB}")
# ====================================================

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = MAX_FILE_SIZE_GB * 1024 * 1024 * 1024
app.secret_key = SESSION_SECRET   # 必须设置，用于 Session

# 代理配置（重要：防止IP欺骗）
# 信任的代理IP列表（Nginx容器IP、本地回环等）
app.config['PROXY_FIX'] = {
    'x_for': 1,      # 信任1层代理
    'x_proto': 1,
    'x_host': 1,
    'x_port': 0,
    'x_prefix': 0
}

# 如果是Docker环境，自动添加容器网络信任
if os.getenv('DOCKER_CONTAINER'):
    app.config['PROXY_FIX']['trusted_proxies'] = [
        '127.0.0.1',
        '::1',
        '172.16.0.0/12',  # Docker默认网络
        '192.168.0.0/16',
        '10.0.0.0/8'
    ]

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

def get_file_list():
    files = []
    for f in os.listdir(UPLOAD_FOLDER):
        path = os.path.join(UPLOAD_FOLDER, f)
        if os.path.isfile(path):  # 只处理文件，忽略目录
            size_mb = round(os.path.getsize(path) / (1024 * 1024), 2)
            files.append((f, size_mb))
    return sorted(files)

def get_unique_filename(filename):
    """生成唯一的文件名，避免覆盖"""
    base_name, ext = os.path.splitext(filename)
    counter = 1
    new_filename = filename
    upload_path = app.config['UPLOAD_FOLDER']

    while os.path.exists(os.path.join(upload_path, new_filename)):
        new_filename = f"{base_name}_{counter}{ext}"
        counter += 1

    return new_filename

def safe_filename(filename):
    """安全处理文件名，保留中文和空格"""
    import re

    if not filename:
        return "unnamed_file"

    # 移除空字节和不可见控制字符
    filename = re.sub(r'[\x00-\x1f\x7f]', '', filename)

    # 移除路径分隔符和危险字符
    filename = re.sub(r'[\\/*?:"<>|]', '', filename)

    # 移除Windows保留设备名
    windows_reserved = [
        'CON', 'PRN', 'AUX', 'NUL',
        'COM1', 'COM2', 'COM3', 'COM4', 'COM5', 'COM6', 'COM7', 'COM8', 'COM9',
        'LPT1', 'LPT2', 'LPT3', 'LPT4', 'LPT5', 'LPT6', 'LPT7', 'LPT8', 'LPT9'
    ]

    name, ext = os.path.splitext(filename)
    base_name = name.upper()

    # 检查是否为保留设备名
    for reserved in windows_reserved:
        if base_name == reserved or base_name.startswith(reserved + '.'):
            # 如果不是保留设备名，添加前缀
            filename = f"file_{filename}"
            break

    # 移除尾随的点（Windows不允许）
    filename = filename.rstrip('.')

    # 限制文件名长度
    if len(filename) > 255:
        name, ext = os.path.splitext(filename)
        filename = name[:255-len(ext)] + ext

    # 如果文件名变为空，使用默认名称
    if not filename.strip():
        filename = "unnamed_file"

    return filename.strip()

# 登录限流机制
login_attempts = defaultdict(list)
MAX_ATTEMPTS = 5
TIME_WINDOW = 300  # 5分钟

def get_real_ip():
    """获取真实客户端IP（支持代理环境）"""
    # 手动处理，更可靠
    if request.headers.get('X-Forwarded-For'):
        # X-Forwarded-For: client, proxy1, proxy2
        # 取第一个非内部IP
        ips = request.headers.get('X-Forwarded-For', '').split(',')
        for ip in ips:
            ip = ip.strip()
            # 跳过内部IP和空值
            if ip and not ip.startswith(('10.', '172.16.', '172.17.', '172.18.', '172.19.', '172.20.', '172.21.', '172.22.', '172.23.', '172.24.', '172.25.', '172.26.', '172.27.', '172.28.', '172.29.', '172.30.', '172.31.', '192.168.', '127.', '::1', '0:', 'fc00:', 'fe80:')):
                return ip
        # 如果没有找到非内部IP，返回第一个
        if ips and ips[0].strip():
            return ips[0].strip()

    if request.headers.get('X-Real-IP'):
        return request.headers.get('X-Real-IP').strip()

    return request.remote_addr

def check_login_rate_limit(ip_address):
    """检查登录频率限制"""
    now = time.time()
    attempts = login_attempts[ip_address]

    # 清理过期的尝试记录
    attempts = [t for t in attempts if now - t < TIME_WINDOW]
    login_attempts[ip_address] = attempts

    if len(attempts) >= MAX_ATTEMPTS:
        return False, f"登录尝试过于频繁，请等待 {TIME_WINDOW//60} 分钟后重试"

    return True, None

def record_login_attempt(ip_address, success):
    """记录登录尝试"""
    now = time.time()
    if not success:
        login_attempts[ip_address].append(now)
    else:
        # 登录成功时清除该IP的尝试记录
        if ip_address in login_attempts:
            del login_attempts[ip_address]


# CSRF保护
def generate_csrf_token():
    """生成CSRF令牌"""
    if 'csrf_token' not in session:
        session['csrf_token'] = secrets.token_hex(32)
    return session['csrf_token']

def validate_csrf_token():
    """验证CSRF令牌"""
    token = request.form.get('csrf_token')
    return token and hmac.compare_digest(token, session.get('csrf_token', ''))

def csrf_protect(f):
    """CSRF保护装饰器"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if request.method in ['POST', 'PUT', 'DELETE', 'PATCH']:
            if not validate_csrf_token():
                return '❌ CSRF令牌验证失败', 403
        return f(*args, **kwargs)
    return decorated_function

# ====================== 主页 ======================
@app.route('/', methods=['GET', 'POST'])
@csrf_protect
def index():
    if request.method == 'POST':
        if 'file' not in request.files:
            return '没有文件上传'
        file = request.files['file']
        if file.filename == '':
            return '未选择文件'
        filename = safe_filename(file.filename)
        # 检查文件是否已存在，如果存在则生成唯一文件名
        unique_filename = get_unique_filename(filename)
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], unique_filename))
        return redirect(url_for('index'))

    files = get_file_list()
    return render_template('index.html', files=files, csrf_token=generate_csrf_token())

# ====================== 下载 ======================
@app.route('/download/<filename>')
def download(filename):
    # URL解码文件名
    filename = urllib.parse.unquote(filename)
    # 安全处理文件名
    filename = safe_filename(filename)
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

# ====================== 管理员登录 + 面板 ======================
@app.route('/admin', methods=['GET', 'POST'])
@csrf_protect
def admin():
    error = None
    if request.method == 'POST':
        # 检查登录频率限制（使用真实IP）
        ip_address = get_real_ip()

        # 调试日志（生产环境可关闭）
        if os.getenv('DEBUG_IP', 'false').lower() == 'true':
            print(f"登录请求 - 原始IP: {request.remote_addr}, 真实IP: {ip_address}, X-Forwarded-For: {request.headers.get('X-Forwarded-For')}")

        allowed, rate_limit_error = check_login_rate_limit(ip_address)
        if not allowed:
            error = rate_limit_error
        else:
            provided_password = request.form.get('password')
            if verify_password(ADMIN_PASSWORD_HASH, provided_password):
                session['admin_logged_in'] = True
                record_login_attempt(ip_address, True)
                return redirect(url_for('admin'))
            else:
                error = '❌ 密码错误，请重试'
                record_login_attempt(ip_address, False)

    # 已登录 → 显示管理页面
    if session.get('admin_logged_in'):
        files = get_file_list()
        return render_template('admin_panel.html', files=files, csrf_token=generate_csrf_token())

    # 未登录 → 显示密码输入框
    return render_template('admin_login.html', error=error, csrf_token=generate_csrf_token())

# ====================== 删除 ======================
@app.route('/delete/<filename>', methods=['POST'])
@csrf_protect
def delete(filename):
    if not session.get('admin_logged_in'):
        return '❌ 请先登录', 403
    # URL解码文件名
    filename = urllib.parse.unquote(filename)
    filename = safe_filename(filename)
    path = os.path.join(UPLOAD_FOLDER, filename)
    if os.path.exists(path):
        os.remove(path)
        return redirect(url_for('admin'))
    return '文件不存在'

# ====================== 退出登录 ======================
@app.route('/logout')
def logout():
    session.pop('admin_logged_in', None)
    return redirect(url_for('index'))

if __name__ == '__main__':
    # 生产环境检测
    import sys
    is_production = os.getenv('FLASK_ENV') == 'production' or os.getenv('GUNICORN_WORKERS') is not None

    if is_production:
        print("🚀 生产环境模式启动")
        # 生产环境使用Gunicorn，这里只做配置检查
        print(f"📁 上传目录: {UPLOAD_FOLDER}")
        print(f"📏 最大文件大小: {MAX_FILE_SIZE_GB}GB")
        print(f"🔐 会话密钥长度: {len(SESSION_SECRET)}字符")
        print("✅ 配置检查完成，等待Gunicorn启动...")
    else:
        print("🔧 开发环境模式启动")
        app.run(host='0.0.0.0', port=5000, debug=False)
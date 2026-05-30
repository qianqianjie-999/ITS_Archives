# ADR-004: 采用 JWT 认证机制

## 状态
已接受

## 背景
系统需要实现用户认证功能，支持前后端分离架构。用户登录后需要保持会话状态，传统的Session-Cookie方式在跨域和移动端支持方面存在局限性。

## 决策
采用 JWT (JSON Web Token) 作为认证机制。

### 核心组件

| 组件 | 说明 |
|------|------|
| PyJWT | JWT编码和解码 |
| Werkzeug | 密码哈希（pbkdf2:sha256） |
| Flask装饰器 | `@token_required`, `@role_required` |

### Token结构

```python
payload = {
    'user_id': user.id,
    'username': username,
    'role': role,
    'exp': datetime.now(timezone.utc) + timedelta(seconds=Config.JWT_ACCESS_TOKEN_EXPIRES)
}
return jwt.encode(payload, Config.JWT_SECRET_KEY, algorithm='HS256')
```

### 认证流程

```
用户登录请求
    ↓
验证用户名密码（pbkdf2:sha256）
    ↓
生成JWT Token（24小时有效期）
    ↓
返回Token给客户端
    ↓
客户端存储Token（localStorage/sessionStorage）
    ↓
后续请求携带Token（Authorization: Bearer <token>）
    ↓
服务端验证Token并获取用户信息
```

### 角色权限控制

| 角色 | 创建 | 更新 | 删除 | 查看 |
|------|------|------|------|------|
| admin | ✅ | ✅ | ✅ | ✅ |
| editor | ✅ | ✅ | ❌ | ✅ |
| viewer | ❌ | ❌ | ❌ | ✅ |

### 实现细节

**Token验证装饰器** (`@token_required`):
```python
def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return {'status': 'error', 'message': '请先登录'}, 401

        token = auth_header.split(' ')[1]
        try:
            payload = jwt.decode(token, Config.JWT_SECRET_KEY, algorithms=['HS256'])
            user = db.session.query(User).get(payload['user_id'])
            if not user or not user.is_active:
                return {'status': 'error', 'message': '用户不存在或已禁用'}, 401
            g.current_user = user
        except jwt.ExpiredSignatureError:
            return {'status': 'error', 'message': '令牌已过期'}, 401
        except jwt.InvalidTokenError:
            return {'status': 'error', 'message': '无效令牌'}, 401

        return f(*args, **kwargs)
    return decorated
```

**角色验证装饰器** (`@role_required`):
```python
def role_required(*roles):
    def decorator(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            if not hasattr(g, 'current_user') or not g.current_user:
                return {'status': 'error', 'message': '请先登录'}, 401
            if g.current_user.role not in roles:
                return {'status': 'error', 'message': '权限不足'}, 403
            return f(*args, **kwargs)
        return decorated
    return decorator
```

### 配置项

| 配置项 | 默认值 | 说明 |
|--------|--------|------|
| JWT_SECRET_KEY | - | 必须设置（生产环境） |
| JWT_ACCESS_TOKEN_EXPIRES | 86400 | Token有效期（秒） |

**警告**：未设置JWT_SECRET_KEY时会有运行时警告。

## 替代方案考虑

| 替代方案 | 优点 | 缺点 |
|---------|------|------|
| Session-Cookie | 实现简单，服务器控制 | 跨域麻烦，不适合移动端 |
| OAuth2.0 | 标准化，支持第三方登录 | 实现复杂 |
| Basic Auth | 极其简单 | 不安全，每次请求都传输密码 |

## 后果

### 正面
- 无状态认证，易于水平扩展
- 跨域支持好，适合移动端和SPA应用
- Token可包含用户信息，减少数据库查询
- 前端完全解耦，可支持多客户端

### 负面
- Token一旦签发无法撤销（直到过期）
- Token体积比Session ID大
- 需要自行实现登出逻辑（黑名单或缩短有效期）
- 需要注意Token安全存储（XSS防护）

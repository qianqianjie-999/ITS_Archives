from functools import wraps
import time
import jwt
from typing import Optional
from flask import request, g
from ..models.user import User
from ..extensions import db
from ..config import Config

# 简单的内存速率限制器
_rate_limit_store: dict[str, list[float]] = {}

def rate_limit(max_requests: int = 5, window_seconds: int = 60):
    """
    基于IP的简单速率限制装饰器。

    参数:
        max_requests: 时间窗口内允许的最大请求数
        window_seconds: 时间窗口大小（秒）
    """
    def decorator(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            client_ip = request.remote_addr or '127.0.0.1'
            now = time.time()
            window_start = now - window_seconds

            # 清理过期记录
            if client_ip in _rate_limit_store:
                _rate_limit_store[client_ip] = [
                    t for t in _rate_limit_store[client_ip] if t > window_start
                ]
            else:
                _rate_limit_store[client_ip] = []

            if len(_rate_limit_store[client_ip]) >= max_requests:
                return {
                    'status': 'error',
                    'message': f'请求过于频繁，请在 {window_seconds} 秒后重试'
                }, 429

            _rate_limit_store[client_ip].append(now)
            return f(*args, **kwargs)
        return decorated
    return decorator

_JWT_OPTIONS = {
    'verify_signature': True,
    'verify_exp': True,
    'verify_iss': True,
    'verify_aud': True,
    'require': ['exp', 'iss', 'aud', 'user_id'],
}


def _decode_token(token: str) -> dict:
    return jwt.decode(
        token,
        Config.JWT_SECRET_KEY,
        algorithms=['HS256'],
        issuer=Config.JWT_ISSUER,
        audience=Config.JWT_AUDIENCE,
        options=_JWT_OPTIONS,
    )


def _extract_token() -> Optional[str]:
    """从 Authorization 头或 ?token= 查询参数中提取 JWT 令牌。"""
    auth_header = request.headers.get('Authorization')
    if auth_header and auth_header.startswith('Bearer '):
        return auth_header.split(' ')[1]
    return request.args.get('token')


def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = _extract_token()
        if not token:
            return {'status': 'error', 'message': '请先登录'}, 401

        try:
            payload = _decode_token(token)
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


def admin_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = _extract_token()
        if not token:
            return {'status': 'error', 'message': '请先登录'}, 401

        try:
            payload = _decode_token(token)
            user = db.session.query(User).get(payload['user_id'])
            if not user or not user.is_active:
                return {'status': 'error', 'message': '用户不存在或已禁用'}, 401
            if user.role != 'admin':
                return {'status': 'error', 'message': '权限不足'}, 403
            g.current_user = user
        except jwt.ExpiredSignatureError:
            return {'status': 'error', 'message': '令牌已过期'}, 401
        except jwt.InvalidTokenError:
            return {'status': 'error', 'message': '无效令牌'}, 401

        return f(*args, **kwargs)
    return decorated
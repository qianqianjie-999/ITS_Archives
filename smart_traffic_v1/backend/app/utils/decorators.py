from functools import wraps
import jwt
from flask import request, g
from ..models.user import User
from ..extensions import db
from ..config import Config

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


def log_operation(operation_type, entity_type, entity_id, old_value=None, new_value=None):
    from datetime import datetime
    import json
    from ..models.user import OperationLog

    log = OperationLog(
        user_id=g.current_user.id if hasattr(g, 'current_user') else None,
        username=g.current_user.username if hasattr(g, 'current_user') else None,
        operation_type=operation_type,
        entity_type=entity_type,
        entity_id=entity_id,
        old_value=json.dumps(old_value) if old_value else None,
        new_value=json.dumps(new_value) if new_value else None,
        ip_address=request.remote_addr
    )
    db.session.add(log)
    db.session.commit()
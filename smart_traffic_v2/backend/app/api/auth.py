from flask import request, session
from flask_restx import Namespace, Resource, fields
from datetime import datetime, timedelta
import jwt
from ..extensions import db
from ..models.user import User
from ..config import Config

ns = Namespace('auth', description='认证相关操作')

login_model = ns.model('Login', {
    'username': fields.String(required=True, description='用户名'),
    'password': fields.String(required=True, description='密码')
})

user_model = ns.model('User', {
    'id': fields.Integer(readonly=True),
    'username': fields.String(),
    'display_name': fields.String(),
    'role': fields.String()
})

def generate_token(user_id: int, username: str, role: str) -> str:
    payload = {
        'user_id': user_id,
        'username': username,
        'role': role,
        'exp': datetime.utcnow() + timedelta(seconds=Config.JWT_ACCESS_TOKEN_EXPIRES)
    }
    return jwt.encode(payload, Config.JWT_SECRET_KEY, algorithm='HS256')

@ns.route('/login')
class Login(Resource):
    @ns.expect(login_model)
    def post(self):
        data = request.json
        username = data.get('username')
        password = data.get('password')

        if not username or not password:
            return {'status': 'error', 'message': '请输入用户名和密码'}, 400

        user = db.session.query(User).filter_by(username=username, is_active=True).first()

        if user and user.check_password(password):
            user.last_login = datetime.utcnow()
            db.session.commit()

            token = generate_token(user.id, user.username, user.role)

            return {
                'status': 'success',
                'token': token,
                'user': user.to_dict()
            }
        else:
            return {'status': 'error', 'message': '用户名或密码错误'}, 401


@ns.route('/logout')
class Logout(Resource):
    def post(self):
        return {'status': 'success'}


@ns.route('/current_user')
class CurrentUser(Resource):
    def get(self):
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return {'status': 'error', 'message': '未登录'}, 401

        token = auth_header.split(' ')[1]
        try:
            payload = jwt.decode(token, Config.JWT_SECRET_KEY, algorithms=['HS256'])
            user = db.session.query(User).get(payload['user_id'])
            if not user:
                return {'status': 'error', 'message': '用户不存在'}, 404
            return {'status': 'success', 'user': user.to_dict()}
        except jwt.ExpiredSignatureError:
            return {'status': 'error', 'message': '令牌已过期'}, 401
        except jwt.InvalidTokenError:
            return {'status': 'error', 'message': '无效令牌'}, 401
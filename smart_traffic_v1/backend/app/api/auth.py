from flask import request, session, g
from flask_restx import Namespace, Resource, fields
from datetime import datetime, timedelta, timezone
import jwt
from ..extensions import db
from ..models.user import User
from ..config import Config
from ..utils.decorators import token_required

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
        'exp': datetime.now(timezone.utc) + timedelta(seconds=Config.JWT_ACCESS_TOKEN_EXPIRES)
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
            user.last_login = datetime.now(timezone.utc)
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
    @token_required
    def post(self):
        return {'status': 'success'}


@ns.route('/current_user')
class CurrentUser(Resource):
    @token_required
    def get(self):
        user = db.session.query(User).filter_by(id=g.current_user.id, is_active=True).first()
        if not user:
            return {'status': 'error', 'message': '用户不存在或已禁用'}, 401
        return {
            'status': 'success',
            'user': user.to_dict()
        }
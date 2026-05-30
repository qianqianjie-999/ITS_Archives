from flask import request
from flask_restx import Namespace, Resource, fields
from ..models.user import User
from ..extensions import db
from ..utils.decorators import admin_required
from datetime import datetime

ns = Namespace('users', description='用户管理')

user_model = ns.model('User', {
    'id': fields.Integer(readOnly=True, description='用户ID'),
    'username': fields.String(required=True, description='用户名'),
    'display_name': fields.String(description='显示名称'),
    'role': fields.String(enum=['admin', 'editor', 'viewer'], description='角色'),
    'is_active': fields.Boolean(description='是否激活'),
    'last_login': fields.DateTime(readOnly=True, description='最后登录时间'),
    'created_at': fields.DateTime(readOnly=True, description='创建时间')
})

user_create_model = ns.model('UserCreate', {
    'username': fields.String(required=True, description='用户名'),
    'password': fields.String(required=True, description='密码'),
    'display_name': fields.String(description='显示名称'),
    'role': fields.String(enum=['admin', 'editor', 'viewer'], default='viewer', description='角色')
})

user_update_model = ns.model('UserUpdate', {
    'display_name': fields.String(description='显示名称'),
    'role': fields.String(enum=['admin', 'editor', 'viewer'], description='角色'),
    'is_active': fields.Boolean(description='是否激活'),
    'password': fields.String(description='新密码（可选）')
})


@ns.route('/')
class UserList(Resource):
    @ns.doc('list_users')
    @ns.marshal_list_with(user_model)
    @admin_required
    def get(self):
        """获取所有用户列表"""
        users = User.query.all()
        return [user.to_dict() for user in users]

    @ns.doc('create_user')
    @ns.expect(user_create_model)
    @ns.marshal_with(user_model)
    @admin_required
    def post(self):
        """创建新用户"""
        data = request.json
        if User.query.filter_by(username=data['username']).first():
            ns.abort(400, '用户名已存在')
        
        user = User(
            username=data['username'],
            display_name=data.get('display_name'),
            role=data.get('role', 'viewer'),
            is_active=True
        )
        user.set_password(data['password'])
        db.session.add(user)
        db.session.commit()
        return user.to_dict(), 201


@ns.route('/<int:user_id>')
@ns.param('user_id', '用户ID')
@ns.response(404, '用户不存在')
class UserResource(Resource):
    @ns.doc('get_user')
    @ns.marshal_with(user_model)
    @admin_required
    def get(self, user_id):
        """获取单个用户信息"""
        user = User.query.get_or_404(user_id)
        return user.to_dict()

    @ns.doc('update_user')
    @ns.expect(user_update_model)
    @ns.marshal_with(user_model)
    @admin_required
    def put(self, user_id):
        """更新用户信息"""
        user = User.query.get_or_404(user_id)
        data = request.json
        
        if 'display_name' in data:
            user.display_name = data['display_name']
        if 'role' in data:
            user.role = data['role']
        if 'is_active' in data:
            user.is_active = data['is_active']
        if 'password' in data and data['password']:
            user.set_password(data['password'])
        
        db.session.commit()
        return user.to_dict()

    @ns.doc('delete_user')
    @ns.response(204, '删除成功')
    @admin_required
    def delete(self, user_id):
        """删除用户"""
        user = User.query.get_or_404(user_id)
        db.session.delete(user)
        db.session.commit()
        return '', 204
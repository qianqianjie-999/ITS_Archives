from flask import Blueprint
from flask_restx import Api

api_bp = Blueprint('api', __name__, url_prefix='/api')

api = Api(
    api_bp,
    version='1.0',
    title='智能交通档案系统 API',
    description='提供路口、点位、项目等管理接口',
    doc='/docs'
)

from .auth import ns as auth_ns
from .intersections import ns as intersections_ns
from .points import ns as points_ns
from .projects import ns as projects_ns
from .attachments import ns as attachments_ns
from .logs import ns as logs_ns

api.add_namespace(auth_ns, path='/auth')
api.add_namespace(intersections_ns, path='/intersections')
api.add_namespace(points_ns, path='/points')
api.add_namespace(projects_ns, path='/projects')
api.add_namespace(attachments_ns, path='/attachments')
api.add_namespace(logs_ns, path='/logs')
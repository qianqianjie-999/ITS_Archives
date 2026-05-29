import os
from flask import Flask
from sqlalchemy.exc import IntegrityError
from .extensions import db, cors, migrate
from .config import config


def create_app(config_name=None):
    if config_name is None:
        config_name = os.environ.get('FLASK_CONFIG', 'default')

    app = Flask(__name__)
    app.config.from_object(config[config_name])

    db.init_app(app)
    allowed_origins = os.environ.get('CORS_ORIGINS', 'http://localhost:5173,http://localhost:3000').split(',')
    cors.init_app(app, resources={r"/api/*": {"origins": allowed_origins}})
    migrate.init_app(app, db)

    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

    from .api import api_bp
    app.register_blueprint(api_bp)

    from .api.auth import ns as auth_ns
    from .api.intersections import ns as intersections_ns
    from .api.points import ns as points_ns
    from .api.projects import ns as projects_ns
    from .api.attachments import ns as attachments_ns
    from .api.logs import ns as logs_ns

    @app.errorhandler(IntegrityError)
    def handle_integrity_error(error):
        db.session.rollback()
        error_msg = str(error.orig) if error.orig else str(error)
        if 'Duplicate entry' in error_msg:
            return {'status': 'error', 'message': '名称已存在，请使用不同的名称'}, 409
        return {'status': 'error', 'message': '数据冲突，操作失败'}, 409

    @app.route('/health')
    def health_check():
        return {'status': 'healthy', 'message': '智能交通档案系统 API 运行中'}

    return app
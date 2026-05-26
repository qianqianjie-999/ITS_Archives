import os
from flask import Flask
from .extensions import db, cors, migrate
from .config import config


def create_app(config_name=None):
    if config_name is None:
        config_name = os.environ.get('FLASK_CONFIG', 'default')

    app = Flask(__name__)
    app.config.from_object(config[config_name])

    db.init_app(app)
    cors.init_app(app, resources={r"/api/*": {"origins": "*"}})
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

    @app.route('/health')
    def health_check():
        return {'status': 'healthy', 'message': '智能交通档案系统 API 运行中'}

    return app
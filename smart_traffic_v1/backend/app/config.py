import os
from dotenv import load_dotenv

load_dotenv()


def _require_env(name: str) -> str:
    """获取必需的环境变量，未设置则抛出错误。"""
    value = os.environ.get(name)
    if not value:
        raise ValueError(
            f'环境变量 {name} 未设置。请检查 .env 文件或系统环境变量。'
        )
    return value


class Config:
    SECRET_KEY = _require_env('SECRET_KEY').encode()

    DB_HOST = os.environ.get('DB_HOST', 'localhost')
    DB_PORT = int(os.environ.get('DB_PORT', 3306))
    DB_USER = os.environ.get('DB_USER', 'smart_traffic')
    DB_PASSWORD = _require_env('DB_PASSWORD')
    DB_NAME = os.environ.get('DB_NAME', 'smart_traffic')

    SQLALCHEMY_DATABASE_URI = (
        f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
        "?charset=utf8mb4"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_pre_ping': True,
        'pool_recycle': 300,
    }

    UPLOAD_FOLDER = os.path.abspath(os.environ.get('UPLOAD_FOLDER', 'uploads'))
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024
    ALLOWED_EXTENSIONS = {'pdf', 'doc', 'docx', 'xls', 'xlsx', 'jpg', 'jpeg', 'png', 'zip', 'rar'}

    JWT_SECRET_KEY = _require_env('JWT_SECRET_KEY')
    JWT_ACCESS_TOKEN_EXPIRES = 86400
    JWT_ISSUER = os.environ.get('JWT_ISSUER', 'smart-traffic-archive')
    JWT_AUDIENCE = os.environ.get('JWT_AUDIENCE', 'smart-traffic-api')

class DevelopmentConfig(Config):
    DEBUG = True

class ProductionConfig(Config):
    DEBUG = False

config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}
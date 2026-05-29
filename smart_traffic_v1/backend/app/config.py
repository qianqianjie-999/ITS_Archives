import os
import warnings
from dotenv import load_dotenv

load_dotenv()

class Config:
    _secret_key = os.environ.get('SECRET_KEY')
    if not _secret_key:
        warnings.warn('SECRET_KEY 未在环境变量中设置，使用不安全的默认值。生产环境请务必设置！', RuntimeWarning)
        _secret_key = 'dev-secret-key-change-in-production'

    SECRET_KEY = _secret_key.encode() if isinstance(_secret_key, str) else _secret_key

    DB_HOST = os.environ.get('DB_HOST', 'localhost')
    DB_PORT = int(os.environ.get('DB_PORT', 3306))
    DB_USER = os.environ.get('DB_USER', 'root')
    DB_PASSWORD = os.environ.get('DB_PASSWORD', '123456')
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

    _jwt_key = os.environ.get('JWT_SECRET_KEY')
    if not _jwt_key:
        warnings.warn('JWT_SECRET_KEY 未在环境变量中设置，使用不安全的默认值。生产环境请务必设置！', RuntimeWarning)
        _jwt_key = 'dev-jwt-secret-key-change-in-production'

    JWT_SECRET_KEY = _jwt_key
    JWT_ACCESS_TOKEN_EXPIRES = 86400

class DevelopmentConfig(Config):
    DEBUG = True

class ProductionConfig(Config):
    DEBUG = False

config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}
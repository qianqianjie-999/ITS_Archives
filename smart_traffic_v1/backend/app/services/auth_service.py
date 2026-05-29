from datetime import datetime, timezone
from ..extensions import db
from ..models.user import User


class AuthService:
    @staticmethod
    def authenticate(username: str, password: str) -> tuple:
        user = db.session.query(User).filter_by(username=username, is_active=True).first()

        if not user:
            return None, '用户不存在'

        if not user.check_password(password):
            return None, '密码错误'

        user.last_login = datetime.now(timezone.utc)
        db.session.commit()

        return user, None

    @staticmethod
    def create_user(username: str, password: str, display_name: str = None, role: str = 'viewer') -> User:
        user = User(
            username=username,
            display_name=display_name or username,
            role=role
        )
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        return user
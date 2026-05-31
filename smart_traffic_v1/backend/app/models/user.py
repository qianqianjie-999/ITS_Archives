from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy import String, Boolean, Enum, TIMESTAMP
from sqlalchemy.orm import Mapped, mapped_column
from typing import Optional
from ..extensions import db

class User(db.Model):
    __tablename__ = 'user'

    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    display_name: Mapped[Optional[str]] = mapped_column(String(100))
    role: Mapped[str] = mapped_column(Enum('admin', 'editor', 'viewer', name='user_role'), default='viewer')
    created_at: Mapped[datetime] = mapped_column(TIMESTAMP, server_default=db.text('CURRENT_TIMESTAMP'))
    last_login: Mapped[Optional[datetime]] = mapped_column(TIMESTAMP, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    def set_password(self, password: str):
        self.password_hash = generate_password_hash(password, method='pbkdf2:sha256')

    def check_password(self, password: str) -> bool:
        return check_password_hash(self.password_hash, password)

    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'display_name': self.display_name,
            'role': self.role,
            'is_active': self.is_active,
            'last_login': self.last_login.isoformat() if self.last_login else None
        }
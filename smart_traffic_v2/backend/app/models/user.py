from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy import String, Boolean, Enum, TIMESTAMP
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import Optional, List
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

    operation_logs: Mapped[List["OperationLog"]] = relationship(back_populates="user")

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


class OperationLog(db.Model):
    __tablename__ = 'operation_log'

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[Optional[int]] = mapped_column(db.ForeignKey('user.id'))
    username: Mapped[Optional[str]] = mapped_column(String(50))
    operation_type: Mapped[str] = mapped_column(String(50), nullable=False)
    entity_type: Mapped[Optional[str]] = mapped_column(String(50))
    entity_id: Mapped[Optional[int]] = mapped_column()
    old_value: Mapped[Optional[str]] = mapped_column(db.Text)
    new_value: Mapped[Optional[str]] = mapped_column(db.Text)
    ip_address: Mapped[Optional[str]] = mapped_column(String(50))
    operation_time: Mapped[datetime] = mapped_column(TIMESTAMP, server_default=db.text('CURRENT_TIMESTAMP'))

    user: Mapped[Optional["User"]] = relationship(back_populates="operation_logs")

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'username': self.username,
            'operation_type': self.operation_type,
            'entity_type': self.entity_type,
            'entity_id': self.entity_id,
            'old_value': self.old_value,
            'new_value': self.new_value,
            'ip_address': self.ip_address,
            'operation_time': self.operation_time.isoformat() if self.operation_time else None
        }
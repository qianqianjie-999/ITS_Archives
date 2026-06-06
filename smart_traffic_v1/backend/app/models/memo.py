from datetime import datetime, timezone
from sqlalchemy import String, Integer, Text, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import Optional, List
from ..extensions import db


class Memo(db.Model):
    __tablename__ = 'memo_list'

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(128), nullable=False)  # 主题
    content: Mapped[Optional[str]] = mapped_column(Text, nullable=True)  # 事件内容
    happen_time: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)  # 事件发生时间
    create_user: Mapped[str] = mapped_column(String(64), nullable=False)  # 记录人
    create_time: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))  # 创建时间
    update_time: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))  # 更新时间
    is_del: Mapped[int] = mapped_column(Integer, default=0)  # 软删除标记：0正常 1删除
    
    # 关联附件
    attachments = relationship('MemoAttachment', back_populates='memo', cascade='all, delete-orphan')

    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'content': self.content,
            'happen_time': self.happen_time.isoformat() if self.happen_time else None,
            'create_user': self.create_user,
            'create_time': self.create_time.isoformat() if self.create_time else None,
            'update_time': self.update_time.isoformat() if self.update_time else None,
            'is_del': self.is_del,
            'attachments': [att.to_dict() for att in self.attachments] if self.attachments else []
        }


class MemoAttachment(db.Model):
    __tablename__ = 'memo_attachment'

    aid: Mapped[int] = mapped_column(primary_key=True)
    memo_id: Mapped[int] = mapped_column(Integer, ForeignKey('memo_list.id', ondelete='CASCADE'), nullable=False)
    file_name: Mapped[str] = mapped_column(String(255), nullable=False)  # 原文件名
    file_path: Mapped[str] = mapped_column(String(512), nullable=False)  # 服务器存储路径
    file_size: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)  # 文件大小(字节)
    file_type: Mapped[Optional[str]] = mapped_column(String(32), nullable=True)  # 文件后缀
    upload_time: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))  # 上传时间

    # 关联备忘录
    memo = relationship('Memo', back_populates='attachments')

    def to_dict(self):
        return {
            'aid': self.aid,
            'memo_id': self.memo_id,
            'file_name': self.file_name,
            'file_path': self.file_path,
            'file_size': self.file_size,
            'file_type': self.file_type,
            'upload_time': self.upload_time.isoformat() if self.upload_time else None
        }
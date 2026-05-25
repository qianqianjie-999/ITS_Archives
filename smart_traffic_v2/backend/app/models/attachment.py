from sqlalchemy import String, Integer, Text, ForeignKey, TIMESTAMP
from sqlalchemy.orm import Mapped, mapped_column
from typing import Optional
from datetime import datetime
from ..extensions import db

class Attachment(db.Model):
    __tablename__ = 'attachment'

    id: Mapped[int] = mapped_column(primary_key=True)
    related_entity_type: Mapped[str] = mapped_column(String(50), nullable=False)
    related_entity_id: Mapped[int] = mapped_column(nullable=False)
    file_name: Mapped[str] = mapped_column(String(255), nullable=False)
    file_path: Mapped[str] = mapped_column(String(500), nullable=False)
    file_size: Mapped[Optional[int]] = mapped_column(Integer)
    mime_type: Mapped[Optional[str]] = mapped_column(String(100))
    upload_time: Mapped[datetime] = mapped_column(TIMESTAMP, server_default=db.text('CURRENT_TIMESTAMP'))
    uploaded_by: Mapped[Optional[str]] = mapped_column(String(100))
    description: Mapped[Optional[str]] = mapped_column(Text)

    def to_dict(self):
        return {
            'id': self.id,
            'related_entity_type': self.related_entity_type,
            'related_entity_id': self.related_entity_id,
            'file_name': self.file_name,
            'file_path': self.file_path,
            'file_size': self.file_size,
            'mime_type': self.mime_type,
            'upload_time': self.upload_time.isoformat() if self.upload_time else None,
            'uploaded_by': self.uploaded_by,
            'description': self.description
        }
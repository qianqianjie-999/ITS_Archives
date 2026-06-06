from sqlalchemy import String, Integer, Text, ForeignKey, TIMESTAMP
from sqlalchemy.orm import Mapped, mapped_column
from typing import Optional
from datetime import datetime, timezone
from ..extensions import db

def format_datetime(dt: datetime) -> str:
    if dt is None:
        return None
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    else:
        dt = dt.astimezone(timezone.utc)
    return dt.isoformat()

class Attachment(db.Model):
    __tablename__ = 'attachments'

    id: Mapped[int] = mapped_column(primary_key=True)
    related_entity_type: Mapped[str] = mapped_column(String(50), nullable=False)
    related_entity_id: Mapped[int] = mapped_column(nullable=False)
    file_name: Mapped[str] = mapped_column(String(255), nullable=False)
    file_path: Mapped[str] = mapped_column(String(500), nullable=False)
    original_filename: Mapped[str] = mapped_column(String(255), nullable=False)
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
            'original_filename': self.original_filename,
            'file_size': self.file_size,
            'mime_type': self.mime_type,
            'upload_time': format_datetime(self.upload_time),
            'uploaded_by': self.uploaded_by,
            'description': self.description
        }
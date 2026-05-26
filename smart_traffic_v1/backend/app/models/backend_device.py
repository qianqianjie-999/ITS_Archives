from sqlalchemy import String, Integer, Text, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import Optional
from ..extensions import db

class BackendDevice(db.Model):
    __tablename__ = 'backend_device'

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    type: Mapped[Optional[str]] = mapped_column(String(50))
    project_id: Mapped[int] = mapped_column(ForeignKey('project.id'), nullable=False)

    project: Mapped["Project"] = relationship(back_populates="backend_devices")

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'type': self.type,
            'project_id': self.project_id,
            'project_name': self.project.name if self.project else None
        }
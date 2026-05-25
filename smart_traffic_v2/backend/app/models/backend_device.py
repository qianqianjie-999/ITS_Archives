from sqlalchemy import String, Integer, Text, ForeignKey, Date
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


class WarrantyExtension(db.Model):
    __tablename__ = 'warranty_extension'

    id: Mapped[int] = mapped_column(primary_key=True)
    facility_type: Mapped[str] = mapped_column(String(50), nullable=False)
    facility_id: Mapped[int] = mapped_column(nullable=False)
    project_id: Mapped[int] = mapped_column(ForeignKey('project.id'), nullable=False)
    extension_date: Mapped[Date] = mapped_column(Date, nullable=False)

    project: Mapped["Project"] = relationship(back_populates="warranty_extensions")

    def to_dict(self):
        return {
            'id': self.id,
            'facility_type': self.facility_type,
            'facility_id': self.facility_id,
            'project_id': self.project_id,
            'project_name': self.project.name if self.project else None,
            'extension_date': self.extension_date.isoformat() if self.extension_date else None
        }
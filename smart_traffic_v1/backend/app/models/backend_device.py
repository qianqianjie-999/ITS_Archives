from sqlalchemy import String, Integer, Text, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import Optional, List
from datetime import date
from ..extensions import db

class BackendDevice(db.Model):
    __tablename__ = 'backend_device'

    id: Mapped[int] = mapped_column(primary_key=True)
    point_id: Mapped[Optional[int]] = mapped_column(ForeignKey('point.id'))
    project_id: Mapped[Optional[int]] = mapped_column(ForeignKey('project.id'))
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    type: Mapped[Optional[str]] = mapped_column(String(50))

    point: Mapped[Optional["Point"]] = relationship(back_populates="backend_devices")
    project: Mapped["Project"] = relationship(back_populates="backend_devices")

    @property
    def warranty_status(self) -> str:
        if self.project and self.project.warranty_expire_date:
            if self.project.warranty_expire_date >= date.today():
                return '在保'
            else:
                return '过保'
        return '无项目'

    def to_dict(self):
        return {
            'id': self.id,
            'point_id': self.point_id,
            'project_id': self.project_id,
            'project_name': self.project.name if self.project else None,
            'acceptance_date': self.project.acceptance_date.isoformat() if self.project and self.project.acceptance_date else None,
            'warranty_period': self.project.warranty_period if self.project else None,
            'warranty_expire_date': self.project.warranty_expire_date.isoformat() if self.project and self.project.warranty_expire_date else None,
            'warranty_status': self.warranty_status,
            'name': self.name,
            'type': self.type,
            'construction_unit': self.project.construction_unit if self.project else None,
            'construction_company': self.project.builder if self.project else None
        }
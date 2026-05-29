from sqlalchemy import String, Integer, Date, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import Optional
from ..extensions import db

class WarrantyExtension(db.Model):
    __tablename__ = 'warranty_extension'

    id: Mapped[int] = mapped_column(primary_key=True)
    facility_type: Mapped[str] = mapped_column(String(50), nullable=False)
    facility_id: Mapped[int] = mapped_column(Integer, nullable=False)
    project_id: Mapped[int] = mapped_column(ForeignKey('project.id'), nullable=False)
    extension_date: Mapped[Optional[Date]] = mapped_column(Date, nullable=False)

    project: Mapped["Project"] = relationship(back_populates="warranty_extensions")

    def to_dict(self):
        return {
            'id': self.id,
            'facility_type': self.facility_type,
            'facility_id': self.facility_id,
            'project_id': self.project_id,
            'project_name': self.project.name if self.project else None,
            'warranty_expire_date': self.project.warranty_expire_date.isoformat() if self.project else None,
            'extension_date': self.extension_date.isoformat() if self.extension_date else None
        }
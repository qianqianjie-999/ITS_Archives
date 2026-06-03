from sqlalchemy import String, Integer, Text, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import datetime
from typing import Optional
from ..extensions import db

class MaintenanceRecord(db.Model):
    __tablename__ = 'maintenance_record'

    id: Mapped[int] = mapped_column(primary_key=True)
    facility_type: Mapped[str] = mapped_column(String(50), nullable=False)
    facility_id: Mapped[int] = mapped_column(Integer, nullable=False)
    fault_level: Mapped[str] = mapped_column(String(20), nullable=False)
    fault_description: Mapped[str] = mapped_column(Text, nullable=False)
    fault_time: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    solution: Mapped[Optional[str]] = mapped_column(Text)
    record_time: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.now)
    recorder_id: Mapped[int] = mapped_column(ForeignKey('user.id'), nullable=False)

    recorder: Mapped["User"] = relationship("User", foreign_keys=[recorder_id])

    def to_dict(self):
        return {
            'id': self.id,
            'facility_type': self.facility_type,
            'facility_id': self.facility_id,
            'fault_level': self.fault_level,
            'fault_level_text': self.get_fault_level_text(),
            'fault_description': self.fault_description,
            'fault_time': self.fault_time.isoformat() if self.fault_time else None,
            'solution': self.solution,
            'record_time': self.record_time.isoformat() if self.record_time else None,
            'recorder_id': self.recorder_id,
            'recorder_name': self.recorder.display_name if self.recorder else None
        }

    def get_fault_level_text(self):
        level_map = {
            'high': '高',
            'medium': '中',
            'low': '低'
        }
        return level_map.get(self.fault_level, self.fault_level)
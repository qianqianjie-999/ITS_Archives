from sqlalchemy import String, Integer, Text, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import Optional, List
from datetime import date
from ..extensions import db

class Point(db.Model):
    __tablename__ = 'point'

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    area: Mapped[Optional[str]] = mapped_column(String(100))
    type: Mapped[Optional[str]] = mapped_column(String(50))

    parking_enforcements: Mapped[List["ParkingEnforcement"]] = relationship(back_populates="point", cascade="all, delete-orphan")
    checkpoints: Mapped[List["Checkpoint"]] = relationship(back_populates="point", cascade="all, delete-orphan")
    backend_devices: Mapped[List["BackendDevice"]] = relationship(back_populates="point", cascade="all, delete-orphan")

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'area': self.area,
            'type': self.type
        }

    @property
    def warranty_status(self) -> dict:
        expire_dates = []
        for pe in self.parking_enforcements:
            if pe.project and pe.project.warranty_expire_date:
                expire_dates.append(pe.project.warranty_expire_date)
        for cp in self.checkpoints:
            if cp.project and cp.project.warranty_expire_date:
                expire_dates.append(cp.project.warranty_expire_date)

        if not expire_dates:
            return {'status': '无项目', 'latest_expire_date': None}

        latest = max(expire_dates)
        return {
            'status': '在保' if latest >= date.today() else '过保',
            'latest_expire_date': latest.isoformat()
        }


class ParkingEnforcement(db.Model):
    __tablename__ = 'parking_enforcement'

    id: Mapped[int] = mapped_column(primary_key=True)
    point_id: Mapped[int] = mapped_column(ForeignKey('point.id'), nullable=False)
    project_id: Mapped[int] = mapped_column(ForeignKey('project.id'), nullable=False)
    camera_area: Mapped[Optional[str]] = mapped_column(String(200))
    camera_count: Mapped[int] = mapped_column(Integer, default=0)
    parking_sign_count: Mapped[int] = mapped_column(Integer, default=0)
    monitor_sign_count: Mapped[int] = mapped_column(Integer, default=0)
    power_source: Mapped[Optional[str]] = mapped_column(Text)
    network_source: Mapped[Optional[str]] = mapped_column(Text)

    point: Mapped["Point"] = relationship(back_populates="parking_enforcements")
    project: Mapped["Project"] = relationship(back_populates="parking_enforcements")

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
            'camera_area': self.camera_area,
            'camera_count': self.camera_count,
            'parking_sign_count': self.parking_sign_count,
            'monitor_sign_count': self.monitor_sign_count,
            'power_source': self.power_source,
            'network_source': self.network_source,
            'construction_unit': self.project.construction_unit if self.project else None,
            'construction_company': self.project.builder if self.project else None
        }


class Checkpoint(db.Model):
    __tablename__ = 'checkpoint'

    id: Mapped[int] = mapped_column(primary_key=True)
    point_id: Mapped[int] = mapped_column(ForeignKey('point.id'), nullable=False)
    project_id: Mapped[int] = mapped_column(ForeignKey('project.id'), nullable=False)
    checkpoint_type: Mapped[Optional[str]] = mapped_column(String(50))
    camera_count: Mapped[int] = mapped_column(Integer, default=0)
    strobe_light_count: Mapped[int] = mapped_column(Integer, default=0)
    radar_count: Mapped[int] = mapped_column(Integer, default=0)
    sign_count: Mapped[int] = mapped_column(Integer, default=0)
    power_source: Mapped[Optional[str]] = mapped_column(Text)
    network_source: Mapped[Optional[str]] = mapped_column(Text)

    point: Mapped["Point"] = relationship(back_populates="checkpoints")
    project: Mapped["Project"] = relationship(back_populates="checkpoints")

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
            'checkpoint_type': self.checkpoint_type,
            'camera_count': self.camera_count,
            'strobe_light_count': self.strobe_light_count,
            'radar_count': self.radar_count,
            'sign_count': self.sign_count,
            'power_source': self.power_source,
            'network_source': self.network_source,
            'construction_unit': self.project.construction_unit if self.project else None,
            'construction_company': self.project.builder if self.project else None
        }
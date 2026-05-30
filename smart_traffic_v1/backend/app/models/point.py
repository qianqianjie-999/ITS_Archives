from sqlalchemy import String, Integer, Text, ForeignKey, Date
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import Optional, List
from datetime import date
from ..extensions import db


class ParkingEnforcementPoint(db.Model):
    __tablename__ = 'parking_enforcement_point'

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False, unique=True)
    area: Mapped[Optional[str]] = mapped_column(String(100))
    type: Mapped[Optional[str]] = mapped_column(String(50))

    parking_enforcements: Mapped[List["ParkingEnforcement"]] = relationship(back_populates="point", cascade="all, delete-orphan")

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'area': self.area,
            'type': self.type
        }

    @property
    def warranty_status(self) -> dict:
        if not self.parking_enforcements:
            return {'status': '无项目', 'latest_expire_date': None}
        
        latest_pe = max(self.parking_enforcements, key=lambda pe: pe.id)
        expire_date = latest_pe.effective_warranty_expire_date

        if not expire_date:
            return {'status': '无项目', 'latest_expire_date': None}

        today = date.today()
        if expire_date >= today:
            status = '在保'
        else:
            status = '过保'

        return {
            'status': status,
            'latest_expire_date': expire_date.isoformat()
        }


class CheckpointPoint(db.Model):
    __tablename__ = 'checkpoint_point'

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False, unique=True)
    area: Mapped[Optional[str]] = mapped_column(String(100))
    type: Mapped[Optional[str]] = mapped_column(String(50))

    checkpoints: Mapped[List["Checkpoint"]] = relationship(back_populates="point", cascade="all, delete-orphan")

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'area': self.area,
            'type': self.type
        }

    @property
    def warranty_status(self) -> dict:
        if not self.checkpoints:
            return {'status': '无项目', 'latest_expire_date': None}
        
        latest_cp = max(self.checkpoints, key=lambda cp: cp.id)
        expire_date = latest_cp.effective_warranty_expire_date

        if not expire_date:
            return {'status': '无项目', 'latest_expire_date': None}

        today = date.today()
        if expire_date >= today:
            status = '在保'
        else:
            status = '过保'

        return {
            'status': status,
            'latest_expire_date': expire_date.isoformat()
        }


class ParkingEnforcement(db.Model):
    __tablename__ = 'parking_enforcement'

    id: Mapped[int] = mapped_column(primary_key=True)
    point_id: Mapped[int] = mapped_column(ForeignKey('parking_enforcement_point.id'), nullable=False)
    project_id: Mapped[int] = mapped_column(ForeignKey('project.id'), nullable=False)
    camera_area: Mapped[Optional[str]] = mapped_column(String(200))
    camera_count: Mapped[int] = mapped_column(Integer, default=0)
    parking_sign_count: Mapped[int] = mapped_column(Integer, default=0)
    monitor_sign_count: Mapped[int] = mapped_column(Integer, default=0)
    power_source: Mapped[Optional[str]] = mapped_column(Text)
    network_source: Mapped[Optional[str]] = mapped_column(Text)
    extended_warranty_expire_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)

    point: Mapped["ParkingEnforcementPoint"] = relationship(back_populates="parking_enforcements")
    project: Mapped["Project"] = relationship(back_populates="parking_enforcements")

    @property
    def effective_warranty_expire_date(self):
        if self.extended_warranty_expire_date:
            return self.extended_warranty_expire_date
        if self.project and self.project.warranty_expire_date:
            return self.project.warranty_expire_date
        return None

    @property
    def warranty_status(self) -> str:
        expire_date = self.effective_warranty_expire_date
        if expire_date:
            if expire_date >= date.today():
                return '在保'
            else:
                return '过保'
        return '无项目'

    def to_dict(self):
        return {
            'id': self.id,
            'point_id': self.point_id,
            'point_name': self.point.name if self.point else None,
            'project_id': self.project_id,
            'project_name': self.project.name if self.project else None,
            'acceptance_date': self.project.acceptance_date.isoformat() if self.project and self.project.acceptance_date else None,
            'warranty_period': self.project.warranty_period if self.project else None,
            'warranty_expire_date': self.effective_warranty_expire_date.isoformat() if self.effective_warranty_expire_date else None,
            'warranty_status': self.warranty_status,
            'camera_area': self.camera_area,
            'camera_count': self.camera_count,
            'parking_sign_count': self.parking_sign_count,
            'monitor_sign_count': self.monitor_sign_count,
            'power_source': self.power_source,
            'network_source': self.network_source,
            'construction_unit': self.project.builder if self.project else None,
            'construction_company': self.project.construction_unit if self.project else None
        }


class Checkpoint(db.Model):
    __tablename__ = 'checkpoint'

    id: Mapped[int] = mapped_column(primary_key=True)
    point_id: Mapped[int] = mapped_column(ForeignKey('checkpoint_point.id'), nullable=False)
    project_id: Mapped[int] = mapped_column(ForeignKey('project.id'), nullable=False)
    checkpoint_type: Mapped[Optional[str]] = mapped_column(String(50))
    camera_count: Mapped[int] = mapped_column(Integer, default=0)
    strobe_light_count: Mapped[int] = mapped_column(Integer, default=0)
    radar_count: Mapped[int] = mapped_column(Integer, default=0)
    sign_count: Mapped[int] = mapped_column(Integer, default=0)
    power_source: Mapped[Optional[str]] = mapped_column(Text)
    network_source: Mapped[Optional[str]] = mapped_column(Text)
    extended_warranty_expire_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)

    point: Mapped["CheckpointPoint"] = relationship(back_populates="checkpoints")
    project: Mapped["Project"] = relationship(back_populates="checkpoints")

    @property
    def effective_warranty_expire_date(self):
        if self.extended_warranty_expire_date:
            return self.extended_warranty_expire_date
        if self.project and self.project.warranty_expire_date:
            return self.project.warranty_expire_date
        return None

    @property
    def warranty_status(self) -> str:
        expire_date = self.effective_warranty_expire_date
        if expire_date:
            if expire_date >= date.today():
                return '在保'
            else:
                return '过保'
        return '无项目'

    def to_dict(self):
        return {
            'id': self.id,
            'point_id': self.point_id,
            'point_name': self.point.name if self.point else None,
            'point_type': self.point.area if self.point else None,
            'project_id': self.project_id,
            'project_name': self.project.name if self.project else None,
            'acceptance_date': self.project.acceptance_date.isoformat() if self.project and self.project.acceptance_date else None,
            'warranty_period': self.project.warranty_period if self.project else None,
            'warranty_expire_date': self.effective_warranty_expire_date.isoformat() if self.effective_warranty_expire_date else None,
            'warranty_status': self.warranty_status,
            'checkpoint_type': self.checkpoint_type,
            'camera_count': self.camera_count,
            'strobe_light_count': self.strobe_light_count,
            'radar_count': self.radar_count,
            'sign_count': self.sign_count,
            'power_source': self.power_source,
            'network_source': self.network_source,
            'construction_unit': self.project.builder if self.project else None,
            'construction_company': self.project.construction_unit if self.project else None
        }

from sqlalchemy import String, Integer, Text, ForeignKey, Enum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import Optional, List
from datetime import date
from ..extensions import db

class Intersection(db.Model):
    __tablename__ = 'intersection'

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False, unique=True)
    type: Mapped[Optional[str]] = mapped_column(Enum('十字路口', '丁字路口', '行人过街', '其他', name='intersection_type'))
    east_west_road: Mapped[Optional[str]] = mapped_column(String(100))
    north_south_road: Mapped[Optional[str]] = mapped_column(String(100))

    traffic_lights: Mapped[List["TrafficLight"]] = relationship(back_populates="intersection", cascade="all, delete-orphan")
    electronic_polices: Mapped[List["ElectronicPolice"]] = relationship(back_populates="intersection", cascade="all, delete-orphan")

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'type': self.type,
            'east_west_road': self.east_west_road,
            'north_south_road': self.north_south_road
        }

    def _get_device_warranty(self, devices):
        expire_dates = []
        for device in devices:
            expire_date = device.effective_warranty_expire_date
            if expire_date:
                expire_dates.append(expire_date)
        
        if not expire_dates:
            return {'warranty_status': '无项目', 'latest_expire_date': None}
        
        today = date.today()
        in_warranty = sum(1 for d in expire_dates if d >= today)
        expired = sum(1 for d in expire_dates if d < today)
        
        if expired == 0:
            status = '在保'
        elif in_warranty == 0:
            status = '过保'
        else:
            status = '混合'
        
        latest = max(expire_dates)
        return {
            'warranty_status': status,
            'latest_expire_date': latest.isoformat()
        }

    @property
    def warranty_status(self) -> dict:
        tl_warranty = self._get_device_warranty(self.traffic_lights)
        ep_warranty = self._get_device_warranty(self.electronic_polices)
        
        return {
            'traffic_light_warranty_status': tl_warranty['warranty_status'],
            'traffic_light_warranty_expire': tl_warranty['latest_expire_date'],
            'electronic_police_warranty_status': ep_warranty['warranty_status'],
            'electronic_police_warranty_expire': ep_warranty['latest_expire_date']
        }


class TrafficLight(db.Model):
    __tablename__ = 'traffic_light'

    id: Mapped[int] = mapped_column(primary_key=True)
    intersection_id: Mapped[int] = mapped_column(ForeignKey('intersection.id'), nullable=False)
    project_id: Mapped[int] = mapped_column(ForeignKey('project.id'), nullable=False)
    signal_type: Mapped[Optional[str]] = mapped_column(String(50))
    signal_count: Mapped[int] = mapped_column(Integer, default=0)
    left_arrow_count: Mapped[int] = mapped_column(Integer, default=0)
    straight_arrow_count: Mapped[int] = mapped_column(Integer, default=0)
    right_arrow_count: Mapped[int] = mapped_column(Integer, default=0)
    full_screen_count: Mapped[int] = mapped_column(Integer, default=0)
    non_motor_count: Mapped[int] = mapped_column(Integer, default=0)
    pedestrian_count: Mapped[int] = mapped_column(Integer, default=0)
    radar_count: Mapped[int] = mapped_column(Integer, default=0)
    guide_screen_count: Mapped[int] = mapped_column(Integer, default=0)
    power_source: Mapped[Optional[str]] = mapped_column(Text)
    extended_warranty_expire_date: Mapped[Optional[date]] = mapped_column(nullable=True)

    intersection: Mapped["Intersection"] = relationship(back_populates="traffic_lights")
    project: Mapped["Project"] = relationship(back_populates="traffic_lights")

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
            'intersection_id': self.intersection_id,
            'intersection_name': self.intersection.name if self.intersection else None,
            'intersection_type': self.intersection.type if self.intersection else None,
            'project_id': self.project_id,
            'project_name': self.project.name if self.project else None,
            'acceptance_date': self.project.acceptance_date.isoformat() if self.project and self.project.acceptance_date else None,
            'warranty_period': self.project.warranty_period if self.project else None,
            'warranty_expire_date': self.effective_warranty_expire_date.isoformat() if self.effective_warranty_expire_date else None,
            'warranty_status': self.warranty_status,
            'signal_type': self.signal_type,
            'signal_count': self.signal_count,
            'left_arrow_count': self.left_arrow_count,
            'straight_arrow_count': self.straight_arrow_count,
            'right_arrow_count': self.right_arrow_count,
            'full_screen_count': self.full_screen_count,
            'non_motor_count': self.non_motor_count,
            'pedestrian_count': self.pedestrian_count,
            'radar_count': self.radar_count,
            'guide_screen_count': self.guide_screen_count,
            'power_source': self.power_source,
            'construction_unit': self.project.builder if self.project else None,
            'construction_company': self.project.construction_unit if self.project else None
        }


class ElectronicPolice(db.Model):
    __tablename__ = 'electronic_police'

    id: Mapped[int] = mapped_column(primary_key=True)
    intersection_id: Mapped[int] = mapped_column(ForeignKey('intersection.id'), nullable=False)
    project_id: Mapped[int] = mapped_column(ForeignKey('project.id'), nullable=False)
    capture_type: Mapped[Optional[str]] = mapped_column(String(50))
    terminal_server_count: Mapped[int] = mapped_column(Integer, default=0)
    forward_capture_count: Mapped[int] = mapped_column(Integer, default=0)
    reverse_capture_count: Mapped[int] = mapped_column(Integer, default=0)
    led_light_count: Mapped[int] = mapped_column(Integer, default=0)
    strobe_light_count: Mapped[int] = mapped_column(Integer, default=0)
    ptz_count: Mapped[int] = mapped_column(Integer, default=0)
    signal_detector_count: Mapped[int] = mapped_column(Integer, default=0)
    network_source: Mapped[Optional[str]] = mapped_column(Text)
    extended_warranty_expire_date: Mapped[Optional[date]] = mapped_column(nullable=True)

    intersection: Mapped["Intersection"] = relationship(back_populates="electronic_polices")
    project: Mapped["Project"] = relationship(back_populates="electronic_polices")

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
            'intersection_id': self.intersection_id,
            'intersection_name': self.intersection.name if self.intersection else None,
            'intersection_type': self.intersection.type if self.intersection else None,
            'project_id': self.project_id,
            'project_name': self.project.name if self.project else None,
            'acceptance_date': self.project.acceptance_date.isoformat() if self.project and self.project.acceptance_date else None,
            'warranty_period': self.project.warranty_period if self.project else None,
            'warranty_expire_date': self.effective_warranty_expire_date.isoformat() if self.effective_warranty_expire_date else None,
            'warranty_status': self.warranty_status,
            'capture_type': self.capture_type,
            'terminal_server_count': self.terminal_server_count,
            'forward_capture_count': self.forward_capture_count,
            'reverse_capture_count': self.reverse_capture_count,
            'led_light_count': self.led_light_count,
            'strobe_light_count': self.strobe_light_count,
            'ptz_count': self.ptz_count,
            'signal_detector_count': self.signal_detector_count,
            'network_source': self.network_source,
            'construction_unit': self.project.builder if self.project else None,
            'construction_company': self.project.construction_unit if self.project else None
        }
from sqlalchemy import String, Integer, Text, ForeignKey, Enum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import Optional, List
from datetime import date
from ..extensions import db

class Intersection(db.Model):
    __tablename__ = 'intersection'

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    type: Mapped[Optional[str]] = mapped_column(Enum('十字路口', '丁字路口', '行人过街', '其他', name='intersection_type'))

    traffic_lights: Mapped[List["TrafficLight"]] = relationship(back_populates="intersection", cascade="all, delete-orphan")
    electronic_polices: Mapped[List["ElectronicPolice"]] = relationship(back_populates="intersection", cascade="all, delete-orphan")

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'type': self.type
        }

    @property
    def warranty_status(self) -> dict:
        expire_dates = []
        for tl in self.traffic_lights:
            if tl.project and tl.project.warranty_expire_date:
                expire_dates.append(tl.project.warranty_expire_date)
        for ep in self.electronic_polices:
            if ep.project and ep.project.warranty_expire_date:
                expire_dates.append(ep.project.warranty_expire_date)

        if not expire_dates:
            return {'warranty_status': '无项目', 'latest_expire_date': None}

        latest = max(expire_dates)
        return {
            'warranty_status': '在保' if latest >= date.today() else '过保',
            'latest_expire_date': latest.isoformat()
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

    intersection: Mapped["Intersection"] = relationship(back_populates="traffic_lights")
    project: Mapped["Project"] = relationship(back_populates="traffic_lights")

    def to_dict(self):
        return {
            'id': self.id,
            'intersection_id': self.intersection_id,
            'project_id': self.project_id,
            'project_name': self.project.name if self.project else None,
            'warranty_expire_date': self.project.warranty_expire_date.isoformat() if self.project else None,
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
            'power_source': self.power_source
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

    intersection: Mapped["Intersection"] = relationship(back_populates="electronic_polices")
    project: Mapped["Project"] = relationship(back_populates="electronic_polices")

    def to_dict(self):
        return {
            'id': self.id,
            'intersection_id': self.intersection_id,
            'project_id': self.project_id,
            'project_name': self.project.name if self.project else None,
            'warranty_expire_date': self.project.warranty_expire_date.isoformat() if self.project else None,
            'capture_type': self.capture_type,
            'terminal_server_count': self.terminal_server_count,
            'forward_capture_count': self.forward_capture_count,
            'reverse_capture_count': self.reverse_capture_count,
            'led_light_count': self.led_light_count,
            'strobe_light_count': self.strobe_light_count,
            'ptz_count': self.ptz_count,
            'signal_detector_count': self.signal_detector_count,
            'network_source': self.network_source
        }
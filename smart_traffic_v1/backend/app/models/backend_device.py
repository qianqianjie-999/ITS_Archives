from sqlalchemy import String, Integer, Text, ForeignKey, Date
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import Optional, List
from datetime import date
from ..extensions import db

class BackendDevice(db.Model):
    __tablename__ = 'backend_device'

    id: Mapped[int] = mapped_column(primary_key=True)
    point_id: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    project_id: Mapped[int] = mapped_column(ForeignKey('project.id'))
    name: Mapped[str] = mapped_column(String(100), nullable=False, unique=True)
    type: Mapped[Optional[str]] = mapped_column(String(50))
    server_count: Mapped[int] = mapped_column(Integer, default=0)
    storage_count: Mapped[int] = mapped_column(Integer, default=0)
    switch_count: Mapped[int] = mapped_column(Integer, default=0)
    firewall_count: Mapped[int] = mapped_column(Integer, default=0)
    fiber_converter_count: Mapped[int] = mapped_column(Integer, default=0)
    power_supply_count: Mapped[int] = mapped_column(Integer, default=0)
    cabinet_count: Mapped[int] = mapped_column(Integer, default=0)
    other_device_count: Mapped[int] = mapped_column(Integer, default=0)
    ip_address: Mapped[Optional[str]] = mapped_column(String(100))
    port: Mapped[Optional[str]] = mapped_column(String(50))
    location: Mapped[Optional[str]] = mapped_column(String(200))
    power_source: Mapped[Optional[str]] = mapped_column(Text)
    network_source: Mapped[Optional[str]] = mapped_column(Text)
    extended_warranty_expire_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)

    project: Mapped["Project"] = relationship(back_populates="backend_devices")

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
            'project_id': self.project_id,
            'project_name': self.project.name if self.project else None,
            'acceptance_date': self.project.acceptance_date.isoformat() if self.project and self.project.acceptance_date else None,
            'warranty_period': self.project.warranty_period if self.project else None,
            'warranty_expire_date': self.effective_warranty_expire_date.isoformat() if self.effective_warranty_expire_date else None,
            'warranty_status': self.warranty_status,
            'name': self.name,
            'type': self.type,
            'server_count': self.server_count,
            'storage_count': self.storage_count,
            'switch_count': self.switch_count,
            'firewall_count': self.firewall_count,
            'fiber_converter_count': self.fiber_converter_count,
            'power_supply_count': self.power_supply_count,
            'cabinet_count': self.cabinet_count,
            'other_device_count': self.other_device_count,
            'ip_address': self.ip_address,
            'port': self.port,
            'location': self.location,
            'power_source': self.power_source,
            'network_source': self.network_source,
            'construction_unit': self.project.builder if self.project else None,
            'construction_company': self.project.construction_unit if self.project else None
        }
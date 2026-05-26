from sqlalchemy import String, DECIMAL, Date
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import Optional, List
from decimal import Decimal
from ..extensions import db

class Project(db.Model):
    __tablename__ = 'project'

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    contract_amount: Mapped[Optional[Decimal]] = mapped_column(DECIMAL(15, 2))
    acceptance_date: Mapped[Optional[Date]] = mapped_column(Date)
    warranty_period: Mapped[Optional[str]] = mapped_column(String(50))
    warranty_expire_date: Mapped[Date] = mapped_column(Date, nullable=False)
    builder: Mapped[Optional[str]] = mapped_column(String(100))
    constructor: Mapped[Optional[str]] = mapped_column(String(100))

    traffic_lights: Mapped[List["TrafficLight"]] = relationship(back_populates="project", lazy='dynamic')
    electronic_polices: Mapped[List["ElectronicPolice"]] = relationship(back_populates="project", lazy='dynamic')
    parking_enforcements: Mapped[List["ParkingEnforcement"]] = relationship(back_populates="project", lazy='dynamic')
    checkpoints: Mapped[List["Checkpoint"]] = relationship(back_populates="project", lazy='dynamic')
    backend_devices: Mapped[List["BackendDevice"]] = relationship(back_populates="project", lazy='dynamic')
    warranty_extensions: Mapped[List["WarrantyExtension"]] = relationship(back_populates="project")

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'contract_amount': float(self.contract_amount) if self.contract_amount else None,
            'acceptance_date': self.acceptance_date.isoformat() if self.acceptance_date else None,
            'warranty_period': self.warranty_period,
            'warranty_expire_date': self.warranty_expire_date.isoformat() if self.warranty_expire_date else None,
            'builder': self.builder,
            'constructor': self.constructor
        }
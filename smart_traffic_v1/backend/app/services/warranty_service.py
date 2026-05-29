from datetime import date
from typing import List, Dict, Optional
from ..extensions import db
from ..models.intersection import Intersection, TrafficLight, ElectronicPolice
from ..models.point import ParkingEnforcementPoint, CheckpointPoint, ParkingEnforcement, Checkpoint
from ..models.project import Project
from ..models.backend_device import BackendDevice
from ..models.warranty_extension import WarrantyExtension


class WarrantyService:
    @staticmethod
    def get_intersection_warranty_status(intersection_id: int) -> Dict:
        intersection = db.session.query(Intersection).get(intersection_id)
        if not intersection:
            return None

        expire_dates = []

        traffic_lights = db.session.query(TrafficLight).filter_by(intersection_id=intersection_id).all()
        for tl in traffic_lights:
            if tl.project and tl.project.warranty_expire_date:
                expire_dates.append(tl.project.warranty_expire_date)

        electronic_polices = db.session.query(ElectronicPolice).filter_by(intersection_id=intersection_id).all()
        for ep in electronic_polices:
            if ep.project and ep.project.warranty_expire_date:
                expire_dates.append(ep.project.warranty_expire_date)

        extensions = db.session.query(WarrantyExtension).filter_by(
            facility_type='intersection',
            facility_id=intersection_id
        ).all()
        for ext in extensions:
            if ext.project and ext.project.warranty_expire_date:
                expire_dates.append(ext.project.warranty_expire_date)

        if not expire_dates:
            return {'status': '无项目', 'latest_expire_date': None}

        latest = max(expire_dates)
        return {
            'status': '在保' if latest >= date.today() else '过保',
            'latest_expire_date': latest.isoformat()
        }

    @staticmethod
    def get_point_warranty_status(point_id: int, point_type: str = 'parking_enforcement') -> Dict:
        model_cls = ParkingEnforcementPoint if point_type == 'parking_enforcement' else CheckpointPoint
        point = db.session.query(model_cls).get(point_id)
        if not point:
            return None

        expire_dates = []

        if point_type == 'parking_enforcement':
            devices = db.session.query(ParkingEnforcement).filter_by(point_id=point_id).all()
        else:
            devices = db.session.query(Checkpoint).filter_by(point_id=point_id).all()
        for d in devices:
            if d.project and d.project.warranty_expire_date:
                expire_dates.append(d.project.warranty_expire_date)

        extensions = db.session.query(WarrantyExtension).filter_by(
            facility_type='point',
            facility_id=point_id
        ).all()
        for ext in extensions:
            if ext.project and ext.project.warranty_expire_date:
                expire_dates.append(ext.project.warranty_expire_date)

        if not expire_dates:
            return {'status': '无项目', 'latest_expire_date': None}

        latest = max(expire_dates)
        return {
            'status': '在保' if latest >= date.today() else '过保',
            'latest_expire_date': latest.isoformat()
        }

    @staticmethod
    def extend_warranty(facility_type: str, facility_id: int, project_name: str, warranty_expire_date: date) -> Project:
        project = Project(
            name=project_name,
            acceptance_date=date.today(),
            warranty_expire_date=warranty_expire_date
        )
        db.session.add(project)
        db.session.flush()

        extension = WarrantyExtension(
            facility_type=facility_type,
            facility_id=facility_id,
            project_id=project.id,
            extension_date=date.today()
        )
        db.session.add(extension)
        db.session.commit()

        return project
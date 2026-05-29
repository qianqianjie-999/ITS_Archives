import csv
import io
from datetime import date
from typing import List
from flask import send_file
from ..extensions import db
from ..models.intersection import Intersection, TrafficLight, ElectronicPolice
from ..models.point import ParkingEnforcementPoint, CheckpointPoint, ParkingEnforcement, Checkpoint
from ..models.project import Project


class ExportService:
    @staticmethod
    def export_intersections() -> io.BytesIO:
        intersections = db.session.query(Intersection).order_by(Intersection.id).all()

        output = io.StringIO()
        writer = csv.writer(output)

        writer.writerow(['ID', '名称', '类型', '最新质保到期', '状态'])

        from ..services.warranty_service import WarrantyService

        for i in intersections:
            status = WarrantyService.get_intersection_warranty_status(i.id)
            writer.writerow([
                i.id,
                i.name,
                i.type or '',
                status.get('latest_expire_date', '') if status else '',
                status.get('status', '') if status else ''
            ])

        output.seek(0)
        return send_file(
            io.BytesIO(output.getvalue().encode('utf-8-sig')),
            mimetype='text/csv',
            as_attachment=True,
            download_name=f'intersections_export_{date.today()}.csv'
        )

    @staticmethod
    def export_parking_enforcement_points() -> io.BytesIO:
        points = db.session.query(ParkingEnforcementPoint).order_by(ParkingEnforcementPoint.id).all()

        output = io.StringIO()
        writer = csv.writer(output)

        writer.writerow(['ID', '点位名称', '抓拍区域', '安装位置'])

        for p in points:
            writer.writerow([p.id, p.name, p.area or '', p.type or ''])

        output.seek(0)
        return send_file(
            io.BytesIO(output.getvalue().encode('utf-8-sig')),
            mimetype='text/csv',
            as_attachment=True,
            download_name=f'parking_enforcement_points_{date.today()}.csv'
        )

    @staticmethod
    def export_checkpoint_points() -> io.BytesIO:
        points = db.session.query(CheckpointPoint).order_by(CheckpointPoint.id).all()

        output = io.StringIO()
        writer = csv.writer(output)

        writer.writerow(['ID', '点位名称', '卡口类型', '安装位置'])

        for p in points:
            writer.writerow([p.id, p.name, p.area or '', p.type or ''])

        output.seek(0)
        return send_file(
            io.BytesIO(output.getvalue().encode('utf-8-sig')),
            mimetype='text/csv',
            as_attachment=True,
            download_name=f'checkpoint_points_{date.today()}.csv'
        )

    @staticmethod
    def export_projects() -> io.BytesIO:
        projects = db.session.query(Project).order_by(Project.id.desc()).all()

        output = io.StringIO()
        writer = csv.writer(output)

        writer.writerow(['ID', '项目名称', '合同金额', '验收日期', '质保期', '质保到期', '建设单位', '施工单位'])

        for p in projects:
            writer.writerow([
                p.id,
                p.name,
                p.contract_amount or '',
                p.acceptance_date.isoformat() if p.acceptance_date else '',
                p.warranty_period or '',
                p.warranty_expire_date.isoformat() if p.warranty_expire_date else '',
                p.builder or '',
                p.construction_unit or ''
            ])

        output.seek(0)
        return send_file(
            io.BytesIO(output.getvalue().encode('utf-8-sig')),
            mimetype='text/csv',
            as_attachment=True,
            download_name=f'projects_export_{date.today()}.csv'
        )
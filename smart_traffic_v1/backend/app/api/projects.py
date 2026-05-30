from flask import request
from flask_restx import Namespace, Resource, fields
from ..extensions import db
from ..models.project import Project
from ..models.warranty_extension import WarrantyExtension
from ..utils.decorators import token_required, role_required
from datetime import date

ns = Namespace('projects', description='项目管理')

project_model = ns.model('Project', {
    'id': fields.Integer(readonly=True),
    'name': fields.String(required=True),
    'contract_amount': fields.Float(),
    'acceptance_date': fields.String(),
    'warranty_period': fields.String(),
    'warranty_expire_date': fields.String(required=True),
    'builder': fields.String(),
    'construction_unit': fields.String()
})

@ns.route('/')
class ProjectList(Resource):
    def get(self):
        facility_type = request.args.get('facility_type')
        facility_id = request.args.get('facility_id', type=int)

        if facility_type and facility_id:
            extensions = db.session.query(WarrantyExtension).filter_by(
                facility_type=facility_type,
                facility_id=facility_id
            ).all()
            project_ids = [ext.project_id for ext in extensions]
            projects = db.session.query(Project).filter(Project.id.in_(project_ids)).all()
        else:
            projects = db.session.query(Project).order_by(Project.id.desc()).all()

        return [p.to_dict() for p in projects]

    @token_required
    @role_required('admin', 'editor')
    @ns.expect(project_model)
    def post(self):
        data = request.json
        project = Project(
            name=data['name'],
            contract_amount=data.get('contract_amount'),
            acceptance_date=date.fromisoformat(data['acceptance_date']) if data.get('acceptance_date') else None,
            warranty_period=data.get('warranty_period'),
            warranty_expire_date=date.fromisoformat(data['warranty_expire_date']),
            builder=data.get('builder'),
            construction_unit=data.get('construction_unit')
        )
        db.session.add(project)
        db.session.commit()
        return {'status': 'success', 'id': project.id}, 201

@ns.route('/<int:project_id>')
class ProjectDetail(Resource):
    def get(self, project_id):
        project = db.session.query(Project).get(project_id)
        if not project:
            return {'status': 'error', 'message': '项目不存在'}, 404
        return project.to_dict()

    @token_required
    @role_required('admin', 'editor')
    @ns.expect(project_model)
    def put(self, project_id):
        project = db.session.query(Project).get(project_id)
        if not project:
            return {'status': 'error', 'message': '项目不存在'}, 404

        data = request.json
        old_warranty_expire_date = project.warranty_expire_date

        for key in ['name', 'contract_amount', 'acceptance_date', 'warranty_period',
                    'warranty_expire_date', 'builder', 'construction_unit']:
            if key in data:
                if key in ['acceptance_date', 'warranty_expire_date'] and data[key]:
                    setattr(project, key, date.fromisoformat(data[key]))
                else:
                    setattr(project, key, data[key])

        new_warranty_expire_date = project.warranty_expire_date

        if old_warranty_expire_date != new_warranty_expire_date:
            from ..models.intersection import TrafficLight, ElectronicPolice
            from ..models.point import ParkingEnforcement, Checkpoint
            from ..models.backend_device import BackendDevice

            db.session.query(TrafficLight).filter_by(project_id=project_id).update(
                {'extended_warranty_expire_date': new_warranty_expire_date}
            )
            db.session.query(ElectronicPolice).filter_by(project_id=project_id).update(
                {'extended_warranty_expire_date': new_warranty_expire_date}
            )
            db.session.query(ParkingEnforcement).filter_by(project_id=project_id).update(
                {'extended_warranty_expire_date': new_warranty_expire_date}
            )
            db.session.query(Checkpoint).filter_by(project_id=project_id).update(
                {'extended_warranty_expire_date': new_warranty_expire_date}
            )
            db.session.query(BackendDevice).filter_by(project_id=project_id).update(
                {'extended_warranty_expire_date': new_warranty_expire_date}
            )

        db.session.commit()
        return {'status': 'success', 'data': project.to_dict()}

    @token_required
    @role_required('admin')
    def delete(self, project_id):
        project = db.session.query(Project).get(project_id)
        if not project:
            return {'status': 'error', 'message': '项目不存在'}, 404

        from ..models.intersection import TrafficLight, ElectronicPolice
        from ..models.point import ParkingEnforcement, Checkpoint
        from ..models.backend_device import BackendDevice
        from ..models.warranty_extension import WarrantyExtension

        referenced_devices = []

        traffic_count = db.session.query(TrafficLight).filter_by(project_id=project_id).count()
        if traffic_count > 0:
            referenced_devices.append(f'信号灯({traffic_count})')

        ep_count = db.session.query(ElectronicPolice).filter_by(project_id=project_id).count()
        if ep_count > 0:
            referenced_devices.append(f'电子警察({ep_count})')

        pe_count = db.session.query(ParkingEnforcement).filter_by(project_id=project_id).count()
        if pe_count > 0:
            referenced_devices.append(f'违停设备({pe_count})')

        cp_count = db.session.query(Checkpoint).filter_by(project_id=project_id).count()
        if cp_count > 0:
            referenced_devices.append(f'卡口设备({cp_count})')

        bd_count = db.session.query(BackendDevice).filter_by(project_id=project_id).count()
        if bd_count > 0:
            referenced_devices.append(f'后端设备({bd_count})')

        ext_count = db.session.query(WarrantyExtension).filter_by(project_id=project_id).count()
        if ext_count > 0:
            referenced_devices.append(f'质保延期记录({ext_count})')

        if referenced_devices:
            return {
                'status': 'error',
                'message': f'无法删除项目，该项目已被以下内容引用：{"、".join(referenced_devices)}。请先删除关联的设备或延期记录。'
            }, 409

        db.session.delete(project)
        db.session.commit()
        return {'status': 'success'}

@ns.route('/warranty-extensions')
class WarrantyExtensionList(Resource):
    def get(self):
        facility_type = request.args.get('facility_type')
        facility_id = request.args.get('facility_id', type=int)

        if facility_type and facility_id:
            extensions = db.session.query(WarrantyExtension).filter_by(
                facility_type=facility_type,
                facility_id=facility_id
            ).all()
        else:
            extensions = db.session.query(WarrantyExtension).all()

        return [ext.to_dict() for ext in extensions]

@ns.route('/warranty-extensions/<int:extension_id>')
class WarrantyExtensionDetail(Resource):
    @token_required
    @role_required('admin')
    def delete(self, extension_id):
        extension = db.session.query(WarrantyExtension).get(extension_id)
        if not extension:
            return {'status': 'error', 'message': '质保延期记录不存在'}, 404

        from ..models.intersection import TrafficLight, ElectronicPolice
        from ..models.point import ParkingEnforcement, Checkpoint

        affected_devices = []

        if extension.facility_type == 'intersection':
            tl_count = db.session.query(TrafficLight).filter_by(
                intersection_id=extension.facility_id,
                project_id=extension.project_id
            ).update({'extended_warranty_expire_date': None})
            if tl_count > 0:
                affected_devices.append(f'信号灯({tl_count})')

            ep_count = db.session.query(ElectronicPolice).filter_by(
                intersection_id=extension.facility_id,
                project_id=extension.project_id
            ).update({'extended_warranty_expire_date': None})
            if ep_count > 0:
                affected_devices.append(f'电子警察({ep_count})')

        elif extension.facility_type == 'point':
            pe_count = db.session.query(ParkingEnforcement).filter_by(
                point_id=extension.facility_id,
                project_id=extension.project_id
            ).update({'extended_warranty_expire_date': None})
            if pe_count > 0:
                affected_devices.append(f'违停设备({pe_count})')

            cp_count = db.session.query(Checkpoint).filter_by(
                point_id=extension.facility_id,
                project_id=extension.project_id
            ).update({'extended_warranty_expire_date': None})
            if cp_count > 0:
                affected_devices.append(f'卡口设备({cp_count})')

        db.session.delete(extension)
        db.session.commit()

        return {
            'status': 'success',
            'message': f'已删除质保延期记录，{", ".join(affected_devices) if affected_devices else "无设备受影响"}'
        }
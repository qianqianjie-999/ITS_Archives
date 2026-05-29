from flask import request
from flask_restx import Namespace, Resource, fields
from ..extensions import db
from ..models.point import ParkingEnforcementPoint, CheckpointPoint, ParkingEnforcement, Checkpoint
from ..models.project import Project
from ..models.backend_device import BackendDevice
from ..models.warranty_extension import WarrantyExtension
from ..utils.decorators import token_required, role_required
from datetime import date

ns = Namespace('points', description='点位与设备管理')

parking_point_model = ns.model('ParkingEnforcementPoint', {
    'id': fields.Integer(readonly=True),
    'name': fields.String(required=True),
    'area': fields.String(),
    'type': fields.String()
})

checkpoint_point_model = ns.model('CheckpointPoint', {
    'id': fields.Integer(readonly=True),
    'name': fields.String(required=True),
    'area': fields.String(),
    'type': fields.String()
})

parking_enforcement_model = ns.model('ParkingEnforcement', {
    'id': fields.Integer(readonly=True),
    'point_id': fields.Integer(),
    'project_id': fields.Integer(),
    'project_name': fields.String(readonly=True),
    'warranty_expire_date': fields.String(readonly=True),
    'camera_count': fields.Integer(),
    'parking_sign_count': fields.Integer(),
    'monitor_sign_count': fields.Integer(),
    'power_source': fields.String(),
    'network_source': fields.String()
})

checkpoint_model = ns.model('Checkpoint', {
    'id': fields.Integer(readonly=True),
    'point_id': fields.Integer(),
    'project_id': fields.Integer(),
    'project_name': fields.String(readonly=True),
    'warranty_expire_date': fields.String(readonly=True),
    'checkpoint_type': fields.String(),
    'camera_count': fields.Integer(),
    'strobe_light_count': fields.Integer(),
    'radar_count': fields.Integer(),
    'sign_count': fields.Integer(),
    'power_source': fields.String(),
    'network_source': fields.String()
})

backend_device_model = ns.model('BackendDevice', {
    'id': fields.Integer(readonly=True),
    'point_id': fields.Integer(),
    'project_id': fields.Integer(),
    'project_name': fields.String(readonly=True),
    'warranty_expire_date': fields.String(readonly=True),
    'warranty_status': fields.String(readonly=True),
    'name': fields.String(required=True),
    'type': fields.String(),
    'server_count': fields.Integer(),
    'storage_count': fields.Integer(),
    'switch_count': fields.Integer(),
    'firewall_count': fields.Integer(),
    'fiber_converter_count': fields.Integer(),
    'power_supply_count': fields.Integer(),
    'cabinet_count': fields.Integer(),
    'other_device_count': fields.Integer(),
    'ip_address': fields.String(),
    'port': fields.String(),
    'location': fields.String(),
    'power_source': fields.String(),
    'network_source': fields.String()
})

extend_warranty_model = ns.model('ExtendWarranty', {
    'project_id': fields.Integer(),
    'project_name': fields.String(),
    'warranty_expire_date': fields.String(required=True)
})


# ==================== Parking Enforcement Points ====================

@ns.route('/parking-points')
class ParkingPointList(Resource):
    def get(self):
        points = db.session.query(ParkingEnforcementPoint).all()
        result = []
        for p in points:
            data = p.to_dict()
            data.update(p.warranty_status)
            result.append(data)
        return result

    @token_required
    @role_required('admin', 'editor')
    @ns.expect(parking_point_model)
    def post(self):
        data = request.json
        point = ParkingEnforcementPoint(
            name=data['name'],
            area=data.get('area', ''),
            type=data.get('type', '')
        )
        db.session.add(point)
        db.session.commit()
        return {'status': 'success', 'data': point.to_dict()}, 201


@ns.route('/parking-points/<int:point_id>')
class ParkingPointDetail(Resource):
    def get(self, point_id):
        point = db.session.query(ParkingEnforcementPoint).get(point_id)
        if not point:
            return {'status': 'error', 'message': '违停点位不存在'}, 404

        devices = db.session.query(ParkingEnforcement).filter_by(point_id=point_id).all()

        extensions = db.session.query(WarrantyExtension).filter_by(
            facility_type='point', facility_id=point_id
        ).all()

        return {
            'point': {**point.to_dict(), **point.warranty_status},
            'parking_enforcements': [pe.to_dict() for pe in devices],
            'warranty_extensions': [ext.to_dict() for ext in extensions]
        }

    @token_required
    @role_required('admin', 'editor')
    @ns.expect(parking_point_model)
    def put(self, point_id):
        point = db.session.query(ParkingEnforcementPoint).get(point_id)
        if not point:
            return {'status': 'error', 'message': '违停点位不存在'}, 404

        data = request.json
        if 'name' in data:
            point.name = data['name']
        if 'area' in data:
            point.area = data['area']
        if 'type' in data:
            point.type = data['type']

        db.session.commit()
        return {'status': 'success', 'data': point.to_dict()}

    @token_required
    @role_required('admin')
    def delete(self, point_id):
        point = db.session.query(ParkingEnforcementPoint).get(point_id)
        if not point:
            return {'status': 'error', 'message': '违停点位不存在'}, 404

        db.session.delete(point)
        db.session.commit()
        return {'status': 'success', 'message': '删除成功'}


# ==================== Checkpoint Points ====================

@ns.route('/checkpoint-points')
class CheckpointPointList(Resource):
    def get(self):
        points = db.session.query(CheckpointPoint).all()
        result = []
        for p in points:
            data = p.to_dict()
            data.update(p.warranty_status)
            result.append(data)
        return result

    @token_required
    @role_required('admin', 'editor')
    @ns.expect(checkpoint_point_model)
    def post(self):
        data = request.json
        point = CheckpointPoint(
            name=data['name'],
            area=data.get('area', ''),
            type=data.get('type', '')
        )
        db.session.add(point)
        db.session.commit()
        return {'status': 'success', 'data': point.to_dict()}, 201


@ns.route('/checkpoint-points/<int:point_id>')
class CheckpointPointDetail(Resource):
    def get(self, point_id):
        point = db.session.query(CheckpointPoint).get(point_id)
        if not point:
            return {'status': 'error', 'message': '卡口点位不存在'}, 404

        devices = db.session.query(Checkpoint).filter_by(point_id=point_id).all()

        extensions = db.session.query(WarrantyExtension).filter_by(
            facility_type='point', facility_id=point_id
        ).all()

        return {
            'point': {**point.to_dict(), **point.warranty_status},
            'checkpoints': [cp.to_dict() for cp in devices],
            'warranty_extensions': [ext.to_dict() for ext in extensions]
        }

    @token_required
    @role_required('admin', 'editor')
    @ns.expect(checkpoint_point_model)
    def put(self, point_id):
        point = db.session.query(CheckpointPoint).get(point_id)
        if not point:
            return {'status': 'error', 'message': '卡口点位不存在'}, 404

        data = request.json
        if 'name' in data:
            point.name = data['name']
        if 'area' in data:
            point.area = data['area']
        if 'type' in data:
            point.type = data['type']

        db.session.commit()
        return {'status': 'success', 'data': point.to_dict()}

    @token_required
    @role_required('admin')
    def delete(self, point_id):
        point = db.session.query(CheckpointPoint).get(point_id)
        if not point:
            return {'status': 'error', 'message': '卡口点位不存在'}, 404

        db.session.delete(point)
        db.session.commit()
        return {'status': 'success', 'message': '删除成功'}


# ==================== Parking Enforcement Devices ====================

@ns.route('/parking-enforcement')
class ParkingEnforcementListAll(Resource):
    def get(self):
        pes = db.session.query(ParkingEnforcement).all()
        return [pe.to_dict() for pe in pes]


@ns.route('/parking-points/<int:point_id>/devices')
class ParkingEnforcementByPoint(Resource):
    def get(self, point_id):
        point = db.session.query(ParkingEnforcementPoint).get(point_id)
        if not point:
            return {'status': 'error', 'message': '违停点位不存在'}, 404
        pes = db.session.query(ParkingEnforcement).filter_by(point_id=point_id).all()
        return [pe.to_dict() for pe in pes]

    @token_required
    @role_required('admin', 'editor')
    @ns.expect(parking_enforcement_model)
    def post(self, point_id):
        point = db.session.query(ParkingEnforcementPoint).get(point_id)
        if not point:
            return {'status': 'error', 'message': '违停点位不存在'}, 404

        data = request.json
        pe = ParkingEnforcement(
            point_id=point_id,
            project_id=data.get('project_id'),
            camera_area=data.get('camera_area', ''),
            camera_count=data.get('camera_count', 0),
            parking_sign_count=data.get('parking_sign_count', 0),
            monitor_sign_count=data.get('monitor_sign_count', 0),
            power_source=data.get('power_source', ''),
            network_source=data.get('network_source', '')
        )
        db.session.add(pe)
        db.session.commit()
        return {'status': 'success', 'data': pe.to_dict()}


@ns.route('/parking-points/<int:point_id>/devices/<int:pe_id>')
class ParkingEnforcementUpdate(Resource):
    @token_required
    @role_required('admin', 'editor')
    @ns.expect(parking_enforcement_model)
    def put(self, point_id, pe_id):
        pe = db.session.query(ParkingEnforcement).filter_by(id=pe_id, point_id=point_id).first()
        if not pe:
            return {'status': 'error', 'message': '违停抓拍设备不存在'}, 404

        data = request.json
        for key in ['project_id', 'camera_area', 'camera_count', 'parking_sign_count',
                    'monitor_sign_count', 'power_source', 'network_source']:
            if key in data:
                setattr(pe, key, data[key])

        db.session.commit()
        return {'status': 'success', 'data': pe.to_dict()}

    @token_required
    @role_required('admin')
    def delete(self, point_id, pe_id):
        pe = db.session.query(ParkingEnforcement).filter_by(id=pe_id, point_id=point_id).first()
        if not pe:
            return {'status': 'error', 'message': '违停抓拍设备不存在'}, 404
        db.session.delete(pe)
        db.session.commit()
        return {'status': 'success', 'message': '删除成功'}


# ==================== Checkpoint Devices ====================

@ns.route('/checkpoints')
class CheckpointListAll(Resource):
    def get(self):
        checkpoints = db.session.query(Checkpoint).all()
        return [cp.to_dict() for cp in checkpoints]


@ns.route('/checkpoint-points/<int:point_id>/devices')
class CheckpointByPoint(Resource):
    def get(self, point_id):
        point = db.session.query(CheckpointPoint).get(point_id)
        if not point:
            return {'status': 'error', 'message': '卡口点位不存在'}, 404
        checkpoints = db.session.query(Checkpoint).filter_by(point_id=point_id).all()
        return [cp.to_dict() for cp in checkpoints]

    @token_required
    @role_required('admin', 'editor')
    @ns.expect(checkpoint_model)
    def post(self, point_id):
        point = db.session.query(CheckpointPoint).get(point_id)
        if not point:
            return {'status': 'error', 'message': '卡口点位不存在'}, 404

        data = request.json
        cp = Checkpoint(
            point_id=point_id,
            project_id=data.get('project_id'),
            checkpoint_type=data.get('checkpoint_type', ''),
            camera_count=data.get('camera_count', 0),
            strobe_light_count=data.get('strobe_light_count', 0),
            radar_count=data.get('radar_count', 0),
            sign_count=data.get('sign_count', 0),
            power_source=data.get('power_source', ''),
            network_source=data.get('network_source', '')
        )
        db.session.add(cp)
        db.session.commit()
        return {'status': 'success', 'data': cp.to_dict()}


@ns.route('/checkpoint-points/<int:point_id>/devices/<int:cp_id>')
class CheckpointUpdate(Resource):
    @token_required
    @role_required('admin', 'editor')
    @ns.expect(checkpoint_model)
    def put(self, point_id, cp_id):
        cp = db.session.query(Checkpoint).filter_by(id=cp_id, point_id=point_id).first()
        if not cp:
            return {'status': 'error', 'message': '治安卡口设备不存在'}, 404

        data = request.json
        for key in ['project_id', 'checkpoint_type', 'camera_count', 'strobe_light_count',
                    'radar_count', 'sign_count', 'power_source', 'network_source']:
            if key in data:
                setattr(cp, key, data[key])

        db.session.commit()
        return {'status': 'success', 'data': cp.to_dict()}

    @token_required
    @role_required('admin')
    def delete(self, point_id, cp_id):
        cp = db.session.query(Checkpoint).filter_by(id=cp_id, point_id=point_id).first()
        if not cp:
            return {'status': 'error', 'message': '治安卡口设备不存在'}, 404
        db.session.delete(cp)
        db.session.commit()
        return {'status': 'success', 'message': '删除成功'}


# ==================== Warranty Extension ====================

@ns.route('/parking-points/<int:point_id>/extend-warranty')
class ParkingPointExtendWarranty(Resource):
    @token_required
    @role_required('admin', 'editor')
    @ns.expect(extend_warranty_model)
    def post(self, point_id):
        point = db.session.query(ParkingEnforcementPoint).get(point_id)
        if not point:
            return {'status': 'error', 'message': '违停点位不存在'}, 404

        data = request.json
        project_id = data.get('project_id')
        if project_id:
            project = db.session.query(Project).get(project_id)
            if not project:
                return {'status': 'error', 'message': '项目不存在'}, 404
            project.warranty_expire_date = date.fromisoformat(data['warranty_expire_date'])
        else:
            project = Project(
                name=data['project_name'],
                acceptance_date=date.today(),
                warranty_expire_date=date.fromisoformat(data['warranty_expire_date'])
            )
            db.session.add(project)
            db.session.flush()

            devices = db.session.query(ParkingEnforcement).filter_by(point_id=point_id).all()
            for d in devices:
                d.project_id = project.id

        extension = WarrantyExtension(
            facility_type='point',
            facility_id=point_id,
            project_id=project.id,
            extension_date=date.today()
        )
        db.session.add(extension)
        db.session.commit()
        return {'status': 'success', 'data': project.to_dict()}


@ns.route('/checkpoint-points/<int:point_id>/extend-warranty')
class CheckpointPointExtendWarranty(Resource):
    @token_required
    @role_required('admin', 'editor')
    @ns.expect(extend_warranty_model)
    def post(self, point_id):
        point = db.session.query(CheckpointPoint).get(point_id)
        if not point:
            return {'status': 'error', 'message': '卡口点位不存在'}, 404

        data = request.json
        project_id = data.get('project_id')
        if project_id:
            project = db.session.query(Project).get(project_id)
            if not project:
                return {'status': 'error', 'message': '项目不存在'}, 404
            project.warranty_expire_date = date.fromisoformat(data['warranty_expire_date'])
        else:
            project = Project(
                name=data['project_name'],
                acceptance_date=date.today(),
                warranty_expire_date=date.fromisoformat(data['warranty_expire_date'])
            )
            db.session.add(project)
            db.session.flush()

            devices = db.session.query(Checkpoint).filter_by(point_id=point_id).all()
            for d in devices:
                d.project_id = project.id

        extension = WarrantyExtension(
            facility_type='point',
            facility_id=point_id,
            project_id=project.id,
            extension_date=date.today()
        )
        db.session.add(extension)
        db.session.commit()
        return {'status': 'success', 'data': project.to_dict()}


# ==================== Backend Devices ====================

@ns.route('/backend-devices')
class BackendDeviceList(Resource):
    def get(self):
        backend_devices = db.session.query(BackendDevice).all()
        return [bd.to_dict() for bd in backend_devices]

    @token_required
    @role_required('admin', 'editor')
    @ns.expect(backend_device_model)
    def post(self):
        data = request.json
        bd = BackendDevice(
            point_id=data.get('point_id'),
            project_id=data.get('project_id'),
            name=data.get('name', ''),
            type=data.get('type', '')
        )
        db.session.add(bd)
        db.session.commit()
        return {'status': 'success', 'data': bd.to_dict()}


@ns.route('/backend-device/<int:bd_id>')
class BackendDeviceUpdate(Resource):
    @token_required
    @role_required('admin', 'editor')
    @ns.expect(backend_device_model)
    def put(self, bd_id):
        bd = db.session.query(BackendDevice).get(bd_id)
        if not bd:
            return {'status': 'error', 'message': '后端设备不存在'}, 404

        data = request.json
        for key in ['name', 'type', 'project_id', 'server_count', 'storage_count',
                    'switch_count', 'firewall_count', 'fiber_converter_count',
                    'power_supply_count', 'cabinet_count', 'other_device_count',
                    'ip_address', 'port', 'location', 'power_source', 'network_source']:
            if key in data:
                setattr(bd, key, data[key])

        db.session.commit()
        return {'status': 'success', 'data': bd.to_dict()}

    @token_required
    @role_required('admin')
    def delete(self, bd_id):
        bd = db.session.query(BackendDevice).get(bd_id)
        if not bd:
            return {'status': 'error', 'message': '后端设备不存在'}, 404

        db.session.delete(bd)
        db.session.commit()
        return {'status': 'success', 'message': '删除成功'}

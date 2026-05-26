from flask import request
from flask_restx import Namespace, Resource, fields
from ..extensions import db
from ..models.point import Point, ParkingEnforcement, Checkpoint
from ..models.project import Project
from datetime import date

ns = Namespace('points', description='点位管理')

point_model = ns.model('Point', {
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
    'device_count': fields.Integer(),
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
    'device_count': fields.Integer(),
    'camera_count': fields.Integer(),
    'strobe_light_count': fields.Integer(),
    'radar_count': fields.Integer(),
    'sign_count': fields.Integer(),
    'power_source': fields.String(),
    'network_source': fields.String()
})

@ns.route('/')
class PointList(Resource):
    def get(self):
        points = db.session.query(Point).all()
        result = []
        for p in points:
            data = p.to_dict()
            data.update(p.warranty_status)
            result.append(data)
        return result

    @ns.expect(point_model)
    def post(self):
        data = request.json
        point = Point(
            name=data['name'],
            area=data.get('area', ''),
            type=data.get('type', '')
        )
        db.session.add(point)
        db.session.commit()
        return {'status': 'success', 'data': point.to_dict()}, 201

@ns.route('/<int:point_id>')
class PointDetail(Resource):
    def get(self, point_id):
        point = db.session.query(Point).get(point_id)
        if not point:
            return {'status': 'error', 'message': '点位不存在'}, 404

        parking_enforcements = db.session.query(ParkingEnforcement).filter_by(point_id=point_id).all()
        checkpoints = db.session.query(Checkpoint).filter_by(point_id=point_id).all()

        return {
            'point': {**point.to_dict(), **point.warranty_status},
            'parking_enforcements': [pe.to_dict() for pe in parking_enforcements],
            'checkpoints': [cp.to_dict() for cp in checkpoints]
        }

    @ns.expect(point_model)
    def put(self, point_id):
        point = db.session.query(Point).get(point_id)
        if not point:
            return {'status': 'error', 'message': '点位不存在'}, 404
        
        data = request.json
        if 'name' in data:
            point.name = data['name']
        if 'area' in data:
            point.area = data['area']
        if 'type' in data:
            point.type = data['type']
        
        db.session.commit()
        return {'status': 'success', 'data': point.to_dict()}

    def delete(self, point_id):
        point = db.session.query(Point).get(point_id)
        if not point:
            return {'status': 'error', 'message': '点位不存在'}, 404
        
        db.session.delete(point)
        db.session.commit()
        return {'status': 'success', 'message': '删除成功'}

@ns.route('/parking-enforcement')
class ParkingEnforcementList(Resource):
    def get(self):
        parking_enforcements = db.session.query(ParkingEnforcement).all()
        return [pe.to_dict() for pe in parking_enforcements]

@ns.route('/<int:point_id>/parking-enforcement')
class ParkingEnforcementCreate(Resource):
    @ns.expect(parking_enforcement_model)
    def post(self, point_id):
        point = db.session.query(Point).get(point_id)
        if not point:
            return {'status': 'error', 'message': '点位不存在'}, 404
        
        data = request.json
        pe = ParkingEnforcement(
            point_id=point_id,
            project_id=data.get('project_id'),
            device_count=data.get('device_count', 0),
            camera_count=data.get('camera_count', 0),
            parking_sign_count=data.get('parking_sign_count', 0),
            monitor_sign_count=data.get('monitor_sign_count', 0),
            power_source=data.get('power_source', ''),
            network_source=data.get('network_source', '')
        )
        db.session.add(pe)
        db.session.commit()
        return {'status': 'success', 'data': pe.to_dict()}

@ns.route('/<int:point_id>/parking-enforcement/<int:pe_id>')
class ParkingEnforcementUpdate(Resource):
    @ns.expect(parking_enforcement_model)
    def put(self, point_id, pe_id):
        pe = db.session.query(ParkingEnforcement).filter_by(id=pe_id, point_id=point_id).first()
        if not pe:
            return {'status': 'error', 'message': '违停抓拍设备不存在'}, 404
        
        data = request.json
        for key in ['project_id', 'device_count', 'camera_count', 'parking_sign_count', 
                    'monitor_sign_count', 'power_source', 'network_source']:
            if key in data:
                setattr(pe, key, data[key])
        
        db.session.commit()
        return {'status': 'success', 'data': pe.to_dict()}

    def delete(self, point_id, pe_id):
        pe = db.session.query(ParkingEnforcement).filter_by(id=pe_id, point_id=point_id).first()
        if not pe:
            return {'status': 'error', 'message': '违停抓拍设备不存在'}, 404
        
        db.session.delete(pe)
        db.session.commit()
        return {'status': 'success', 'message': '删除成功'}

@ns.route('/checkpoints')
class CheckpointList(Resource):
    def get(self):
        checkpoints = db.session.query(Checkpoint).all()
        return [cp.to_dict() for cp in checkpoints]

@ns.route('/<int:point_id>/checkpoint')
class CheckpointCreate(Resource):
    @ns.expect(checkpoint_model)
    def post(self, point_id):
        point = db.session.query(Point).get(point_id)
        if not point:
            return {'status': 'error', 'message': '点位不存在'}, 404
        
        data = request.json
        cp = Checkpoint(
            point_id=point_id,
            project_id=data.get('project_id'),
            device_count=data.get('device_count', 0),
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

@ns.route('/<int:point_id>/checkpoint/<int:cp_id>')
class CheckpointUpdate(Resource):
    @ns.expect(checkpoint_model)
    def put(self, point_id, cp_id):
        cp = db.session.query(Checkpoint).filter_by(id=cp_id, point_id=point_id).first()
        if not cp:
            return {'status': 'error', 'message': '治安卡口设备不存在'}, 404
        
        data = request.json
        for key in ['project_id', 'device_count', 'camera_count', 'strobe_light_count', 
                    'radar_count', 'sign_count', 'power_source', 'network_source']:
            if key in data:
                setattr(cp, key, data[key])
        
        db.session.commit()
        return {'status': 'success', 'data': cp.to_dict()}

    def delete(self, point_id, cp_id):
        cp = db.session.query(Checkpoint).filter_by(id=cp_id, point_id=point_id).first()
        if not cp:
            return {'status': 'error', 'message': '治安卡口设备不存在'}, 404
        
        db.session.delete(cp)
        db.session.commit()
        return {'status': 'success', 'message': '删除成功'}


@ns.route('/<int:point_id>/extend-warranty')
class ExtendWarranty(Resource):
    def post(self, point_id):
        point = db.session.query(Point).get(point_id)
        if not point:
            return {'status': 'error', 'message': '点位不存在'}, 404

        data = request.json
        project = Project(
            name=data['project_name'],
            acceptance_date=date.today(),
            warranty_expire_date=date.fromisoformat(data['warranty_expire_date'])
        )
        db.session.add(project)
        db.session.flush()

        from ..models.backend_device import WarrantyExtension
        extension = WarrantyExtension(
            facility_type='point',
            facility_id=point_id,
            project_id=project.id,
            extension_date=date.today()
        )
        db.session.add(extension)
        db.session.commit()

        return {'status': 'success', 'project_id': project.id}
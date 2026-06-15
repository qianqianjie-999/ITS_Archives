from flask import request
from flask_restx import Namespace, Resource, fields
from ..extensions import db
from ..models.point import ParkingEnforcementPoint, CheckpointPoint, ParkingEnforcement, Checkpoint, SkyNetPoint, SkyNet
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
    'type': fields.String(),
    'latitude': fields.Float(),
    'longitude': fields.Float()
})

sky_net_point_model = ns.model('SkyNetPoint', {
    'id': fields.Integer(readonly=True),
    'name': fields.String(required=True),
    'monitor_area': fields.String(),
    'location': fields.String(),
    'latitude': fields.Float(),
    'longitude': fields.Float()
})

checkpoint_point_model = ns.model('CheckpointPoint', {
    'id': fields.Integer(readonly=True),
    'name': fields.String(required=True),
    'area': fields.String(),
    'type': fields.String(),
    'latitude': fields.Float(),
    'longitude': fields.Float()
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

sky_net_model = ns.model('SkyNet', {
    'id': fields.Integer(readonly=True),
    'point_id': fields.Integer(),
    'project_id': fields.Integer(),
    'project_name': fields.String(readonly=True),
    'warranty_expire_date': fields.String(readonly=True),
    'camera_count': fields.Integer(),
    'bracket_count': fields.Integer(),
    'pole_count': fields.Integer(),
    'box_count': fields.Integer(),
    'fill_light_count': fields.Integer(),
    'speaker_count': fields.Integer(),
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
    'model': fields.String(),
    'type': fields.String(),
    'quantity': fields.Integer(),
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
    @token_required
    def get(self):
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        if per_page == 0:
            points = db.session.query(ParkingEnforcementPoint).all()
            result = []
            for p in points:
                data = p.to_dict()
                data.update(p.warranty_status)
                result.append(data)
            return {'data': result}
        per_page = min(per_page, 100)
        paginated = db.session.query(ParkingEnforcementPoint).paginate(page=page, per_page=per_page, error_out=False)
        result = []
        for p in paginated.items:
            data = p.to_dict()
            data.update(p.warranty_status)
            result.append(data)
        return {
            'data': result,
            'page': paginated.page,
            'per_page': paginated.per_page,
            'total': paginated.total,
            'pages': paginated.pages
        }

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
    @token_required
    def get(self, point_id):
        point = db.session.query(ParkingEnforcementPoint).get(point_id)
        if not point:
            return {'status': 'error', 'message': '违停点位不存在'}, 404

        devices = db.session.query(ParkingEnforcement).filter_by(point_id=point_id).all()

        extensions = db.session.query(WarrantyExtension).filter_by(
            facility_type='point', facility_id=point_id
        ).all()

        return {
            'data': {
                'point': {**point.to_dict(), **point.warranty_status},
                'parking_enforcements': [pe.to_dict() for pe in devices],
                'warranty_extensions': [ext.to_dict() for ext in extensions]
            }
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
        if 'selected_project_id' in data:
            point.selected_project_id = data['selected_project_id']

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


# ==================== SkyNet Points ====================

@ns.route('/sky-net-points')
class SkyNetPointList(Resource):
    @token_required
    def get(self):
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        if per_page == 0:
            points = db.session.query(SkyNetPoint).all()
            result = []
            for p in points:
                data = p.to_dict()
                data.update(p.warranty_status)
                result.append(data)
            return {'data': result}
        per_page = min(per_page, 100)
        paginated = db.session.query(SkyNetPoint).paginate(page=page, per_page=per_page, error_out=False)
        result = []
        for p in paginated.items:
            data = p.to_dict()
            data.update(p.warranty_status)
            result.append(data)
        return {
            'data': result,
            'page': paginated.page,
            'per_page': paginated.per_page,
            'total': paginated.total,
            'pages': paginated.pages
        }

    @token_required
    @role_required('admin', 'editor')
    @ns.expect(sky_net_point_model)
    def post(self):
        data = request.json
        point = SkyNetPoint(
            name=data['name'],
            monitor_area=data.get('monitor_area', ''),
            location=data.get('location', '')
        )
        db.session.add(point)
        db.session.commit()
        return {'status': 'success', 'data': point.to_dict()}, 201


@ns.route('/sky-net-points/<int:point_id>')
class SkyNetPointDetail(Resource):
    @token_required
    def get(self, point_id):
        point = db.session.query(SkyNetPoint).get(point_id)
        if not point:
            return {'status': 'error', 'message': '天网点位不存在'}, 404

        devices = db.session.query(SkyNet).filter_by(point_id=point_id).all()

        extensions = db.session.query(WarrantyExtension).filter_by(
            facility_type='point', facility_id=point_id
        ).all()

        return {
            'data': {
                'point': {**point.to_dict(), **point.warranty_status},
                'sky_nets': [sn.to_dict() for sn in devices],
                'warranty_extensions': [ext.to_dict() for ext in extensions]
            }
        }

    @token_required
    @role_required('admin', 'editor')
    @ns.expect(sky_net_point_model)
    def put(self, point_id):
        point = db.session.query(SkyNetPoint).get(point_id)
        if not point:
            return {'status': 'error', 'message': '天网点位不存在'}, 404

        data = request.json
        if 'name' in data:
            point.name = data['name']
        if 'monitor_area' in data:
            point.monitor_area = data['monitor_area']
        if 'location' in data:
            point.location = data['location']
        if 'selected_project_id' in data:
            point.selected_project_id = data['selected_project_id']

        db.session.commit()
        return {'status': 'success', 'data': point.to_dict()}

    @token_required
    @role_required('admin')
    def delete(self, point_id):
        point = db.session.query(SkyNetPoint).get(point_id)
        if not point:
            return {'status': 'error', 'message': '天网点位不存在'}, 404

        db.session.delete(point)
        db.session.commit()
        return {'status': 'success', 'message': '删除成功'}


# ==================== SkyNet Devices ====================

@ns.route('/sky-net')
class SkyNetListAll(Resource):
    @token_required
    def get(self):
        sns = db.session.query(SkyNet).all()
        
        grouped = {}
        for sn in sns:
            key = sn.point_id
            if key not in grouped or sn.id > grouped[key].id:
                grouped[key] = sn
        
        return {'data': [sn.to_dict() for sn in grouped.values()]}


@ns.route('/sky-net-points/<int:point_id>/devices')
class SkyNetByPoint(Resource):
    @token_required
    def get(self, point_id):
        point = db.session.query(SkyNetPoint).get(point_id)
        if not point:
            return {'status': 'error', 'message': '天网点位不存在'}, 404
        sns = db.session.query(SkyNet).filter_by(point_id=point_id).all()
        return {'data': [sn.to_dict() for sn in sns]}

    @token_required
    @role_required('admin', 'editor')
    @ns.expect(sky_net_model)
    def post(self, point_id):
        point = db.session.query(SkyNetPoint).get(point_id)
        if not point:
            return {'status': 'error', 'message': '天网点位不存在'}, 404

        data = request.json
        sn = SkyNet(
            point_id=point_id,
            project_id=data.get('project_id'),
            camera_area=data.get('camera_area', ''),
            camera_count=data.get('camera_count', 0),
            bracket_count=data.get('bracket_count', 0),
            pole_count=data.get('pole_count', 0),
            box_count=data.get('box_count', 0),
            fill_light_count=data.get('fill_light_count', 0),
            speaker_count=data.get('speaker_count', 0),
            power_source=data.get('power_source', ''),
            network_source=data.get('network_source', '')
        )
        db.session.add(sn)
        db.session.commit()
        return {'status': 'success', 'data': sn.to_dict()}


@ns.route('/sky-net-points/<int:point_id>/devices/<int:sn_id>')
class SkyNetUpdate(Resource):
    @token_required
    @role_required('admin', 'editor')
    @ns.expect(sky_net_model)
    def put(self, point_id, sn_id):
        sn = db.session.query(SkyNet).filter_by(id=sn_id, point_id=point_id).first()
        if not sn:
            return {'status': 'error', 'message': '天网相机设备不存在'}, 404

        data = request.json
        for key in ['project_id', 'camera_area', 'camera_count', 'bracket_count',
                    'pole_count', 'box_count', 'fill_light_count', 'speaker_count',
                    'power_source', 'network_source']:
            if key in data:
                setattr(sn, key, data[key])

        db.session.commit()
        return {'status': 'success', 'data': sn.to_dict()}

    @token_required
    @role_required('admin')
    def delete(self, point_id, sn_id):
        sn = db.session.query(SkyNet).filter_by(id=sn_id, point_id=point_id).first()
        if not sn:
            return {'status': 'error', 'message': '天网相机设备不存在'}, 404
        db.session.delete(sn)
        db.session.commit()
        return {'status': 'success', 'message': '删除成功'}


# ==================== SkyNet Warranty Extension ====================

@ns.route('/sky-net-points/<int:point_id>/extend-warranty')
class SkyNetPointExtendWarranty(Resource):
    @token_required
    @role_required('admin', 'editor')
    @ns.expect(extend_warranty_model)
    def post(self, point_id):
        point = db.session.query(SkyNetPoint).get(point_id)
        if not point:
            return {'status': 'error', 'message': '天网点位不存在'}, 404

        data = request.json
        project_id = data.get('project_id')
        warranty_expire_date = date.fromisoformat(data['warranty_expire_date'])

        if project_id:
            project = db.session.query(Project).get(project_id)
            if not project:
                return {'status': 'error', 'message': '项目不存在'}, 404
        else:
            project_name = data.get('project_name', f'质保延期项目_{point.name}')
            project = Project(
                name=project_name,
                acceptance_date=date.today(),
                warranty_expire_date=warranty_expire_date
            )
            db.session.add(project)
            db.session.flush()

        created_count = 0

        devices = db.session.query(SkyNet).filter_by(point_id=point_id).all()
        for d in devices:
            new_sn = SkyNet(
                point_id=point_id,
                project_id=project.id,
                camera_area=d.camera_area,
                camera_count=d.camera_count,
                bracket_count=d.bracket_count,
                pole_count=d.pole_count,
                box_count=d.box_count,
                fill_light_count=d.fill_light_count,
                speaker_count=d.speaker_count,
                power_source=d.power_source,
                network_source=d.network_source
            )
            db.session.add(new_sn)
            created_count += 1

        if created_count == 0:
            db.session.rollback()
            return {'status': 'error', 'message': '没有可延期的设备'}, 400

        extension = WarrantyExtension(
            facility_type='point',
            facility_id=point_id,
            project_id=project.id,
            extension_date=date.today()
        )
        db.session.add(extension)

        db.session.commit()
        return {'status': 'success', 'project_id': project.id, 'message': f'已为{created_count}个设备创建质保延期记录'}


# ==================== Checkpoint Points ====================

@ns.route('/checkpoint-points')
class CheckpointPointList(Resource):
    @token_required
    def get(self):
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        if per_page == 0:
            points = db.session.query(CheckpointPoint).all()
            result = []
            for p in points:
                data = p.to_dict()
                data.update(p.warranty_status)
                result.append(data)
            return {'data': result}
        per_page = min(per_page, 100)
        paginated = db.session.query(CheckpointPoint).paginate(page=page, per_page=per_page, error_out=False)
        result = []
        for p in paginated.items:
            data = p.to_dict()
            data.update(p.warranty_status)
            result.append(data)
        return {
            'data': result,
            'page': paginated.page,
            'per_page': paginated.per_page,
            'total': paginated.total,
            'pages': paginated.pages
        }

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
    @token_required
    def get(self, point_id):
        point = db.session.query(CheckpointPoint).get(point_id)
        if not point:
            return {'status': 'error', 'message': '卡口点位不存在'}, 404

        devices = db.session.query(Checkpoint).filter_by(point_id=point_id).all()

        extensions = db.session.query(WarrantyExtension).filter_by(
            facility_type='point', facility_id=point_id
        ).all()

        return {
            'data': {
                'point': {**point.to_dict(), **point.warranty_status},
                'checkpoints': [cp.to_dict() for cp in devices],
                'warranty_extensions': [ext.to_dict() for ext in extensions]
            }
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
        if 'selected_project_id' in data:
            point.selected_project_id = data['selected_project_id']

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
    @token_required
    def get(self):
        pes = db.session.query(ParkingEnforcement).all()
        
        grouped = {}
        for pe in pes:
            key = pe.point_id
            if key not in grouped or pe.id > grouped[key].id:
                grouped[key] = pe
        
        return {'data': [pe.to_dict() for pe in grouped.values()]}

@ns.route('/parking-points/<int:point_id>/devices')
class ParkingEnforcementByPoint(Resource):
    @token_required
    def get(self, point_id):
        point = db.session.query(ParkingEnforcementPoint).get(point_id)
        if not point:
            return {'status': 'error', 'message': '违停点位不存在'}, 404
        pes = db.session.query(ParkingEnforcement).filter_by(point_id=point_id).all()
        return {'data': [pe.to_dict() for pe in pes]}

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
    @token_required
    def get(self):
        checkpoints = db.session.query(Checkpoint).all()
        
        grouped = {}
        for cp in checkpoints:
            key = cp.point_id
            if key not in grouped or cp.id > grouped[key].id:
                grouped[key] = cp
        
        return {'data': [cp.to_dict() for cp in grouped.values()]}


@ns.route('/checkpoint-points/<int:point_id>/devices')
class CheckpointByPoint(Resource):
    @token_required
    def get(self, point_id):
        point = db.session.query(CheckpointPoint).get(point_id)
        if not point:
            return {'status': 'error', 'message': '卡口点位不存在'}, 404
        checkpoints = db.session.query(Checkpoint).filter_by(point_id=point_id).all()
        return {'data': [cp.to_dict() for cp in checkpoints]}

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
        warranty_expire_date = date.fromisoformat(data['warranty_expire_date'])

        if project_id:
            project = db.session.query(Project).get(project_id)
            if not project:
                return {'status': 'error', 'message': '项目不存在'}, 404
        else:
            project_name = data.get('project_name', f'质保延期项目_{point.name}')
            project = Project(
                name=project_name,
                acceptance_date=date.today(),
                warranty_expire_date=warranty_expire_date
            )
            db.session.add(project)
            db.session.flush()

        created_count = 0

        devices = db.session.query(ParkingEnforcement).filter_by(point_id=point_id).all()
        for d in devices:
            new_pe = ParkingEnforcement(
                point_id=point_id,
                project_id=project.id,
                camera_area=d.camera_area,
                camera_count=d.camera_count,
                parking_sign_count=d.parking_sign_count,
                monitor_sign_count=d.monitor_sign_count,
                power_source=d.power_source,
                network_source=d.network_source
            )
            db.session.add(new_pe)
            created_count += 1

        if created_count == 0:
            db.session.rollback()
            return {'status': 'error', 'message': '没有可延期的设备'}, 400

        extension = WarrantyExtension(
            facility_type='point',
            facility_id=point_id,
            project_id=project.id,
            extension_date=date.today()
        )
        db.session.add(extension)

        db.session.commit()
        return {'status': 'success', 'project_id': project.id, 'message': f'已为{created_count}个设备创建质保延期记录'}


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
        warranty_expire_date = date.fromisoformat(data['warranty_expire_date'])

        if project_id:
            project = db.session.query(Project).get(project_id)
            if not project:
                return {'status': 'error', 'message': '项目不存在'}, 404
        else:
            project_name = data.get('project_name', f'质保延期项目_{point.name}')
            project = Project(
                name=project_name,
                acceptance_date=date.today(),
                warranty_expire_date=warranty_expire_date
            )
            db.session.add(project)
            db.session.flush()

        created_count = 0

        devices = db.session.query(Checkpoint).filter_by(point_id=point_id).all()
        for d in devices:
            new_cp = Checkpoint(
                point_id=point_id,
                project_id=project.id,
                checkpoint_type=d.checkpoint_type,
                camera_count=d.camera_count,
                strobe_light_count=d.strobe_light_count,
                radar_count=d.radar_count,
                sign_count=d.sign_count,
                power_source=d.power_source,
                network_source=d.network_source
            )
            db.session.add(new_cp)
            created_count += 1

        if created_count == 0:
            db.session.rollback()
            return {'status': 'error', 'message': '没有可延期的设备'}, 400

        extension = WarrantyExtension(
            facility_type='point',
            facility_id=point_id,
            project_id=project.id,
            extension_date=date.today()
        )
        db.session.add(extension)

        db.session.commit()
        return {'status': 'success', 'project_id': project.id, 'message': f'已为{created_count}个设备创建质保延期记录'}


# ==================== Backend Devices ====================

@ns.route('/backend-devices')
class BackendDeviceList(Resource):
    @token_required
    def get(self):
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)

        backend_devices = db.session.query(BackendDevice).order_by(BackendDevice.id).all()
        import re
        suffix_pattern = re.compile(r' \(\d+\)$')

        filtered_devices = [bd for bd in backend_devices if not suffix_pattern.search(bd.name)]
        total = len(filtered_devices)

        if per_page == 0:
            return {
                'data': [bd.to_dict() for bd in filtered_devices],
                'page': 1,
                'per_page': total,
                'total': total,
                'pages': 1
            }

        per_page = min(per_page, 100)
        pages = (total + per_page - 1) // per_page
        start = (page - 1) * per_page
        end = start + per_page
        page_items = filtered_devices[start:end]

        return {
            'data': [bd.to_dict() for bd in page_items],
            'page': page,
            'per_page': per_page,
            'total': total,
            'pages': pages
        }

    @token_required
    @role_required('admin', 'editor')
    @ns.expect(backend_device_model)
    def post(self):
        data = request.json
        bd = BackendDevice(
            point_id=data.get('point_id'),
            project_id=data.get('project_id'),
            name=data.get('name', ''),
            model=data.get('model', ''),
            type=data.get('type', ''),
            quantity=data.get('quantity', 1)
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
        for key in ['name', 'model', 'type', 'quantity', 'project_id', 'server_count', 'storage_count',
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


@ns.route('/backend-device/<int:bd_id>/extend-warranty')
class BackendDeviceExtendWarranty(Resource):
    @token_required
    @role_required('admin', 'editor')
    @ns.expect(extend_warranty_model)
    def post(self, bd_id):
        bd = db.session.query(BackendDevice).get(bd_id)
        if not bd:
            return {'status': 'error', 'message': '后端设备不存在'}, 404

        data = request.json
        project_id = data.get('project_id')
        warranty_expire_date = date.fromisoformat(data['warranty_expire_date'])

        if project_id:
            project = db.session.query(Project).get(project_id)
            if not project:
                return {'status': 'error', 'message': '项目不存在'}, 404
        else:
            project_name = data.get('project_name', f'质保延期项目_{bd.name}')
            project = Project(
                name=project_name,
                acceptance_date=date.today(),
                warranty_expire_date=warranty_expire_date
            )
            db.session.add(project)
            db.session.flush()

        # 把现有记录重命名（加后缀），新记录用原始名称
        base_name = bd.name
        
        # 查找现有记录并加后缀
        existing_devices = db.session.query(BackendDevice).filter_by(name=base_name).all()
        for idx, existing_bd in enumerate(existing_devices, 1):
            new_existing_name = f"{base_name} ({idx})"
            # 确保目标名称不重复
            while db.session.query(BackendDevice).filter_by(name=new_existing_name).first():
                idx += 1
                new_existing_name = f"{base_name} ({idx})"
            existing_bd.name = new_existing_name
        
        new_bd = BackendDevice(
            point_id=bd.point_id,
            project_id=project.id,
            name=base_name,
            type=bd.type,
            server_count=bd.server_count,
            storage_count=bd.storage_count,
            switch_count=bd.switch_count,
            firewall_count=bd.firewall_count,
            fiber_converter_count=bd.fiber_converter_count,
            power_supply_count=bd.power_supply_count,
            cabinet_count=bd.cabinet_count,
            other_device_count=bd.other_device_count,
            ip_address=bd.ip_address,
            port=bd.port,
            location=bd.location,
            power_source=bd.power_source,
            network_source=bd.network_source
        )
        db.session.add(new_bd)

        from ..models.warranty_extension import WarrantyExtension
        extension = WarrantyExtension(
            facility_type='backend_device',
            facility_id=bd_id,
            project_id=project.id,
            extension_date=date.today()
        )
        db.session.add(extension)

        db.session.commit()
        return {'status': 'success', 'project_id': project.id, 'message': '已创建质保延期记录'}


@ns.route('/backend-device/<int:bd_id>/history')
class BackendDeviceHistory(Resource):
    def get(self, bd_id):
        bd = db.session.query(BackendDevice).get(bd_id)
        if not bd:
            return {'status': 'error', 'message': '后端设备不存在'}, 404
        
        # 获取设备原始名称（去掉 (数字) 后缀）
        import re
        base_name = re.sub(r' \(\d+\)$', '', bd.name)
        
        # 查找所有以此名称开头的记录，按ID升序（最早的在前）
        history_records = db.session.query(BackendDevice).filter(
            BackendDevice.name.like(f"{base_name}%")
        ).order_by(BackendDevice.id.asc()).all()
        
        return {'data': [hr.to_dict() for hr in history_records]}

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
        
        grouped = {}
        for pe in pes:
            key = pe.point_id
            if key not in grouped or pe.id > grouped[key].id:
                grouped[key] = pe
        
        return [pe.to_dict() for pe in grouped.values()]

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
        
        grouped = {}
        for cp in checkpoints:
            key = cp.point_id
            if key not in grouped or cp.id > grouped[key].id:
                grouped[key] = cp
        
        return [cp.to_dict() for cp in grouped.values()]


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
    def get(self):
        backend_devices = db.session.query(BackendDevice).all()
        
        # 过滤出不带 "(数字)" 后缀的记录（原始名称记录，即最新记录）
        filtered_devices = []
        import re
        suffix_pattern = re.compile(r' \(\d+\)$')
        
        for bd in backend_devices:
            if not suffix_pattern.search(bd.name):
                filtered_devices.append(bd)
        
        return [bd.to_dict() for bd in filtered_devices]

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
        
        return [hr.to_dict() for hr in history_records]

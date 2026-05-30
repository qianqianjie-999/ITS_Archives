from flask import request
from flask_restx import Namespace, Resource, fields
from ..extensions import db
from ..models.intersection import Intersection, TrafficLight, ElectronicPolice
from ..models.project import Project
from ..utils.decorators import token_required, role_required
from datetime import date

ns = Namespace('intersections', description='路口管理')

intersection_model = ns.model('Intersection', {
    'id': fields.Integer(readonly=True),
    'name': fields.String(required=True),
    'type': fields.String(),
    'east_west_road': fields.String(),
    'north_south_road': fields.String()
})

intersection_detail_model = ns.model('IntersectionDetail', {
    'id': fields.Integer(),
    'name': fields.String(),
    'type': fields.String(),
    'east_west_road': fields.String(),
    'north_south_road': fields.String(),
    'warranty_status': fields.String(),
    'latest_expire_date': fields.String()
})

traffic_light_model = ns.model('TrafficLight', {
    'id': fields.Integer(readonly=True),
    'intersection_id': fields.Integer(),
    'project_id': fields.Integer(),
    'project_name': fields.String(readonly=True),
    'warranty_expire_date': fields.String(readonly=True),
    'signal_type': fields.String(),
    'signal_count': fields.Integer(),
    'left_arrow_count': fields.Integer(),
    'straight_arrow_count': fields.Integer(),
    'right_arrow_count': fields.Integer(),
    'full_screen_count': fields.Integer(),
    'non_motor_count': fields.Integer(),
    'pedestrian_count': fields.Integer(),
    'radar_count': fields.Integer(),
    'guide_screen_count': fields.Integer(),
    'power_source': fields.String()
})

electronic_police_model = ns.model('ElectronicPolice', {
    'id': fields.Integer(readonly=True),
    'intersection_id': fields.Integer(),
    'project_id': fields.Integer(),
    'project_name': fields.String(readonly=True),
    'warranty_expire_date': fields.String(readonly=True),
    'capture_type': fields.String(),
    'terminal_server_count': fields.Integer(),
    'forward_capture_count': fields.Integer(),
    'reverse_capture_count': fields.Integer(),
    'led_light_count': fields.Integer(),
    'strobe_light_count': fields.Integer(),
    'ptz_count': fields.Integer(),
    'signal_detector_count': fields.Integer(),
    'network_source': fields.String()
})

@ns.route('/')
class IntersectionList(Resource):
    def get(self):
        intersections = db.session.query(Intersection).all()
        result = []
        for i in intersections:
            data = i.to_dict()
            data.update(i.warranty_status)
            result.append(data)
        return result

    @token_required
    @role_required('admin', 'editor')
    @ns.expect(intersection_model)
    def post(self):
        data = request.json
        intersection = Intersection(
            name=data['name'],
            type=data.get('type', ''),
            east_west_road=data.get('east_west_road'),
            north_south_road=data.get('north_south_road')
        )
        db.session.add(intersection)
        db.session.commit()
        return {'status': 'success', 'data': intersection.to_dict()}, 201

@ns.route('/<int:intersection_id>')
class IntersectionDetail(Resource):
    def get(self, intersection_id):
        intersection = db.session.query(Intersection).get(intersection_id)
        if not intersection:
            return {'status': 'error', 'message': '路口不存在'}, 404

        traffic_lights = db.session.query(TrafficLight).filter_by(intersection_id=intersection_id).all()
        electronic_polices = db.session.query(ElectronicPolice).filter_by(intersection_id=intersection_id).all()

        return {
            'intersection': {**intersection.to_dict(), **intersection.warranty_status},
            'traffic_lights': [tl.to_dict() for tl in traffic_lights],
            'electronic_polices': [ep.to_dict() for ep in electronic_polices]
        }

    @token_required
    @role_required('admin', 'editor')
    @ns.expect(intersection_model)
    def put(self, intersection_id):
        intersection = db.session.query(Intersection).get(intersection_id)
        if not intersection:
            return {'status': 'error', 'message': '路口不存在'}, 404

        data = request.json
        if 'name' in data:
            intersection.name = data['name']
        if 'type' in data:
            intersection.type = data['type']
        if 'east_west_road' in data:
            intersection.east_west_road = data['east_west_road']
        if 'north_south_road' in data:
            intersection.north_south_road = data['north_south_road']

        db.session.commit()
        return {'status': 'success', 'data': intersection.to_dict()}

    @token_required
    @role_required('admin')
    def delete(self, intersection_id):
        intersection = db.session.query(Intersection).get(intersection_id)
        if not intersection:
            return {'status': 'error', 'message': '路口不存在'}, 404

        db.session.delete(intersection)
        db.session.commit()
        return {'status': 'success', 'message': '删除成功'}

@ns.route('/traffic-lights')
class TrafficLightListAll(Resource):
    def get(self):
        traffic_lights = db.session.query(TrafficLight).all()
        
        grouped = {}
        for tl in traffic_lights:
            key = tl.intersection_id
            if key not in grouped or tl.id > grouped[key].id:
                grouped[key] = tl
        
        return [tl.to_dict() for tl in grouped.values()]

@ns.route('/electronic-polices')
class ElectronicPoliceListAll(Resource):
    def get(self):
        electronic_polices = db.session.query(ElectronicPolice).all()
        
        grouped = {}
        for ep in electronic_polices:
            key = ep.intersection_id
            if key not in grouped or ep.id > grouped[key].id:
                grouped[key] = ep
        
        return [ep.to_dict() for ep in grouped.values()]

@ns.route('/<int:intersection_id>/traffic-light')
class TrafficLightCreate(Resource):
    @token_required
    @role_required('admin', 'editor')
    @ns.expect(traffic_light_model)
    def post(self, intersection_id):
        intersection = db.session.query(Intersection).get(intersection_id)
        if not intersection:
            return {'status': 'error', 'message': '路口不存在'}, 404

        data = request.json
        traffic_light = TrafficLight(
            intersection_id=intersection_id,
            project_id=data.get('project_id'),
            signal_type=data.get('signal_type', ''),
            signal_count=data.get('signal_count', 0),
            left_arrow_count=data.get('left_arrow_count', 0),
            straight_arrow_count=data.get('straight_arrow_count', 0),
            right_arrow_count=data.get('right_arrow_count', 0),
            full_screen_count=data.get('full_screen_count', 0),
            non_motor_count=data.get('non_motor_count', 0),
            pedestrian_count=data.get('pedestrian_count', 0),
            radar_count=data.get('radar_count', 0),
            guide_screen_count=data.get('guide_screen_count', 0),
            power_source=data.get('power_source', '')
        )
        db.session.add(traffic_light)
        db.session.commit()
        return {'status': 'success', 'data': traffic_light.to_dict()}, 201

@ns.route('/<int:intersection_id>/traffic-light/<int:tl_id>')
class TrafficLightUpdate(Resource):
    @token_required
    @role_required('admin', 'editor')
    @ns.expect(traffic_light_model)
    def put(self, intersection_id, tl_id):
        traffic_light = db.session.query(TrafficLight).filter_by(id=tl_id, intersection_id=intersection_id).first()
        if not traffic_light:
            return {'status': 'error', 'message': '信号灯不存在'}, 404

        data = request.json
        for key in ['project_name', 'signal_type', 'signal_count', 'left_arrow_count', 'straight_arrow_count',
                    'right_arrow_count', 'full_screen_count', 'non_motor_count', 'pedestrian_count',
                    'radar_count', 'guide_screen_count', 'power_source']:
            if key in data:
                setattr(traffic_light, key, data[key])

        db.session.commit()
        return {'status': 'success', 'data': traffic_light.to_dict()}

    @token_required
    @role_required('admin')
    def delete(self, intersection_id, tl_id):
        traffic_light = db.session.query(TrafficLight).filter_by(id=tl_id, intersection_id=intersection_id).first()
        if not traffic_light:
            return {'status': 'error', 'message': '信号灯不存在'}, 404

        db.session.delete(traffic_light)
        db.session.commit()
        return {'status': 'success', 'message': '删除成功'}

@ns.route('/<int:intersection_id>/electronic-police')
class ElectronicPoliceCreate(Resource):
    @token_required
    @role_required('admin', 'editor')
    @ns.expect(electronic_police_model)
    def post(self, intersection_id):
        intersection = db.session.query(Intersection).get(intersection_id)
        if not intersection:
            return {'status': 'error', 'message': '路口不存在'}, 404

        data = request.json
        ep = ElectronicPolice(
            intersection_id=intersection_id,
            project_id=data.get('project_id'),
            capture_type=data.get('capture_type', ''),
            terminal_server_count=data.get('terminal_server_count', 0),
            forward_capture_count=data.get('forward_capture_count', 0),
            reverse_capture_count=data.get('reverse_capture_count', 0),
            led_light_count=data.get('led_light_count', 0),
            strobe_light_count=data.get('strobe_light_count', 0),
            ptz_count=data.get('ptz_count', 0),
            signal_detector_count=data.get('signal_detector_count', 0),
            network_source=data.get('network_source', '')
        )
        db.session.add(ep)
        db.session.commit()
        return {'status': 'success', 'data': ep.to_dict()}, 201

@ns.route('/<int:intersection_id>/electronic-police/<int:ep_id>')
class ElectronicPoliceUpdate(Resource):
    @token_required
    @role_required('admin', 'editor')
    @ns.expect(electronic_police_model)
    def put(self, intersection_id, ep_id):
        ep = db.session.query(ElectronicPolice).filter_by(id=ep_id, intersection_id=intersection_id).first()
        if not ep:
            return {'status': 'error', 'message': '电子警察不存在'}, 404

        data = request.json
        if 'project_id' in data:
            ep.project_id = data['project_id']
        for key in ['capture_type', 'terminal_server_count', 'forward_capture_count',
                    'reverse_capture_count', 'led_light_count', 'strobe_light_count',
                    'ptz_count', 'signal_detector_count', 'network_source']:
            if key in data:
                setattr(ep, key, data[key])

        db.session.commit()
        return {'status': 'success', 'data': ep.to_dict()}

    @token_required
    @role_required('admin')
    def delete(self, intersection_id, ep_id):
        ep = db.session.query(ElectronicPolice).filter_by(id=ep_id, intersection_id=intersection_id).first()
        if not ep:
            return {'status': 'error', 'message': '电子警察不存在'}, 404

        db.session.delete(ep)
        db.session.commit()
        return {'status': 'success', 'message': '删除成功'}

@ns.route('/<int:intersection_id>/extend-warranty')
class ExtendWarranty(Resource):
    @token_required
    @role_required('admin', 'editor')
    def post(self, intersection_id):
        intersection = db.session.query(Intersection).get(intersection_id)
        if not intersection:
            return {'status': 'error', 'message': '路口不存在'}, 404

        data = request.json
        device_type = data.get('device_type', 'both')
        project_id = data.get('project_id')
        warranty_expire_date = date.fromisoformat(data['warranty_expire_date'])

        if project_id:
            project = db.session.query(Project).get(project_id)
            if not project:
                return {'status': 'error', 'message': '项目不存在'}, 404
        else:
            project_name = data.get('project_name', f'质保延期项目_{intersection.name}')
            project = Project(
                name=project_name,
                acceptance_date=date.today(),
                warranty_expire_date=warranty_expire_date
            )
            db.session.add(project)
            db.session.flush()

        created_count = 0

        if device_type in ['traffic_light', 'both']:
            traffic_lights = db.session.query(TrafficLight).filter_by(intersection_id=intersection_id).all()
            for tl in traffic_lights:
                new_tl = TrafficLight(
                    intersection_id=intersection_id,
                    project_id=project.id,
                    signal_type=tl.signal_type,
                    signal_count=tl.signal_count,
                    left_arrow_count=tl.left_arrow_count,
                    straight_arrow_count=tl.straight_arrow_count,
                    right_arrow_count=tl.right_arrow_count,
                    full_screen_count=tl.full_screen_count,
                    non_motor_count=tl.non_motor_count,
                    pedestrian_count=tl.pedestrian_count,
                    radar_count=tl.radar_count,
                    guide_screen_count=tl.guide_screen_count,
                    power_source=tl.power_source
                )
                db.session.add(new_tl)
                created_count += 1

        if device_type in ['electronic_police', 'both']:
            electronic_polices = db.session.query(ElectronicPolice).filter_by(intersection_id=intersection_id).all()
            for ep in electronic_polices:
                new_ep = ElectronicPolice(
                    intersection_id=intersection_id,
                    project_id=project.id,
                    capture_type=ep.capture_type,
                    terminal_server_count=ep.terminal_server_count,
                    forward_capture_count=ep.forward_capture_count,
                    reverse_capture_count=ep.reverse_capture_count,
                    led_light_count=ep.led_light_count,
                    strobe_light_count=ep.strobe_light_count,
                    ptz_count=ep.ptz_count,
                    signal_detector_count=ep.signal_detector_count,
                    network_source=ep.network_source
                )
                db.session.add(new_ep)
                created_count += 1

        if created_count == 0:
            db.session.rollback()
            return {'status': 'error', 'message': '没有可延期的设备'}, 400

        from ..models.warranty_extension import WarrantyExtension
        extension = WarrantyExtension(
            facility_type='intersection',
            facility_id=intersection_id,
            project_id=project.id,
            extension_date=date.today()
        )
        db.session.add(extension)

        db.session.commit()

        return {'status': 'success', 'project_id': project.id, 'message': f'已为{created_count}个设备创建质保延期记录'}
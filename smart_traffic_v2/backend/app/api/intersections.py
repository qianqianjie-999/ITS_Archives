from flask import request
from flask_restx import Namespace, Resource, fields
from ..extensions import db
from ..models.intersection import Intersection, TrafficLight, ElectronicPolice
from ..models.project import Project
from datetime import date

ns = Namespace('intersections', description='路口管理')

intersection_model = ns.model('Intersection', {
    'id': fields.Integer(readonly=True),
    'name': fields.String(required=True),
    'type': fields.String()
})

intersection_detail_model = ns.model('IntersectionDetail', {
    'id': fields.Integer(),
    'name': fields.String(),
    'type': fields.String(),
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

@ns.route('/<int:intersection_id>/traffic-light/<int:tl_id>')
class TrafficLightUpdate(Resource):
    @ns.expect(traffic_light_model)
    def put(self, intersection_id, tl_id):
        traffic_light = db.session.query(TrafficLight).filter_by(id=tl_id, intersection_id=intersection_id).first()
        if not traffic_light:
            return {'status': 'error', 'message': '信号灯不存在'}, 404

        data = request.json
        for key in ['signal_type', 'signal_count', 'left_arrow_count', 'straight_arrow_count',
                    'right_arrow_count', 'full_screen_count', 'non_motor_count', 'pedestrian_count',
                    'radar_count', 'guide_screen_count', 'power_source']:
            if key in data:
                setattr(traffic_light, key, data[key])

        db.session.commit()
        return {'status': 'success', 'data': traffic_light.to_dict()}

@ns.route('/<int:intersection_id>/electronic-police/<int:ep_id>')
class ElectronicPoliceUpdate(Resource):
    @ns.expect(electronic_police_model)
    def put(self, intersection_id, ep_id):
        ep = db.session.query(ElectronicPolice).filter_by(id=ep_id, intersection_id=intersection_id).first()
        if not ep:
            return {'status': 'error', 'message': '电子警察不存在'}, 404

        data = request.json
        for key in ['capture_type', 'terminal_server_count', 'forward_capture_count',
                    'reverse_capture_count', 'led_light_count', 'strobe_light_count',
                    'ptz_count', 'signal_detector_count', 'network_source']:
            if key in data:
                setattr(ep, key, data[key])

        db.session.commit()
        return {'status': 'success', 'data': ep.to_dict()}

@ns.route('/<int:intersection_id>/extend-warranty')
class ExtendWarranty(Resource):
    def post(self, intersection_id):
        intersection = db.session.query(Intersection).get(intersection_id)
        if not intersection:
            return {'status': 'error', 'message': '路口不存在'}, 404

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
            facility_type='intersection',
            facility_id=intersection_id,
            project_id=project.id,
            extension_date=date.today()
        )
        db.session.add(extension)
        db.session.commit()

        return {'status': 'success', 'project_id': project.id}
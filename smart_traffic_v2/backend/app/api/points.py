from flask_restx import Namespace, Resource, fields
from ..extensions import db
from ..models.point import Point, ParkingEnforcement, Checkpoint

ns = Namespace('points', description='点位管理')

point_model = ns.model('Point', {
    'id': fields.Integer(readonly=True),
    'name': fields.String(required=True),
    'area': fields.String(),
    'type': fields.String()
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
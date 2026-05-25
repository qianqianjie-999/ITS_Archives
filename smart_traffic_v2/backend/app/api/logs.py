import json
from flask import request
from flask_restx import Namespace, Resource, fields
from ..extensions import db
from ..models.user import OperationLog

ns = Namespace('logs', description='操作日志')

log_model = ns.model('OperationLog', {
    'id': fields.Integer(readonly=True),
    'user_id': fields.Integer(),
    'username': fields.String(),
    'operation_type': fields.String(),
    'entity_type': fields.String(),
    'entity_id': fields.Integer(),
    'old_value': fields.Raw(),
    'new_value': fields.Raw(),
    'ip_address': fields.String(),
    'operation_time': fields.String()
})

@ns.route('/')
class LogList(Resource):
    def get(self):
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        offset = (page - 1) * per_page

        total = db.session.query(OperationLog).count()
        logs = db.session.query(OperationLog).order_by(
            OperationLog.operation_time.desc()
        ).limit(per_page).offset(offset).all()

        result = []
        for log in logs:
            data = log.to_dict()
            if data.get('old_value'):
                try:
                    data['old_value'] = json.loads(data['old_value'])
                except:
                    pass
            if data.get('new_value'):
                try:
                    data['new_value'] = json.loads(data['new_value'])
                except:
                    pass
            result.append(data)

        return {
            'status': 'success',
            'logs': result,
            'total': total,
            'page': page,
            'per_page': per_page
        }
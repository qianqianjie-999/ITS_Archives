from flask import request, g
from flask_restx import Namespace, Resource, fields
from ..extensions import db
from ..models.maintenance_record import MaintenanceRecord
from ..models.user import User
from ..utils.decorators import token_required, role_required
from datetime import datetime

ns = Namespace('maintenance', description='维修记录管理')

maintenance_record_model = ns.model('MaintenanceRecord', {
    'id': fields.Integer(readonly=True),
    'facility_type': fields.String(required=True),
    'facility_id': fields.Integer(required=True),
    'fault_level': fields.String(required=True),
    'fault_level_text': fields.String(readonly=True),
    'fault_description': fields.String(required=True),
    'fault_time': fields.String(readonly=True),
    'solution': fields.String(),
    'record_time': fields.String(readonly=True),
    'recorder_id': fields.Integer(required=True),
    'recorder_name': fields.String(readonly=True)
})

maintenance_create_model = ns.model('MaintenanceRecordCreate', {
    'facility_type': fields.String(required=True),
    'facility_id': fields.Integer(required=True),
    'fault_level': fields.String(required=True),
    'fault_description': fields.String(required=True),
    'fault_time': fields.String(),
    'solution': fields.String()
})


@ns.route('/<facility_type>/<int:facility_id>')
class MaintenanceRecordList(Resource):
    @token_required
    def get(self, facility_type, facility_id):
        records = MaintenanceRecord.query.filter_by(
            facility_type=facility_type,
            facility_id=facility_id
        ).order_by(MaintenanceRecord.record_time.desc()).all()
        return {'data': [record.to_dict() for record in records]}


@ns.route('/')
class MaintenanceRecordResource(Resource):
    @token_required
    @ns.expect(maintenance_create_model)
    def post(self):
        data = request.json
        current_user = g.current_user
        
        fault_time = None
        if data.get('fault_time'):
            try:
                fault_time = datetime.fromisoformat(data['fault_time'].replace('Z', '+00:00'))
            except:
                fault_time = None
        
        record = MaintenanceRecord(
            facility_type=data['facility_type'],
            facility_id=data['facility_id'],
            fault_level=data['fault_level'],
            fault_description=data['fault_description'],
            fault_time=fault_time,
            solution=data.get('solution'),
            recorder_id=current_user.id
        )
        
        db.session.add(record)
        db.session.commit()
        
        return {'data': record.to_dict()}, 201

    @token_required
    @role_required('admin')
    @ns.doc(params={'id': '维修记录ID'})
    def delete(self):
        record_id = request.args.get('id')
        if not record_id:
            return {'status': 'error', 'message': '缺少记录ID'}, 400
        
        record = MaintenanceRecord.query.get(record_id)
        if not record:
            return {'status': 'error', 'message': '维修记录不存在'}, 404
        
        db.session.delete(record)
        db.session.commit()
        
        return {'status': 'success', 'message': '维修记录已删除'}
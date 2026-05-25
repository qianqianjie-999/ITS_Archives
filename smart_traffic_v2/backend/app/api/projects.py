from flask import request
from flask_restx import Namespace, Resource, fields
from ..extensions import db
from ..models.project import Project
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
    'constructor': fields.String()
})

@ns.route('/')
class ProjectList(Resource):
    def get(self):
        projects = db.session.query(Project).order_by(Project.id.desc()).all()
        return [p.to_dict() for p in projects]

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
            constructor=data.get('constructor')
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

    @ns.expect(project_model)
    def put(self, project_id):
        project = db.session.query(Project).get(project_id)
        if not project:
            return {'status': 'error', 'message': '项目不存在'}, 404

        data = request.json
        for key in ['name', 'contract_amount', 'acceptance_date', 'warranty_period',
                    'warranty_expire_date', 'builder', 'constructor']:
            if key in data:
                if key in ['acceptance_date', 'warranty_expire_date'] and data[key]:
                    setattr(project, key, date.fromisoformat(data[key]))
                else:
                    setattr(project, key, data[key])

        db.session.commit()
        return {'status': 'success', 'data': project.to_dict()}

    def delete(self, project_id):
        project = db.session.query(Project).get(project_id)
        if not project:
            return {'status': 'error', 'message': '项目不存在'}, 404
        db.session.delete(project)
        db.session.commit()
        return {'status': 'success'}
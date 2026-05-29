from flask import request, send_from_directory, current_app
from flask_restx import Namespace, Resource, fields
from ..extensions import db
from ..models.attachment import Attachment
from ..models.intersection import Intersection
from ..models.point import ParkingEnforcementPoint, CheckpointPoint
from ..utils.decorators import token_required, role_required
import os
from werkzeug.utils import secure_filename

ns = Namespace('attachments', description='附件管理')

attachment_model = ns.model('Attachment', {
    'id': fields.Integer(readonly=True),
    'related_entity_type': fields.String(),
    'related_entity_id': fields.Integer(),
    'file_name': fields.String(),
    'original_filename': fields.String(),
    'file_size': fields.Integer(),
    'upload_time': fields.String(readonly=True)
})

ALLOWED_EXTENSIONS = {'pdf', 'doc', 'docx', 'xls', 'xlsx', 'jpg', 'jpeg', 'png', 'gif'}


def _get_upload_folder():
    return current_app.config['UPLOAD_FOLDER']

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@ns.route('/')
class AttachmentList(Resource):
    def get(self):
        related_entity_type = request.args.get('related_entity_type')
        related_entity_id = request.args.get('related_entity_id', type=int)
        
        query = db.session.query(Attachment)
        if related_entity_type:
            query = query.filter_by(related_entity_type=related_entity_type)
        if related_entity_id:
            query = query.filter_by(related_entity_id=related_entity_id)
        
        return [a.to_dict() for a in query.all()]

@ns.route('/upload')
class AttachmentUpload(Resource):
    @token_required
    @role_required('admin', 'editor')
    def post(self):
        if 'file' not in request.files:
            return {'status': 'error', 'message': '未选择文件'}, 400
        
        file = request.files['file']
        if file.filename == '':
            return {'status': 'error', 'message': '未选择文件'}, 400
        
        if file and allowed_file(file.filename):
            related_entity_type = request.form.get('related_entity_type')
            related_entity_id = request.form.get('related_entity_id', type=int)
            
            if not related_entity_type or related_entity_id is None:
                return {'status': 'error', 'message': '缺少实体类型或ID'}, 400
            
            if related_entity_type == 'intersection':
                facility = db.session.query(Intersection).get(related_entity_id)
            elif related_entity_type == 'point' or related_entity_type == 'parking_enforcement':
                facility = db.session.query(ParkingEnforcementPoint).get(related_entity_id) or db.session.query(CheckpointPoint).get(related_entity_id)
            else:
                return {'status': 'error', 'message': '无效的实体类型'}, 400
            
            if not facility:
                return {'status': 'error', 'message': '实体不存在'}, 404
            
            filename = secure_filename(file.filename)
            unique_filename = f"{related_entity_type}_{related_entity_id}_{filename}"
            upload_folder = _get_upload_folder()
            file_path = os.path.join(upload_folder, unique_filename)
            file.save(file_path)
            
            attachment = Attachment(
                related_entity_type=related_entity_type,
                related_entity_id=related_entity_id,
                file_name=unique_filename,
                file_path=file_path,
                original_filename=filename,
                file_size=os.path.getsize(file_path)
            )
            db.session.add(attachment)
            db.session.commit()
            
            return {'status': 'success', 'data': attachment.to_dict()}, 201
        
        return {'status': 'error', 'message': '不允许的文件类型'}, 400

@ns.route('/<int:attachment_id>')
class AttachmentDetail(Resource):
    def get(self, attachment_id):
        attachment = db.session.query(Attachment).get(attachment_id)
        if not attachment:
            return {'status': 'error', 'message': '附件不存在'}, 404

        upload_folder = _get_upload_folder()
        file_path = os.path.join(upload_folder, attachment.file_name)
        if not os.path.exists(file_path):
            return {'status': 'error', 'message': '文件已删除'}, 404

        return send_from_directory(upload_folder, attachment.file_name, as_attachment=True, download_name=attachment.file_name)

    @token_required
    @role_required('admin')
    def delete(self, attachment_id):
        attachment = db.session.query(Attachment).get(attachment_id)
        if not attachment:
            return {'status': 'error', 'message': '附件不存在'}, 404
        
        upload_folder = _get_upload_folder()
        file_path = os.path.join(upload_folder, attachment.file_name)
        if os.path.exists(file_path):
            os.remove(file_path)
        
        db.session.delete(attachment)
        db.session.commit()
        
        return {'status': 'success', 'message': '删除成功'}
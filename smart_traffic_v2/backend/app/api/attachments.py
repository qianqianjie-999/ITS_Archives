import os
from datetime import datetime
from flask import request, current_app, send_file
from flask_restx import Namespace, Resource, fields
from werkzeug.utils import secure_filename
from ..extensions import db
from ..models.attachment import Attachment

ns = Namespace('attachments', description='附件管理')

attachment_model = ns.model('Attachment', {
    'id': fields.Integer(readonly=True),
    'related_entity_type': fields.String(required=True),
    'related_entity_id': fields.Integer(required=True),
    'file_name': fields.String(required=True),
    'file_size': fields.Integer(),
    'mime_type': fields.String(),
    'uploaded_by': fields.String(),
    'description': fields.String()
})

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in current_app.config['ALLOWED_EXTENSIONS']

@ns.route('/')
class AttachmentUpload(Resource):
    def post(self):
        if 'file' not in request.files:
            return {'status': 'error', 'message': '没有文件'}, 400

        file = request.files['file']
        entity_type = request.form.get('entity_type')
        entity_id = request.form.get('entity_id')
        description = request.form.get('description', '')

        if file.filename == '':
            return {'status': 'error', 'message': '没有选择文件'}, 400

        if not entity_type or not entity_id:
            return {'status': 'error', 'message': '缺少实体信息'}, 400

        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
            unique_filename = f"{timestamp}_{filename}"

            entity_folder = os.path.join(
                current_app.config['UPLOAD_FOLDER'],
                f"{entity_type}_{entity_id}"
            )
            os.makedirs(entity_folder, exist_ok=True)

            file_path = os.path.join(entity_folder, unique_filename)
            file.save(file_path)

            file_size = os.path.getsize(file_path)
            mime_type = file.content_type

            attachment = Attachment(
                related_entity_type=entity_type,
                related_entity_id=int(entity_id),
                file_name=filename,
                file_path=file_path,
                file_size=file_size,
                mime_type=mime_type,
                uploaded_by=request.form.get('uploaded_by', 'anonymous'),
                description=description
            )
            db.session.add(attachment)
            db.session.commit()

            return {'status': 'success', 'id': attachment.id}, 201
        else:
            return {'status': 'error', 'message': '不支持的文件类型'}, 400

@ns.route('/<entity_type>/<int:entity_id>')
class AttachmentList(Resource):
    def get(self, entity_type, entity_id):
        attachments = db.session.query(Attachment).filter_by(
            related_entity_type=entity_type,
            related_entity_id=entity_id
        ).order_by(Attachment.upload_time.desc()).all()
        return [a.to_dict() for a in attachments]

@ns.route('/<int:attachment_id>')
class AttachmentDetail(Resource):
    def delete(self, attachment_id):
        attachment = db.session.query(Attachment).get(attachment_id)
        if not attachment:
            return {'status': 'error', 'message': '附件不存在'}, 404

        if os.path.exists(attachment.file_path):
            os.remove(attachment.file_path)

        db.session.delete(attachment)
        db.session.commit()
        return {'status': 'success'}

@ns.route('/<int:attachment_id>/download')
class AttachmentDownload(Resource):
    def get(self, attachment_id):
        attachment = db.session.query(Attachment).get(attachment_id)
        if not attachment or not os.path.exists(attachment.file_path):
            return {'status': 'error', 'message': '文件不存在'}, 404

        return send_file(
            attachment.file_path,
            as_attachment=True,
            download_name=attachment.file_name
        )
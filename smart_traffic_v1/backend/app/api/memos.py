import os
import uuid
from flask import Blueprint, request, jsonify, current_app, send_from_directory, make_response
from app.models.memo import Memo, MemoAttachment
from app.extensions import db
from datetime import datetime, timezone
from werkzeug.utils import secure_filename
from flask import send_file

memo_bp = Blueprint('memo', __name__, url_prefix='/memos')
memo_bp.url_map.strict_slashes = False

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'pdf', 'doc', 'docx', 'xls', 'xlsx', 'zip', 'rar'}


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@memo_bp.route('/', methods=['GET'])
def get_memos():
    # 筛选条件
    keyword = request.args.get('keyword', '')
    create_user = request.args.get('create_user', '')
    start_date = request.args.get('start_date', '')
    end_date = request.args.get('end_date', '')
    
    # 分页
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    
    query = Memo.query.filter_by(is_del=0)  # 只查询未删除的
    
    if keyword:
        query = query.filter(Memo.title.like(f'%{keyword}%'))
    if create_user:
        query = query.filter_by(create_user=create_user)
    if start_date:
        start_dt = datetime.fromisoformat(start_date)
        query = query.filter(Memo.happen_time >= start_dt)
    if end_date:
        end_dt = datetime.fromisoformat(end_date)
        query = query.filter(Memo.happen_time <= end_dt)
    
    # 按创建时间倒序
    query = query.order_by(Memo.create_time.desc())
    
    # 分页
    pagination = query.paginate(page=page, per_page=per_page, error_out=False)
    memos = pagination.items
    
    return jsonify({
        'items': [memo.to_dict() for memo in memos],
        'total': pagination.total,
        'page': page,
        'per_page': per_page,
        'pages': pagination.pages
    })


@memo_bp.route('/<int:memo_id>', methods=['GET'])
def get_memo(memo_id):
    memo = Memo.query.filter_by(id=memo_id, is_del=0).first_or_404()
    return jsonify(memo.to_dict())


@memo_bp.route('/', methods=['POST'])
def create_memo():
    # 处理表单数据
    title = request.form.get('title')
    content = request.form.get('content', '')
    happen_time_str = request.form.get('happen_time', '')
    create_user = request.form.get('create_user', 'system')
    
    # 解析事件发生时间
    happen_time = None
    if happen_time_str:
        happen_time = datetime.fromisoformat(happen_time_str.replace('Z', '+00:00'))
    
    # 创建备忘录
    memo = Memo(
        title=title,
        content=content,
        happen_time=happen_time,
        create_user=create_user
    )
    db.session.add(memo)
    db.session.flush()  # 获取 memo.id
    
    # 处理附件上传
    files = request.files.getlist('files')
    upload_folder = os.path.join(current_app.config['UPLOAD_FOLDER'], 'memos')
    os.makedirs(upload_folder, exist_ok=True)
    
    for file in files:
        if file and file.filename and allowed_file(file.filename):
            original_filename = file.filename
            ext = original_filename.rsplit('.', 1)[1].lower() if '.' in original_filename else ''
            saved_filename = f"{uuid.uuid4().hex}.{ext}" if ext else uuid.uuid4().hex
            file_path = os.path.join(upload_folder, saved_filename)
            file.save(file_path)
            file_size = os.path.getsize(file_path)
            
            attachment = MemoAttachment(
                memo_id=memo.id,
                file_name=original_filename,
                file_path=saved_filename,
                file_size=file_size,
                file_type=ext
            )
            db.session.add(attachment)
    
    db.session.commit()
    return jsonify(memo.to_dict()), 201


@memo_bp.route('/<int:memo_id>', methods=['PUT'])
def update_memo(memo_id):
    memo = Memo.query.filter_by(id=memo_id, is_del=0).first_or_404()
    
    title = request.form.get('title')
    content = request.form.get('content', '')
    happen_time_str = request.form.get('happen_time', '')
    create_user = request.form.get('create_user')
    
    if title:
        memo.title = title
    if content is not None:
        memo.content = content
    if happen_time_str:
        memo.happen_time = datetime.fromisoformat(happen_time_str.replace('Z', '+00:00'))
    if create_user:
        memo.create_user = create_user
    
    memo.update_time = datetime.now(timezone.utc)
    
    # 处理新增附件
    files = request.files.getlist('files')
    upload_folder = os.path.join(current_app.config['UPLOAD_FOLDER'], 'memos')
    os.makedirs(upload_folder, exist_ok=True)
    
    for file in files:
        if file and file.filename and allowed_file(file.filename):
            original_filename = file.filename
            ext = original_filename.rsplit('.', 1)[1].lower() if '.' in original_filename else ''
            saved_filename = f"{uuid.uuid4().hex}.{ext}" if ext else uuid.uuid4().hex
            file_path = os.path.join(upload_folder, saved_filename)
            file.save(file_path)
            file_size = os.path.getsize(file_path)
            
            attachment = MemoAttachment(
                memo_id=memo.id,
                file_name=original_filename,
                file_path=saved_filename,
                file_size=file_size,
                file_type=ext
            )
            db.session.add(attachment)
    
    db.session.commit()
    return jsonify(memo.to_dict())


@memo_bp.route('/<int:memo_id>', methods=['DELETE'])
def delete_memo(memo_id):
    """软删除备忘录"""
    memo = Memo.query.filter_by(id=memo_id, is_del=0).first_or_404()
    memo.is_del = 1
    memo.update_time = datetime.now(timezone.utc)
    db.session.commit()
    return jsonify({'message': '备忘录已删除'}), 200


@memo_bp.route('/<int:memo_id>/attachments/<int:aid>', methods=['DELETE'])
def delete_attachment(memo_id, aid):
    """删除单个附件"""
    attachment = MemoAttachment.query.filter_by(aid=aid, memo_id=memo_id).first_or_404()
    
    # 删除服务器文件
    upload_folder = os.path.join(current_app.config['UPLOAD_FOLDER'], 'memos')
    file_path = os.path.join(upload_folder, attachment.file_path)
    if os.path.exists(file_path):
        os.remove(file_path)
    
    db.session.delete(attachment)
    db.session.commit()
    return jsonify({'message': '附件已删除'}), 200


@memo_bp.route('/attachments/<path:filename>')
def download_attachment(filename):
    """下载备忘录附件"""
    upload_folder = os.path.join(current_app.config['UPLOAD_FOLDER'], 'memos')
    file_path = os.path.join(upload_folder, filename)
    
    if not os.path.exists(file_path):
        return jsonify({'error': '文件不存在'}), 404
    
    return send_from_directory(upload_folder, filename, as_attachment=True)


@memo_bp.route('/attachments/<path:filename>/preview')
def preview_attachment(filename):
    """预览备忘录附件"""
    upload_folder = os.path.join(current_app.config['UPLOAD_FOLDER'], 'memos')
    file_path = os.path.join(upload_folder, filename)
    
    if not os.path.exists(file_path):
        return jsonify({'error': '文件不存在'}), 404
    
    ext = filename.rsplit('.', 1)[1].lower() if '.' in filename else ''
    
    # 根据文件类型设置 MIME 类型
    mime_types = {
        'pdf': 'application/pdf',
        'png': 'image/png',
        'jpg': 'image/jpeg',
        'jpeg': 'image/jpeg',
        'gif': 'image/gif',
        'doc': 'application/msword',
        'docx': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
        'xls': 'application/vnd.ms-excel',
        'xlsx': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    }
    
    mime_type = mime_types.get(ext, 'application/octet-stream')
    
    response = make_response(send_file(file_path))
    response.headers['Content-Type'] = mime_type
    response.headers['Content-Disposition'] = 'inline'
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    return response
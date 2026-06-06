from flask import Blueprint, request, jsonify
from app.models.memo import Memo
from app.extensions import db
from datetime import datetime

memo_bp = Blueprint('memo', __name__, url_prefix='/api/memos')


@memo_bp.route('/', methods=['GET'])
def get_memos():
    category = request.args.get('category')
    status = request.args.get('status')
    priority = request.args.get('priority')
    
    query = Memo.query
    
    if category:
        query = query.filter_by(category=category)
    if status:
        query = query.filter_by(status=status)
    if priority:
        query = query.filter_by(priority=priority)
    
    memos = query.order_by(Memo.created_at.desc()).all()
    return jsonify([memo.to_dict() for memo in memos])


@memo_bp.route('/<int:memo_id>', methods=['GET'])
def get_memo(memo_id):
    memo = Memo.query.get_or_404(memo_id)
    return jsonify(memo.to_dict())


@memo_bp.route('/', methods=['POST'])
def create_memo():
    data = request.get_json()
    
    memo = Memo(
        title=data.get('title'),
        content=data.get('content'),
        category=data.get('category'),
        priority=data.get('priority', 'medium'),
        status=data.get('status', 'pending'),
        attachments=data.get('attachments', [])
    )
    
    db.session.add(memo)
    db.session.commit()
    
    return jsonify(memo.to_dict()), 201


@memo_bp.route('/<int:memo_id>', methods=['PUT'])
def update_memo(memo_id):
    memo = Memo.query.get_or_404(memo_id)
    data = request.get_json()
    
    if 'title' in data:
        memo.title = data['title']
    if 'content' in data:
        memo.content = data['content']
    if 'category' in data:
        memo.category = data['category']
    if 'priority' in data:
        memo.priority = data['priority']
    if 'status' in data:
        memo.status = data['status']
    if 'attachments' in data:
        memo.attachments = data['attachments']
    
    memo.updated_at = datetime.utcnow()
    db.session.commit()
    
    return jsonify(memo.to_dict())


@memo_bp.route('/<int:memo_id>', methods=['DELETE'])
def delete_memo(memo_id):
    memo = Memo.query.get_or_404(memo_id)
    db.session.delete(memo)
    db.session.commit()
    return jsonify({'message': '备忘录已删除'}), 200
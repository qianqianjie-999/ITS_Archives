from flask import Flask, render_template, request, jsonify, redirect, url_for, session, send_file
from functools import wraps
import pymysql
from db_config import get_db_connection
from datetime import date, datetime
import os
import json
import csv
import io
import hashlib
import secrets

app = Flask(__name__)
app.config['SECRET_KEY'] = secrets.token_hex(32)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024

ALLOWED_EXTENSIONS = {'pdf', 'doc', 'docx', 'xls', 'xlsx', 'jpg', 'jpeg', 'png', 'zip', 'rar'}

def hash_password(password):
    return hashlib.pbkdf2_hmac('sha256', password.encode(), b'salt_v1', 100000).hex()

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            if request.is_json:
                return jsonify({'status': 'error', 'message': '请先登录'}), 401
            return redirect('/login')
        return f(*args, **kwargs)
    return decorated_function

def role_required(*roles):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if 'role' not in session:
                return jsonify({'status': 'error', 'message': '权限不足'}), 403
            if session['role'] not in roles:
                return jsonify({'status': 'error', 'message': '权限不足'}), 403
            return f(*args, **kwargs)
        return decorated_function
    return decorator

def log_operation(operation_type, entity_type, entity_id, old_value, new_value):
    conn = get_db_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("""
                INSERT INTO operation_log (user_id, username, operation_type, entity_type, entity_id, old_value, new_value, ip_address)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                session.get('user_id'),
                session.get('username'),
                operation_type,
                entity_type,
                entity_id,
                json.dumps(old_value) if old_value else None,
                json.dumps(new_value) if new_value else None,
                request.remote_addr
            ))
            conn.commit()
    finally:
        conn.close()

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/login')
def login_page():
    if 'user_id' in session:
        return redirect('/')
    return render_template('login.html')

@app.route('/api/login', methods=['POST'])
def api_login():
    data = request.json
    username = data.get('username')
    password = data.get('password')

    if not username or not password:
        return jsonify({'status': 'error', 'message': '请输入用户名和密码'}), 400

    conn = get_db_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM user WHERE username = %s AND is_active = TRUE", (username,))
            user = cur.fetchone()

            if user and user['password_hash'] == hash_password(password):
                session['user_id'] = user['id']
                session['username'] = user['username']
                session['display_name'] = user['display_name']
                session['role'] = user['role']

                cur.execute("UPDATE user SET last_login = NOW() WHERE id = %s", (user['id'],))
                conn.commit()

                return jsonify({
                    'status': 'success',
                    'user': {
                        'id': user['id'],
                        'username': user['username'],
                        'display_name': user['display_name'],
                        'role': user['role']
                    }
                })
            else:
                return jsonify({'status': 'error', 'message': '用户名或密码错误'}), 401
    finally:
        conn.close()

@app.route('/api/logout', methods=['POST'])
def api_logout():
    session.clear()
    return jsonify({'status': 'success'})

@app.route('/api/current_user')
def api_current_user():
    if 'user_id' not in session:
        return jsonify({'status': 'error', 'message': '未登录'}), 401
    return jsonify({
        'status': 'success',
        'user': {
            'id': session.get('user_id'),
            'username': session.get('username'),
            'display_name': session.get('display_name'),
            'role': session.get('role')
        }
    })

@app.route('/')
@login_required
def index():
    return render_template('index.html')

@app.route('/intersection/<int:intersection_id>')
@login_required
def intersection_detail(intersection_id):
    return render_template('intersection_detail.html', intersection_id=intersection_id)

@app.route('/points')
@login_required
def point_list():
    return render_template('point_list.html')

@app.route('/projects')
@login_required
def project_list():
    return render_template('project_list.html')

@app.route('/logs')
@login_required
@role_required('admin')
def operation_logs():
    return render_template('log_list.html')

@app.route('/api/intersections')
@login_required
def api_intersections():
    conn = get_db_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM intersection_warranty_status ORDER BY id")
            rows = cur.fetchall()
        return jsonify(rows)
    finally:
        conn.close()

@app.route('/api/intersection/<int:intersection_id>')
@login_required
def api_intersection(intersection_id):
    conn = get_db_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM intersection WHERE id = %s", (intersection_id,))
            intersection = cur.fetchone()

            cur.execute("""
                SELECT tl.*, p.name AS project_name, p.warranty_expire_date
                FROM traffic_light tl
                JOIN project p ON tl.project_id = p.id
                WHERE tl.intersection_id = %s
            """, (intersection_id,))
            traffic_lights = cur.fetchall()

            cur.execute("""
                SELECT ep.*, p.name AS project_name, p.warranty_expire_date
                FROM electronic_police ep
                JOIN project p ON ep.project_id = p.id
                WHERE ep.intersection_id = %s
            """, (intersection_id,))
            electronic_polices = cur.fetchall()

            cur.execute("""
                SELECT * FROM attachment
                WHERE related_entity_type = 'intersection' AND related_entity_id = %s
                ORDER BY upload_time DESC
            """, (intersection_id,))
            attachments = cur.fetchall()

        return jsonify({
            'intersection': intersection,
            'traffic_lights': traffic_lights,
            'electronic_polices': electronic_polices,
            'attachments': attachments
        })
    finally:
        conn.close()

@app.route('/api/traffic_light/<int:tl_id>', methods=['PUT'])
@login_required
@role_required('admin', 'editor')
def update_traffic_light(tl_id):
    data = request.json
    conn = get_db_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM traffic_light WHERE id = %s", (tl_id,))
            old_data = cur.fetchone()

            sql = """
                UPDATE traffic_light SET
                signal_type=%s,
                signal_count=%s,
                left_arrow_count=%s,
                straight_arrow_count=%s,
                right_arrow_count=%s,
                full_screen_count=%s,
                non_motor_count=%s,
                pedestrian_count=%s,
                radar_count=%s,
                guide_screen_count=%s,
                power_source=%s
                WHERE id=%s
            """
            cur.execute(sql, (
                data.get('signal_type', ''),
                data.get('signal_count', 0),
                data.get('left_arrow_count', 0),
                data.get('straight_arrow_count', 0),
                data.get('right_arrow_count', 0),
                data.get('full_screen_count', 0),
                data.get('non_motor_count', 0),
                data.get('pedestrian_count', 0),
                data.get('radar_count', 0),
                data.get('guide_screen_count', 0),
                data.get('power_source', ''),
                tl_id
            ))
            conn.commit()

            log_operation('UPDATE', 'traffic_light', tl_id, dict(old_data) if old_data else None, data)

        return jsonify({'status': 'success'})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500
    finally:
        conn.close()

@app.route('/api/electronic_police/<int:ep_id>', methods=['PUT'])
@login_required
@role_required('admin', 'editor')
def update_electronic_police(ep_id):
    data = request.json
    conn = get_db_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM electronic_police WHERE id = %s", (ep_id,))
            old_data = cur.fetchone()

            sql = """
                UPDATE electronic_police SET
                capture_type=%s,
                terminal_server_count=%s,
                forward_capture_count=%s,
                reverse_capture_count=%s,
                led_light_count=%s,
                strobe_light_count=%s,
                ptz_count=%s,
                signal_detector_count=%s,
                network_source=%s
                WHERE id=%s
            """
            cur.execute(sql, (
                data.get('capture_type', ''),
                data.get('terminal_server_count', 0),
                data.get('forward_capture_count', 0),
                data.get('reverse_capture_count', 0),
                data.get('led_light_count', 0),
                data.get('strobe_light_count', 0),
                data.get('ptz_count', 0),
                data.get('signal_detector_count', 0),
                data.get('network_source', ''),
                ep_id
            ))
            conn.commit()

            log_operation('UPDATE', 'electronic_police', ep_id, dict(old_data) if old_data else None, data)

        return jsonify({'status': 'success'})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500
    finally:
        conn.close()

@app.route('/api/intersection/extend_warranty', methods=['POST'])
@login_required
@role_required('admin', 'editor')
def extend_warranty():
    data = request.json
    intersection_id = data['intersection_id']
    project_name = data['project_name']
    warranty_expire_date = data['warranty_expire_date']
    conn = get_db_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("""
                INSERT INTO project (name, acceptance_date, warranty_expire_date)
                VALUES (%s, %s, %s)
            """, (project_name, date.today(), warranty_expire_date))
            project_id = cur.lastrowid

            cur.execute("""
                INSERT INTO warranty_extension (facility_type, facility_id, project_id, extension_date)
                VALUES (%s, %s, %s, %s)
            """, ('intersection', intersection_id, project_id, date.today()))
            conn.commit()

            log_operation('EXTEND_WARRANTY', 'intersection', intersection_id, None, {'project_id': project_id, 'project_name': project_name})

        return jsonify({'status': 'success', 'project_id': project_id})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500
    finally:
        conn.close()

@app.route('/api/points')
@login_required
def api_points():
    conn = get_db_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM point_warranty_status ORDER BY id")
            rows = cur.fetchall()
        return jsonify(rows)
    finally:
        conn.close()

@app.route('/api/projects')
@login_required
def api_projects():
    conn = get_db_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM project ORDER BY id DESC")
            rows = cur.fetchall()
        return jsonify(rows)
    finally:
        conn.close()

@app.route('/api/logs')
@login_required
@role_required('admin')
def api_logs():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    offset = (page - 1) * per_page

    conn = get_db_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT COUNT(*) as total FROM operation_log")
            total = cur.fetchone()['total']

            cur.execute("""
                SELECT * FROM operation_log
                ORDER BY operation_time DESC
                LIMIT %s OFFSET %s
            """, (per_page, offset))
            logs = cur.fetchall()

            for log in logs:
                if log['old_value']:
                    try:
                        log['old_value'] = json.loads(log['old_value'])
                    except:
                        pass
                if log['new_value']:
                    try:
                        log['new_value'] = json.loads(log['new_value'])
                    except:
                        pass

        return jsonify({
            'status': 'success',
            'logs': logs,
            'total': total,
            'page': page,
            'per_page': per_page
        })
    finally:
        conn.close()

@app.route('/api/upload', methods=['POST'])
@login_required
@role_required('admin', 'editor')
def upload_file():
    if 'file' not in request.files:
        return jsonify({'status': 'error', 'message': '没有文件'}), 400

    file = request.files['file']
    entity_type = request.form.get('entity_type')
    entity_id = request.form.get('entity_id')
    description = request.form.get('description', '')

    if file.filename == '':
        return jsonify({'status': 'error', 'message': '没有选择文件'}), 400

    if not entity_type or not entity_id:
        return jsonify({'status': 'error', 'message': '缺少实体信息'}), 400

    if file and allowed_file(file.filename):
        filename = file.filename
        timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
        unique_filename = f"{timestamp}_{filename}"

        entity_folder = os.path.join(app.config['UPLOAD_FOLDER'], f"{entity_type}_{entity_id}")
        os.makedirs(entity_folder, exist_ok=True)

        file_path = os.path.join(entity_folder, unique_filename)
        file.save(file_path)

        file_size = os.path.getsize(file_path)
        mime_type = file.content_type

        conn = get_db_connection()
        try:
            with conn.cursor() as cur:
                cur.execute("""
                    INSERT INTO attachment (related_entity_type, related_entity_id, file_name, file_path, file_size, mime_type, uploaded_by, description)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                """, (entity_type, entity_id, filename, file_path, file_size, mime_type, session.get('username'), description))
                conn.commit()
                attachment_id = cur.lastrowid

            log_operation('UPLOAD', entity_type, entity_id, None, {'file_name': filename, 'attachment_id': attachment_id})

            return jsonify({'status': 'success', 'attachment_id': attachment_id})
        finally:
            conn.close()
    else:
        return jsonify({'status': 'error', 'message': '不支持的文件类型'}), 400

@app.route('/api/attachments/<entity_type>/<int:entity_id>')
@login_required
def api_attachments(entity_type, entity_id):
    conn = get_db_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT * FROM attachment
                WHERE related_entity_type = %s AND related_entity_id = %s
                ORDER BY upload_time DESC
            """, (entity_type, entity_id))
            attachments = cur.fetchall()
        return jsonify({'status': 'success', 'attachments': attachments})
    finally:
        conn.close()

@app.route('/api/attachment/<int:attachment_id>/delete', methods=['DELETE'])
@login_required
@role_required('admin', 'editor')
def delete_attachment(attachment_id):
    conn = get_db_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM attachment WHERE id = %s", (attachment_id,))
            attachment = cur.fetchone()

            if not attachment:
                return jsonify({'status': 'error', 'message': '附件不存在'}), 404

            if os.path.exists(attachment['file_path']):
                os.remove(attachment['file_path'])

            cur.execute("DELETE FROM attachment WHERE id = %s", (attachment_id,))
            conn.commit()

            log_operation('DELETE', 'attachment', attachment_id, {'file_name': attachment['file_name']}, None)

        return jsonify({'status': 'success'})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500
    finally:
        conn.close()

@app.route('/download/<int:attachment_id>')
@login_required
def download_attachment(attachment_id):
    conn = get_db_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM attachment WHERE id = %s", (attachment_id,))
            attachment = cur.fetchone()

            if not attachment or not os.path.exists(attachment['file_path']):
                return jsonify({'status': 'error', 'message': '文件不存在'}), 404

        return send_file(attachment['file_path'], as_attachment=True, download_name=attachment['file_name'])
    finally:
        conn.close()

@app.route('/api/export/intersections')
@login_required
def export_intersections():
    conn = get_db_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM intersection_warranty_status ORDER BY id")
            intersections = cur.fetchall()

        output = io.StringIO()
        writer = csv.writer(output)

        writer.writerow(['ID', '名称', '类型', '最新质保到期', '状态'])

        for item in intersections:
            writer.writerow([
                item['id'],
                item['name'],
                item['type'] or '',
                item['latest_expire_date'] or '',
                item['warranty_status']
            ])

        output.seek(0)
        return send_file(
            io.BytesIO(output.getvalue().encode('utf-8-sig')),
            mimetype='text/csv',
            as_attachment=True,
            download_name=f'intersections_export_{date.today()}.csv'
        )
    finally:
        conn.close()

@app.route('/api/export/points')
@login_required
def export_points():
    conn = get_db_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM point_warranty_status ORDER BY id")
            points = cur.fetchall()

        output = io.StringIO()
        writer = csv.writer(output)

        writer.writerow(['ID', '名称', '区域', '类型', '最新质保到期', '状态'])

        for item in points:
            writer.writerow([
                item['id'],
                item['name'],
                item['area'] or '',
                item['type'] or '',
                item['latest_expire_date'] or '',
                item['warranty_status']
            ])

        output.seek(0)
        return send_file(
            io.BytesIO(output.getvalue().encode('utf-8-sig')),
            mimetype='text/csv',
            as_attachment=True,
            download_name=f'points_export_{date.today()}.csv'
        )
    finally:
        conn.close()

@app.route('/api/export/projects')
@login_required
def export_projects():
    conn = get_db_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM project ORDER BY id DESC")
            projects = cur.fetchall()

        output = io.StringIO()
        writer = csv.writer(output)

        writer.writerow(['ID', '项目名称', '合同金额', '验收日期', '质保期', '质保到期', '建设单位', '施工单位'])

        for item in projects:
            writer.writerow([
                item['id'],
                item['name'],
                item['contract_amount'] or '',
                item['acceptance_date'] or '',
                item['warranty_period'] or '',
                item['warranty_expire_date'],
                item['builder'] or '',
                item['constructor'] or ''
            ])

        output.seek(0)
        return send_file(
            io.BytesIO(output.getvalue().encode('utf-8-sig')),
            mimetype='text/csv',
            as_attachment=True,
            download_name=f'projects_export_{date.today()}.csv'
        )
    finally:
        conn.close()

if __name__ == '__main__':
    os.makedirs('uploads', exist_ok=True)
    app.run(debug=True, host='0.0.0.0', port=5000)

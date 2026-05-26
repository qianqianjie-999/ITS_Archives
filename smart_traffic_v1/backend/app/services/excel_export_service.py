import io
from datetime import date
from openpyxl import Workbook
from openpyxl.styles import Font, Alignment, Border, Side, PatternFill
from openpyxl.utils import get_column_letter
from flask import send_file
from ..extensions import db
from ..models.intersection import Intersection, TrafficLight, ElectronicPolice
from ..models.point import Point, ParkingEnforcement, Checkpoint
from ..models.project import Project
from ..models.backend_device import BackendDevice


class ExcelExportService:
    @staticmethod
    def _get_project_info(project_id):
        project = db.session.query(Project).get(project_id)
        if not project:
            return {
                'name': '',
                'acceptance_date': '',
                'warranty_period': '',
                'warranty_expire_date': '',
                'builder': '',
                'constructor': ''
            }
        return {
            'name': project.name or '',
            'acceptance_date': project.acceptance_date.isoformat() if project.acceptance_date else '',
            'warranty_period': project.warranty_period or '',
            'warranty_expire_date': project.warranty_expire_date.isoformat() if project.warranty_expire_date else '',
            'builder': project.builder or '',
            'constructor': project.constructor or ''
        }

    @staticmethod
    def _get_warranty_status(project_id):
        project = db.session.query(Project).get(project_id)
        if not project or not project.warranty_expire_date:
            return '无项目'
        if project.warranty_expire_date >= date.today():
            return '在保'
        return '过保'

    @staticmethod
    def _get_intersection_type_name(intersection_id):
        intersection = db.session.query(Intersection).get(intersection_id)
        return intersection.type if intersection else ''

    @staticmethod
    def _get_intersection_name(intersection_id):
        intersection = db.session.query(Intersection).get(intersection_id)
        return intersection.name if intersection else ''

    @staticmethod
    def _get_point_info(point_id):
        point = db.session.query(Point).get(point_id)
        if not point:
            return {'name': '', 'area': '', 'type': ''}
        return {
            'name': point.name or '',
            'area': point.area or '',
            'type': point.type or ''
        }

    @staticmethod
    def _get_backend_device_type_name(device_id):
        device = db.session.query(BackendDevice).get(device_id)
        return device.type if device else ''

    @staticmethod
    def export_statistics() -> send_file:
        wb = Workbook()
        wb.remove(wb.active)

        ExcelExportService._create_traffic_light_sheet(wb)
        ExcelExportService._create_electronic_police_sheet(wb)
        ExcelExportService._create_parking_enforcement_sheet(wb)
        ExcelExportService._create_checkpoint_sheet(wb)
        ExcelExportService._create_backend_device_sheet(wb)

        output = io.BytesIO()
        wb.save(output)
        output.seek(0)

        return send_file(
            output,
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            as_attachment=True,
            download_name=f'智能交通设备统计_{date.today()}.xlsx'
        )

    @staticmethod
    def download_template() -> send_file:
        wb = Workbook()
        wb.remove(wb.active)

        ExcelExportService._create_traffic_light_template(wb)
        ExcelExportService._create_electronic_police_template(wb)
        ExcelExportService._create_parking_enforcement_template(wb)
        ExcelExportService._create_checkpoint_template(wb)
        ExcelExportService._create_backend_device_template(wb)

        output = io.BytesIO()
        wb.save(output)
        output.seek(0)

        return send_file(
            output,
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            as_attachment=True,
            download_name='智能交通数据导入模板.xlsx'
        )

    @staticmethod
    def _create_traffic_light_template(wb):
        ws = wb.create_sheet('信号灯')
        headers = [
            '路口名称', '路口类型', '归属项目', '项目验收日期', '项目质保期',
            '项目质保到期时间', '质保状态', '建设单位', '施工单位',
            '信号机类型', '信号机数量', '左转箭头灯数量', '直行箭头数量',
            '右转箭头数量', '满屏灯数量', '非机动灯数量', '人行灯数量',
            '车流量雷达数量', '诱导屏数量', '取电说明'
        ]
        ws.append(headers)
        ws.append(['', '', '', '', '', '', '', '', '', '', 0, 0, 0, 0, 0, 0, 0, 0, 0, ''])
        ExcelExportService._auto_adjust_column_width(ws)

    @staticmethod
    def _create_electronic_police_template(wb):
        ws = wb.create_sheet('电子警察')
        headers = [
            '路口名称', '路口类型', '归属项目', '项目验收日期', '项目质保期',
            '项目质保到期时间', '质保状态', '建设单位', '施工单位',
            '抓拍类型', '终端服务器数量', '正向抓拍数量', '反向抓拍数量',
            'LED灯', '爆闪灯', '监控球机数量', '信号灯检测器数量', '取网说明'
        ]
        ws.append(headers)
        ws.append(['', '', '', '', '', '', '', '', '', '', 0, 0, 0, 0, 0, 0, 0, ''])
        ExcelExportService._auto_adjust_column_width(ws)

    @staticmethod
    def _create_parking_enforcement_template(wb):
        ws = wb.create_sheet('违停球')
        headers = [
            '点位名称', '抓拍区域', '归属项目', '项目验收日期', '项目质保期',
            '项目质保到期时间', '质保状态', '建设单位', '施工单位',
            '抓拍机数量', '违停标牌数量', '监控标牌数量', '取电说明', '取网说明'
        ]
        ws.append(headers)
        ws.append(['', '', '', '', '', '', '', '', '', 0, 0, 0, '', ''])
        ExcelExportService._auto_adjust_column_width(ws)

    @staticmethod
    def _create_checkpoint_template(wb):
        ws = wb.create_sheet('卡口')
        headers = [
            '点位名称', '卡口类型', '归属项目', '项目验收日期', '项目质保期',
            '项目质保到期时间', '质保状态', '建设单位', '施工单位',
            '抓拍机数量', '爆闪灯数量', '测速雷达数量', '标牌数量', '取电说明', '取网说明'
        ]
        ws.append(headers)
        ws.append(['', '', '', '', '', '', '', '', '', 0, 0, 0, 0, '', ''])
        ExcelExportService._auto_adjust_column_width(ws)

    @staticmethod
    def _create_backend_device_template(wb):
        ws = wb.create_sheet('后端设备')
        headers = [
            '设备名称', '设备类型', '归属项目', '项目验收日期', '项目质保期',
            '项目质保到期时间', '质保状态', '建设单位', '施工单位'
        ]
        ws.append(headers)
        ws.append(['', '', '', '', '', '', '', '', ''])
        ExcelExportService._auto_adjust_column_width(ws)

    @staticmethod
    def _create_traffic_light_sheet(wb):
        ws = wb.create_sheet('信号灯')
        headers = [
            '路口名称', '路口类型', '归属项目', '项目验收日期', '项目质保期',
            '项目质保到期时间', '质保状态', '建设单位', '施工单位',
            '信号机类型', '信号机数量', '左转箭头灯数量', '直行箭头数量',
            '右转箭头数量', '满屏灯数量', '非机动灯数量', '人行灯数量',
            '车流量雷达数量', '诱导屏数量', '取电说明'
        ]
        ws.append(headers)

        traffic_lights = db.session.query(TrafficLight).all()
        intersection_types = ['十字路口', '丁字路口', '行人过街', '其他']

        for intersection_type in intersection_types:
            type_lights = [tl for tl in traffic_lights
                          if ExcelExportService._get_intersection_type_name(tl.intersection_id) == intersection_type]

            if not type_lights:
                row = ['', intersection_type, '', '', '', '', '无项目', '', '', '', '', '', '', '', '', '', '', '', '', '']
                ws.append(row)
                continue

            for tl in type_lights:
                project_info = ExcelExportService._get_project_info(tl.project_id)
                intersection_name = ExcelExportService._get_intersection_name(tl.intersection_id)
                warranty_status = ExcelExportService._get_warranty_status(tl.project_id)

                row = [
                    intersection_name,
                    intersection_type,
                    project_info['name'],
                    project_info['acceptance_date'],
                    project_info['warranty_period'],
                    project_info['warranty_expire_date'],
                    warranty_status,
                    project_info['builder'],
                    project_info['constructor'],
                    tl.signal_type or '',
                    tl.signal_count or 0,
                    tl.left_arrow_count or 0,
                    tl.straight_arrow_count or 0,
                    tl.right_arrow_count or 0,
                    tl.full_screen_count or 0,
                    tl.non_motor_count or 0,
                    tl.pedestrian_count or 0,
                    tl.radar_count or 0,
                    tl.guide_screen_count or 0,
                    tl.power_source or ''
                ]
                ws.append(row)

        ExcelExportService._auto_adjust_column_width(ws)

    @staticmethod
    def _create_electronic_police_sheet(wb):
        ws = wb.create_sheet('电子警察')
        headers = [
            '路口名称', '路口类型', '归属项目', '项目验收日期', '项目质保期',
            '项目质保到期时间', '质保状态', '建设单位', '施工单位',
            '抓拍类型', '终端服务器数量', '正向抓拍数量', '反向抓拍数量',
            'LED灯', '爆闪灯', '监控球机数量', '信号灯检测器数量', '取网说明'
        ]
        ws.append(headers)

        ep_list = db.session.query(ElectronicPolice).all()
        intersection_types = ['十字路口', '丁字路口', '行人过街', '其他']

        for intersection_type in intersection_types:
            type_eps = [ep for ep in ep_list
                       if ExcelExportService._get_intersection_type_name(ep.intersection_id) == intersection_type]

            if not type_eps:
                row = ['', intersection_type, '', '', '', '', '无项目', '', '', '', '', '', '', '', '', '', '', '']
                ws.append(row)
                continue

            for ep in type_eps:
                project_info = ExcelExportService._get_project_info(ep.project_id)
                intersection_name = ExcelExportService._get_intersection_name(ep.intersection_id)
                warranty_status = ExcelExportService._get_warranty_status(ep.project_id)

                row = [
                    intersection_name,
                    intersection_type,
                    project_info['name'],
                    project_info['acceptance_date'],
                    project_info['warranty_period'],
                    project_info['warranty_expire_date'],
                    warranty_status,
                    project_info['builder'],
                    project_info['constructor'],
                    ep.capture_type or '',
                    ep.terminal_server_count or 0,
                    ep.forward_capture_count or 0,
                    ep.reverse_capture_count or 0,
                    ep.led_light_count or 0,
                    ep.strobe_light_count or 0,
                    ep.ptz_count or 0,
                    ep.signal_detector_count or 0,
                    ep.network_source or ''
                ]
                ws.append(row)

        ExcelExportService._auto_adjust_column_width(ws)

    @staticmethod
    def _create_parking_enforcement_sheet(wb):
        ws = wb.create_sheet('违停球')
        headers = [
            '点位名称', '抓拍区域', '归属项目', '项目验收日期', '项目质保期',
            '项目质保到期时间', '质保状态', '建设单位', '施工单位',
            '抓拍机数量', '违停标牌数量', '监控标牌数量', '取电说明', '取网说明'
        ]
        ws.append(headers)

        pe_list = db.session.query(ParkingEnforcement).all()
        warranty_statuses = ['在保', '过保']

        for warranty_status in warranty_statuses:
            type_pes = [pe for pe in pe_list
                       if ExcelExportService._get_warranty_status(pe.project_id) == warranty_status]

            if not type_pes:
                row = ['', '', '', '', '', '', warranty_status, '', '', '', '', '', '', '']
                ws.append(row)
                continue

            for pe in type_pes:
                project_info = ExcelExportService._get_project_info(pe.project_id)
                point_info = ExcelExportService._get_point_info(pe.point_id)

                row = [
                    point_info['name'],
                    point_info['area'],
                    project_info['name'],
                    project_info['acceptance_date'],
                    project_info['warranty_period'],
                    project_info['warranty_expire_date'],
                    warranty_status,
                    project_info['builder'],
                    project_info['constructor'],
                    pe.camera_count or 0,
                    pe.parking_sign_count or 0,
                    pe.monitor_sign_count or 0,
                    pe.power_source or '',
                    pe.network_source or ''
                ]
                ws.append(row)

        ExcelExportService._auto_adjust_column_width(ws)

    @staticmethod
    def _create_checkpoint_sheet(wb):
        ws = wb.create_sheet('卡口')
        headers = [
            '点位名称', '卡口类型', '归属项目', '项目验收日期', '项目质保期',
            '项目质保到期时间', '质保状态', '建设单位', '施工单位',
            '抓拍机数量', '爆闪灯数量', '测速雷达数量', '标牌数量', '取电说明', '取网说明'
        ]
        ws.append(headers)

        cp_list = db.session.query(Checkpoint).all()
        checkpoint_types = ['雷达测速卡口', '闯禁区卡口', '大货车不靠右行驶卡口', '单行道卡口']

        for cp_type in checkpoint_types:
            type_cps = [cp for cp in cp_list
                       if ExcelExportService._get_point_info(cp.point_id)['type'] == cp_type]

            if not type_cps:
                row = ['', cp_type, '', '', '', '', '无项目', '', '', '', '', '', '', '', '']
                ws.append(row)
                continue

            for cp in type_cps:
                project_info = ExcelExportService._get_project_info(cp.project_id)
                point_info = ExcelExportService._get_point_info(cp.point_id)
                warranty_status = ExcelExportService._get_warranty_status(cp.project_id)

                row = [
                    point_info['name'],
                    cp_type,
                    project_info['name'],
                    project_info['acceptance_date'],
                    project_info['warranty_period'],
                    project_info['warranty_expire_date'],
                    warranty_status,
                    project_info['builder'],
                    project_info['constructor'],
                    cp.camera_count or 0,
                    cp.strobe_light_count or 0,
                    cp.radar_count or 0,
                    cp.sign_count or 0,
                    cp.power_source or '',
                    cp.network_source or ''
                ]
                ws.append(row)

        ExcelExportService._auto_adjust_column_width(ws)

    @staticmethod
    def _create_backend_device_sheet(wb):
        ws = wb.create_sheet('后端设备')
        headers = [
            '设备名称', '设备类型', '归属项目', '项目验收日期', '项目质保期',
            '项目质保到期时间', '质保状态', '建设单位', '施工单位'
        ]
        ws.append(headers)

        devices = db.session.query(BackendDevice).all()
        device_types = ['网络交换设备', '网络安全设备', '服务器', '存储设备', '显示设备', '操作设备', '消防设备', '用电设备', '空调设备']

        for device_type in device_types:
            type_devices = [d for d in devices
                          if ExcelExportService._get_backend_device_type_name(d.id) == device_type]

            if not type_devices:
                row = ['', device_type, '', '', '', '', '无项目', '', '']
                ws.append(row)
                continue

            for d in type_devices:
                project_info = ExcelExportService._get_project_info(d.project_id)
                warranty_status = ExcelExportService._get_warranty_status(d.project_id)

                row = [
                    d.name or '',
                    device_type,
                    project_info['name'],
                    project_info['acceptance_date'],
                    project_info['warranty_period'],
                    project_info['warranty_expire_date'],
                    warranty_status,
                    project_info['builder'],
                    project_info['constructor']
                ]
                ws.append(row)

        ExcelExportService._auto_adjust_column_width(ws)

    @staticmethod
    def _auto_adjust_column_width(ws):
        for column in ws.columns:
            max_length = 0
            column_letter = get_column_letter(column[0].column)
            for cell in column:
                try:
                    if len(str(cell.value)) > max_length:
                        max_length = len(str(cell.value))
                except:
                    pass
            adjusted_width = min(max_length + 2, 50)
            ws.column_dimensions[column_letter].width = adjusted_width

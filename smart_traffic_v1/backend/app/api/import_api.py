from flask import request
from flask_restx import Namespace, Resource
from werkzeug.datastructures import FileStorage
from ..services.excel_import_service import ExcelImportService

ns = Namespace('import', description='数据导入')

upload_parser = ns.parser()
upload_parser.add_argument('type', location='form', required=True, help='导入类型: intersection, point, project, device')
upload_parser.add_argument('file', location='files', type=FileStorage, required=True, help='Excel文件')

@ns.route('/excel')
class ExcelImport(Resource):
    @ns.expect(upload_parser)
    def post(self):
        args = upload_parser.parse_args()
        import_type = args['type']
        file = args['file']

        try:
            result = ExcelImportService.import_excel(file, import_type)
            return {
                'status': 'success',
                'message': f'成功导入 {result["count"]} 条数据',
                'count': result['count'],
                'errors': result.get('errors', [])
            }
        except Exception as e:
            return {
                'status': 'error',
                'message': str(e)
            }, 400

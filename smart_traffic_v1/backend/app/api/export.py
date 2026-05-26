from flask_restx import Namespace, Resource
from ..services.excel_export_service import ExcelExportService

ns = Namespace('export', description='数据导出')

@ns.route('/statistics')
class StatisticsExport(Resource):
    def get(self):
        return ExcelExportService.export_statistics()

@ns.route('/template')
class TemplateExport(Resource):
    def get(self):
        return ExcelExportService.download_template()

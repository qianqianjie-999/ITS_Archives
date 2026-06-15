from flask_restx import Namespace, Resource
from ..services.excel_export_service import ExcelExportService
from ..utils.decorators import token_required

ns = Namespace('export', description='数据导出')

@ns.route('/statistics')
class StatisticsExport(Resource):
    @token_required
    def get(self):
        return ExcelExportService.export_statistics()

@ns.route('/template')
class TemplateExport(Resource):
    @token_required
    def get(self):
        return ExcelExportService.download_template()

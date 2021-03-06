# -*- encoding: utf-8 -*-
##############################################################################
#                                                                            #
#   --- Deby Wahyu Kurdian ---                                               #
#                                                                            #
##############################################################################

from odoo.addons.jasper_reports import JasperDataParser
from odoo.addons.jasper_reports import jasper_report

class jasper_report_flight_time_fw_rw(JasperDataParser.JasperDataParser):
    def __init__(self, cr, uid, ids, data, context):
        super(jasper_report_flight_time_fw_rw, self).__init__(cr, uid, ids, data, context)

    def generate_data_source(self, cr, uid, ids, data, context):
        return 'parameters'

    def generate_parameters(self, cr, uid, ids, data, context):
        return {
                'date_from'     : str(data['form']['date_from']),
                'date_to'       : str(data['form']['date_to']),
                'type_id'       : data['form']['type_id'][0],
                }
    
    def generate_properties(self, cr, uid, ids, data, context):
        return {}

    def generate_output(self,cr, uid, ids, data, context):
        return data['form']['report_type']
    
    def generate_records(self, cr, uid, ids, data, context):
        return {}

jasper_report.ReportJasper('report.report_flight_time_fw_rw', 'wizard.report.flight.time.fw.rw', parser=jasper_report_flight_time_fw_rw,)

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

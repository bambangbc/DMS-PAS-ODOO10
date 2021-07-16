# -*- encoding: utf-8 -*-
##############################################################################
#                                                                            #
#   --- Deby Wahyu Kurdian ---                                               #
#                                                                            #
##############################################################################

from odoo.addons.jasper_reports import JasperDataParser
from odoo.addons.jasper_reports import jasper_report

class jasper_report_flight_time_fw_rw_02(JasperDataParser.JasperDataParser):
    def __init__(self, cr, uid, ids, data, context):
        super(jasper_report_flight_time_fw_rw_02, self).__init__(cr, uid, ids, data, context)

    def generate_data_source(self, cr, uid, ids, data, context):
        return 'parameters'

    def generate_parameters(self, cr, uid, ids, data, context):
        return {
                'date_cutoff'       : str(data['form']['date_cutoff']),
                'date_from'         : str(data['form']['date_from']),
                'date_to'           : str(data['form']['date_to']),
                'category_id'       : str(data['form']['category_id']),
                'type_ids'          : str(data['form']['type_ids']),
                'crew_ids'          : str(data['form']['crew_ids']),
                'fl_acquisition_ids': str(data['form']['fl_acquisition_ids']),
                }
    
    def generate_properties(self, cr, uid, ids, data, context):
        return {}

    def generate_output(self,cr, uid, ids, data, context):
        return data['form']['report_type']
    
    def generate_records(self, cr, uid, ids, data, context):
        return {}

jasper_report.ReportJasper('report.tunggakan', 'wizard.report.flight.time.fw.rw.02', parser=jasper_report_flight_time_fw_rw_02,)
jasper_report.ReportJasper('report.bln_berjalan', 'wizard.report.flight.time.fw.rw.02', parser=jasper_report_flight_time_fw_rw_02,)
jasper_report.ReportJasper('report.master', 'wizard.report.flight.time.fw.rw.02', parser=jasper_report_flight_time_fw_rw_02,)

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

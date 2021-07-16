# -*- coding: utf-8 -*-
# © 2017 Ibrohim Binladin | ibradiiin@gmail.com | +62-838-7190-9782
import base64
#import tempfile
from odoo import api, fields, models, _
# import odoo.addons.jasper_reports as jr
from datetime import datetime, timedelta
import odoo.addons.jasper_reports.jasper_report as jr
#import odoo.addons.decimal_precision as dp
from odoo.exceptions import UserError
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT

MONTH = [(0,''), (1,'JAN'), (2,'FEB'),(3,'MAR'),(4,'APR'), (5,'MAY'), (6,'JUN'),
        (7,'JUL'), (8,'AUG'), (9,'SEP'),(10,'OCT'), (11,'NOV'), (12,'DEC')]
MONTHS = [(0,''), (1,'JANUARY'), (2,'FEBRUARY'),(3,'MARCH'),(4,'APRIL'), (5,'MAY'), (6,'JUNE'),
        (7,'JULY'), (8,'AUGUST'), (9,'SEPTEMBER'),(10,'OCTOBER'), (11,'NOVEMBER'), (12,'DECEMBER')]

class ExportCSVSalesOrder(models.TransientModel):
    _name = "sale.export.csv"

    name = fields.Char(string='File Name')
    data_file = fields.Binary(string='File')

    @api.multi
    def eksport_csv_sale_order(self):
        context = dict(self._context or {})
        orders = self.env['sale.order'].browse(self._context.get('active_ids', []))
        ir_model_data = self.env['ir.model.data']
        active_ids = context.get('active_ids')
        result = 'id;SO Number;Sales Area;Disc Channel;Division;Sales Grp;Sales Off;Sales Type;Sold To;Ship To;Bill To;Payer;Salesperson;Flight Order;Reg;Flight Date;Material;Description;Qty;UoM'
        number = []
        for x in orders:
            number.append(x.name)
            for y in x.order_line:
                result += '\n' + ';'.join(
                    [str(x.id), str(x.name), str('x_sales_area'), str('x_disc_channel'), str('x_divisi'), str(x.team_id.name),
                     str('x_sales_off'), str('x_sales_type'), str(x.partner_id.name), str(x.partner_invoice_id.name),
                     str(x.partner_shipping_id.name), str(x.partner_id.name), str(x.user_id.name), str('x_flight_order'),
                     str(x.fl_acquisition_id.name), str(x.date_departure), str(y.product_id.default_code), str(y.name),
                     str(y.product_uom_qty), str(y.product_uom.name)])

        out = base64.encodestring(result)
        self.write({'data_file': out, 'name': 'Eksport_'+ '_'.join(number) +'.csv'})

        view_rec = ir_model_data.get_object_reference('ib_pelita_report', 'view_export_csv_order_wizard')
        view_id = view_rec[1] or False

        return {
            'view_type': 'form',
            'view_id': [view_id],
            'view_mode': 'form',
            'res_id': active_ids and active_ids[0], #val.id,
            'res_model': 'sale.export.csv',
            'type': 'ir.actions.act_window',
            'target': 'new',
        }



class OperationalReports(models.TransientModel):
    _name = "operational.reports"
    _description = "Pelita Report"

    report_type = fields.Selection([
        ('data_jam_fl_fw', 'Data Jam Terbang Test Flight F/W'),
        ('data_jam_fl_rw', 'Data Jam Terbang Test Flight R/W'),
        ('data_jam_vvip_fw', 'Data Jam Terbang VVIP Flight F/W'),
        ('fl_prod_fw_aircraft', 'Flying Hours Production F/W Aircraft'),
        ('fl_prod_fw_crew', 'Flying Hours Production F/W Crew'),
        ('fl_prod_rw_aircraft', 'Flying Hours Production R/W Aircraft'),
        ('fl_prod_rw_crew', 'Flying Hours Production R/W Crew'),
        ('record_fl_hours_fw_tipi', 'Records Flying Hours Crew F/W TIPI'),
        ('record_fl_hours_rw_tipi', 'Records Flying Hours Crew R/W TIPI')],
        string='Report Type', required=True) #default='pilot_monthly'  #('pilot_monthly', 'Pilot Monthly'),
    crew_id = fields.Many2one('hr.employee', string='Crew')
    date_from = fields.Date(string='Start Date', required=True)
    date_to = fields.Date(string='End Date', required=True)
    pdf_ok = fields.Boolean(string='Print to PDF', default=False)

    @api.multi
    def print_report(self, data):
        context = dict(self._context or {})
        for wizard in self:
            if 'form' not in data:
                data['form'] = {}

            start_dt = datetime.strptime(wizard['date_from'], "%Y-%m-%d") #tgl_paling_tua/lama
            end_dt = datetime.strptime(wizard['date_to'], "%Y-%m-%d") #tgl_paling_muda/baru
            numYear = float((end_dt - start_dt).days) / 364.0
            numMonth = int((numYear - int(numYear)) * 364 / 30)
            if wizard['report_type'] in ('data_jam_vvip_fw','fl_prod_fw_aircraft','fl_prod_rw_aircraft','fl_prod_rw_crew','record_fl_hours_fw_tipi') and numMonth > 3:
                raise UserError(_('Date period can not be more than 3 months.'))
            elif wizard['report_type']=='fl_prod_fw_crew' and numMonth > 4:
                raise UserError(_('Date period can not be more than 4 months.'))
            elif wizard['report_type']=='record_fl_hours_rw_tipi' and numMonth > 2:
                raise UserError(_('Date period can not be more than 2 months.'))

            report_name, objek = '', ''
            if wizard['report_type'] == "pilot_monthly":
                objek = 'crew.schedule'
            elif wizard['report_type'] != "pilot_monthly":
                objek = 'flight.maintenance.log'
            else:
                objek = 'hr.employee'

            if wizard['pdf_ok'] == True: #output: PDF
                report_name = str(wizard['report_type']) + "_pdf"
            else:#output: XLS
                report_name = str(wizard['report_type']) + "_xls"

            data['form']['month_label'] = ''
            if wizard['report_type'] in ('fl_prod_fw_aircraft', 'fl_prod_rw_aircraft'):
                data['form']['month_label'] = str(MONTHS[int(end_dt.month+1)][1]) + " " + str(end_dt.year)

            data['form']['crew_id'] = 0
            if wizard['crew_id']:
                data['form']['crew_id'] = int(wizard['crew_id'][0])
            data['form']['subdir_report'] = "/opt/odoo/custom/extra_pas/ib_pelita_report/report/"
            data['form']['start_date'] = wizard['date_from']
            data['form']['end_date'] = wizard['date_to']
            data['form']['month1'] = data['form']['month1_start'] = data['form']['month1_end'] = ''
            data['form']['month2'] = data['form']['month2_start'] = data['form']['month2_end'] = ''
            data['form']['month3'] = data['form']['month3_start'] = data['form']['month3_end'] = ''
            data['form']['month4'] = data['form']['month4_start'] = data['form']['month4_end'] = ''
            start_month1 = start_month2 = start_month3 = start_month4 = month1 = month2 = month3 = month4 = ''
            if wizard['report_type'] not in ('data_jam_fl_fw','data_jam_fl_rw'):
                start_month1 = datetime(end_dt.year, end_dt.month, 1)
                data['form']['month1_end'] = end_dt.strftime('%Y-%m-%d')
                data['form']['month1_start'] = start_month1.strftime('%Y-%m-%d')
                data['form']['month1'] = str(MONTH[int(start_month1.month)][1]) + " '" + str(start_month1.year)[2:]
                end_month2 = start_month1 + timedelta(days=-1)
                data['form']['month2_end'] = end_month2.strftime('%Y-%m-%d')
                start_month2 = datetime(end_month2.year, end_month2.month, 1)
                data['form']['month2_start'] = start_month2.strftime('%Y-%m-%d')
                data['form']['month2'] = str(MONTH[int(start_month2.month)][1]) + " '" + str(start_month2.year)[2:]
            if wizard['report_type'] in ('data_jam_vvip_fw','fl_prod_fw_aircraft','fl_prod_rw_aircraft','fl_prod_rw_crew','record_fl_hours_fw_tipi'):
                end_month3 = start_month2 + timedelta(days=-1)
                data['form']['month3_end'] = end_month3.strftime('%Y-%m-%d')
                start_month3 = datetime(end_month3.year, end_month3.month, 1)
                data['form']['month3_start'] = start_month3.strftime('%Y-%m-%d')
                data['form']['month3'] = str(MONTH[int(start_month3.month)][1]) + " '" + str(start_month3.year)[2:]
            if wizard['report_type'] == 'fl_prod_fw_crew':
                end_month4 = start_month3 + timedelta(days=-1)
                data['form']['month4_end'] = end_month4.strftime('%Y-%m-%d')
                start_month4 = datetime(end_month4.year, end_month4.month, 1)
                data['form']['month4_start'] = start_month4.strftime('%Y-%m-%d')
                data['form']['month4'] = str(MONTH[int(start_month4.month)][1]) + " '" + str(start_month4.year)[2:]
            data['model'] = objek
            # data['ids'] = self.env[objek].search(dom)
            return {
                'type': 'ir.actions.report.xml',
                'report_name': report_name,
                'datas': data,
            }




def operational_reports(cr, uid, ids, data, context):
    return {
        'parameters': {
            'start_date': data['form']['start_date'],
            'end_date': data['form']['end_date'],
            'month1': data['form']['month1'],
            'month1_start': data['form']['month1_start'],
            'month1_end': data['form']['month1_end'],
            'month2': data['form']['month2'],
            'month2_start': data['form']['month2_start'],
            'month2_end': data['form']['month2_end'],
            'month3': data['form']['month3'],
            'month3_start': data['form']['month3_start'],
            'month3_end': data['form']['month3_end'],
            'month4': data['form']['month4'],
            'month4_start': data['form']['month4_start'],
            'month4_end': data['form']['month4_end'],
            # 'crew_id': data['form']['crew_id'],
            'month_label': data['form']['month_label'],
            'SUBREPORT_DIR': data['form']['subdir_report'],
        },
    }
jr.ReportJasper(
    'report.data_jam_fl_fw_xls',
    'flight.maintenance.log',
    parser=operational_reports
    )
jr.ReportJasper(
    'report.data_jam_fl_rw_xls',
    'flight.maintenance.log',
    parser=operational_reports
    )
jr.ReportJasper(
    'report.data_jam_vvip_fw_xls',
    'flight.maintenance.log',
    parser=operational_reports
    )
jr.ReportJasper(
    'report.fl_prod_fw_aircraft_xls',
    'flight.maintenance.log',
    parser=operational_reports
    )
jr.ReportJasper(
    'report.fl_prod_fw_crew_xls',
    'flight.maintenance.log',
    parser=operational_reports
    )
jr.ReportJasper(
    'report.fl_prod_rw_aircraft_xls',
    'flight.maintenance.log',
    parser=operational_reports
    )
jr.ReportJasper(
    'report.fl_prod_rw_crew_xls',
    'flight.maintenance.log',
    parser=operational_reports
    )
jr.ReportJasper(
    'report.record_fl_hours_fw_tipi_xls',
    'flight.maintenance.log',
    parser=operational_reports
    )
jr.ReportJasper(
    'report.record_fl_hours_rw_tipi_xls',
    'flight.maintenance.log',
    parser=operational_reports
    )



##############################################################################
#                                                                            #
#   --- Deby Wahyu Kurdian ---                                               #
#                                                                            #
##############################################################################
from odoo import api, fields, models, _

class wizard_report_flight_time_fw_rw_02(models.TransientModel):
    _name           = "wizard.report.flight.time.fw.rw.02"
    _description    = "Flying Hours Production-02"

    month_of_year       = fields.Many2one('month.of.year', string='Month of Year', readonly=False, required=True)
    date_from           = fields.Date(required=True)
    date_to             = fields.Date(required=True)
    date_cutoff         = fields.Date(required=True)
    category_id         = fields.Selection([('fixedwing', 'Fixed Wing'), ('rotary', 'Rotary')])
    type_ids            = fields.Many2many(comodel_name="aircraft.aircraft", string="Aircraft Type")
    crew_ids            = fields.Many2many(comodel_name="hr.employee", string="Crew Name")
    fl_acquisition_ids  = fields.Many2many(comodel_name="aircraft.acquisition", string="Registration No")
    report_type         = fields.Selection([('html', 'HTML'), ('csv', 'CSV'), ('xls', 'XLS'), ('rtf', 'RTF'),
                                    ('odt', 'ODT'), ('ods', 'ODS'), ('txt', 'Text'), ('pdf', 'PDF'),
                                    ('jrprint', 'Jasper Print')], string='Type'
                                   , default='xls')

    name_of_sheet      = fields.Selection([('sheet1', 'Bln Berjalan'), ('sheet2', 'Tunggakan'), ('sheet3', 'Master')], string="Name of Sheet", default="sheet1")

    @api.onchange('month_of_year')
    def onchange_month(self):
        if self.month_of_year:
            self.date_from      = self.month_of_year.date_from
            self.date_to        = self.month_of_year.date_to
            self.date_cutoff    = self.month_of_year.date_cutoff

    @api.multi
    def create_report(self):
        data = self.read()[-1]
        if self.name_of_sheet == "sheet1":
            return {
                'type'          : 'ir.actions.report.xml',
                'report_name'   : 'bln_berjalan',
                'datas'         : {
                    'model'         : 'wizard.report.flight.time.fw.rw.02',
                    'id'            : self._context.get('active_ids') and self._context.get('active_ids')[0] or self.id,
                    'ids'           : self._context.get('active_ids') and self._context.get('active_ids') or [],
                    'report_type'   : data['report_type'],
                    'form'          : data
                },
                'nodestroy': False
            }
        elif self.name_of_sheet == "sheet2":
            return {
                'type'          : 'ir.actions.report.xml',
                'report_name'   : 'tunggakan',
                'datas'         : {
                    'model'         : 'wizard.report.flight.time.fw.rw.02',
                    'id'            : self._context.get('active_ids') and self._context.get('active_ids')[0] or self.id,
                    'ids'           : self._context.get('active_ids') and self._context.get('active_ids') or [],
                    'report_type'   : data['report_type'],
                    'form'          : data
                },
                'nodestroy': False
            }
        else:
            return {
                'type'          : 'ir.actions.report.xml',
                'report_name'   : 'master',
                'datas'         : {
                    'model'         : 'wizard.report.flight.time.fw.rw.02',
                    'id'            : self._context.get('active_ids') and self._context.get('active_ids')[0] or self.id,
                    'ids'           : self._context.get('active_ids') and self._context.get('active_ids') or [],
                    'report_type'   : data['report_type'],
                    'form'          : data
                },
                'nodestroy': False
            }

wizard_report_flight_time_fw_rw_02()
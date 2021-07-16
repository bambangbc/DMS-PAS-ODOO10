##############################################################################
#                                                                            #
#   --- Deby Wahyu Kurdian ---                                               #
#                                                                            #
##############################################################################
from odoo import api, fields, models, _

class wizard_report_flight_time_fw_rw(models.TransientModel):
    _name           = "wizard.report.flight.time.fw.rw"
    _description    = "Flying Hours Production"

    date_from       = fields.Date(required=True, default=lambda self: self._context.get("From", fields.Date.context_today(self)))
    date_to         = fields.Date(required=True, default=lambda self: self._context.get("To", fields.Date.context_today(self)))
    type_id         = fields.Many2one(comodel_name="aircraft.aircraft", string="Aircraft Type", required=1)
    report_type     = fields.Selection([('html', 'HTML'), ('csv', 'CSV'), ('xls', 'XLS'), ('rtf', 'RTF'),
                                    ('odt', 'ODT'), ('ods', 'ODS'), ('txt', 'Text'), ('pdf', 'PDF'),
                                    ('jrprint', 'Jasper Print')], string='Type'
                                   , default='xls')

    @api.multi
    def create_report(self):
        data = self.read()[-1]
        return {
            'type'          : 'ir.actions.report.xml',
            'report_name'   : 'report_flight_time_fw_rw',
            'datas'         : {
                'model'         : 'wizard.report.flight.time.fw.rw',
                'id'            : self._context.get('active_ids') and self._context.get('active_ids')[0] or self.id,
                'ids'           : self._context.get('active_ids') and self._context.get('active_ids') or [],
                'report_type'   : data['report_type'],
                'form'          : data
            },
            'nodestroy': False
        }
wizard_report_flight_time_fw_rw()
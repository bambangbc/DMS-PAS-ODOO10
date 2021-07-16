from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

class ir_sequence(models.Model):
    _inherit = 'ir.sequence'

    auto_reset = fields.Boolean('Auto Reset Every Month')

    @api.multi
    def autoreset_sequence(self):
    	obj = self.env['ir.sequence']
    	src = obj.search([('auto_reset','=',True)])
    	for autoreset in src :
    		autoreset.write({'number_next_actual':1})


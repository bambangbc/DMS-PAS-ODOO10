from odoo import models, fields, api
from odoo.exceptions import ValidationError

class resPartner(models.Model):
	_inherit = 'res.partner'

	job_id = fields.Many2one('hr.job','Job Position', default=lambda self: self.env['hr.job'].search([('name','=','Mekanik')]))
	department_id = fields.Many2one('hr.department','Department')

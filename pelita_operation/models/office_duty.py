# -*- coding: utf-8 -*-
from odoo import fields, models,api, _
# import pytz
# from odoo.addons.mail.models.mail_template import format_tz
# from datetime import date, datetime, timedelta
# from odoo.exceptions import UserError, AccessError
import logging
_logger = logging.getLogger(__name__)

class OfficeDuty(models.Model):
	_name = 'office.duty'
	name = fields.Many2one('hr.employee','Name')
	base_operation_id = fields.Many2one('base.operation','Base Operation')
	date_from = fields.Datetime('Date From')
	date_to = fields.Datetime('Date To')
	#date_duty = fields.Date('Date')
	#time_from = fields.Float('Time From')
	#time_to = fields.Float('Time To')
	state = fields.Selection([('draft', 'Draft'),('validated', 'Validated'),('cancel', 'Cancelled'),
		('setcrew','Crew Set')],
            string='Status', readonly=True, copy=False, index=True, track_visibility='onchange', default='draft')

	@api.multi
	def action_set_to_draft(self):
		return self.write({'state': 'draft'})

	@api.multi
	def action_validate(self):
		cs = self.env['crew.schedule']
		for od in self:
			cs.create({'name': 'Office Duty',
							   'employee_id' : od.name.id,
							   'date_from' : od.date_from,
							   'date_to' : od.date_to,
							   })    
			self.write({'state': 'validated'})
		return True

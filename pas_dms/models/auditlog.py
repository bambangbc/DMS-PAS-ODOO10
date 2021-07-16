from odoo import models, api, fields
from odoo.exceptions import UserError, AccessError, ValidationError

import time
from datetime import datetime, timedelta
from dateutil import relativedelta

from odoo.addons.muk_dms.models import dms_base

class AuditLog(models.Model):
	_name = "audit.log"
	_description = "mengtrack semua transaksi user pada file dms"

	name = fields.Char('Nama File')
	date = fields.Datetime('Tanggal')
	method = fields.Char('Method')
	user_id = fields.Many2one('res.users','User Pengguna')
	name_old = fields.Char('Name Lama')
	name_new = fields.Char('Name Baru')
	exp_old = fields.Char('Expiration Lama')
	exp_new = fields.Char('Expiration Baru')
	pic_old = fields.Char('PIC Lama')
	pic_new = fields.Char('PIC Baru')
	ews_old = fields.Char('EWS Lama')
	ews_new = fields.Char('EWS Baru')
	content_old = fields.Binary('Content Lama')
	content_new = fields.Binary('Content Baru')
	directory_old = fields.Char('Directory Lama')
	directory_new = fields.Char('Directory Baru')
	#line_ids = fields.One2many('audit.log.line','audit_id','Detail')

#class LineAuditLog(models.Model):
#	_name = "audit.log.line"
#	_description = "detail dari audit log"
#
#	name = fields.Char('Description')
#	content_old = fields.Char('Konten Lama')
#	content_new = fields.Char('Konten Baru')
#	audit_id = fields.Many2one('audit.log', 'Audit')
 

class File(dms_base.DMSModel):
	_inherit = 'muk_dms.file'

	@api.model
	def create(self, vals):
		name = vals['name']
		createlog =  self.env['audit.log'].sudo().create({'name':name,
													'date':str(datetime.today()),
													'method':'Create',
													'user_id':self.env.user.id})
		return super(File, self).create(vals)

	@api.multi
	def unlink(self):
		unlinklog = self.env['audit.log'].sudo().create({'name':self.name,
												'date':str(datetime.today()),
												'method':'Delete',
												'user_id':self.env.user.id})
		return super(File, self).unlink()

	def _compute_content(self):
		for record in self:
			record.content = record._get_content()
			### auditlog ###
			readlog = self.env['audit.log'].sudo().create({'name':record.name,
													'date' : str(datetime.today()),
													'method': 'Read',
													'user_id':record.env.user.id})
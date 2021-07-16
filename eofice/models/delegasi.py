from odoo import models, fields, api, _
from odoo.exceptions import UserError, AccessError, ValidationError
from datetime import datetime, timedelta

#class ResUsers(models.Model):
#	_inherit = "res.users"
#
#	delegasi = fields.Boolean('Delegasi')

class Delegasi(models.Model):
	_name = "delegasi"
	_description = "Pendelegasian tugas"

	name = fields.Char('Keterangan',required=True)
	date_from = fields.Date('Dari',required=True)
	date_to = fields.Date('Sampai',required=True)
	user_id = fields.Many2one('res.users', string='Pemberi Delegasi',default= lambda self: self.env.user, readonly=True)
	user_id2 = fields.Many2one('res.users', string='Penerima Delegasi',required=True, domain="[('id','!=',user_id)]")
	user_id3 = fields.Many2one('res.users', string='User Sementara')
	state = fields.Selection([('draft', 'Draft'),('inprogres','In Progres'),('done','Done')], 'Status', indext=True,readonly=True, default='draft')
	surat_masuk = fields.Boolean('Surat Masuk',default=True)
	disposisi = fields.Boolean('Disposisi',default=True)
	nota = fields.Boolean('Nota',default=True)
	memorandum = fields.Boolean('Memorandum',default=True)
	surat_keluar = fields.Boolean('Surat Keluar',default=True)
	tanda_terima = fields.Boolean('Tanda Terima Dokumen',default=True)

	@api.multi
	def unlink(self):
		for unl in self :
			if unl.state == 'done' or unl.state == 'inprogres' :
				raise UserError(_('Anda Tidak Bisa Menghapus Karna Status Sudah Done.'))
			return super(Delegasi, self).unlink()

	@api.model
	def create(self,vals):
		if vals['date_from'] > vals['date_to'] :
			raise UserError(_('Tanggal mulai Tidak boleh lebih besar dari tanggal berakhir.'))
		return super(Delegasi, self).create(vals)

	@api.multi
	def automatic_close(self):
		date_now = datetime.today()
		del_obj = self.env['delegasi']
		del_src = del_obj.search([('date_to','<',str(date_now)[:10]),('state','=','inprogres')])
		del_src_in = del_obj.search([('date_from','=',str(date_now)[:10]),('state','=','inprogres')])
		for act in del_src_in :
			sequence = self.env['ir.sequence'].sudo().next_by_code('delegasi')
			act.user_id.sudo().write({'password':'PJS'+str(sequence)})
			act.sudo().write({'state':'done'})

			#### Search Employee ####
			emp_obj = self.env['hr.employee']
			emp_src = emp_obj.sudo().search([('user_id','=',self.user_id.id)])

			#### search email company ####
			com_obj = self.env['res.company']
			com_src = com_obj.sudo().search([],limit=1)
			for comp in com_src :
				for send in emp_src :
					body_html = '<p>Kepada '+str(self.user_id.name)+',</p> \n'+'<p> Anda melakukan pendelegasian kepada '+str(self.user_id2.name)+' Selama peiode '+str(self.date_from)+' sampai '+str(self.date_to)+' Dengan Passwor Baru PJS'+str(sequence)
					mail        = self.env['mail.mail']
					notif_mail  = mail.sudo().create({'subject'    : 'Pendelegasian',
															'email_from'    : comp.email,
															'email_to'      : send.user_id.partner_id.email,
															#'email_cc'     :
															'auto_delete'   : True,
															'type'          : 'notification',
															#'recipient_ids' : [(6, 0, [gr.partner_id.id])],
															'notification'  : True,
															'body_html'     : body_html,
															})
			send = self.env['mail.mail'].sudo().process_email_queue()

			#### search email company ####
			com_obj = self.env['res.company']
			com_src = com_obj.sudo().search([],limit=1)
			for comp in com_src :
				for send in emp_src :
					body_html = '<p>Kepada '+str(self.user_id2.name)+',</p> \n'+'<p> Anda mendapatkan pendelegasian dari '+str(self.user_id.name)+' Selama peiode '+str(self.date_from)+' sampai '+str(self.date_to)+' Dengan Passwor Baru PJS'+str(sequence)
					mail        = self.env['mail.mail']
					notif_mail  = mail.sudo().create({'subject'    : 'Pendelegasian',
															'email_from'    : comp.email,
															'email_to'      : send.user_id.partner_id.email,
															#'email_cc'     :
															'auto_delete'   : True,
															'type'          : 'notification',
															#'recipient_ids' : [(6, 0, [gr.partner_id.id])],
															'notification'  : True,
															'body_html'     : body_html,
															})
			send = self.env['mail.mail'].sudo().process_email_queue()
			act.sudo().write({'state':'inprogres'})

		for act in del_src :
			sequence = self.env['ir.sequence'].sudo().next_by_code('delegasi')
			act.user_id.sudo().write({'password':'PJS'+str(sequence)})
			act.sudo().write({'state':'done'})

			#### Search Employee ####
			emp_obj = self.env['hr.employee']
			emp_src = emp_obj.sudo().search([('user_id','=',self.user_id.id)])

			#### search email company ####
			com_obj = self.env['res.company']
			com_src = com_obj.sudo().search([],limit=1)
			for comp in com_src :
				for send in emp_src :
					body_html = '<p>Kepada '+str(self.user_id.name)+',</p> \n'+'<p> Pendelegasian anda kepada '+str(self.user_id2.name)+' Selama peiode '+str(self.date_from)+' sampai '+str(self.date_to)+'sudah selesai, dan password baru anda PJS'+str(sequence)
					mail        = self.env['mail.mail']
					notif_mail  = mail.sudo().create({'subject'    : 'Pendelegasian',
															'email_from'    : comp.email,
															'email_to'      : send.user_id.partner_id.email,
															#'email_cc'     :
															'auto_delete'   : True,
															'type'          : 'notification',
															#'recipient_ids' : [(6, 0, [gr.partner_id.id])],
															'notification'  : True,
															'body_html'     : body_html,
															})
			send = self.env['mail.mail'].sudo().process_email_queue()

	@api.multi
	def validate(self):
		if self.date_from <= str(datetime.now())[:10] :
			delegasi = self.user_id
			sequence = self.env['ir.sequence'].sudo().next_by_code('delegasi')
			delegasi.sudo().write({'password':'PJS'+str(sequence)})

			#### Search Employee ####
			emp_obj = self.env['hr.employee']
			emp_src = emp_obj.sudo().search([('user_id','=',self.user_id.id)])

			#### search email company ####
			com_obj = self.env['res.company']
			com_src = com_obj.sudo().search([],limit=1)
			for comp in com_src :
				for send in emp_src :
					body_html = '<p>Kepada '+str(self.user_id.name)+',</p> \n'+'<p> Anda melakukan pendelegasian kepada '+str(self.user_id2.name)+' Selama peiode '+str(self.date_from)+' sampai '+str(self.date_to)+' Dengan Passwor Baru PJS'+str(sequence)
					mail        = self.env['mail.mail']
					notif_mail  = mail.sudo().create({'subject'    : 'Pendelegasian',
															'email_from'    : comp.email,
															'email_to'      : send.user_id.partner_id.email,
															#'email_cc'     :
															'auto_delete'   : True,
															'type'          : 'notification',
															#'recipient_ids' : [(6, 0, [gr.partner_id.id])],
															'notification'  : True,
															'body_html'     : body_html,
															})
								   # _logger.info("created due date invoice alert to %s" % (gr.partner_id.email) )

			#### Search Employee ####
			emp_obj = self.env['hr.employee']
			emp_src = emp_obj.sudo().search([('user_id','=',self.user_id2.id)])

			#### search email company ####
			com_obj = self.env['res.company']
			com_src = com_obj.sudo().search([],limit=1)
			for comp in com_src :
				for send in emp_src :
					body_html = '<p>Kepada '+str(self.user_id2.name)+',</p> \n'+'<p> Anda mendapatkan pendelegasian dari '+str(self.user_id.name)+' Selama peiode '+str(self.date_from)+' sampai '+str(self.date_to)+' Dengan Passwor Baru PJS'+str(sequence)
					mail        = self.env['mail.mail']
					notif_mail  = mail.sudo().create({'subject'    : 'Pendelegasian',
															'email_from'    : comp.email,
															'email_to'      : send.user_id.partner_id.email,
															#'email_cc'     :
															'auto_delete'   : True,
															'type'          : 'notification',
															#'recipient_ids' : [(6, 0, [gr.partner_id.id])],
															'notification'  : True,
															'body_html'     : body_html,
															})
			send = self.env['mail.mail'].sudo().process_email_queue()
		self.state = "inprogres"

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
from datetime import datetime, timedelta


class surat_keluar(models.Model):
	_name = "surat.keluar"
	_description = "Surat keluar"
	_order = "date desc"

	name = fields.Char('No',required=True, index=True, copy=False, default='New')
	kepada = fields.Many2one('res.partner','Ditujukan untuk', required=True)
	pengirim = fields.Many2one('hr.department','Pengirim')
	tembusan = fields.Many2many('hr.job',"kepadsk_category_rel","kepadask_id","jobsk_id", string='Tembusan')
	alamat = fields.Char('Alamat')
	alamat2 = fields.Char('Alamat2')
	kota = fields.Char('kota')
	provinsi = fields.Many2one('res.country.state','provinsi')
	negara = fields.Many2one('res.country','Negara')
	up = fields.Many2many('res.partner',"res_partner_rel","up_id","partner_id", string='Attn.')
	#tembusan = fields.Char('Copies')
	perihal = fields.Char('Perihal/Subject')
	date = fields.Datetime('Tanggal', default=fields.Datetime.now, required=True)
	content = fields.Html('Isi Konten')
	attach = fields.Binary('Attachment')
	state = fields.Selection(
		[('draft','Draft'),('checker1','Checker 1'),('checker2','Checker 2'),('checker3','Checker 3'),('checker4','Checker 4'),('checker5','Checker 5'),('signer','signer'),('done','Done')],'Status', indext=True, readonly=True, default='draft')
	template = fields.Many2one("sk.stage","Template Stage", required=True, domain="[('department_id','=',pengirim)]")
	user_id = fields.Many2one('res.users', string='Responsible',default= lambda self: self.env.user, readonly=True)
	backdate = fields.Date('Back Date')
	nomor_manual = fields.Char('Nomor Surat Manual')
	uid = fields.Boolean('user_id', compute="_get_responsible")
	uid1 = fields.Boolean('Checker 1', compute="_get_checker1")
	uid2 = fields.Boolean('Checker 2', compute="_get_checker2")
	uid3 = fields.Boolean('Checker 3', compute="_get_checker3")
	uid4 = fields.Boolean('Checker 4', compute="_get_checker4")
	uid5 = fields.Boolean('Checker 5', compute="_get_checker5")
	uid6 = fields.Boolean('Signer', compute="_get_signer")
	lampiran = fields.Char('Lampiran')
	###### surat masuk #######
	no_ref = fields.Many2one('surat.masuk','Nomor Surat Masuk')
	perihal_sm = fields.Char('Perihal/Subjek')
	#pengirim = fields.Char('Pengirim')
	date2 = fields.Date('Tanggal')
	note = fields.Html('Catatan')

	@api.depends()
	def _get_responsible(self):
		for rec in self :
			if rec.user_id.id == self.env.user.id and rec.state == 'draft':
				rec.uid = True
				rec.write({'uid':True})
			else :
				rec.uid = False
				rec.write({'uid':False})

	@api.depends()
	def _get_checker1(self):
		for rec in self :
			if rec.template.user_id1.id == self.env.user.id or rec.template.user_idd1.id == self.env.user.id :
				rec.uid1 = True
				rec.write({'uid1':True})

	@api.depends()
	def _get_checker2(self):
		for rec in self :
			if rec.template.user_id2.id == self.env.user.id or rec.template.user_idd2.id == self.env.user.id:
				rec.uid2 = True
				rec.write({'uid2':True})

	@api.depends()
	def _get_checker3(self):
		for rec in self :
			if rec.template.user_id3.id == self.env.user.id or rec.template.user_idd3.id == self.env.user.id:
				rec.uid3 = True
				rec.write({'uid3':True})

	@api.depends()
	def _get_checker4(self):
		for rec in self :
			if rec.template.user_id4.id == self.env.user.id or rec.template.user_idd4.id == self.env.user.id:
				rec.uid4 = True
				rec.write({'uid1':True})

	@api.depends()
	def _get_checker5(self):
		for rec in self :
			if rec.template.user_id5.id == self.env.user.id or rec.template.user_idd5.id == self.env.user.id:
				rec.uid5 = True
				rec.write({'uid1':True})

	@api.depends()
	def _get_signer(self):
		for rec in self :
			if rec.template.user_id6.id == self.env.user.id or rec.template.user_idd6.id == self.env.user.id:
				rec.uid6 = True
				rec.write({'uid6':True})

	@api.onchange('user_id')
	def _user_department(self):
		emp_obj = self.env['hr.employee']
		emp_src = emp_obj.search([('user_id','=', self.user_id.id)])
		for department in emp_src :
			self.pengirim = department.department_id

	@api.onchange('no_ref')
	def _onchange_masuk(self):
		noref = self.no_ref
		self.perihal_sm = noref.subject
		#self.partner = noref.partner.name
		self.date2 = noref.date3

	@api.multi
	def confirm(self):

		####### Search Employee #######
		emp_obj = self.env['hr.employee']
		emp_src = emp_obj.search([('user_id','=',self.template.user_id1.id)])

		#### search email company ####
		com_obj = self.env['res.company']
		com_src = com_obj.search([],limit=1)
		for comp in com_src :
			for send in emp_src :
				body_html = '<p>Kepada '+str(send.job_id.name)+',</p> \n'+'<p> anda sebagai Checker 1 untuk surat keluar dengan Nomor '+str(self.name)+' Dengan Perihal '+str(self.perihal)+' Mohon Untuk Segera Di tindak lanjuti'
				mail        = self.env['mail.mail']
				notif_mail  = mail.create({'subject'    : 'Surat Keluar '+str(self.perihal),
														'email_from'    : comp.email,
														'email_to'      : send.work_email,
														#'email_cc'     :
														'auto_delete'   : True,
														'type'          : 'notification',
														#'recipient_ids' : [(6, 0, [gr.partner_id.id])],
														'notification'  : True,
														'body_html'     : body_html,
														})
							   # _logger.info("created due date invoice alert to %s" % (gr.partner_id.email) )
			send = self.env['mail.mail'].process_email_queue()
		self.state = "checker1"

	@api.multi
	def checker1(self):
		if self.template.checker2 == True :
			####### Search Employee #######
			emp_obj = self.env['hr.employee']
			emp_src = emp_obj.search([('user_id','=',self.template.user_id2.id)])

			#### search email company ####
			com_obj = self.env['res.company']
			com_src = com_obj.search([],limit=1)
			for comp in com_src :
				for send in emp_src :
					body_html = '<p>Kepada '+str(send.job_id.name)+',</p> \n'+'<p> anda sebagai Checker 2 untuk surat keluar dengan Nomor '+str(self.name)+' Dengan Perihal '+str(self.perihal)+' Mohon Untuk Segera Di tindak lanjuti'
					mail        = self.env['mail.mail']
					notif_mail  = mail.create({'subject'    : 'Surat Keluar '+str(self.perihal),
															'email_from'    : comp.email,
															'email_to'      : send.work_email,
															#'email_cc'     :
															'auto_delete'   : True,
															'type'          : 'notification',
															#'recipient_ids' : [(6, 0, [gr.partner_id.id])],
															'notification'  : True,
															'body_html'     : body_html,
															})
								   # _logger.info("created due date invoice alert to %s" % (gr.partner_id.email) )
				send = self.env['mail.mail'].process_email_queue()
			self.state = "checker2"
		else :
			####### Search Employee #######
			emp_obj = self.env['hr.employee']
			emp_src = emp_obj.search([('user_id','=',self.template.user_id6.id)])

			#### search email company ####
			com_obj = self.env['res.company']
			com_src = com_obj.search([],limit=1)
			for comp in com_src :
				for send in emp_src :
					body_html = '<p>Kepada '+str(send.job_id.name)+',</p> \n'+'<p> anda sebagai Signer untuk surat keluar dengan Nomor '+str(self.name)+' Dengan Perihal '+str(self.perihal)+' Mohon Untuk Segera Di tindak lanjuti'
					mail        = self.env['mail.mail']
					notif_mail  = mail.create({'subject'    : 'Surat Keluar '+str(self.perihal),
															'email_from'    : comp.email,
															'email_to'      : send.work_email,
															#'email_cc'     :
															'auto_delete'   : True,
															'type'          : 'notification',
															#'recipient_ids' : [(6, 0, [gr.partner_id.id])],
															'notification'  : True,
															'body_html'     : body_html,
															})
								   # _logger.info("created due date invoice alert to %s" % (gr.partner_id.email) )
				send = self.env['mail.mail'].process_email_queue()
			self.state = "signer"

	@api.multi
	def checker2(self):
		if self.template.checker3 == True :
			####### Search Employee #######
			emp_obj = self.env['hr.employee']
			emp_src = emp_obj.search([('user_id','=',self.template.user_id3.id)])

			#### search email company ####
			com_obj = self.env['res.company']
			com_src = com_obj.search([],limit=1)
			for comp in com_src :
				for send in emp_src :
					body_html = '<p>Kepada '+str(send.job_id.name)+',</p> \n'+'<p> anda sebagai Checker 3 untuk surat keluar dengan Nomor '+str(self.name)+' Dengan Perihal '+str(self.perihal)+' Mohon Untuk Segera Di tindak lanjuti'
					mail        = self.env['mail.mail']
					notif_mail  = mail.create({'subject'    : 'Surat Keluar '+str(self.perihal),
															'email_from'    : comp.email,
															'email_to'      : send.work_email,
															#'email_cc'     :
															'auto_delete'   : True,
															'type'          : 'notification',
															#'recipient_ids' : [(6, 0, [gr.partner_id.id])],
															'notification'  : True,
															'body_html'     : body_html,
															})
								   # _logger.info("created due date invoice alert to %s" % (gr.partner_id.email) )
				send = self.env['mail.mail'].process_email_queue()
			self.state = "checker3"
		else :
			####### Search Employee #######
			emp_obj = self.env['hr.employee']
			emp_src = emp_obj.search([('user_id','=',self.template.user_id6.id)])

			#### search email company ####
			com_obj = self.env['res.company']
			com_src = com_obj.search([],limit=1)
			for comp in com_src :
				for send in emp_src :
					body_html = '<p>Kepada '+str(send.job_id.name)+',</p> \n'+'<p> anda sebagai Signer untuk surat keluar dengan Nomor '+str(self.name)+' Dengan Perihal '+str(self.perihal)+' Mohon Untuk Segera Di tindak lanjuti'
					mail        = self.env['mail.mail']
					notif_mail  = mail.create({'subject'    : 'Surat Keluar '+str(self.perihal),
															'email_from'    : comp.email,
															'email_to'      : send.work_email,
															#'email_cc'     :
															'auto_delete'   : True,
															'type'          : 'notification',
															#'recipient_ids' : [(6, 0, [gr.partner_id.id])],
															'notification'  : True,
															'body_html'     : body_html,
															})
								   # _logger.info("created due date invoice alert to %s" % (gr.partner_id.email) )
				send = self.env['mail.mail'].process_email_queue()
			self.state = "signer"

	@api.multi
	def checker3(self):
		if self.template.checker4 == True :
			####### Search Employee #######
			emp_obj = self.env['hr.employee']
			emp_src = emp_obj.search([('user_id','=',self.template.user_id4.id)])

			#### search email company ####
			com_obj = self.env['res.company']
			com_src = com_obj.search([],limit=1)
			for comp in com_src :
				for send in emp_src :
					body_html = '<p>Kepada '+str(send.job_id.name)+',</p> \n'+'<p> anda sebagai Checker 4 untuk surat keluar dengan Nomor '+str(self.name)+' Dengan Perihal '+str(self.perihal)+' Mohon Untuk Segera Di tindak lanjuti'
					mail        = self.env['mail.mail']
					notif_mail  = mail.create({'subject'    : 'Surat Keluar '+str(self.perihal),
															'email_from'    : comp.email,
															'email_to'      : send.work_email,
															#'email_cc'     :
															'auto_delete'   : True,
															'type'          : 'notification',
															#'recipient_ids' : [(6, 0, [gr.partner_id.id])],
															'notification'  : True,
															'body_html'     : body_html,
															})
								   # _logger.info("created due date invoice alert to %s" % (gr.partner_id.email) )
				send = self.env['mail.mail'].process_email_queue()
			self.state = "checker4"
		else :
			####### Search Employee #######
			emp_obj = self.env['hr.employee']
			emp_src = emp_obj.search([('user_id','=',self.template.user_id6.id)])

			#### search email company ####
			com_obj = self.env['res.company']
			com_src = com_obj.search([],limit=1)
			for comp in com_src :
				for send in emp_src :
					body_html = '<p>Kepada '+str(send.job_id.name)+',</p> \n'+'<p> anda sebagai Signer untuk surat keluar dengan Nomor '+str(self.name)+' Dengan Perihal '+str(self.perihal)+' Mohon Untuk Segera Di tindak lanjuti'
					mail        = self.env['mail.mail']
					notif_mail  = mail.create({'subject'    : 'Surat Keluar '+str(self.perihal),
															'email_from'    : comp.email,
															'email_to'      : send.work_email,
															#'email_cc'     :
															'auto_delete'   : True,
															'type'          : 'notification',
															#'recipient_ids' : [(6, 0, [gr.partner_id.id])],
															'notification'  : True,
															'body_html'     : body_html,
															})
								   # _logger.info("created due date invoice alert to %s" % (gr.partner_id.email) )
				send = self.env['mail.mail'].process_email_queue()
			self.state = "signer"

	@api.multi
	def checker4(self):
		if self.template.checker5 == True :
			####### Search Employee #######
			emp_obj = self.env['hr.employee']
			emp_src = emp_obj.search([('user_id','=',self.template.user_id5.id)])

			#### search email company ####
			com_obj = self.env['res.company']
			com_src = com_obj.search([],limit=1)
			for comp in com_src :
				for send in emp_src :
					body_html = '<p>Kepada '+str(send.job_id.name)+',</p> \n'+'<p> anda sebagai Checker 5 untuk surat keluar dengan Nomor '+str(self.name)+' Dengan Perihal '+str(self.perihal)+' Mohon Untuk Segera Di tindak lanjuti'
					mail        = self.env['mail.mail']
					notif_mail  = mail.create({'subject'    : 'Surat Keluar '+str(self.perihal),
															'email_from'    : comp.email,
															'email_to'      : send.work_email,
															#'email_cc'     :
															'auto_delete'   : True,
															'type'          : 'notification',
															#'recipient_ids' : [(6, 0, [gr.partner_id.id])],
															'notification'  : True,
															'body_html'     : body_html,
															})
								   # _logger.info("created due date invoice alert to %s" % (gr.partner_id.email) )
				send = self.env['mail.mail'].process_email_queue()
			self.state = "checker5"
		else :
			####### Search Employee #######
			emp_obj = self.env['hr.employee']
			emp_src = emp_obj.search([('user_id','=',self.template.user_id6.id)])

			#### search email company ####
			com_obj = self.env['res.company']
			com_src = com_obj.search([],limit=1)
			for comp in com_src :
				for send in emp_src :
					body_html = '<p>Kepada '+str(send.job_id.name)+',</p> \n'+'<p> anda sebagai Signer untuk surat keluar dengan Nomor '+str(self.name)+' Dengan Perihal '+str(self.perihal)+' Mohon Untuk Segera Di tindak lanjuti'
					mail        = self.env['mail.mail']
					notif_mail  = mail.create({'subject'    : 'Surat Keluar '+str(self.perihal),
															'email_from'    : comp.email,
															'email_to'      : send.work_email,
															#'email_cc'     :
															'auto_delete'   : True,
															'type'          : 'notification',
															#'recipient_ids' : [(6, 0, [gr.partner_id.id])],
															'notification'  : True,
															'body_html'     : body_html,
															})
								   # _logger.info("created due date invoice alert to %s" % (gr.partner_id.email) )
				send = self.env['mail.mail'].process_email_queue()
			self.state = "signer"

	@api.multi
	def checker5(self):

		####### Search Employee #######
		emp_obj = self.env['hr.employee']
		emp_src = emp_obj.search([('user_id','=',self.template.user_id6.id)])

		#### search email company ####
		com_obj = self.env['res.company']
		com_src = com_obj.search([],limit=1)
		for comp in com_src :
			for send in emp_src :
				body_html = '<p>Kepada '+str(send.job_id.name)+',</p> \n'+'<p> anda sebagai Signer untuk surat keluar dengan Nomor '+str(self.name)+' Dengan Perihal '+str(self.perihal)+' Mohon Untuk Segera Di tindak lanjuti'
				mail        = self.env['mail.mail']
				notif_mail  = mail.create({'subject'    : 'Surat Keluar '+str(self.perihal),
														'email_from'    : comp.email,
														'email_to'      : send.work_email,
														#'email_cc'     :
														'auto_delete'   : True,
														'type'          : 'notification',
														#'recipient_ids' : [(6, 0, [gr.partner_id.id])],
														'notification'  : True,
														'body_html'     : body_html,
														})
							   # _logger.info("created due date invoice alert to %s" % (gr.partner_id.email) )
			send = self.env['mail.mail'].process_email_queue()
		self.state = "signer"

	@api.multi
	def signer(self):
		if self.name == 'New' :
			#### mengambil sequence ####
			sequence = self.env['ir.sequence'].sudo().next_by_code('surat.keluar') or '/'

			#### mengambil tahun ####
			years = str(datetime.now().year)

			#### mengambil code department ####
			code = self.template.user_id6.job_id.code_sk
			if code == False :
				code = "-"

			##### membuat penomoran #####
			self.name = sequence+"/"+code+"/PAS/"+years
		self.state = "done"

	#@api.onchange('kepada')
	#def _onchange_suratkeluar(self):
	#	partner = self.kepada
	#	self.alamat = partner.street
	#	self.alamat2 = partner.street2
	#	self.kota = partner.city
	#	self.provinsi = partner.state_id
	#	self.negara = partner.country_id
	#	res_obj = self.env['res.partner']
	#	res_src = res_obj.search([('parent_id','=',self.kepada.id)])
	#	if self.kepada.id != False :
	#		self.up = res_src

class ResPartner(models.Model):
	_inherit = "res.partner"

	surat_keluar = fields.Many2many('surat.keluar',"res_partner_rel","partner_id","up_id", string='Attn.')

class JobPosition(models.Model):
	_inherit = "hr.job"

	sk_ids = fields.Many2many("surat.keluar","kepadask_category_rel","jobsk_id","kepadask_id", string="memorandum")
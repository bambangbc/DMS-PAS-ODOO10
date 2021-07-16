from odoo import models, fields, api, _
from odoo.exceptions import UserError, AccessError, ValidationError
from datetime import datetime, timedelta


class surat_memorandum(models.Model):
	_name = "surat.memorandum"
	_description = "Surat Memorandum"
	_inherit = ['ir.needaction_mixin']
	_order='date desc'

	name = fields.Char('No',required=True, index=True, copy=False, default='New')
	kepada = fields.Many2many('hr.job',"kepadamemo_category_rel","kepada_id","job_id", string="Ditujukan Untuk")
	kepada_dep = fields.Many2many('hr.department','kepadamemodep_category_rel','kepada_dep','department_id', string="Ditujukan untuk department")
	kepada_usr = fields.Many2many('res.users','kepadamemousr_category_rel','kepada_usr','user_id', string="Ditujukan untuk user")
	user_ids3 = fields.Many2many('res.users',"user4_category_rel","memo_id4","user_id4",'Ditujukan kepada Delegasi')
	tembusan = fields.Many2many('hr.job',"kepadamemo2_category_rel","kepada_id2","job_id2", string='Tembusan')
	tembusan_dep = fields.Many2many('hr.department',"kepadamemodep2_category_rel","kepada_dep2","department_id2", string='Tembusan Department')
	tembusan_usr = fields.Many2many('res.users',"kepadamemousr2_category_rel","kepada_usr2","user_id2", string='Tembusan user')
	perihal = fields.Char('Subject')
	date = fields.Datetime('Date',default=fields.Datetime.now,required=True)
	content = fields.Html('Contents')
	note = fields.Html('Note')
	jenis_surat = fields.Selection(
		[('surat_masuk', 'Surat Masuk'), ('surat_keluar', 'Surat Keluar'),
		 ('nota', 'Nota'),('memorandum','Memodarndum')], 'Jenis Surat', default='memorandum')
	attach = fields.Binary('Attachment')
	source = fields.Char('source Document')
	dispo_ids = fields.One2many('disposisi.masuk', 'no_memo', string='disposisi')
	dispo_id = fields.Many2one('disposisi.masuk', compute='_compute_dispo_id', string='Current Disposisi', help='Latest dispo of the employee')
	memo_count = fields.Integer(compute='_compute_memo_count', string="Surat Masuk")
	state = fields.Selection(
		[('draft','Draft'),('checker1','Checker 1'),('checker2','Checker 2'),('checker3','Checker 3'),('checker4','Checker 4'),('checker5','Checker 5'),('signer','signer'),('inprogres','In Progress'),('done','Done')],'Status', indext=True, readonly=True, default='draft')
	user_id = fields.Many2one('res.users', string='Pembuat Memorandum',default= lambda self: self.env.user)
	user_id1 = fields.Many2one('hr.job','Pembuat Memorandum', compute='_user_memo', store=True)
	pengirim = fields.Many2one('hr.department','Pengirim')
	active_user = fields.Char('active_user',compute='_get_active_user')
	active_validate = fields.Char('active_validate',compute='_get_active_validate')
	validate_done = fields.Many2many('hr.job',"kepadamemo3_category_rel","kepada_id3","job_id3", string="Memo Done By")
	validate_show = fields.Many2many('hr.job',"kepadamemo4_category_rel","kepada_id4","job_id4", string="validate show By")
	report_true = fields.Char('report_true',compute="_get_report_true")
	report_tem_true = fields.Char('report_tem_true',compute="_get_report_tem_true")
	button_dispo = fields.Boolean('Disposisi', compute="_get_btnds")
	button_memo = fields.Boolean('Nota', compute="_get_btnmem")
	uid1 = fields.Boolean('Checker 1', compute="_get_checker1")
	uid2 = fields.Boolean('Checker 2', compute="_get_checker2")
	uid3 = fields.Boolean('Checker 3', compute="_get_checker3")
	uid4 = fields.Boolean('Checker 4', compute="_get_checker4")
	uid5 = fields.Boolean('Checker 5', compute="_get_checker5")
	uid6 = fields.Boolean('Signer', compute="_get_signer")
	uid_u1 = fields.Many2one('res.users','uid1')
	uid_u2 = fields.Many2one('res.users','uid2')
	uid_u3 = fields.Many2one('res.users','uid3')
	uid_u4 = fields.Many2one('res.users','uid4')
	uid_u5 = fields.Many2one('res.users','uid5')
	uid_u6 = fields.Many2one('res.users','uid6')
	rahsia = fields.Selection([('rahasia','Rahasia'),('biasa','Biasa')],'Sifat Dokumen',default="biasa")
	template = fields.Many2one("memo.stage","Template Stage", required=True, domain="[('department_id','=',pengirim)]")
	signer = fields.Many2one("res.users","Signer")
	folowup = fields.Boolean('Folow Up', default=True)
	auto_done = fields.Char('auto done',compute='_auto_done')
	mixin = fields.Char('mix',compute="_mix")
	mixin2 = fields.Char('mix')
	lampiran = fields.Char('Lampiran')
	#### tanda terima dokuemn ####
	no_tanda_terima = fields.Many2one('tanda.terima', string="Nomor Tanda Terima")

	@api.onchange('template')
	def _template(self):
		self.uid_u1 = self.template.user_id1
		self.uid_u2 = self.template.user_id2
		self.uid_u3 = self.template.user_id3
		self.uid_u4 = self.template.user_id4
		self.uid_u5 = self.template.user_id5
		self.uid_u6 = self.template.user_id6

	@api.model
	def _needaction_domain_get(self, domain=None):
		for rec in self :
			import pdb;pdb.set_trace()
			if rec.uid1 == True and rec.state == 'checker1' and rec.state != 'draft' and rec.state != 'done':
				rec.mixin = 'true'
				rec.mixin2 = 'true'
				rec.write({'mixin':'true','mixin2':'true'})
			elif rec.uid2 == True and rec.state == 'checker2' and rec.state != 'draft' and rec.state != 'done':
				rec.mixin = 'true'
				rec.mixin2 = 'true'
				rec.write({'mixin':'true','mixin2':'true'})
			elif rec.uid3 == True and rec.state == 'checker3' and rec.state != 'draft' and rec.state != 'done':
				rec.mixin = 'true'
				rec.mixin2 = 'true'
				rec.write({'mixin':'true','mixin2':'true'})
			elif rec.uid4 == True and rec.state == 'checker4' and rec.state != 'draft' and rec.state != 'done':
				rec.mixin = 'true'
				rec.mixin2 = 'true'
				rec.write({'mixin':'true','mixin2':'true'})
			elif rec.uid5 == True and rec.state == 'checker5' and rec.state != 'draft' and rec.state != 'done':
				rec.mixin = 'true'
				rec.mixin2 = 'true'
				rec.write({'mixin':'true','mixin2':'true'})
			elif rec.uid6 == True and rec.state == 'signer' and rec.state != 'draft' and rec.state != 'done':
				rec.mixin = 'true'
				rec.mixin2 = 'true'
				rec.write({'mixin':'true','mixin2':'true'})
			else :
				rec.mixin = 'false'
				rec.mixin2 = 'false'
				rec.write({'mixin':'false','mixin2':'false'})
		return ['|',('mixin2','=','true'),('kepada','in',self.env.user.job_id.id)]

	@api.depends()
	def _mix(self):
		for rec in self :
			if rec.uid1 == True and rec.state == 'checker1' and rec.state != 'draft' and rec.state != 'done':
				rec.mixin = 'true'
				rec.mixin2 = 'true'
				rec.write({'mixin':'true','mixin2':'true'})
			elif rec.uid2 == True and rec.state == 'checker2' and rec.state != 'draft' and rec.state != 'done':
				rec.mixin = 'true'
				rec.mixin2 = 'true'
				rec.write({'mixin':'true','mixin2':'true'})
			elif rec.uid3 == True and rec.state == 'checker3' and rec.state != 'draft' and rec.state != 'done':
				rec.mixin = 'true'
				rec.mixin2 = 'true'
				rec.write({'mixin':'true','mixin2':'true'})
			elif rec.uid4 == True and rec.state == 'checker4' and rec.state != 'draft' and rec.state != 'done':
				rec.mixin = 'true'
				rec.mixin2 = 'true'
				rec.write({'mixin':'true','mixin2':'true'})
			elif rec.uid5 == True and rec.state == 'checker5' and rec.state != 'draft' and rec.state != 'done':
				rec.mixin = 'true'
				rec.mixin2 = 'true'
				rec.write({'mixin':'true','mixin2':'true'})
			elif rec.uid6 == True and rec.state == 'signer' and rec.state != 'draft' and rec.state != 'done':
				rec.mixin = 'true'
				rec.mixin2 = 'true'
				rec.write({'mixin':'true','mixin2':'true'})
			else :
				rec.mixin = 'false'
				rec.mixin2 = 'false'
				rec.write({'mixin':'false','mixin2':'false'})

	@api.depends()
	def _auto_done(self):
		for rec in self :
			xxx = False
			for nm in rec.kepada :
				if nm.id == self.env.user.job_id.id :
					xxx = True
			if rec.folowup == False and rec.state == 'inprogres' and xxx == True:
				rec.write({'state':'done','auto_done':'baca'})

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

	def _get_btnds(self):
		grp_obj = self.env['res.groups'].search([('name','=','Disposisi Create')])
		for btnds in grp_obj :
			for btn in btnds.users :
				if btn.id == self.env.user.id or self.env.user.id == 1 :
					if self.state == 'inprogres' or self.state == 'done' :
						self.button_dispo = True
						self.update({'button_dispo':True})

	def _get_btnmem(self):
		grp_obj = self.env['res.groups'].search([('name','=','Memorandum Create')])
		for btnnt in grp_obj :
			for btn in btnnt.users :
				if btn.id == self.env.user.id or self.env.user.id == 1 :
					if self.state == 'inprogres' or self.state == 'done' :
						self.button_memo = True
						self.update({'button_memo':True})

	@api.onchange('kepada')
	def _kepada(self):
		dep_ids = []
		emp_obj = self.env['hr.employee']
		for kep in self.kepada :
			emp_src = emp_obj.sudo().search([('job_id', '=', kep.id)])
			for emp in emp_src :
				if emp.user_id.id :
					dep_ids.append(emp.user_id.id)
		self.kepada_usr = dep_ids

	@api.onchange('tembusan')
	def _tembusan(self):
		dep_ids = []
		emp_obj = self.env['hr.employee']
		for tem in self.tembusan :
			emp_src = emp_obj.sudo().search([('job_id', '=', tem.id)])
			for emp in emp_src :
				if emp.user_id.id :
					dep_ids.append(emp.user_id.id)
		self.tembusan_usr = dep_ids

	@api.onchange('rahsia')
	def _rahsia(self) :
		dep_ids = []
		tmb_ids = []
		if self.rahsia == 'biasa' :
			for kep in self.kepada :
				dep_ids.append(kep.department_id.id)
				self.kepada_dep = dep_ids
			for tem in self.tembusan :
				tmb_ids.append(tem.department_id.id)
				self.tembusan_dep = tmb_ids
		else :
			self.kepada_dep = False
			self.tembusan_dep = False

	@api.onchange('user_id')
	def _user_departmenr(self):
		emp_obj = self.env['hr.employee']
		emp_src = emp_obj.search([('user_id', '=', self.user_id.id)])
		#import pdb;pdb.set_trace()
		for job in emp_src :
			self.user_id1 = job.job_id
			self.pengirim = job.department_id

	@api.onchange('template')
	def _conhange_singer(self):
		self.signer6 = self.template.signer6

	@api.model
	def create(self,vals):
		emp_obj = self.env['hr.employee']
		emp_src = emp_obj.sudo().search([('user_id','=', vals['user_id'])])
		return super(surat_memorandum, self).create(vals)

	@api.multi
	def unlink(self):
		if self.state == 'done' :
			raise UserError(_('Anda Tidak Bisa Menghapus Karna Status Sudah Done.'))
		return super(surat_memorandum, self).unlink()

	@api.depends()
	def _get_report_true(self):
		for rec in self :
			x = 0
			#y = 0
			for data in rec.kepada :
				x +=1
			#for data2 in rec.tembusan :
			#	y +=1
			#if x > 1 or y >= 1 :
			if x > 1 :
				rec.report_true = "true"
				rec.update({'report_true':'true'})
			else :
				rec.report_true = "false"
				rec.update({'report_true':'false'})

	@api.depends()
	def _get_report_tem_true(self):
		for rec in self :
			y = 0
			for data in rec.tembusan :
				y +=1
			if y > 1 :
				rec.report_tem_true = "true"
				rec.update({'report_tem_true':'true'})
			else :
				rec.report_team_true = "false"
				rec.update({'report_tem_true':'false'})

	@api.depends()
	def _get_active_validate(self):
		for rec in self :
		#	xxx = 0
		#	yyy = 0
		#	zzz = 0
		#	for active in rec.kepada :
		#		emp_obj = self.env['hr.employee']
		#		emp_src = emp_obj.sudo().search([('job_id','=',active.id)])
		#		for emp in emp_src :
		#			if emp.user_id.id == self.env.user.id or self.env.user.id == 1 :
		#				xxx = 1
		#	for active_val in rec.validate_done :
		#		emp_obj = self.env['hr.employee']
		#		emp_src = emp_obj.sudo().search([('job_id','=',active_val.id)])
		#		for emp in emp_src :
		#			if emp.user_id.id == self.env.user.id or self.env.user.id == 1 :
		#				yyy = 1
		#	for act_val in rec.validate_show :
		#		emp_obj = self.env['hr.employee']
		#		emp_src = emp_obj.sudo().search([('job_id','=',act_val.id)])
		#		for emp in emp_src :
		#			if emp.user_id.id == self.env.user.id or self.env.user.id == 1 :
		#				zzz = 1
		#	if xxx == 1 and yyy != 1 and zzz == 1:
		#		rec.active_validate = "true"
		#		rec.update({'active_validate':'true'})
		#	else :
		#		rec.active_validate = "false"
		#		rec.update({'active_validate':'false'})
			if rec.user_id.id == self.env.user.id :
				rec.update({'active_validate':'true'})
			else :
				rec.update({'active_validate':'false'})

	@api.depends()
	def _get_active_user(self):
		for rec in self :
			for active in rec.kepada :
				emp_obj = self.env['hr.employee']
				emp_src = emp_obj.sudo().search([('job_id','=',active.id)])
				for emp in emp_src :
					if emp.user_id.id == self.env.user.id or self.env.user.id == 1 :
						rec.active_user = "true"
						rec.update({'active_user':'true'})
			for active in rec.tembusan :
				emp_obj = self.env['hr.employee']
				emp_src = emp_obj.sudo().search([('job_id','=',active.id)])
				for emp2 in emp_src :
					if emp2.user_id.id == self.env.user.id or self.env.user.id == 1 :
						rec.active_user = "true"
						rec.update({'active_user':'true'})
			for active in rec.user_ids3 :
				if active.id == self.env.user.id :
					rec.active_user = 'true'
					rec.update({'active_user':'true'})

	def _compute_memo_count(self):
		memo_data = self.env['disposisi.masuk'].sudo().read_group([('no_memo', 'in', self.ids)], ['no_memo'], ['no_memo'])
		result = dict((data['no_memo'][0], data['no_memo_count']) for data in memo_data)
		for memo in self:
			memo.memo_count = result.get(memo.id, 0)

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
				body_html = '<p>Kepada '+str(send.job_id.name)+',</p> \n'+'<p> anda sebagai Checker 1 untuk Memorandum dengan Nomor '+str(self.name)+' Dengan Perihal '+str(self.perihal)+' Mohon Untuk Segera Di tindak lanjuti'
				mail        = self.env['mail.mail']
				notif_mail  = mail.create({'subject'    : 'Memorandum '+str(self.perihal),
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
					body_html = '<p>Kepada '+str(send.job_id.name)+',</p> \n'+'<p> anda sebagai Checker 2 untuk Memorandum dengan Nomor '+str(self.name)+' Dengan Perihal '+str(self.perihal)+' Mohon Untuk Segera Di tindak lanjuti'
					mail        = self.env['mail.mail']
					notif_mail  = mail.create({'subject'    : 'Memorandum '+str(self.perihal),
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
					body_html = '<p>Kepada '+str(send.job_id.name)+',</p> \n'+'<p> anda sebagai Signer untuk Memorandum dengan Nomor '+str(self.name)+' Dengan Perihal '+str(self.perihal)+' Mohon Untuk Segera Di tindak lanjuti'
					mail        = self.env['mail.mail']
					notif_mail  = mail.create({'subject'    : 'Memorandum '+str(self.perihal),
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
					body_html = '<p>Kepada '+str(send.job_id.name)+',</p> \n'+'<p> anda sebagai Checker 3 untuk Memorandum dengan Nomor '+str(self.name)+' Dengan Perihal '+str(self.perihal)+' Mohon Untuk Segera Di tindak lanjuti'
					mail        = self.env['mail.mail']
					notif_mail  = mail.create({'subject'    : 'Memorandum '+str(self.perihal),
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
					body_html = '<p>Kepada '+str(send.job_id.name)+',</p> \n'+'<p> anda sebagai Signer untuk Memorandum dengan Nomor '+str(self.name)+' Dengan Perihal '+str(self.perihal)+' Mohon Untuk Segera Di tindak lanjuti'
					mail        = self.env['mail.mail']
					notif_mail  = mail.create({'subject'    : 'Memorandum '+str(self.perihal),
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
					body_html = '<p>Kepada '+str(send.job_id.name)+',</p> \n'+'<p> anda sebagai Checker 4 untuk Memorandum dengan Nomor '+str(self.name)+' Dengan Perihal '+str(self.perihal)+' Mohon Untuk Segera Di tindak lanjuti'
					mail        = self.env['mail.mail']
					notif_mail  = mail.create({'subject'    : 'Memorandum '+str(self.perihal),
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
					body_html = '<p>Kepada '+str(send.job_id.name)+',</p> \n'+'<p> anda sebagai Signer untuk Memorandum dengan Nomor '+str(self.name)+' Dengan Perihal '+str(self.perihal)+' Mohon Untuk Segera Di tindak lanjuti'
					mail        = self.env['mail.mail']
					notif_mail  = mail.create({'subject'    : 'Memorandum '+str(self.perihal),
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
					body_html = '<p>Kepada '+str(send.job_id.name)+',</p> \n'+'<p> anda sebagai Checker 5 untuk Memorandum dengan Nomor '+str(self.name)+' Dengan Perihal '+str(self.perihal)+' Mohon Untuk Segera Di tindak lanjuti'
					mail        = self.env['mail.mail']
					notif_mail  = mail.create({'subject'    : 'Memorandum '+str(self.perihal),
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
					body_html = '<p>Kepada '+str(send.job_id.name)+',</p> \n'+'<p> anda sebagai Signer untuk Memorandum dengan Nomor '+str(self.name)+' Dengan Perihal '+str(self.perihal)+' Mohon Untuk Segera Di tindak lanjuti'
					mail        = self.env['mail.mail']
					notif_mail  = mail.create({'subject'    : 'Memorandum '+str(self.perihal),
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
				body_html = '<p>Kepada '+str(send.job_id.name)+',</p> \n'+'<p> anda sebagai Signer untuk Memorandum dengan Nomor '+str(self.name)+' Dengan Perihal '+str(self.perihal)+' Mohon Untuk Segera Di tindak lanjuti'
				mail        = self.env['mail.mail']
				notif_mail  = mail.create({'subject'    : 'Memorandum '+str(self.perihal),
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
			##### mengambil sequence #####
			sequence = self.env['ir.sequence'].sudo().next_by_code('surat.memorandum') or '/'

			#### mengambil tahun ####
			years = str(datetime.now().year)

			#### mengambil code department ####
			code = self.template.user_id6.job_id.code_memo
			if code == False :
				code = "-"

			##### membuat penomoran #####
			self.name = code+"/PAS/"+sequence+"/"+years
		self.state = "inprogres"

	@api.multi
	def validate(self):
		#self.write({'validate_done':[(4,[self.env.user.partner_id.job_id.id])]})
		#for user in self.kepada :
		#	usr = 'no'
		#	for val in self.validate_done :
		#		if user.id == val.id :
		#			usr = 'yes'
		#	if usr != 'yes' :
		#		return True

		#if
		self.state = "done"



class JobPosition(models.Model):
	_inherit = "hr.job"

	memorandum_ids = fields.Many2many("surat.memorandum","kepadamemo_category_rel","job_id","kepada_id", string="memorandum")
	memorandum_ids2 = fields.Many2many("surat.memorandum","kepadamemo2_category_rel","job_id2","kepada_id2", string="memorandum")
	memorandum_ids3 = fields.Many2many("surat.memorandum","kepadamemo3_category_rel","job_id3","kepada_id3", string="memorandum")
	memorandum_ids4 = fields.Many2many("surat.memorandum","kepadamemo4_category_rel","job_id4","kepada_id4", string="memorandum")

class HrDepartment(models.Model):
	_inherit = "hr.department"

	memorandum_ids = fields.Many2many("surat.memorandum","kepadamemodep_category_rel","department_id","kepada_dep", string="memorandum")
	memorandum_ids2 = fields.Many2many("surat.memorandum","kepadamemodep2_category_rel","department_id2","kepada_dep2", string="memorandum")

class ResUsers(models.Model):
	_inherit = "res.users"

	disposisi_ids3 = fields.Many2many("surat.memorandum","user4_category_rel","user_id4","memo_id4", string="disposisi")
	memorandum_ids = fields.Many2many("surat.memorandum","kepadamemousr_category_rel","user_id","kepada_usr", string="memorandum")
	memorandum_ids2 = fields.Many2many("surat.memorandum","kepadamemousr2_category_rel","user_id2","kepada_usr2", string="memorandum")
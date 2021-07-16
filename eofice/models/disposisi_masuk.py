from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
from datetime import datetime, timedelta

class disposisi_masuk(models.Model):
	_name = "disposisi.masuk"
	_description = "Disposisi surat masuk"
	_inherit = ['ir.needaction_mixin']
	_order='date desc'

	name = fields.Char('No',required=True, index=True, copy=False, default='New')
	#user_ids = fields.Many2many('hr.job',"user_category_rel","user_id","job_id", string="Ditujukan Kepada")
	user_ids1 = fields.Many2many('hr.job','dispo_category_rel','dispo_id','job_id',string='Ditujukan kepada',domain="['|',('all_dsp','=',all_dispo),('parent_id','child_of',[user_id1])]")
	user_ids2 = fields.Many2many('hr.job',"dispo2_category_rel","user_id2","job_id2",'Ditujukan kepada',domain="['|',('all_dsp','=',all_dispo),('parent_id','child_of',[user_id1])]")
	user_ids4 = fields.Many2many('hr.job','dispo3_category_rel','dispo_id2','job_id2',string='Ditujukan kepada',domain="['|',('all_dsp','=',all_dispo),('parent_id','child_of',[user_id1])]")
	user_ids5 = fields.Many2many('hr.job',"dispo4_category_rel","user_id3","job_id3",'Ditujukan kepada',domain="['|',('all_dsp','=',all_dispo),('parent_id','child_of',[user_id1])]")
	user_ids3 = fields.Many2many('res.users',"user3_category_rel","dispo_id3","user_id3",'Ditujukan kepada Delegasi')
	level_id = fields.Char('Level',compute='_get_level')
	hide_level = fields.Char('Hide Level',compute='_get_hide_level')
	action2 = fields.Many2one('action.action','Action', domain="[('active','=',True)]")
	action3 = fields.Many2one('action.action','Action', domain="[('active','=',True)]")
	action4 = fields.Many2one('action.action','Action', domain="[('active','=',True)]")
	action5 = fields.Many2one('action.action','Action', domain="[('active','=',True)]")
	date = fields.Datetime('Tanggal',default=fields.Datetime.now, required=True)
	note = fields.Html('Catatan')
	source = fields.Char('Source Document')
	state = fields.Selection(
		[('draft','Draft'),('inprogres','In Progress'),('done','Done')],'Status', indext=True, readonly=True, default='draft')
	active_user = fields.Char('active user',compute='_get_active_user')
	user_act = fields.Char('nama user delegasi',compute='_get_user_act')
	job_delegasi = fields.Char('Job Pemberi Delegasi',compute='_get_job_del')
	user_id1 = fields.Many2one('hr.job','Pembuat Dispo', compute='_user_disposisi', store=True)
	user_id2 = fields.Many2one('res.users', string='Responsible',default= lambda self: self.env.user)
	all_dispo = fields.Boolean('All Dispo')
	pengirim = fields.Many2one('hr.department','pengirim')
	button_dispo = fields.Boolean('Disposisi', compute="_get_btnds")
	button_nota = fields.Boolean('Nota', compute="_get_btnnt")
	note_forward = fields.Html('Catatan Forward')
	forward_to = fields.Many2one('hr.job','Forward Kepada')
	active_validate = fields.Char('active_validate',compute='_get_active_validate')
	validate_done = fields.Many2many('hr.job',"kepadadispo3_category_rel","kepada_id4","job_id4", string="Dispo Done By")
	########## keterangan surat masuk ###########
	jenis_surat = fields.Selection(
		[('surat_masuk', 'Surat Masuk'), ('surat_keluar', 'Surat Keluar'),
		 ('nota', 'Nota'),('memorandum','Memodarndum')], 'Jenis Surat')
	no_ref = fields.Many2one('surat.masuk',string='Nomor surat masuk')
	name_ref = fields.Char('Surat Masuk')
	partner = fields.Char('Pengirim')
	subject = fields.Char('perihal/Subjek')
	total_set = fields.Char('Jumlah set')
	date1 = fields.Date('Tanggal Fisik Surat')
	date2 = fields.Date('Tanggal penerimaan surat')
	date_now = fields.Date('Date Now',compute='_date_now')
	status_surat = fields.Selection(
		[('segera', 'S'), ('penting', 'P'),
		 ('rahasia', 'R'),('biasa','B')], 'Status Surat')
	#attach = fields.Binary("Attachments")
	#### nota ####
	no_nota = fields.Many2one('surat.nota',string='Nomor Nota')
	kepada_nota = fields.Many2one('hr.job','Ditujukan Untuk')
	tembusan_nota = fields.Many2one('hr.job','Tembusan')
	perihal_nota = fields.Char('Perihal/Subjek')
	date_nota = fields.Date('Tanggal')
	#### memorandum ####
	no_memo = fields.Many2one('surat.memorandum',string='Nomor memorandum')
	kepada_memo = fields.Many2one('hr.job','Ditujukan Untuk')
	tembusan_memo = fields.Many2one('hr.department','Tembusan')
	perihal_memo = fields.Char('Perihal/Subjek')
	date_memo = fields.Date('Tanggal')
	#### Tanda Terima ####
	no_tanda_terima = fields.Many2one('tanda.terima', string="Nomor Tanda Terima")
	partner_tante = fields.Many2one('res.partner','Pengirim')
	user_tante =  fields.Many2one('hr.job','Ditujukan Untuk')
	date_tante = fields.Date('Tanggal')
	konten_tante = fields.Char('Konten')

	@api.model
	def _needaction_domain_get(self, domain=None):
		return [('state', '=', 'inprogres'),('user_id2','!=',self.env.user.id)]

	@api.multi
	def prints(self):
		if self.env.user.job_id.name == 'President Director' :
			return self.env['report'].get_action(self, 'eofice.report_disposisi2')
		else :
			return self.env['report'].get_action(self, 'eofice.report_disposisi')

	#@api.model
	#def create(self,vals):
		#if self.env.user.partner_id.job_id.name == "President Director" :
		#	code_dis = self.env.user.partner_id.job_id.code_dispo
		#	if code_dis == False :
		#		code_dis = "-"
		#	vals['name'] = code_dis+"/"+self.env['ir.sequence'].sudo().next_by_code('disposisi.masuk') or '/'
		#return super(disposisi_masuk, self).create(vals)

	def _get_btnds(self):
		grp_obj = self.env['res.groups'].search([('name','=','Disposisi Create')])
		for btnds in grp_obj :
			for btn in btnds.users :
				if btn.id == self.env.user.id or self.env.user.id == 1 :
					self.button_dispo = True
					self.update({'button_dispo':True})

	def _get_btnnt(self):
		grp_obj = self.env['res.groups'].search([('name','=','Nota Dinas Create')])
		for btnnt in grp_obj :
			for btn in btnnt.users :
				if btn.id == self.env.user.id or self.env.user.id == 1 :
					self.button_nota = True
					self.update({'button_nota':True})

	def _get_level(self):
		for rec in self :
			for active in rec.user_ids1 :
				emp_obj = self.env['hr.employee']
				emp_src = emp_obj.sudo().search([('job_id','=',active.id)])
				for emp in emp_src :
					if emp.user_id.id == self.env.user.id  and self.env.user.job_id.level_id.name == 'LD3' and active.level_id.name == 'LD3' and rec.state == 'inprogres':
						rec.level_id = 'true'
						rec.update({'level_id':'true'})
						return True
					else :
						rec.level_id = 'false'
						rec.update({'level_id':'false'})

	def _get_hide_level(self):
		for rec in self :
			if self.env.user.job_id.level_id.name == 'LD3' or self.env.user.job_id.level_id.name == '':
				rec.hide_level = 'true'
				rec.update({'hide_level':'true'})
			else :
				rec.hide_level = 'false'
				rec.update({'hide_level':'false'})

	def _get_active_user(self):
		for rec in self :
			if rec.user_id2.id == self.env.user.id :
				rec.active_user = 'true'
				rec.update({'active_user':'true'})
			else :
				for active in rec.user_ids1 :
					usr = 'no'
					for val in rec.validate_done :
						if active.id == val.id :
							usr = 'yes'
					if usr == 'yes' :
						rec.active_user = 'false'
						rec.update({'active_user':'false'})
					else :
						emp_obj = self.env['hr.employee']
						emp_src = emp_obj.sudo().search([('job_id','=',active.id)])
						for emp in emp_src :
							if emp.user_id.id == self.env.user.id or self.env.user.id == 1 :
								rec.active_user = 'true'
								rec.update({'active_user':'true'})
								return True
				for active in rec.user_ids2 :
					usr = 'no'
					for val in rec.validate_done :
						if active.id == val.id :
							usr = 'yes'
					if usr == 'yes' :
						rec.active_user = 'false'
						rec.update({'active_user':'false'})
					else :
						emp_obj = self.env['hr.employee']
						emp_src = emp_obj.sudo().search([('job_id','=',active.id)])
						for emp2 in emp_src :
							if emp2.user_id.id == self.env.user.id or self.env.user.id == 1 :
								rec.active_user = 'true'
								rec.update({'active_user':'true'})
								return True
				for active in rec.user_ids4 :
					usr = 'no'
					for val in rec.validate_done :
						if active.id == val.id :
							usr = 'yes'
					if usr == 'yes' :
						rec.active_user = 'false'
						rec.update({'active_user':'false'})
					else :
						emp_obj = self.env['hr.employee']
						emp_src = emp_obj.sudo().search([('job_id','=',active.id)])
						for emp2 in emp_src :
							if emp2.user_id.id == self.env.user.id or self.env.user.id == 1 :
								rec.active_user = 'true'
								rec.update({'active_user':'true'})
								return True
				for active in rec.user_ids5 :
					usr = 'no'
					for val in rec.validate_done :
						if active.id == val.id :
							usr = 'yes'
					if usr == 'yes' :
						rec.active_user = 'false'
						rec.update({'active_user':'false'})
					else :
						emp_obj = self.env['hr.employee']
						emp_src = emp_obj.sudo().search([('job_id','=',active.id)])
						for emp2 in emp_src :
							if emp2.user_id.id == self.env.user.id or self.env.user.id == 1 :
								rec.active_user = 'true'
								rec.update({'active_user':'true'})
								return True

	def _get_user_act(self):
		for rec in self :
			#import pdb;pdb.set_trace()
			if self.env.user.name[:3] == "PJS" :
				dl_obj = self.env['delegasi']
				for act in dl_obj.sudo().search([('user_id3','=',self.env.user.id)])[0] :
					rec.user_act = act.user_id2.name
					rec.update({'active_user':act.user_id2.name})
			else :
				rec.user_act = "false"
				rec.update({'user_act':"false"})

	def _get_job_del(self):
		for rec in self :
			rec.job_delegasi = rec.sudo().user_id2.job_id.name
			rec.update({'job_delegasi':rec.sudo().user_id2.job_id.name})

	def _date_now(self):
		for rec in self :
			rec.date_now = str(datetime.today())[:10]
			rec.update({'date_now':str(datetime.today())[:10]})

	@api.multi
	@api.depends('user_id2')
	def _user_disposisi(self):
		emp_obj = self.env['hr.employee']
		emp_src = emp_obj.search([('user_id', '=', self.user_id2.id)])
		for job in emp_src :
			self.user_id1 = job.job_id
			self.pengirim = job.department_id
			self.all_dispo = job.job_id.all_dispo

	@api.onchange('no_ref')
	def _onchange_noref_id(self):
		noref = self.no_ref
		self.name_ref = noref.name
		self.partner =  noref.partner.name
		self.subject = noref.subject
		self.total_set = noref.total_set
		self.date1 = noref.date
		self.date2 = noref.date3
		self.status_surat = noref.status_surat

	@api.onchange('no_nota')
	def _onchange_nonota_id(self):
		nonota = self.no_nota
		self.kepada_nota = nonota.kepada
		self.tembusan_nota = nonota.tembusan
		self.perihal_nota = nonota.perihal
		self.date_nota = nonota.date
		self.note = nonota.content
	@api.onchange('no_memo')
	def _onchange_nomemo_id(self):
		nomemo = self.no_memo
		self.perihal_memo = nomemo.perihal
		self.date_memo = nomemo.date
		self.note = nomemo.content

	@api.onchange('no_tanda_terima')
	def _onchange_notante(self):
		notante = self.no_tanda_terima
		self.partner_tante = notante.partner_id
		self.user_tante = notante.user_id
		self.date_tante = notante.date
		self.konten_tante = notante.konten

	@api.multi
	def confirm(self):
		### delegasi ###
		#del_obj = self.env['delegasi']
		#delegasi = []
		#for dis in self.user_ids1 :
	#		emp_obj = self.env['hr.employee']
	#		emp_src = emp_obj.sudo().search([('job_id','=',dis.id)])
	#		for emp in emp_src :
	#			del_src = del_obj.sudo().search([('state','=','inprogres'),('user_id','=',emp.user_id.id)])
	#			for dele in del_src :
	#				if dele.disposisi == True :
	#					delegasi.append(dele.user_id3.id)
	#	for dis2 in self.user_ids2 :
	#		emp_obj = self.env['hr.employee']
	#		emp_src = emp_obj.sudo().search([('job_id','=',dis.id)])
	#		for emp in emp_src :
	#			del_src = del_obj.sudo().search([('state','=','inprogres'),('user_id','=',dis2.id)])
	#			for dele in del_src :
	#				if dele.disposisi == True :
	#					delegasi.append(dele.user_id3.id)
	#	self.write({'user_ids3' : [(4,[delegasi])]})

		if self.name == 'New' :
			code_dis = self.user_id1.code_dispo
			if code_dis == False :
				code_dis = "-"
			self.name = code_dis+"/"+self.env['ir.sequence'].sudo().next_by_code('disposisi.masuk') or '/'
		###### create attachment ########
		att_src = True
		att_obj = self.env['ir.attachment']
		if self.no_ref :
			att_src = att_obj.search([('res_model','=','surat.masuk'),('res_id','=',self.no_ref.id)])
		elif self.no_nota :
			att_src = att_obj.search([('res_model','=','surat.nota'),('res_id','=',self.no_nota.id)])
		elif self.no_memo :
			att_src = att_obj.search([('res_model','=','surat.memorandum'),('res_id','=',self.no_memo.id)])
		if att_src != True :
			for attachments in att_src:
				attachment = self.env['ir.attachment'].create({'name':attachments.name,
													'type':'binary',
													'datas':attachments.datas,
													'mimetype':attachments.mimetype,
													'res_model':'disposisi.masuk',
													'res_id':self.id,
													'res_name':self.name})

		##### mengirim email ke email tujuan ####

		#### Search Employee1 ####
		emp_obj = self.env['hr.employee']

		#### search email company ####
		com_obj = self.env['res.company']
		com_src = com_obj.search([],limit=1)
		for comp in com_src :
			for emp in self.user_ids1 :
				emp_src = emp_obj.search([('job_id','=',emp.id)])
				for send in emp_src :
					body_html = '<p>Kepada '+str(emp.name)+',</p> \n'+'<p> Ada disposisi masuk dengan nomor '+str(self.name)+', Mohon Untuk Segera Di tindak lanjuti'
					mail        = self.env['mail.mail']
					notif_mail  = mail.create({'subject'    : 'Disposisi Masuk',
															'email_from'    : comp.email,
															'email_to'      : send.work_email,
															#'email_cc'     :
															'auto_delete'   : True,
															'type'          : 'notification',
															#'recipient_ids' : [(6, 0, [gr.partner_id.id])],
															'notification'  : True,
															'body_html'     : body_html,
															})
			for emp2 in self.user_ids2 :
				emp_src2 = emp_obj.search([('job_id','=',emp2.id)])
				for send1 in emp_src2 :
					body_html = '<p>Kepada '+str(emp2.name)+',</p> \n'+'<p> Ada disposisi masuk dengan nomor '+str(self.name)+', Mohon Untuk Segera Di tindak lanjuti'
					mail        = self.env['mail.mail']
					notif_mail  = mail.create({'subject'    : 'Disposisi Masuk',
															'email_from'    : comp.email,
															'email_to'      : send1.work_email,
															#'email_cc'     :
															'auto_delete'   : True,
															'type'          : 'notification',
															#'recipient_ids' : [(6, 0, [gr.partner_id.id])],
															'notification'  : True,
															'body_html'     : body_html,
															})
							   # _logger.info("created due date invoice alert to %s" % (gr.partner_id.email) )
			send = self.env['mail.mail'].process_email_queue()
		self.state = "inprogres"

	#@api.multi
	#def validate(self):
	#	self.write({'validate_done':[(4,[self.env.user.partner_id.job_id.id])]})
	#	for user in self.user_ids1 :
	#		usr = 'no'
	#		for val in self.validate_done :
	#			if user.id == val.id :
	#				usr = 'yes'
	#		if usr != 'yes' :
	#			return True
	#	for user in self.user_ids2 :
	#		usr = 'no'
	#		for val in self.validate_done :
	#			if user.id == val.id :
	#				usr = 'yes'
	#		if usr != 'yes' :
	#			return True
	#	for user in self.user_ids4 :
	#		usr = 'no'
	#		for val in self.validate_done :
	#			if user.id == val.id :
	#				usr = 'yes'
	#		if usr != 'yes' :
	#			return True
	#	for user in self.user_ids5 :
	#		usr = 'no'
	#		for val in self.validate_done :
	#			if user.id == val.id :
	#				usr = 'yes'
	#		if usr != 'yes' :
	#			return True
	#	self.state = "done"
	#	dis_obj = self.env['disposisi.masuk']
	#	dis_src = dis_obj.sudo().search([('name','=',self.source)])
	#	#dis = self.source
	#	xxx = False
	#	yy = 0
	#	if dis_src != False :
	#		dis_tr = True
	#	while dis_tr == True :
	#		dis_tr = False
	#		for dis in dis_src :
	#			cek_source = dis_obj.sudo().search([('source','=',dis.name)])
	#			for cek in cek_source :
	#				yy += 1
	#				if cek.state != 'done' :
	#					xxx = True
	#			if yy == 1 :
	#				if len(dis.user_ids1) > 1 or len(dis.user_ids2) >= 1 :
	#					xxx = True
	#			if xxx == False :
	#				dis.update({'state':'done'})
	#			if xxx == False and dis.source != False :
	#				dis_tr =True
	#			dis_src = dis_obj.sudo().search([('name','=',dis.source)])

	#@api.multi
	#def validate(self):
	#	self.state = "done"
	#	dis_obj = self.env['disposisi.masuk']
	#	dis_src = dis_obj.sudo().search([('name','=',self.source)])
	#	#dis = self.source
	#	xxx = False
	#	if dis_src != False :
	#		dis_tr = True
	#	while dis_tr == True :
	#		dis_tr = False
	#		for dis in dis_src :
	#			cek_source = dis_obj.sudo().search([('source','=',dis.name)])
	#			for cek in cek_source :
	#				if cek.state != 'done' :
	#					xxx = True
	#			if xxx == False :
	#				dis.update({'state':'done'})
	#			if xxx == False and dis.source != False :
	#				dis_tr =True
	#			dis_src = dis_obj.sudo().search([('name','=',dis.source)])

	@api.multi
	def validate(self):
		if self.env.user.id != self.user_id2.id or self.env.user.id == 1:
			self.write({'validate_done':[(4,[self.env.user.job_id.id])]})
			for user in self.user_ids1 :
				usr = 'no'
				for val in self.validate_done :
					if user.id == val.id :
						usr = 'yes'
				if usr != 'yes' :
					return True
			for user in self.user_ids2 :
				usr = 'no'
				for val in self.validate_done :
					if user.id == val.id :
						usr = 'yes'
				if usr != 'yes' :
					return True
			#for user in self.user_ids4 :
			#	usr = 'no'
			#	for val in self.validate_done :
			#		if user.id == val.id :
			#			usr = 'yes'
			#	if usr != 'yes' :
			#		return True
			#for user in self.user_ids5 :
			#	usr = 'no'
			#	for val in self.validate_done :
			#		if user.id == val.id :
			#			usr = 'yes'
			#	if usr != 'yes' :
			#		return True
			#self.state = "done"
			dis_obj = self.env['disposisi.masuk']
			dis_src = dis_obj.sudo().search([('name','=',self.source)])
			#dis = self.source
			xxx = False
			yy = 0
			if dis_src != False :
				dis_tr = True
			while dis_tr == True :
				dis_tr = False
				for dis in dis_src :
					cek_source = dis_obj.sudo().search([('source','=',dis.name)])
					for cek in cek_source :
						yy += 1
						if cek.state != 'done' :
							xxx = True
					if yy == 1 :
						if len(dis.user_ids1) > 1 or len(dis.user_ids2) >= 1 :
							xxx = True
					if xxx == False :
						dis.update({'state':'done'})
					if xxx == False and dis.source != False :
						dis_tr =True
					dis_src = dis_obj.sudo().search([('name','=',dis.source)])
		else :
			for user in self.user_ids1 :
				usr = 'no'
				for val in self.validate_done :
					if user.id == val.id :
						usr = 'yes'
				if usr != 'yes' :
					return True
			for user in self.user_ids2 :
				usr = 'no'
				for val in self.validate_done :
					if user.id == val.id :
						usr = 'yes'
				if usr != 'yes' :
					return True
			self.state = "done"
			dis_obj = self.env['disposisi.masuk']
			dis_src = dis_obj.sudo().search([('name','=',self.source)])
			#dis = self.source
			pembuat = self.user_id1.id
			xxx = False
			if dis_src != False :
				dis_tr = True
			while dis_tr == True :
				dis_tr = False
				for dis in dis_src :
					cek_source = dis_obj.sudo().search([('source','=',dis.name)])

					dis.write({'validate_done':[(4,[pembuat])]})
					pembuat = dis.user_id1.id
					for user in dis.user_ids1 :
						usr = 'no'
						for val in dis.validate_done :
							if user.id == val.id :
								usr = 'yes'
						if usr != 'yes' :
							return True
					for user in dis.user_ids2 :
						usr = 'no'
						for val in dis.validate_done :
							if user.id == val.id :
								usr = 'yes'
						if usr != 'yes' :
							return True

					#for cek in cek_source :
					#	if cek.state != 'done' :
					#		xxx = True
					#if xxx == False :
					#	dis.update({'state':'done'})
					dis.update({'state':'done'})
					if dis.source != False :
						dis_tr =True
					dis_src = dis_obj.sudo().search([('name','=',dis.source)])


class JobPosition(models.Model):
	_inherit = "hr.job"

	disposisi_ids = fields.Many2many('disposisi.masuk','dispo_category_rel','job_id','dispo_id', string='disposisi')
	disposisi_ids2 = fields.Many2many("disposisi.masuk","dispo2_category_rel","job_id2","user_id2", string="disposisi")
	disposisi_ids3 = fields.Many2many('disposisi.masuk','dispo3_category_rel','job_id2','dispo_id2', string='disposisi')
	disposisi_ids4 = fields.Many2many("disposisi.masuk","dispo4_category_rel","job_id3","user_id3", string="disposisi")
	disposisi_ids5 = fields.Many2many("disposisi.masuk","kepadadispo3_category_rel","job_id4","kepada_id4", string="disposisi")

class ResUsers(models.Model):
	_inherit = "res.users"

	disposisi_ids3 = fields.Many2many("disposisi.masuk","user3_category_rel","user_id3","dispo_id3", string="disposisi")

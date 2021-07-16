from odoo import models, fields, api, _
from odoo.exceptions import UserError, AccessError, ValidationError
from datetime import datetime, timedelta


class surat_masuk(models.Model):
	_name = "surat.masuk"
	_description = "Surat Masuk"
	_inherit = ['ir.needaction_mixin']
	_order='date3 desc'

	name = fields.Char('No',required=True, index=True, copy=False, default='New')
	status_surat = fields.Selection(
		[('segera', 'S'), ('penting', 'P'),
		 ('rahasia', 'R'),('biasa','B')], 'Status Surat')
	jenis_surat = fields.Selection(
		[('surat_masuk', 'Surat Masuk'), ('surat_keluar', 'Surat Keluar'),
		 ('nota', 'Nota'),('memorandum','Memodarndum')], 'Jenis Surat', default='surat_masuk')
	no_ref = fields.Char('Nomor Fisik Surat')
	partner = fields.Many2one('res.partner','Pengirim Surat')
	user_id1 = fields.Many2one('res.users', string='Pembuat',default= lambda self: self.env.user)
	user_id2 = fields.Many2one('hr.job','Job User Pembuat')
	user_id = fields.Many2one('hr.job','Ditujukan Untuk', domain="['|',('department_id','=',user_dpt),('name','=',manager_pembuat)]", required=True)
	tembusan = fields.Many2one('hr.job','Tembusan')
	tembusan2 = fields.Many2many('hr.job','sm_category_rel','sm_id','jobsm_id',string='Tembusan')
	manager_pembuat = fields.Char('manager Pembuat')
	user_delegasi = fields.Many2one('res.users', string="User Pendelegasian")
	user_dpt = fields.Many2one('hr.department','Dep Pembuat')
	user_tujuan = fields.Many2one('res.users', string="User Penerima")
	user_tembusan = fields.Many2one('res.users', string="User Tembusan")
	active_user = fields.Boolean('active user',compute='_get_active_user')
	subject = fields.Char('Perihal/Subject')
	total_set = fields.Char('Jumlah Set')
	date = fields.Datetime("Tanggal Fisik Surat")
	date3 = fields.Datetime('Tanggal penerimaan surat', default=fields.Datetime.now,required=True)
	dispo_ids = fields.One2many('disposisi.masuk', 'no_ref', string='disposisi')
	dispo_id = fields.Many2one('disposisi.masuk', compute='_compute_dispo_id', string='Current Disposisi', help='Latest dispo of the employee')
	surat_masuk_count = fields.Integer(compute='_compute_surat_count', string="Surat Masuk")
	state = fields.Selection(
		[('draft','Draft'),('inprogres','In Progress'),('done','Done')],'Status', indext=True, readonly=True, default='draft')
	#pengirim = fields.Many2one('hr.department','Pengirim',readonly=True)
	dms = fields.Boolean('Dms',default=True)
	####### surat keluar ##########
	no_suratklr = fields.Many2one('surat.keluar', 'No Surat Keluar')
	perihal = fields.Char('Perihal/Subjek')
	date_sk = fields.Date('Tanggal')

	@api.model
	def _needaction_domain_get(self, domain=None):
		return [('state', '=', 'inprogres'),('user_tujuan','=',self.env.user.id)]


	@api.multi
	def unlink(self):
		for unl in self :
			if unl.state == 'done' :
				raise UserError(_('Anda Tidak Bisa Menghapus Karna Status Sudah Done.'))
			return super(surat_masuk, self).unlink()

	@api.onchange('no_suratklr')
	def _onchange_keluar(self):
		no_surat = self.no_suratklr
		#self.pengirim = no_surat.pengirim
		self.perihal = no_surat.perihal
		self.date = no_surat.date

	@api.onchange('user_id1')
	def _onchange_user1(self) :
		for rec in self:
			rec.user_dpt = rec.user_id1.department_id
			rec.user_id2 = rec.user_id1.job_id
			rec.manager_pembuat = rec.user_id1.job_id.manager_id.name

	@api.onchange('user_id')
	def _onchange_user(self):
		for rec in self :
			emp_obj = self.env['hr.employee']
			emp_src = emp_obj.sudo().search([('job_id','=',rec.user_id.id)])
			for emp in emp_src :
				self.user_tujuan = emp.user_id

	@api.onchange('tembusan')
	def _onchange_tembusan(self):
		for rec in self :
			emp_obj = self.env['hr.employee']
			emp_src_tmb = emp_obj.sudo().search([('job_id','=',rec.tembusan.id)])
			for tem in emp_src_tmb :
				self.user_tembusan = tem.user_id

	@api.depends()
	def _get_active_user(self):
		for rec in self :
			emp_obj = self.env['hr.employee']
			emp_src = emp_obj.sudo().search([('job_id','=',rec.user_id.id)])
			for emp in emp_src :
				if emp.user_id.id == self.env.user.id or self.env.user.id == 1 :
					rec.active_user = True
					self.write({'active_user':True})
			emp2_obj = self.env['hr.employee']
			emp2_src = emp_obj.sudo().search([('job_id','=',rec.tembusan.id)])
			for emp2 in emp2_src :
				if emp2.user_id.id == self.env.user.id or self.env.user.id == 1 :
					rec.active_user = "true"
					rec.update({'active_user':'true'})

	def _compute_surat_count(self):
		#import pdb;pdb.set_trace()
		surat_data = self.env['disposisi.masuk'].sudo().read_group([('no_ref', 'in', self.ids)], ['no_ref'], ['no_ref'])
		#if self.env.user.id == 1:
		#	surat_data = self.env['disposisi.masuk'].sudo().read_group([('no_ref', 'in', self.ids)], ['no_ref'], ['no_ref'])
		#else :
		#	surat_data = self.env['disposisi.masuk'].sudo().read_group(['|','|','|',('pengirim','=',self.env.user.partner_id.department_id.id),('user_ids1','in',self.env.user.partner_id.job_id.id),('user_ids2','in',self.env.user.partner_id.job_id.id),('user_ids3','in',self.env.user.id)], ['no_ref'], ['no_ref'])
		result = dict((data['no_ref'][0], data['no_ref_count']) for data in surat_data)
		for surat_masuk in self:
			surat_masuk.surat_masuk_count = result.get(surat_masuk.id, 0)

	@api.multi
	def confirm(self):
		### delegasi ###
		#del_obj = self.env['delegasi']
		#del_src = del_obj.sudo().search([('state','=','inprogres'),('user_id','=',self.user_tujuan.id)])
		#for dele in del_src :
		#	if dele.surat_masuk == True :

		if self.name == 'New' :
			#### mengambil bulan romawi ####
			#aray_bln = ['I','II','III','IV','V','VI','VII','VIII','IX','X','XI','XII']
			#month = aray_bln[(datetime.now().month)-1]

			#### mengambil tahun ####
			years = str(datetime.now().year)

			#### mengambil sequence ####
			sequence = self.env['ir.sequence'].sudo().next_by_code('surat.masuk')

			#### mengambil code department #####
			dept = self.user_id.code_sm
			if dept == False :
				dept = "-"

			#### membuat penomoran
			self.name = sequence+"/SM/"+dept+"/"+years

		##### mengirim email ke email tujuan ####

		#### Search Employee ####
		emp_obj = self.env['hr.employee']
		emp_src = emp_obj.sudo().search([('job_id','=',self.user_id.id)])

		#### search email company ####
		com_obj = self.env['res.company']
		com_src = com_obj.sudo().search([],limit=1)
		for comp in com_src :
			for send in emp_src :
				body_html = '<p>Kepada '+str(self.user_id.name)+',</p> \n'+'<p> Ada surat masuk dengan nomor '+str(self.name)+' Dengan Perihal '+str(self.subject)+' Mohon Untuk Segera Di tindak lanjuti'
				mail        = self.env['mail.mail']
				notif_mail  = mail.sudo().create({'subject'    : 'Surat Masuk perihal '+str(self.subject),
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
			send = self.env['mail.mail'].sudo().process_email_queue()
		self.state = "inprogres"
		self.dms = False

	@api.multi
	def validate(self):
		self.state = "done"

class JobPosition(models.Model):
	_inherit = "hr.job"

	sm_ids = fields.Many2many('surat.masuk','sm_category_rel','jobsm_id','sm_id', string='disposisi')




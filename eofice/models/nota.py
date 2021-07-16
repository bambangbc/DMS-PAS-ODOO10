from odoo import models, fields, api, _
from odoo.exceptions import UserError, AccessError, ValidationError
from datetime import datetime, timedelta


class surat_nota(models.Model):
	_name = "surat.nota"
	_description = "Surat Nota"
	_inherit = ['ir.needaction_mixin']
	_order='date desc'

	name = fields.Char('No',required=True, index=True, copy=False, default='New')
	kepada = fields.Many2one('hr.job','Ditujukan Untuk')
	user_tujuan = fields.Many2one('res.users',string="user Tujuan")
	user_delegasi = fields.Many2one('res.users', string="User Pendelegasian")
	tembusan = fields.Many2one('hr.job','Tembusan')
	perihal = fields.Char('Perihal/Subjek')
	date = fields.Datetime('Tanggal', default=fields.Datetime.now, required=True)
	content = fields.Html('Deskripsi')
	jenis_surat = fields.Selection(
		[('surat_masuk', 'Surat Masuk'), ('surat_keluar', 'Surat Keluar'),
		 ('nota', 'Nota'),('memorandum','Memodarndum')], 'Jenis Surat', default='nota')
	attach = fields.Binary('Attachment')
	dispo_ids = fields.One2many('disposisi.masuk', 'no_nota', string='disposisi')
	dispo_id = fields.Many2one('disposisi.masuk', 'Source Document', help='Latest dispo of the employee')
	nota_count = fields.Integer(compute='_compute_nota_count', string="Nota")
	state = fields.Selection(
		[('draft','Draft'),('inprogres','In Progress'),('done','Done')],'Status', indext=True, readonly=True, default='draft')
	active_user = fields.Boolean('active_user',compute='_get_active_user')
	user_id = fields.Many2one('res.users', string='Responsible',default= lambda self: self.env.user)
	pengirim = fields.Many2one('hr.department','Pengirim',readonly=True)
	button_dispo = fields.Boolean('Disposisi', compute="_get_btnds")
	###### tanda terima #######
	no_tanda_terima = fields.Many2one('tanda.terima','Tanda Terima Dokumen')

	api.model
	def _needaction_domain_get(self, domain=None):
		return [('state', '=', 'inprogres'),('user_tujuan','=',self.env.user.id)]

	def _get_btnds(self):
		grp_obj = self.env['res.groups'].search([('name','=','Disposisi Create')])
		for btnds in grp_obj :
			for btn in btnds.users :
				if btn.id == self.env.user.id or self.env.user.id == 1 :
					self.button_dispo = True
					self.update({'button_dispo':True})

	@api.onchange('dispo_id')
	def _onchange_dispo(self):
		for rec in self:
			rec.kepada = rec.dispo_id.user_id1

	@api.onchange('kepada')
	def _onchange_user(self):
		for rec in self:
			emp_obj = self.env['hr.employee']
			emp_src = emp_obj.sudo().search([('job_id','=',rec.kepada.id)])
			for emp in emp_src :
				rec.user_tujuan = emp.user_id

	@api.model
	def create(self,vals):
		emp_obj = self.env['hr.employee']
		emp_src = emp_obj.sudo().search([('user_id','=', vals['user_id'])])
		emp_src2 = emp_obj.sudo().search([('job_id','=',vals['kepada'])])
		for department in emp_src :
			vals['pengirim'] = department.department_id.id
		for emp in emp_src2 :
			vals['user_tujuan'] = emp.user_id.id
		return super(surat_nota, self).create(vals)

	@api.multi
	def unlink(self):
		for unl in self :
			if unl.state == 'done' :
				raise UserError(_('Anda Tidak Bisa Menghapus Karna Status Sudah Done.'))
			return super(surat_nota, self).unlink()

	@api.depends()
	def _get_active_user(self):
		for rec in self :
			emp_obj = self.env['hr.employee']
			emp_src = emp_obj.sudo().search([('job_id','=',rec.kepada.id)])
			for emp in emp_src :
				if emp.user_id.id == self.env.user.id or self.env.user.id == 1 or rec.user_delegasi.id == self.env.user.id:
					rec.active_user = True
					self.write({'active_user':True})

	def _compute_nota_count(self):
		nota_data = self.env['disposisi.masuk'].sudo().read_group([('no_nota', 'in', self.ids)], ['no_nota'], ['no_nota'])
		result = dict((data['no_nota'][0], data['no_nota_count']) for data in nota_data)
		for nota in self:
			nota.nota_count = result.get(nota.id, 0)

	@api.multi
	def refuse(self):
		#### Search Employee ####
		emp_obj = self.env['hr.employee']
		emp_src = emp_obj.search([('user_id','=',self.user_id.id)])

		#### search email company ####
		com_obj = self.env['res.company']
		com_src = com_obj.search([],limit=1)
		for comp in com_src :
			for send in emp_src :
				body_html = '<p>Kepada '+str(self.user_id.job_id.name)+',</p> \n'+'<p> Nota Anda Di tolak dengan nomor '+str(self.name)+' Dengan Perihal '+str(self.perihal)+' Mohon Untuk Segera Di tindak lanjuti'
				mail        = self.env['mail.mail']
				notif_mail  = mail.create({'subject'    : 'Nota masuk '+str(self.perihal),
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
		self.state = "draft"

	@api.multi

	def confirm(self):
		### delegasi ###
		del_obj = self.env['delegasi']
		del_src = del_obj.sudo().search([('state','=','inprogres'),('user_id','=',self.user_tujuan.id)])
		for dele in del_src :
			if dele.surat_masuk == True :
				self.user_delegasi = dele.user_id3

		if self.name == 'New' :
			#### mengambil sequence ####
			sequence = self.env['ir.sequence'].sudo().next_by_code('surat.nota') or '/'

			#### mengambil tahun ####
			years = str(datetime.now().year)

			#### mengambil code department ####
			code = self.user_id.job_id.code_nota
			if code == False :
				code = "-"

			##### membuat penomoran #####
			self.name = "ND/"+code+"/PAS/"+sequence+"/"+years

		##### mengirim email ke email tujuan ####

		#### Search Employee ####
		emp_obj = self.env['hr.employee']
		emp_src = emp_obj.search([('job_id','=',self.kepada.id)])

		#### search email company ####
		com_obj = self.env['res.company']
		com_src = com_obj.search([],limit=1)
		for comp in com_src :
			for send in emp_src :
				body_html = '<p>Kepada '+str(self.kepada.name)+',</p> \n'+'<p> Ada Nota masuk dengan nomor '+str(self.name)+' Dengan Perihal '+str(self.perihal)+' Mohon Untuk Segera Di tindak lanjuti'
				mail        = self.env['mail.mail']
				notif_mail  = mail.create({'subject'    : 'Nota masuk '+str(self.perihal),
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
		self.state = "inprogres"

	@api.multi
	def validate(self):
		self.state = "done"

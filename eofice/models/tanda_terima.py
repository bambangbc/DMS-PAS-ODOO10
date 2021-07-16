from odoo import models, fields, api, _
from odoo.exceptions import UserError, AccessError, ValidationError
from datetime import datetime, timedelta

class TandaTerima(models.Model):
	_name = "tanda.terima"
	_description = "Tanda Terima Dokuemn"
	_order = "date desc"

	name = fields.Char('No', Required=True, index=True, copy=False, default="New")
	partner_id = fields.Many2one('res.partner', 'Pengirim')
	user_id = fields.Many2one('hr.job','Ditujukan Untuk')
	user_tujuan = fields.Many2one('res.users', string="Nama Penjabat")
	user_delegasi = fields.Many2one('res.users', string="Nama Pejabat Delegasi")
	date = fields.Datetime("Tanggal" , default=fields.Datetime.now, Required=True)
	konten = fields.Char("Konten")
	catatan = fields.Html('Catatan')
	no_dispo = fields.Many2one('disposisi.masuk','Disposisi')
	dispo_ids = fields.One2many('disposisi.masuk','no_tanda_terima',string="Disposisi")
	dispo_count = fields.Integer(compute='_compute_dispo_count',string="Disposisi")
	no_memo = fields.Many2one('surat.memorandum','Memorandum')
	memo_ids = fields.One2many('surat.memorandum','no_tanda_terima',string="Memorandum")
	memo_count = fields.Integer(compute='_compute_memo_count',string="Memorandum")
	#no_nota = fields.Many2one('surat.nota','Nota')
	nota_ids = fields.One2many('surat.nota','no_tanda_terima',string="Nota")
	nota_count = fields.Integer(compute='_compute_nota_count',string="Nota")
	state = fields.Selection(
		[('draft','Draft'),('inprogres','In Progress'),('done','Done')],'Status', indext=True, readonly=True, default='draft')
	active_user = fields.Boolean('active user', compute='_get_active_user')
	user_id1 = fields.Many2one('res.users', string='Responsible',default= lambda self: self.env.user)
	pengirim = fields.Many2one('hr.department','Pengirim',readonly=True)
	button_dispo = fields.Boolean('Disposisi', compute="_get_btnds")
	button_nota = fields.Boolean('Nota', compute="_get_btnnt")
	button_memo = fields.Boolean('Nota', compute="_get_btnmem")

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

	def _get_btnmem(self):
		grp_obj = self.env['res.groups'].search([('name','=','Memorandum Create')])
		for btnnt in grp_obj :
			for btn in btnnt.users :
				if btn.id == self.env.user.id or self.env.user.id == 1 :
					self.button_memo = True
					self.update({'button_memo':True})

	@api.onchange('user_id')
	def _onchange_user(self):
		for rec in self:
			emp_obj = self.env['hr.employee']
			emp_src = emp_obj.sudo().search([('job_id','=',rec.user_id.id)])
			for emp in emp_src :
				rec.user_tujuan = emp.user_id

	@api.model
	def create(self,vals):
		emp_obj = self.env['hr.employee']
		emp_src = emp_obj.sudo().search([('user_id','=', vals['user_id1'])])
		for department in emp_src :
			vals['pengirim'] = department.department_id.id
		return super(TandaTerima, self).create(vals)

	@api.multi
	def unlink(self):
		for unl in self :
			if unl.state == 'done' :
				raise UserError(_('Anda Tidak Bisa Menghapus Karna Status Sudah Done.'))
			return super(TandaTerima, self).unlink()

	@api.depends()
	def _get_active_user(self):
		for rec in self :
			if rec.user_tujuan.id == self.env.user.id or self.env.user.id == 1 or rec.user_delegasi.id == self.env.user.id:
				rec.active_user = True
				self.update({'active_user':True})

	def _compute_dispo_count(self):
		dispo_data = self.env['disposisi.masuk'].sudo().read_group([('no_tanda_terima', 'in', self.ids)],['no_tanda_terima'], ['no_tanda_terima'])
		result = dict((data['no_tanda_terima'][0], data['no_tanda_terima_count']) for data in dispo_data)
		for dispo in self :
			dispo.dispo_count = result.get(dispo.id, 0)

	def _compute_memo_count(self):
		memo_data = self.env['surat.memorandum'].sudo().read_group([('no_tanda_terima', 'in', self.ids)],['no_tanda_terima'], ['no_tanda_terima'])
		result = dict((data['no_tanda_terima'][0], data['no_tanda_terima_count']) for data in memo_data)
		for memo in self :
			memo.memo_count = result.get(memo.id, 0)

	def _compute_nota_count(self):
		nota_data = self.env['surat.nota'].sudo().read_group([('no_tanda_terima', 'in', self.ids)],['no_tanda_terima'], ['no_tanda_terima'])
		result = dict((data['no_tanda_terima'][0], data['no_tanda_terima_count']) for data in nota_data)
		for nota in self :
			nota.nota_count = result.get(nota.id, 0)

	@api.multi
	def confirm(self):
		### delegasi ###
		del_obj = self.env['delegasi']
		del_src = del_obj.sudo().search([('state','=','inprogres'),('user_id','=',self.user_tujuan.id)])
		for dele in del_src :
			if dele.surat_masuk == True :
				self.user_delegasi = dele.user_id3

		if self.name == 'New' :
			self.name = self.env['ir.sequence'].next_by_code('tanda.terima')

		#### Search Employee ####
		emp_obj = self.env['hr.employee']
		emp_src = emp_obj.search([('job_id','=',self.user_id.id)])

		#### search email company ####
		com_obj = self.env['res.company']
		com_src = com_obj.search([],limit=1)
		for comp in com_src :
			for send in emp_src :
				body_html = '<p>Kepada '+str(self.user_id.name)+',</p> \n'+'<p> Ada Tanda Terima Dokument dengan nomor '+str(self.name)+', Mohon Untuk Segera Di tindak lanjuti'
				mail        = self.env['mail.mail']
				notif_mail  = mail.create({'subject'    : 'Tanda Terima Dokument '+str(self.konten),
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
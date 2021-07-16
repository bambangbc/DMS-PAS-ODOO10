from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

class action(models.Model):
	_name = "action.action"
	_description ="action yang harus dilakukan oleh pihak yang didisposisikan"

	name = fields.Char('Name')
	action1 = fields.Many2many('disposisi.masuk','action_category_rel','action_id',"action_id1",string="Action")
	active = fields.Boolean('Active', default=True)

class level(models.Model):
	_name = "eof.level"

	name = fields.Char('Name')

class department(models.Model):
	_inherit = "hr.department"

	code = fields.Char('Kode Surat Masuk')
	code_sk = fields.Char('Kode Surat Keluar')
	code_memo = fields.Char('Kode Memorandum')
	code_nota = fields.Char ('Kode Nota')

class MasterJobDispo(models.Model):
	_name = "master.dispo"

	name = fields.Many2one('res.users','User')
	child_ids = fields.Many2many('hr.job',"child_ids_rel","masterdispo_id","masterjob_id", string="Ditujukan Kepada")

class MasterJob(models.Model):
	_inherit = "hr.job"

	master_dispo = fields.Many2many("master.dispo","child_ids_rel","masterjob_id","masterdispo_id",string="Master Dispo")
	code_dispo = fields.Char("Kode Disposisi")
	code_sm = fields.Char('Kode Surat Masuk')
	code_sk = fields.Char('Kode Surat Keluar')
	code_memo = fields.Char('Kode Memorandum')
	code_nota = fields.Char('Kode Nota')
	manager_id = fields.Many2one('hr.job','Manager')
	level_id = fields.Many2one('eof.level','Level')
	active = fields.Boolean('Active', default=True)
	child1_ids = fields.Many2many('hr.job',"child_ids1_rel","masterdispo1_id","masterjob1_id", string="Ditujukan Kepada")
	parent_id = fields.Many2one('hr.job', string='Parent Job', index=True)
	all_dsp = fields.Boolean('all True', default=True)
	all_dispo = fields.Boolean('Dapat Melakukan Disposisi Keseluruh Pihak')

class RecruitmentStage(models.Model):
	_name = "sk.stage"
	_description = "Stage of Disposisi"

	name = fields.Char("Nama Template", required=True, translate=True)
	department_id = fields.Many2one("hr.department","Department")
	checker1 =fields.Boolean('Checker ke 1')
	user_id1 =fields.Many2one('res.users', 'User')
	checker2 =fields.Boolean('Checker ke 2')
	user_id2 =fields.Many2one('res.users', 'User')
	checker3 =fields.Boolean('Checker ke 3')
	user_id3 =fields.Many2one('res.users', 'User')
	checker4 =fields.Boolean('Checker ke 4')
	user_id4 =fields.Many2one('res.users', 'User')
	checker5 =fields.Boolean('Checker ke 5')
	user_id5 =fields.Many2one('res.users', 'User')
	signer6 =fields.Boolean('signer')
	user_id6 =fields.Many2one('res.users', 'User')
	#### delegasi ####
	user_idd1 = fields.Many2one('res.users','user')
	user_idd2 = fields.Many2one('res.users','user')
	user_idd3 = fields.Many2one('res.users','user')
	user_idd4 = fields.Many2one('res.users','user')
	user_idd5 = fields.Many2one('res.users','user')
	user_idd6 = fields.Many2one('res.users','user')

class memoStage(models.Model):
	_name = "memo.stage"
	_description = "Stage of Memo"

	name = fields.Char("Nama Template", required=True, translate=True)
	department_id = fields.Many2one("hr.department","Department")
	checker1 =fields.Boolean('Checker ke 1')
	user_id1 =fields.Many2one('res.users', 'User')
	checker2 =fields.Boolean('Checker ke 2')
	user_id2 =fields.Many2one('res.users', 'User')
	checker3 =fields.Boolean('Checker ke 3')
	user_id3 =fields.Many2one('res.users', 'User')
	checker4 =fields.Boolean('Checker ke 4')
	user_id4 =fields.Many2one('res.users', 'User')
	checker5 =fields.Boolean('Checker ke 5')
	user_id5 =fields.Many2one('res.users', 'User')
	signer6 =fields.Boolean('signer')
	user_id6 =fields.Many2one('res.users', 'User')
	#### delegasi ####
	user_idd1 = fields.Many2one('res.users','user')
	user_idd2 = fields.Many2one('res.users','user')
	user_idd3 = fields.Many2one('res.users','user')
	user_idd4 = fields.Many2one('res.users','user')
	user_idd5 = fields.Many2one('res.users','user')
	user_idd6 = fields.Many2one('res.users','user')

class HrEmployee(models.Model):
	_inherit = "hr.employee"

	@api.model
	def create(self, vals):
		if vals.get('user_id'):
			usr_id = vals['user_id']
			dep = False
			job = False
			if vals.get('department_id', False):
				dep = vals['department_id']
			if vals.get('job_id', False):
				job = vals['job_id']
			self.env['res.partner'].sudo().search([('id', '=', usr_id)]).write({'department_id': dep,'job_id':job})
		return super(HrEmployee, self).create(vals)


	@api.multi
	def write(self, vals):
		for employee in self:
			if employee.user_id.id or vals.get('user_id'):
				usr_id = employee.user_id.partner_id.id and employee.user_id.partner_id.id or False
				dep = employee.department_id.id
				job = employee.job_id.id
				if vals.get('department_id', False) and (vals.get('user_id', False) or employee.user_id):
					if vals.get('user_id', False):
						usr_id = vals['user_id']
					dep = vals['department_id']
				if vals.get('job_id', False) and (vals.get('user_id', False) or employee.user_id):
					if vals.get('user_id', False):
						usr_id = vals['user_id']
					job = vals['job_id']
				self.env['res.partner'].sudo().search([('id', '=', usr_id)]).write({'department_id': dep,'job_id':job})
		return super(HrEmployee, self).write(vals)


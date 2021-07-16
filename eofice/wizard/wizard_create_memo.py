from odoo import api, fields, models, _
from odoo.addons import decimal_precision as dp
from odoo.exceptions import UserError


class CreateMemo(models.TransientModel):
    _name = "create.memo"
    _description = "Membuat Memorandum"

    kepada = fields.Many2many('hr.job', "memcreate_category_rel",
                              "memcreate_id", "job_id", string="Ditujukan Untuk")
    tembusan = fields.Many2many(
        'hr.job', "memcreate_category_rel2", "memcreate_id2", "job_id2", string='Tembusan')
    perihal = fields.Char('Subject')
    date = fields.Datetime('Date', default=fields.Datetime.now, required=True)
    content = fields.Html('Contents')
    template = fields.Many2one("memo.stage", "Template Stage",
                               required=True, domain="[('department_id','=',pengirim)]")
    user_id = fields.Many2one(
        'res.users', string='Responsible', default=lambda self: self.env.user)
    pengirim = fields.Many2one('hr.department', 'Pengirim')
    type_memo = fields.Selection(
        [('creatememo', 'CM'), ('replymemo', 'RM')], 'Jenis Memo')
    rahasia = fields.Selection([('rahasia','Rahasia'),('biasa','Biasa')],'Sifat Dokumen',default="biasa")

    @api.onchange('user_id')
    def _user_departmenr(self):
        memo = self.env['surat.memorandum'].sudo().browse(
            self.env.context['active_id'])
        emp_obj = self.env['hr.employee']
        emp_src = emp_obj.search([('user_id', '=', self.user_id.id)])
        for job in emp_src:
            self.user_id1 = job.job_id
            self.pengirim = job.department_id
            self.perihal = memo.perihal
            if self.type_memo == 'replymemo':
                self.kepada = memo.user_id.job_id
                self.tembusan = memo.tembusan

    @api.multi
    def create_memo(self):
        memo = self.env['surat.memorandum'].sudo().browse(
            self.env.context['active_id'])
        memo.write(
            {'validate_show': [(4, [self.env.user.job_id.id])]})
        kepada = []
        tembusan = []
        kepada_usr = []
        tembusan_usr = []
        kepada_dep = []
        tembusan_dep = []
        emp_obj = self.env['hr.employee']
        for wizard in self:
            for wz in wizard.kepada:
                kepada.append(wz.id)
                emp_src = emp_obj.sudo().search([('job_id','=',wz.id)])
                for emp in emp_src :
                    if emp.user_id.id:
                        kepada_usr.append(emp.user_id.id)
            for wz2 in wizard.tembusan:
                tembusan.append(wz2.id)
                emp_src = emp_obj.sudo().search([('job_id','=',wz2.id)])
                for emp in emp_src :
                    if emp.user_id.id:
                        tembusan_usr.append(emp.user_id.id)
            if wizard.rahasia == 'biasa' :
                for kep in self.kepada :
                    kepada_dep.append(kep.department_id.id)
                for tem in self.tembusan :
                    tembusan_dep.append(tem.department_id.id)
            if kepada == []:
                users = False
            else:
                users = [(4, [kepada])]
            if tembusan == []:
                users1 = False
            else:
                users1 = [(4, [tembusan])]
            if kepada_usr == [] :
                user2 = False
            else :
                user2 = [(4,[kepada_usr])]
            if tembusan_usr == [] :
                user3 = False
            else :
                user3 = [(4,[tembusan_usr])]
            if kepada_dep == [] :
                user4 = False
            else :
                user4 = [(4,[kepada_dep])]
            if tembusan_dep == [] :
                user5 = False
            else :
                user5 = [(4,[kepada_dep])]
        emp_src = emp_obj.sudo().search([('user_id', '=', self.env.user.id)])
        for emp in emp_src:
            pengirim = emp.department_id.id
            memo_create = self.env['surat.memorandum'].create({'kepada': users,
                                                               'tembusan': users1,
                                                               'kepada_usr': user2,
                                                               'tembusan_usr': user3,
                                                               'kepada_dep': user4,
                                                               'tembusan_dep': user5,
                                                               'perihal': wizard.perihal,
                                                               'date': wizard.date,
                                                               'content': wizard.content,
                                                               'source': memo.name,
                                                               'pengirim': wizard.pengirim.id,
                                                               'user_id': self.env.user.id,
                                                               'template': wizard.template.id,

                                                               })
        ctx = dict(self.env.context)
        return {
            'name': _('Memorandum'),
            'view_type': 'form',
            'view_mode': 'form,tree',
            'res_model': 'surat.memorandum',
            'res_id': memo_create.id,
            'type': 'ir.actions.act_window',
            'context': ctx,
        }


class JobPosition(models.Model):
    _inherit = "hr.job"
    memcreate_ids = fields.Many2many(
        'create.memo', 'memcreate_category_rel', 'job_id', 'memcreate_id', string='Memorandum')
    memcreate_ids2 = fields.Many2many(
        'create.memo', 'memcreate2_category_rel', 'job_id2', 'memcreate_id2', string='Memorandum')

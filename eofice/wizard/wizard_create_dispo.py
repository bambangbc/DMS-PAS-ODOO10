from odoo import api, fields, models, _
from odoo.exceptions import UserError


class CreateDispo(models.TransientModel):
    _name = "create.dispo"
    _description = "Membuat Disposisi"

    user_ids1 = fields.Many2many(
        'hr.job', 'discreate_category_rel', 'discreate_id', 'job_id',
        string='Ditujukan Kepada', domain="[('parent_id','child_of',[user_id1])]")
    user_ids2 = fields.Many2many(
        'hr.job', 'discreate2_category_rel', 'discreate_id2', 'job_id2',
        string='Ditujukan Kepada', domain="[('parent_id','child_of',[user_id1])]")
    user_ids3 = fields.Many2many(
        'hr.job', 'discreate3_category_rel', 'discreate_id3', 'job_id3',
        string='Ditujukan Kepada', domain="[('parent_id','child_of',[user_id1])]")
    user_ids4 = fields.Many2many(
        'hr.job', 'discreate4_category_rel', 'discreate_id4', 'job_id4',
        string='Ditujukan Kepada', domain="[('parent_id','child_of',[user_id1])]")
    action2 = fields.Many2one('action.action', 'Action')
    action3 = fields.Many2one('action.action', 'Action')
    date = fields.Date('Tanggal', default=fields.Datetime.now)
    note = fields.Html('Catatan')
    user_id1 = fields.Many2one('hr.job','Pembuat Dispo', default=lambda self: self.env.user.job_id )


    @api.multi
    def create_dispo(self):
        dispo = self.env['disposisi.masuk'].sudo().browse(
            self.env.context['active_id'])
        user_idss1 = []
        user_idss2 = []
        user_idss3 = []
        user_idss4 = []
        for wizard in self:
            for wz in wizard.user_ids1:
                user_idss1.append(wz.id)
            for wz2 in wizard.user_ids2:
                user_idss2.append(wz2.id)
            for wz3 in wizard.user_ids3:
                user_idss3.append(wz3.id)
            for wz4 in wizard.user_ids4:
                user_idss4.append(wz4.id)
            if user_idss1 == []:
                users = False
            else:
                users = [(4, [user_idss1])]
            if user_idss2 == []:
                users1 = False
            else:
                users1 = [(4, [user_idss2])]
            if user_idss3 == []:
                users2 = False
            else:
                users2 = [(4, [user_idss3])]
            if user_idss4 == []:
                users3 = False
            else:
                users3 = [(4, [user_idss4])]
        emp_obj = self.env['hr.employee']
        if self.env.user.name[:3] != 'PJS':
            emp_src = emp_obj.sudo().search(
                [('user_id', '=', self.env.user.id)])
        else:
            delegator = dispo.user_id2.id
            emp_src = emp_obj.sudo().search([('user_id', '=', delegator)])
        if not emp_src:
            raise UserError(
            	_('Pembuat Disposisi tidak bisa membuat disposisi lagi karna tidak Memiliki data employee'))
        for emp in emp_src:
            pengirim = emp.department_id.id
            dispo_create = self.env['disposisi.masuk'].create({'user_ids1': users,
                                                               'user_ids2': users1,
                                                               'user_ids4': users2,
                                                               'user_ids5': users3,
                                                               'date': wizard.date,
                                                               'note': wizard.note,
                                                               'source': dispo.name,
                                                               'pengirim': pengirim,
                                                               'user_id2': self.env.user.id,
                                                               ######### surat Masuk #########
                                                               'no_ref': dispo.no_ref.id,
                                                               'name_ref': dispo.no_ref.name,
                                                               'partner': dispo.no_ref.partner.name,
                                                               'subject': dispo.no_ref.subject,
                                                               'total_set': dispo.no_ref.total_set,
                                                               'date1': dispo.no_ref.date,
                                                               'date2': dispo.no_ref.date3,
                                                               'status_surat': dispo.status_surat,
                                                               ######### nota #############
                                                               'no_nota': dispo.no_nota.id,
                                                               'kepada_nota': dispo.kepada_nota.id,
                                                               'tembusan_nota': dispo.tembusan_nota.id,
                                                               'perihal_nota': dispo.perihal_nota,
                                                               'date_nota': dispo.date,
                                                               ######### memorandum ########
                                                               'no_memo': dispo.no_memo.id,
                                                               'kepada_memo': dispo.kepada_memo.id,
                                                               'tembusan_memo': dispo.tembusan_memo.id,
                                                               'perihal_memo': dispo.perihal_memo,
                                                               'date_memo': dispo.date_memo,

                                                               })
        ctx = dict(self.env.context)
        return {
            'name': _('Disposisi'),
            'view_type': 'form',
            'view_mode': 'form,tree',
            'res_model': 'disposisi.masuk',
            'res_id': dispo_create.id,
            'type': 'ir.actions.act_window',
            'context': ctx,
        }


class JobPosition(models.Model):
    _inherit = "hr.job"
    discreate_ids = fields.Many2many(
        'create.dispo', 'discreate_category_rel', 'job_id', 'discreate_id', string='disposisi')
    discreate_ids2 = fields.Many2many(
        'create.dispo', 'discreate2_category_rel', 'job_id2', 'discreate_id2', string='disposisi')
    discreate_ids3 = fields.Many2many(
        'create.dispo', 'discreate3_category_rel', 'job_id3', 'discreate_id3', string='disposisi')
    discreate_ids4 = fields.Many2many(
        'create.dispo', 'discreate4_category_rel', 'job_id4', 'discreate_id4', string='disposisi')

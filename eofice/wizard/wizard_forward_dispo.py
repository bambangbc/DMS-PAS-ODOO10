from odoo import api, fields, models, _
from odoo.addons import decimal_precision as dp
from odoo.exceptions import UserError


class CreateDispo(models.TransientModel):
    _name = "forward.dispo"
    _description = "forward disposisi"

    note = fields.Html('catatan', required=True)
    forward_to = fields.Many2one('hr.job', 'Forward Kepada',  domain="[('parent_id','child_of',[user_id1])]")
    user_id1 = fields.Many2one('hr.job','Pembuat Dispo', default=lambda self: self.env.user.job_id )

    @api.multi
    def create_forward(self):
        sm = self.env['disposisi.masuk'].sudo().browse(
            self.env.context['active_id'])
        file_create = sm.write(
            {'note_forward': self.note, 'forward_to': self.forward_to.id})

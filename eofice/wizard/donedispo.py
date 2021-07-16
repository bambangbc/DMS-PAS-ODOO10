from openerp import models, fields, api
from openerp.exceptions import except_orm


class purchaseConfirmWizard(models.TransientModel):
    _name = 'done.disposisi'

    warning = fields.Char(readonly=True)

    @api.multi
    def confirm(self):
        sk = self.env['disposisi.masuk'].browse(self.env.context['active_id'])
        sk_create = sk.update({'state': 'done'})

    @api.model
    def default_get(self, fields_list):
        warning = 'Apakah Anda Yakin Akan melanjutanya (cek apakah Orang yang anda tuju sudah melakukan Action)'
        return {'warning': warning}

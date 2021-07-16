from odoo import api, fields, models, _
from odoo.addons import decimal_precision as dp
from odoo.exceptions import UserError


class CreateDispo(models.TransientModel):
    _name = "create.file.sm"
    _description = "membuat file surat masuk"

    directory = fields.Many2one(
        'muk_dms.directory',
        string="Directory",
        ondelete='restrict',
        auto_join=True,
        required=True)

    @api.multi
    def create_file(self):
        sm = self.env['ir.attachment'].sudo().browse(
            self.env.context['active_id'])
        file_create = self.env['muk_dms.file'].create({'name': sm.name,
                                                       'content': sm.datas,
                                                       'directory': self.directory.id,

                                                       })

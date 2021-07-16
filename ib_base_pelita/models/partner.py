# -*- coding: utf-8 -*-
# © 2017 Ibrohim Binladin | ibradiiin@gmail.com | +62-838-7190-9782
from odoo import api, fields, models, _
from odoo.osv.expression import get_unaccent_wrapper
import logging
_logger = logging.getLogger(__name__)


class Partners(models.Model):
    _inherit = 'res.partner'

    code = fields.Char(size=64, index=True)
    division_id = fields.Many2one('sale.division', 'Division', ondelete='set null', index=True)
    type = fields.Selection(
        [('contact', 'Contact'),
         ('invoice', 'Invoice address [Bill To]'),
         ('delivery', 'Shipping address [Ship To]'),
         ('other', 'Other address'),
         ('payer', 'Payer address [Payer]')], string='Address Type',
        default='contact',
        help="Used to select automatically the right address according to the context in sales and purchases documents.\nThe parent of this address is buyer or seller's address [Sold To]")
    state_name = fields.Char(related='state_id.name', string="State Name", readonly=True)
    country_name = fields.Char(related='country_id.name', string="Country Name", readonly=True)

    _sql_constraints = [
            ('partner_code_company_uniq', 'unique (code,company_id)', 'The code of the partner must be unique per company !')
        ]

    @api.multi
    def name_get(self):
        res = []
        for partner in self:
            name = partner.name or ''
            if partner.code:
                name = "[%s] %s" % (partner.code, name)
            if partner.company_name or partner.parent_id:
                if not name and partner.type in ['invoice', 'delivery', 'other']:
                    name = dict(self.fields_get(['type'])['type']['selection'])[partner.type]
                if not partner.is_company:
                    name = "%s, %s" % (partner.commercial_company_name or partner.parent_id.name, name)
            if self._context.get('show_address_only'):
                name = partner._display_address(without_company=True)
            if self._context.get('show_address'):
                name = name + "\n" + partner._display_address(without_company=True)
            name = name.replace('\n\n', '\n')
            name = name.replace('\n\n', '\n')
            if self._context.get('show_email') and partner.email:
                name = "%s <%s>" % (name, partner.email)
            if self._context.get('html_format'):
                name = name.replace('\n', '<br/>')
            res.append((partner.id, name))
        return res

    @api.multi
    @api.onchange('vat')
    def onchange_vat_partner(self):
        if not self.vat:
            return {}
        vals = {}
        warning = {}
        result = {}
        if len(str(self.vat)) == 15:
            try:
                int(self.vat[:15])
                npwp_partner = self.vat[:2] + '.' + self.vat[2:5] + '.' + self.vat[5:8] + '.' + \
                               self.vat[8:9] + '-' + self.vat[9:12] + '.' + self.vat[12:15]
                vals['vat'] = npwp_partner
            except:
                warning['title'] = _("Incorrect NPWP number format!")
                warning['message'] = _("The format input of the NPWP number must be of integer type (15 digits) "
                                       "like this '99 .999.999.9-999.999 ', and entered without punctuation")
                result = {'warning': warning}
        else:
            warning['title'] = _("Incorrect NPWP number format!")
            warning['message'] = _("The format input of the NPWP number must be of integer type (15 digits) "
                                   "like this '99 .999.999.9-999.999 ', and entered without punctuation")
            result = {'warning': warning}

        self.update(vals)
        return result



class UserManagement(models.Model):
    _inherit = 'res.users'

    division_id = fields.Many2one('sale.division', related='partner_id.division_id',
                                  string='Division', store=False, readonly=True, copy=False)






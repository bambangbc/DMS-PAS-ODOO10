# -*- coding: utf-8 -*-
# © 2017 Ibrohim Binladin | ibradiiin@gmail.com | +62-838-7190-9782
from odoo import api, fields, models, _
import logging
_logger = logging.getLogger(__name__)


class PelitaBusinessUnit(models.Model):
    _name = 'pelita.business.unit'
    _description = "Board of Director Subordination"

    name = fields.Char(string='BOD Subordination', required=True)
    code = fields.Char(string='Code')
    active = fields.Boolean(string='Status', default=True,
                            help="Set active to false to hide the tax without removing it.")
    product_categ_id = fields.Many2one('product.category', 'Product Category', required=True, default=1)
    note = fields.Text(string='Description')
    partner_id = fields.Many2one('res.partner', 'Partner', copy=False)


# class ResUsers(models.Model):
#     _inherit = 'res.users'
#
#     business_unit_ids = fields.Many2many('pelita.business.unit', 'res_users_business_unit_rel', 'user_id',
#                                      'business_unit_id', string='Business Unit', copy=False)
#     main_business_unit = fields.Many2one('pelita.business.unit', 'Main Business Unit')
#     division_id = fields.Many2one('sale.division', 'Division')


class ProductTemplate(models.Model):
    _inherit = "product.template"

    def _get_default_category_id(self):
        if self._context.get('categ_id') or self._context.get('default_categ_id'):
            return self._context.get('categ_id') or self._context.get('default_categ_id')
        category = self.env.ref('product.product_category_all', raise_if_not_found=False)
        result = category and category.type == 'normal' and category.id or False
        unit_bisnis = self.env['res.users'].browse(self._uid).main_business_unit
        if unit_bisnis:
            result = unit_bisnis.product_categ_id and unit_bisnis.product_categ_id.id
        return result

    categ_id = fields.Many2one(
        'product.category', 'Internal Category',
        change_default=True, default=_get_default_category_id, domain="[('type','=','normal')]",
        required=True, help="Select category for the current product")



# class Partners(models.Model):
#     _inherit = "res.partner"
#
#     employee_ok = fields.Boolean(string='Is a Employee', default=False,
#                               help="Check this box if this contact is a employee.")

    # @api.model
    # def create(self, vals):
    #     partner = super(Partners, self).create(vals)
    #     context = dict(self._context or {})
    #     if context.get('active_model') == 'res.users'
    #     active_ids = context.get('active_ids')
    #     return partner
    #
    #     if context['active_model'] == 'account.invoice':
    #         ids = context['active_ids']

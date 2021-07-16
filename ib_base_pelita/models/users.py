# -*- coding: utf-8 -*-
# © 2017 Ibrohim Binladin | ibradiiin@gmail.com | +62-838-7190-9782
from odoo import api, fields, models, _
from odoo.osv import expression
from odoo.exceptions import ValidationError
import logging
_logger = logging.getLogger(__name__)


class SaleDivision(models.Model):
    _name = 'sale.division'

    name = fields.Char(string='Division', required=True)
    code = fields.Char(string='Code')
    active = fields.Boolean(string='Status', default=True,
                            help="Set active to false to hide the tax without removing it.")

    @api.model
    def name_search(self, name, args=None, operator='ilike', limit=100):
        args = args or []
        domain = []
        if name:
            domain = ['|', ('code', '=ilike', name + '%'), ('name', operator, '%' + name + '%')]
            if operator in expression.NEGATIVE_TERM_OPERATORS:
                domain = ['&', '!'] + domain[1:]
        divisi = self.search(domain + args, limit=limit)
        return divisi.name_get()

    @api.multi
    @api.depends('name', 'code')
    def name_get(self):
        result = []
        for divisi in self:
            name = "%s" % (str(divisi.name) or _(''))
            if divisi.code:
                name = "%s" % (_("[" + str(divisi.code) + "] " + str(divisi.name)) or _(''))
            result.append((divisi.id, name))
        return result


class UserManagement(models.Model):
    _inherit = 'res.users'

    business_unit_ids = fields.Many2many('pelita.business.unit', 'res_users_business_unit_rel', 'user_id', 
                                         'business_unit_id', string='Business Unit', copy=False)
    main_business_unit = fields.Many2one('pelita.business.unit', 'Main Business Unit')

    @api.multi
    @api.constrains('main_business_unit', 'business_unit_ids')
    def _check_business_unit(self):
        if any(user.business_unit_ids and user.main_business_unit not in user.business_unit_ids for user in self):
            raise ValidationError(_("The chosen business unit is not in the allowed business units for this user.\n"
                                    "'Main Business Unit' must exist in the 'Allowed Business Unit' group."))

    @api.multi
    def write(self, values):
        business_unit_obj = self.env['pelita.business.unit']
        res = super(UserManagement, self).write(values)
        for user in self.with_context(self._context or {}):
            main_business_unit_id = user.main_business_unit and user.main_business_unit.id
            if values.get('main_business_unit', False):
                main_business_unit_id = values['main_business_unit']
            if main_business_unit_id:
                main_bu_code = business_unit_obj.browse(main_business_unit_id).code
                if main_bu_code and main_bu_code!='':
                    groups_bu = self.env['res.groups'].sudo().search([
                        ('name', 'like', '%'+main_bu_code+'%')], limit=1)
                    if groups_bu:
                        vals = {'groups_id': [(4, groups_bu.id)]}
                        super(UserManagement, self).write(vals)
                if user.business_unit_ids:
                    allowed_bu_ids = [bu.id for bu in user.business_unit_ids if bu.id != main_business_unit_id]
                    if allowed_bu_ids:
                        for allow_bu_id in allowed_bu_ids:
                            bu_code = business_unit_obj.browse(allow_bu_id).code
                            if bu_code and bu_code != '':
                                group_bu_ids = self.env['res.groups'].sudo().search([
                                    ('name', 'like', '%' + bu_code + '%')], limit=1)
                                if group_bu_ids:
                                    val = {'groups_id': [(4, group_bu_ids.id)]}
                                    super(UserManagement, self).write(val)
            elif user.business_unit_ids or values.get('business_unit_ids', False):
                business_units = values['business_unit_ids'] if values.get('business_unit_ids') else user.business_unit_ids 
                if business_units:
                    for b_unit in business_units:
                        business_unit_code = business_unit_obj.browse(b_unit).code
                        if business_unit_code and business_unit_code != '':
                            group_ids = self.env['res.groups'].sudo().search([
                                    ('name', 'like', '%' + business_unit_code + '%')], limit=1)
                            if group_ids:
                                vals1 = {'groups_id': [(4, group_ids.id)]}
                                super(UserManagement, self).write(vals1)
        return res
    
    # @api.model
    # def create(self, values):
    #     if 'groups_id' in values:
    #         user = self.new(values)
    #         gs = user.groups_id | user.groups_id.mapped('trans_implied_ids')
    #         values['groups_id'] = type(self).groups_id.convert_to_write(gs, user.groups_id)
    #     return super(UserManagement, self).create(values)


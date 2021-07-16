# -*- coding: utf-8 -*-
# © 2017 Ibrohim Binladin | ibradiiin@gmail.com | +62-838-7190-9782
import datetime
from odoo import api, fields, models, _
import odoo.addons.decimal_precision as dp
import logging
_logger = logging.getLogger(__name__)


class AccountAnalyticAccount(models.Model):
    _inherit = 'account.analytic.account'
    _description = 'Analytic Account'
    _order = "priority desc, sequence, date_start, code, name, id"
    
    def _get_next_date(self):
        return (datetime.date.today() + datetime.timedelta(days=+1)).strftime('%Y-%m-%d')

    name = fields.Char(string='Analytic Account', index=True, required=True, track_visibility='onchange')
    code = fields.Char(string='Reference', index=True, track_visibility='onchange')
    active = fields.Boolean('Active', default=True,
            help="If the active field is set to False, it will allow you to hide the account without removing it.")
    description = fields.Text(translate=True)
    # npwp = fields.Char(related='partner_id.npwp', string='NPWP', store=False, copy=False)
    date_start = fields.Datetime(string='Start Date', default=fields.Datetime.now())
    date_end = fields.Datetime(string='Expired Date', index=True, track_visibility='onchange')
    partner_id = fields.Many2one('res.partner', string='Customer', auto_join=True, track_visibility='onchange')
    order_id = fields.Many2one('sale.order', string='SO Number', readonly=True)
    order_line_ids = fields.One2many(related='order_id.order_line', store=False, readonly=True)
    amount_total = fields.Monetary(related='order_id.amount_total', string='Total Contract Value', store=True,
                                   readonly=True, default=0.0)
    order_ref = fields.Char(related='order_id.client_order_ref', string='PO No', readonly=True)
    color = fields.Integer(string='Color Index')
    priority = fields.Selection([('0','Normal'),('1','High')], default='0', index=True)
    #readonly=True, states={'draft': [('readonly', False)]}
    sequence = fields.Integer(string='Sequence', index=True, default=10,
        help="Gives the sequence order when displaying a list of tasks.")
    recurring_next_date = fields.Date( #fields.Date.context_today,
        default=_get_next_date, 
        copy=False,
        string='Date of Next Invoice',
    )

    # @api.model
    # def create(self, vals):
    #     context = dict(self.env.context, mail_create_nolog=True)
    #     analytic_account = super(AccountAnalyticAccount, self).create(vals)
    #     if context.get('source') and context['source']=='sale.order':
    #         #vals['use_tasks'] = True
    #         if context.get('validity_date') and context['validity_date']:
    #             vals['date'] = context['validity_date']
    #     # analytic_account.project_create(vals)
    #     return analytic_account
    
    
# class ProjectProjects(models.Model):
#     _inherit = "project.project"
#     _description = "Project"
# 
#     @api.model
#     def create(self, vals):
#         new_project = super(ProjectProjects, self).create(vals)
#         if vals.get('date_start', ''):
#             if vals.get('analytic_account_id', False):
#                 self.env['account.analytic.account'].browse(vals['analytic_account_id']).write(
#                     {'date_start': vals['date_start'], 'date_end': vals['date'] if vals.get('date') else ''})
#             elif new_project.analytic_account_id:
#                 new_project.analytic_account_id.write(
#                     {'date_start': vals['date_start'], 'date_end': vals['date'] if vals.get('date') else ''})            
#         return new_project
    
    
    







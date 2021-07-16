# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.osv import expression

import logging
_logger = logging.getLogger(__name__)


class partner_pelita(models.Model):
    _inherit = 'res.partner'

    dist_channel_id = fields.Many2one('sale.distribution.channel', 'Distribution Channel',
                                      ondelete='set null', index=True)
    sale_office_id = fields.Many2one('sale.sales.office', 'Sales Office', 
                                     ondelete='set null', index=True)
    # currency_part_id = fields.Many2one('res.currency', 'Currency', ondelete='set null', index=True)
    foreign_curr_id = fields.Many2one('res.currency', 'Foreign Currency', 
                                      ondelete='set null', index=True)
    # term_payment_id = fields.Many2one('account.payment.term', 'Terms of Payment', 
    #                                   ondelete='set null', index=True)
    # sale_incoterm_id = fields.Many2one('stock.incoterms', 'Incoterm', ondelete='set null', index=True)
    sales_area_id = fields.Many2one('sale.sales.area', 'Sales Area', ondelete='set null', index=True)
    stp_number = fields.Char(string="No.Sold to Party")
    tax_classification_ids = fields.Many2many('account.tax', 'res_partner_tax_default_rel',
                               'partner_id', 'tax_id', string='Default Taxes', help="Tax classification for customs")
    industry_id = fields.Many2one('res.partner.industries', 'Industry', ondelete='set null', help="Types of Industries")
    transport_system = fields.Selection([('own', 'Own Transport'),('services', 'Transportation Services')], 
                                        string="Transport System")
    payment_system = fields.Selection([('cash', 'Cash'), ('prepayment', 'Prepayment'),('credit', 'Credit')],
                                   string="Payment System")
    stp_product_type = fields.Many2one('product.category', 'Types of products', ondelete='set null',
                                       domain=[('name', 'not in', ('PAS','PTC','PAF','PCA'))])
    stp_delivery_plant = fields.Char("Delivery Plant")
    ### Contract ###
    stp_contract = fields.Selection([('yes', 'Yes'), ('no', 'No')], string="Bound by Contract")
    start_date_contract = fields.Date(index=True, string="Start Date", help="Term of the contract")
    end_date_contract = fields.Date(index=True, string="End Date", help="Term of the contract")
    stp_price_enforcement = fields.Selection([('payment', 'Payment'), ('submission', 'Submission')], string="Price Enforcement")
    ### Customer Classification ###
    stp_company_type = fields.Many2one('res.company.type', 'Type of Company', ondelete='set null')
    reconciliation_account_id = fields.Many2one('account.account', string='Reconciliation Account')
    ### Pricing / Statistic ###
    # foreign_currency_id = fields.Many2one('res.currency', string='Foreign Currency')
    stp_price_group = fields.Char("Price Group")
    stp_pricelist_type = fields.Char("Price List Type")
    ### Delivery And Payment Terms ###
    # soldtp_termpayment = fields.Char("Terms of Payment", size=4)
    stp_invoicing_list_dates = fields.Date(index=True, string="Invoicing List Dates")
    stp_incoterm = fields.Selection([
        ('EXW', 'EX WORKS'), ('FCA', 'FREE CARRIER'), ('FAS', 'FREE ALONGSIDE SHIP'), ('FOB', 'FREE ON BOARD'),
        ('FRC', 'FRANCO'), ('CFR', 'COST AND FREIGHT'), ('CIF', 'COST, INSURANCE AND FREIGHT'), ('CPT', 'CARRIAGE PAID TO'),
        ('DAT', 'DELIVERED AT TERMINAL'), ('DDP', 'DELIVERED DUTY PAID')
    ], string="Incoterm")
    
    
    
    
class TypeCompany(models.Model):
    _name = "res.company.type"
    _description = 'The type of company'

    name = fields.Char(string='Type of Company', required=True)
    active = fields.Boolean(string='Status', default=True,
                            help="Set active to false to hide the tax without removing it.")
    
    
    
    
class IndustryPartner(models.Model):
    _name = 'res.partner.industries'
    _description = 'types of partner industries'

    name = fields.Char(string='Industry', required=True)
    code = fields.Char(string='Industry Code')
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
        part_industry = self.search(domain + args, limit=limit)
        return part_industry.name_get()

    @api.multi
    @api.depends('name', 'code')
    def name_get(self):
        result = []
        for pi in self:
            name = "%s" % (str(pi.name) or _(''))
            if pi.code:
                name = "%s" % (_("[" + str(pi.code) + "] " + str(pi.name)) or _(''))
            result.append((pi.id, name))
        return result
    
    
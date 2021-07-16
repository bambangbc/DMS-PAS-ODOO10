# -*- coding: utf-8 -*-
# © 2017 Ibrohim Binladin | ibradiiin@gmail.com | +62-838-7190-9782 | http://ibrohimbinladin.wordpress.com
from odoo import api, fields, models, _
import odoo.addons.decimal_precision as dp


class AccountInvoiceLine(models.Model):
    _inherit = "account.invoice.line"

    @api.one
    @api.depends('invoice_line_tax_ids.name','invoice_line_tax_ids.amount')
    def _generate_taxes(self):
        tax_desc = []
        tax_amount = 0.0
        if self.invoice_line_tax_ids:
            for ilt in self.invoice_line_tax_ids:
                tax_amount += ilt.amount
                if ilt.name:
                    tax_desc.append(ilt.name)
        self.tax_description = '%s' % (', '.join(tax_desc) or _(''))
        self.tax_subtotal = tax_amount

    uom = fields.Char(related='uom_id.name', string="UoM", readonly=True)  #store=True
    tax_description = fields.Text(string='Tax Descriptions', compute='_generate_taxes', copy=False)
    tax_subtotal = fields.Float(string='Tax per Line', compute='_generate_taxes',
                                copy=False, digits=dp.get_precision('Product Price'))




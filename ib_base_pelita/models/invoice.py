# -*- coding: utf-8 -*-
# © 2017 Ibrohim Binladin | ibradiiin@gmail.com | +62-838-7190-9782
import math
from odoo import api, fields, models, _
from . import amount_to_text_en
from . import amount_to_text_id
import odoo.addons.decimal_precision as dp
from odoo.exceptions import UserError, RedirectWarning, ValidationError
import logging
_logger = logging.getLogger(__name__)


class AccountInvoice(models.Model):
    _inherit = "account.invoice"

    @api.one
    @api.depends('invoice_line_ids.price_subtotal', 'tax_line_ids.amount', 'currency_id', 'company_id', 'date_invoice', 'type')
    def _compute_amount(self):
        self.amount_untaxed = sum(line.price_subtotal for line in self.invoice_line_ids)
        self.amount_tax = sum(line.amount for line in self.tax_line_ids)
        self.amount_total = self.amount_untaxed + self.amount_tax
        amount_total_company_signed = self.amount_total
        amount_untaxed_signed = self.amount_untaxed
        if self.currency_id and self.company_id and self.currency_id != self.company_id.currency_id:
            currency_id = self.currency_id.with_context(date=self.date_invoice)
            amount_total_company_signed = currency_id.compute(self.amount_total, self.company_id.currency_id)
            amount_untaxed_signed = currency_id.compute(self.amount_untaxed, self.company_id.currency_id)
        sign = self.type in ['in_refund', 'out_refund'] and -1 or 1
        self.amount_total_company_signed = amount_total_company_signed * sign
        self.amount_total_signed = self.amount_total * sign
        self.amount_untaxed_signed = amount_untaxed_signed * sign
        if self.currency_id:
            text_amount = amount_to_text_id.amount_to_text(math.ceil(self.amount_total), 'id', self.currency_id.name)
            if self.currency_id.name == "USD" or self.currency_id.symbol == "$":
                text_amount = amount_to_text_en.amount_to_text(math.ceil(self.amount_total), 'en', self.currency_id.name)
            self.text_amount = text_amount

    #text_amount = fields.Text(string="Spelled Out")
    approved_by = fields.Many2one('res.users', string='Approved by')
    text_amount = fields.Text(string='Spelled Out', store=True, readonly=True, compute='_compute_amount')

    @api.multi
    def button_dummy(self):
        return True

    @api.model
    def create(self, vals):
        invoice = super(AccountInvoice, self).create(vals)
        #total = sum([line.price_subtotal for line in invoice.invoice_line_ids])
        if invoice.amount_total or invoice.amount_total > 0.0:
            text_amount = amount_to_text_id.amount_to_text(invoice.amount_total, 'id', invoice.currency_id.name)
            if invoice.currency_id.name == "USD":
                text_amount = amount_to_text_en.amount_to_text(invoice.amount_total, 'en', invoice.currency_id.name)
            invoice.write({'text_amount': text_amount})

        return invoice

    @api.multi
    def action_invoice_paid(self):
        # lots of duplicate calls to action_invoice_paid, so we remove those already paid
        to_pay_invoices = self.filtered(lambda inv: inv.state != 'paid')
        if to_pay_invoices.filtered(lambda inv: inv.state != 'open'):
            raise UserError(_('Invoice must be validated in order to set it to register payment.'))
        if to_pay_invoices.filtered(lambda inv: not inv.reconciled):
            raise UserError(_('You cannot pay an invoice which is partially paid. You need to reconcile payment entries first.'))
        for invoice in self:
            for line in invoice.invoice_line_ids:
                if line.product_id.product_tmpl_id.log_availability:
                    for log in line.product_id.product_tmpl_id.log_availability:
                        if log.state == 'active':
                            log.action_done()
        return to_pay_invoices.write({'state': 'paid'})



class AccountInvoiceLine(models.Model):
    _inherit = "account.invoice.line"

    @api.one
    @api.depends('price_subtotal', 'invoice_line_tax_ids.name', 'invoice_line_tax_ids.amount')
    def _generate_taxes(self):
        tax_desc = []
        tax_amount = 0.0
        if self.invoice_line_tax_ids:
            for ilt in self.invoice_line_tax_ids:
                tax_amount += (ilt.amount/100.0) * self.price_subtotal
                if ilt.name:
                    tax_desc.append(ilt.name)
        self.tax_description = '%s' % (', '.join(tax_desc) or _(''))
        self.tax_subtotal = tax_amount

    uom = fields.Char(related='uom_id.name', string="UoM", readonly=True)  # store=True
    tax_description = fields.Text(string='Tax Descriptions', compute='_generate_taxes', copy=False)
    tax_subtotal = fields.Float(string='Tax per Line', compute='_generate_taxes',
                                    copy=False, digits=dp.get_precision('Product Price'))



class ResPartnerBank(models.Model):
    _inherit = "res.partner.bank"

    bank_street = fields.Char(related='bank_id.street', string="Bank Street", readonly=True)
    bank_city = fields.Char(related='bank_id.city', string="Bank City", readonly=True)
    currency_bank = fields.Char(related='currency_id.name', string="Currency Bank", readonly=True)


#     sales_channel_id = fields.Many2one(comodel_name='res.partner',
#         string='Sales channel', ondelete='set null',
#         domain="[('category_id', 'ilike', 'sales channel')]", index=True, )
#
#     @api.multi
#     def onchange_partner_id(self, type, partner_id, date_invoice=False, payment_term=False,
#             partner_bank_id=False, company_id=False):
#         res = super(AccountInvoice, self).onchange_partner_id(
#             type, partner_id, date_invoice=date_invoice,
#             payment_term=payment_term, partner_bank_id=partner_bank_id,
#             company_id=company_id)
#         if partner_id:
#             partner = self.env['res.partner'].browse(partner_id)
#             res['value'].update({
#                 'sales_channel_id': partner.sales_channel_id,
#             })
#         return res
#
#     @api.model
#     def _prepare_refund(self, invoice, date=None, period_id=None, description=None,
#             journal_id=None):
#         values = super(AccountInvoice, self)._prepare_refund(
#             invoice, date=date, period_id=period_id,
#             description=description, journal_id=journal_id)
#         values.update({
#             'sales_channel_id': invoice.sales_channel_id.id,
#         })
#         return values
#
#
#
# class AccountInvoiceReport(models.Model):
#     _inherit = "account.invoice.report"
#
#     sales_channel_id = fields.Many2one('res.partner', string="Sales channel", ondelete='set null', required=False)
#
#     def _select(self):
#         select_str = super(AccountInvoiceReport, self)._select()
#         select_str += """,
#                     sub.sales_channel_id as sales_channel_id
#         """
#         return select_str
#
#     def _sub_select(self):
#         select_str = super(AccountInvoiceReport, self)._sub_select()
#         select_str += """,
#                     ai.sales_channel_id as sales_channel_id
#         """
#         return select_str
#
#     def _group_by(self):
#         group_by_str = super(AccountInvoiceReport, self)._group_by()
#         group_by_str += """,
#                     ai.sales_channel_id
#         """
#         return group_by_str


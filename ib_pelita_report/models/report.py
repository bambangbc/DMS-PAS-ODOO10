# -*- coding: utf-8 -*-
# © 2017 Ibrohim Binladin | ibradiiin@gmail.com | +62-838-7190-9782 | http://ibrohimbinladin.wordpress.com
##########################################################################################################
from datetime import datetime
from odoo import api, fields, models, _
from odoo.exceptions import UserError
import odoo.addons.jasper_reports.jasper_report as jr
import odoo.addons.decimal_precision as dp


class SaleOrder(models.Model):
    _inherit = "sale.order"

    @api.multi
    def print_data_order(self):
        self.filtered(lambda s: s.state == 'draft').write({'state': 'sent'})
        datas = {
            'ids': self.ids,
            'model': 'sale.order',
            'form': self.read(self.ids[0]),
        }
        return {
            'type': 'ir.actions.report.xml',
            'report_name': 'sales.order.xls',
            'datas': datas,
            'nodestroy': True
        }


# def sales_reports( cr, uid, ids, data, context ):
#     return {
#         'parameters': {
#         },
#     }
# jasper_reports.ReportJasper(
#     'report.sales.order.xls',
#     'sale.order',
#     parser=sales_reports
#     )


class AccountInvoice(models.Model):
    _inherit = "account.invoice"

    @api.multi
    def print_customer_invoice(self):
        report_name = ''
        if self._context.get('report_name'):
            report_name = self._context['report_name']
        #invoice = self.browse(self.ids[0])
        invoice_id = 0
        inv_number = str('')
        # raise UserError(_('INV_IDS: %s, INV_ID: %s, INV_NO: %s') % (self.ids, int(invoice.id) or self.ids[0], '%' + str(invoice.number) +'%' or '%' + str(invoice.internal_number) +'%'))
        for invoice in self:
            invoice_id = int(invoice.id) or self.ids[0]
            inv_number = '%' + str(invoice.number) +'%' or '%' + str(invoice.internal_number) +'%'
        datas = {
            'ids': self.ids,
            'invoice_id': invoice_id,
            'inv_number': inv_number,
            'model': 'account.invoice',
            'form': self.read(self.ids), #[0]
        }
        return {
            'type': 'ir.actions.report.xml',
            'report_name': report_name,
            'datas': datas,
            'nodestroy': True
        }

def customer_invoice_report(cr, uid, ids, data, context):
    return {
        'parameters': {
            'invoice_id': data['invoice_id'],
            'inv_number': data['inv_number'],
        },
    }
jr.ReportJasper(
    'report.patc.cust.invoice.pdf',
    'account.invoice',
    parser=customer_invoice_report
    )
jr.ReportJasper(
    'report.paf.cust.invoice.pdf',
    'account.invoice',
    parser=customer_invoice_report
    )
jr.ReportJasper(
    'report.pas.cust.invoice.pdf',
    'account.invoice',
    parser=customer_invoice_report
    )



# class AccountInvoiceLine(models.Model):
#     _inherit = "account.invoice.line"
#
#     @api.one
#     @api.depends('invoice_line_tax_ids.name','invoice_line_tax_ids.amount')
#     def _generate_taxes(self):
#         tax_desc = []
#         tax_amount = 0.0
#         if self.invoice_line_tax_ids:
#             for ilt in self.invoice_line_tax_ids:
#                 tax_amount += ilt.amount
#                 if ilt.name:
#                     tax_desc.append(ilt.name)
#         self.tax_description = '%s' % (', '.join(tax_desc) or _(''))
#         self.tax_subtotal = tax_amount
#
#     uom = fields.Char(related='uom_id.name', string="UoM", readonly=True)  #store=True
#     tax_description = fields.Text(string='Tax Descriptions', compute='_generate_taxes', copy=False)
#     tax_subtotal = fields.Float(string='Tax per Line', compute='_generate_taxes',
#                                 copy=False, digits=dp.get_precision('Product Price'))



# class FlightMaintenanceLogRotary(models.Model):
#     _inherit = "maintenance.log.rotary"
#
#     @api.multi
#     def print_fml_rotary(self):
#         datas = {
#             'ids': self._ids,
#             'model': 'maintenance.log.rotary',
#             'form': self.read(self._ids[0]),
#         }
#         return {
#             'type': 'ir.actions.report.xml',
#             'report_name': 'fml.rotary.pdf',
#             'datas': datas,
#             'nodestroy': True
#         }


# def maintenance_log_rotary( cr, uid, ids, data, context ):
#     return {
#         'parameters': {
#         },
#     }
# jr.ReportJasper(
#     'report.fml.rotary.pdf',
#     'maintenance.log.rotary',
#     parser=maintenance_log_rotary
#     )

# class FlightMaintenanceLogFixWing(models.Model):
#     _inherit = "maintenance.log.fixwing"
#
#     @api.multi
#     def print_fml_fixwing(self):
#         datas = {
#             'ids': self._ids,
#             'model': 'maintenance.log.fixwing',
#             'form': self.read(self._ids[0]),
#         }
#         return {
#             'type': 'ir.actions.report.xml',
#             'report_name': 'fml.fixwing.pdf',
#             'datas': datas,
#             'nodestroy': True
#         }


# def maintenance_log_fixwing( cr, uid, ids, data, context ):
#     return {
#         'parameters': {
#         },
#     }
# jr.ReportJasper(
#     'report.fml.fixwing.pdf',
#     'maintenance.log.fixwing',
#     parser=maintenance_log_fixwing
#     )

# def purchase_reports( cr, uid, ids, data, context ):
#     return {
#         'parameters': {
#             'title': "Purchase Order  No.",
# 			'print_datetime': str(datetime(x.year, x.month, x.day, x.hour, x.minute, x.second).strftime("%d-%m-%Y %H:%M:%S")),
#         },
#     }
# jr.ReportJasper(
#     'report.purchase.order.pdf',
#     'purchase.order',
#     parser=purchase_reports
#     )

# class purchase_order(osv.osv):
#     _inherit = "purchase.order"
#
#     def print_purchase_order(self, cr, uid, ids, context=None):
#         assert len(ids) == 1, 'This option should only be used for a single id at a time.'
#         context = context or {}
#         wf_service = netsvc.LocalService("workflow")
#         wf_service.trg_validate(uid, 'purchase.order', ids[0], 'send_rfq', cr)
#
#         datas = {
#             'ids': ids,
#             'model': 'purchase.order',
#             'form': self.read(cr, uid, ids[0], context=context),
#         }
#         return {
#             'type': 'ir.actions.report.xml',
#             'report_name': 'purchase.order.pdf',
#             'datas': datas,
#             'nodestroy': True
#         }


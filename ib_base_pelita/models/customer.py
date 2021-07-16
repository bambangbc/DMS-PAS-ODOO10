# -*- coding: utf-8 -*-
# © 2017 Ibrohim Binladin | ibradiiin@gmail.com | +62-838-7190-9782
from odoo import api, fields, models, _

import logging
_logger = logging.getLogger(__name__)


class PartnerCustomer(models.Model):
    _inherit = "res.partner"
    _name = "res.partner"

    dist_channel_id = fields.Many2one('sale.distribution.channel', 'Distribution Channel', 
                                      ondelete='set null', index=True)
    # sale_office_id = fields.Many2one('sale.sales.office', 'Sales Office', ondelete='set null', index=True)
    # currency_part_id = fields.Many2one('res.currency', 'Currency', ondelete='set null', index=True)
    # foreign_curr_id = fields.Many2one('res.currency', 'Foreign Currency', ondelete='set null', index=True)
    # term_payment_id = fields.Many2one('account.payment.term', 'Terms of Payment', ondelete='set null', index=True)
    # sale_incoterm_id = fields.Many2one('stock.incoterms', 'Incoterm', ondelete='set null', index=True)




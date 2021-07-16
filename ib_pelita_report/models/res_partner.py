# -*- coding: utf-8 -*-
# © 2017 Ibrohim Binladin | ibradiiin@gmail.com | +62-838-7190-9782 | http://ibrohimbinladin.wordpress.com
from odoo import api, fields, models, _


class Partners(models.Model):
    _inherit = "res.partner"

    state_name = fields.Char(related='state_id.name', string="State Name", readonly=True)
    country_name = fields.Char(related='country_id.name', string="Country Name", readonly=True)




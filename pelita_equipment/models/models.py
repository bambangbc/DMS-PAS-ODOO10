# -*- coding: utf-8 -*-

from odoo import models, fields, api


class PelitaMaintenance(models.Model):
    _inherit = 'maintenance.request'

    equipment_id = fields.Many2one(string='Aircraft')
    


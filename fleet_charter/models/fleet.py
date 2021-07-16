# -*- coding: utf-8 -*-

from odoo import models, fields


class FleetReservedTime(models.Model):
    _name = "charter.fleet.reserved"
    _description = "Reserved Time"

    customer_id = fields.Many2one('res.partner', string='Customer')
    date_from = fields.Date(string='Reserved Date From')
    date_to = fields.Date(string='Reserved Date To')
    reserved_obj = fields.Many2one('fleet.vehicle')


class EmployeeFleet(models.Model):
    _inherit = 'fleet.vehicle'

    charter_check_availability = fields.Boolean(default=True, copy=False)
    color = fields.Char(string='Color', default='#FFFFFF')
    charter_reserved_time = fields.One2many('charter.fleet.reserved', 'reserved_obj', String='Reserved Time', readonly=1,
                                           ondelete='cascade')
    driver_id = fields.Many2one(string="Pilot")
    doors = fields.Integer(string="Max Passenger", default='7')
    fuel_type = fields.Selection([('gasoline', 'Gasoline'),
                                  ('avgas_seratustigapuluh', 'AVgas 100/130'),
                                  ('avgas_seratus', 'AVGas 100LL'),
                                  ('avgas_lapandua', 'AVgas 82 UL'),
                                  ('diesel', 'Diesel/Biodiesel')],
                                 'Fuel Type', help='Fuel Used by the aircraft')

    _sql_constraints = [('vin_sn_unique', 'unique (vin_sn)', "Chassis Number already exists !"),
                        ('license_plate_unique', 'unique (license_plate)', "License plate already exists !")]

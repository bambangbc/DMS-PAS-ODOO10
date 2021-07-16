# -*- coding: utf-8 -*-
# © 2017 Ibrohim Binladin | ibradiiin@gmail.com | +62-838-7190-9782
from odoo import api, fields, models, _
import logging
_logger = logging.getLogger(__name__)


class AirServiceInformation(models.TransientModel):
    _name = "sale.air_service_info"
    _description = "Air Service Info"

    order_line_id = fields.Many2one('sale.order.line', string="Order Lines", readonly=True,
                                    default=lambda self: self._context.get('active_id', False))
    fl_acquisition_id = fields.Many2one('aircraft.acquisition', string="Fleet Acquisition", copy=False)
    craft_name = fields.Char(related='fl_acquisition_id.aircraft_name.name', string="Aircraft Name", readonly=True, store=False)
    craft_type = fields.Many2one('aircraft.type', related='fl_acquisition_id.aircraft_name.aircraft_type_id',
                                 string='Aircraft Type', store=False, readonly=True)
    craft_categ = fields.Many2one('aircraft.category', related='fl_acquisition_id.aircraft_name.aircraft_categ_id',
                                  string='Aircraft Category', store=False, readonly=True)
    craft_availseat = fields.Integer(related='fl_acquisition_id.aircraft_name.available_seat',
                                     string='Available Seat', readonly=True, store=False)
    craft_color = fields.Char(related='fl_acquisition_id.aircraft_name.aircraft_color',
                              string='Aircraft Color', readonly=True, store=False)
    craft_status = fields.Selection(related='fl_acquisition_id.product_tmpl_id.aircraft_state',
                                    store=False, readonly=True)
    craft_reg_code = fields.Char(related='fl_acquisition_id.name', string='Registration Code',
                                 readonly=True, store=False)
    craft_ownership = fields.Selection(related='fl_acquisition_id.ownership', store=False, readonly=True)
    # Base Operation required=True,
    base_ops_id = fields.Many2one('base.operation', string="Base Operation")
    base_code = fields.Char(string="Code", related='base_ops_id.code', readonly=True, store=False)
    base_desc = fields.Text(string="Description", related='base_ops_id.description', readonly=True, store=False)
    base_coordinate = fields.Char(string="Coordinate", related='base_ops_id.coordinate', readonly=True, store=False)
    # Area  required=True,
    area_ops_id = fields.Many2one('area.operation', string="Area Operation")
    area_code = fields.Char(string="Code", related='area_ops_id.code', readonly=True, store=False)
    area_desc = fields.Text(string='Description', related='area_ops_id.description', readonly=True, store=False)
    area_coordinate = fields.Char(string="Coordinate", related='area_ops_id.coordinate', readonly=True, store=False)
    # Passanger and Crew Information
    pass_qty = fields.Integer(string="Passenger", related='order_line_id.pass_qty', readonly=True, store=False)
    pass_cargo = fields.Integer(string="Cargo (Max Weight)", related='order_line_id.pass_cargo', readonly=True, store=False)
    pass_ticket = fields.Selection(string="Ticket", related='order_line_id.pass_ticket', readonly=True, store=False)
    crew_set = fields.Integer(string="Crew Set", related='order_line_id.crew_set', readonly=True, store=False)
    technician_set = fields.Integer(string="Technician Set", related='order_line_id.technician_set', readonly=True, store=False)
    fuel_consump = fields.Float(string="Fuels Consumption", related='order_line_id.fuel_consump', readonly=True, store=False)

    @api.onchange('order_line_id')
    def onchange_order_line_id(self):
        oline = self.env['sale.order.line'].browse(self.order_line_id.id)
        return {'value': {
            'fl_acquisition_id': oline.fleet_acquisition_id and oline.fleet_acquisition_id.id or False,
            'base_ops_id': oline.base_ops_id and oline.base_ops_id or False,
            'area_ops_id': oline.area_ops_id and oline.area_ops_id or False,
        }}



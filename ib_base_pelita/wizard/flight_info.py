# -*- coding: utf-8 -*-
# © 2017 Ibrohim Binladin | ibradiiin@gmail.com | +62-838-7190-9782
from odoo import api, fields, models, _
from odoo.exceptions import UserError
import logging
_logger = logging.getLogger(__name__)


class SaleFlightInformation(models.TransientModel):
    _name = "sale.flight_information"
    _description = "Flight Information"

    order_line_id = fields.Many2one('sale.order.line', string="Order Lines", readonly=True, default=lambda self: self._context.get('active_id', False))
    flight_request_line = fields.One2many('sale.flight.request.info', 'flight_info_id', string='Flight Requisition Lines', readonly=True)
    flight_schedule_line = fields.One2many('sale.flight.schedule.info', 'flight_information_id',
                                          string='Flight Schedule Lines', readonly=True)

    @api.onchange('order_line_id')
    def onchange_order_line_id(self):
        olines = self.env['sale.order.line'].browse(self.order_line_id.id)
        #raise UserError(_('ID get: %s, id from self: %s') % (self.order_line_id, self.id))
        fl_req_info_line = []
        if olines.flight_requisition_ids:
            for fl_req in olines.flight_requisition_ids:
                fl_req_info_line.append((0, 0, {
                    'number': fl_req.name or _(''),
                    'route_operation_id': fl_req.route_operation_id and fl_req.route_operation_id.id or False,
                    'aircraft_id': fl_req.aircraft_id and fl_req.aircraft_id.id or False,
                    'state': fl_req.state,
                    }))
        fl_sch_info_line = []
        if olines.flight_schedule_ids:
            for fl_schedule in olines.flight_schedule_ids:
                fl_sch_info_line.append((0, 0, {
                    'fs_number': fl_schedule.name or _(''),
                    'flight_order_no': fl_schedule.flight_order_no or _(''),
                    'fl_acquisition_id': fl_schedule.fl_acquisition_id and fl_schedule.fl_acquisition_id.id or False,
                    'schedule_commercial_id': fl_schedule.schedule_commercial_id.id or False,
                    'flight_category': fl_schedule.flight_category,
                    'flight_type': fl_schedule.flight_type,
                    'internal_flight_type_id': fl_schedule.internal_flight_type_id.id or False,
                    'status': fl_schedule.state,
                }))
        return {'value': {
            'flight_request_line': fl_req_info_line,
            'flight_schedule_line': fl_sch_info_line,
        }}




class SaleFlightRequestInfoLines(models.TransientModel):

    STATE_SELECTION = [('draft', 'Draft'),('validated', 'Validated'),('cancel', 'Cancelled')]

    _name = "sale.flight.request.info"
    _description = "Flight Requisition Info Line"

    flight_info_id = fields.Many2one('sale.flight_information', string="Flight Information", readonly=True)
    number = fields.Char(string='Number', readonly=True)
    route_operation_id = fields.Many2one('route.operation', string='Route', readonly=True)
    state = fields.Selection(STATE_SELECTION, string="Status", readonly=True)
    aircraft_id = fields.Many2one('aircraft.acquisition', 'Aircraft', readonly=True)
    route_line_ids = fields.One2many(related='route_operation_id.route_line_ids', string="Flight Route",
                                     store=False, readonly=True)



class SaleFlightScheduleInfoLines(models.TransientModel):

    STATE_SELECTION = [('draft', 'Draft'),('validated', 'Validated'),('cancel', 'Cancelled'),('setcrew','Set Crew')]

    _name = "sale.flight.schedule.info"
    _description = "Flight Schedule Info Line"

    flight_information_id = fields.Many2one('sale.flight_information', string="Flight Information", readonly=True)
    fs_number = fields.Char('Flight No', readonly=True)
    flight_order_no = fields.Char('Flight Ord No', readonly=True)
    fl_acquisition_id = fields.Many2one('aircraft.acquisition', 'Aircraft', readonly=True)
    schedule_commercial_id = fields.Many2one('schedule.commercial', 'Schedule Commercial', readonly=True)
    flight_category = fields.Selection([('domestic', 'Domestic'),
                                        ('international', 'International')], 'Flight Category', readonly=True)
    flight_type = fields.Selection([('commercial', 'Commercial'),
                                    ('noncommercial', 'Non-Commercial')], string='Flight Type', readonly=True)
    internal_flight_type_id = fields.Many2one('internal.flight.type', 'Internal Flight Type', readonly=True)
    status = fields.Selection(STATE_SELECTION, string="Status", readonly=True)



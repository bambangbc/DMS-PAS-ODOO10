# -*- coding: utf-8 -*-
from odoo import fields, models,api, _

import logging
_logger = logging.getLogger(__name__)

class FlightRequisition(models.Model):
	_name = 'flight.requisition'
	_inherit = ["mail.thread", "ir.needaction_mixin"]
	_order = "date_request desc, name desc"

	name = fields.Char('Number')
	date_request = fields.Date('Date Request')
	destination = fields.Many2one('area.operation','To')
	date_from = fields.Date(string='Date of Flight(From)', track_visibility='onchange')
	date_to = fields.Date(string='Date of Flight (To)', track_visibility='onchange')
	etd = fields.Datetime(string='ETD', track_visibility='onchange')
	aircraft_id = fields.Many2one('aircraft.acquisition', 'Aircraft', required=True, readonly=True)
	customer_id = fields.Many2one('res.partner', string='Customer', domain=[('customer','=',True)], 
								  readonly=True, track_visibility='onchange')
	base_operation_id = fields.Many2one('base.operation','Base Operation')
	creator_id = fields.Many2one('res.users','Creator')
	route_operation_ids = fields.One2many('base.operation','route_id','Route')
	state = fields.Selection([('draft', 'Draft'),('validated', 'Validated'),('cancel', 'Cancelled')],
            string='Status', readonly=True, copy=False, index=True, track_visibility='onchange', default='draft')



class BaseRouteOperation(models.Model):
	_inherit = 'base.operation'

	route_id = fields.Many2one('flight.requisition')



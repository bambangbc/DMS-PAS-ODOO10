# -*- coding: utf-8 -*-

from odoo import models, fields, api


class PelitaSaleOrder(models.Model):
	#_name = 'pelita.sale'
	_inherit = 'sale.order'

	
	#ref_contract = fields.Char('Contract Ref')
	#service	= fields.Boolean(string='Serviceable')
	
  	business_type = fields.Selection([
        (0, 'Onspot'),
        (1, 'Contractual')
        ], "Type",
        help="""DO NOT forget to choose one of them""")

  	# Date fields:
	date_departure = fields.Datetime('Departure')
	date_arrival = fields.Datetime('Arrival')

	# Aircraft
	craft_name = fields.Char(string="Aircraft Name", readonly=True, states={'draft': [('readonly', False)], 'sent': [('readonly', False)]})
	craft_type = fields.Char(string='Aircraft Type')
	# craft_categ = fields.Many2one('aircraft.category', string='Aircraft Category')
	craft_categ = fields.Char(string='Aircraft Category') # sudah Many2one jadi saya biarkan khawatir bentrok
	craft_ownership = fields.Selection([('leasing','Leasing'),('owner','Owner')], string='Ownership',
			default='leasing', readonly=True, states={'draft': [('readonly', False)], 'sent': [('readonly', False)]})
	craft_reg_code = fields.Char(string='Registration Code',
			readonly=True, states={'draft': [('readonly', False)], 'sent': [('readonly', False)]})
	craft_availseat = fields.Integer(string='Available Seat',
			readonly=True, states={'draft': [('readonly', False)], 'sent': [('readonly', False)]})
	craft_color = fields.Char(string='Aircraft Color',
			readonly=True, states={'draft': [('readonly', False)], 'sent': [('readonly', False)]})
	craft_status = fields.Selection([(0, 'Serviceable'),(1, 'Unserviceable')],
			string='Status', readonly=True, states={'draft': [('readonly', False)], 'sent': [('readonly', False)]})

	# Passenger
	pass_qty = fields.Integer('Passenger', readonly=True, states={'draft': [('readonly', False)], 'sent': [('readonly', False)]})
	pass_cargo = fields.Integer('Cargo (Max Weight)', readonly=True,
							  states={'draft': [('readonly', False)], 'sent': [('readonly', False)]})
	# pass_cargo = fields.Char(string="Cargo (Max Weight)",
	# 		readonly=True, states={'draft': [('readonly', False)], 'sent': [('readonly', False)]})
	pass_ticket = fields.Selection([(0, 'Non VVIP'),(1, 'VVIP')],
			string='Ticket', default=1, readonly=True, states={'draft': [('readonly', False)], 'sent': [('readonly', False)]})

	# Crew & Technicians
	crew_set = fields.Integer(string="Crew Set",
			readonly=True, states={'draft': [('readonly', False)], 'sent': [('readonly', False)]})
	technician_set = fields.Integer(string="Technician Set",
			readonly=True, states={'draft': [('readonly', False)], 'sent': [('readonly', False)]})
	fuel_consump = fields.Float(string="Fuels Consumption",
			readonly=True, states={'draft': [('readonly', False)], 'sent': [('readonly', False)]})

	#route_name = fields.Many2one('route.route', string="Route Name")
	# route_from = fields.Many2one('route.route', string='From', required=True,
	# 		readonly=True, states={'draft': [('readonly', False)], 'sent': [('readonly', False)]})
	# route_to = fields.Many2one('route.route', string='To', required=True,
	# 		readonly=True, states={'draft': [('readonly', False)], 'sent': [('readonly', False)]})
	# Route  required=True,
	route_id = fields.Many2one('route.operation', "Route",
			readonly=True, states={'draft': [('readonly', False)], 'sent': [('readonly', False)]})
	route_from = fields.Many2one('route.route', related='route_id.from_route_id',
								  string='From', store=False, readonly=True)
	route_to = fields.Many2one('route.route', related='route_id.to_route_id',
								  string='To', store=False, readonly=True)
	nm_distance = fields.Float(
		string="Distance (NM)", 
		related='route_id.distance_nm', 
		readonly=True, store=False,
		help="1 Kilometer = 0,6 Nautical Miles")
	km_distance = fields.Float(
		string="Distance (KM)", 
		related='route_id.distance_km',
		readonly=True, store=False,
		help="1 Nautical Miles = 1,85 Kilometers")

	# Base Operation required=True,
	base_name = fields.Many2one('base.operation', string="Name",
				readonly=True, states={'draft': [('readonly', False)], 'sent': [('readonly', False)]})
	base_code = fields.Char(string="Code", related='base_name.code', readonly=True)
	base_desc = fields.Text(string="Description", related='base_name.description', readonly=True)
	base_coordinate = fields.Char(string="Coordinate", related='base_name.coordinate', readonly=True)
	base_status = fields.Selection(string="Status", related='base_name.status', readonly=True)


	# Area  required=True,
	area_name = fields.Many2one('area.operation', string="Name",
				readonly=True, states={'draft': [('readonly', False)], 'sent': [('readonly', False)]})
	area_code = fields.Char(string="Code", related='area_name.code', readonly=True)
	area_desc = fields.Text(string='Description', related='area_name.description', readonly=True)
	area_coordinate = fields.Char(string="Coordinate", related='area_name.coordinate', readonly=True)
	area_status = fields.Selection(string="Status", related='area_name.status', readonly=True)



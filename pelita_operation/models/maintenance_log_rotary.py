# -*- coding: utf-8 -*-
from odoo import fields, models,api, _
# import pytz
# from odoo.addons.mail.models.mail_template import format_tz
# from datetime import date, datetime, timedelta
# from odoo.exceptions import UserError, AccessError
import logging
_logger = logging.getLogger(__name__)


class MaintenanceLogRotary(models.Model):
	_name = 'maintenance.log.rotary'
	name = fields.Char('Log Number' ,index=True, default=lambda self: _('New'))
	date_lt = fields.Date('Date (LT)')
	etd = fields.Datetime('ETD (Local Time)')
	eta = fields.Datetime('ETA (Local Time)')
	flight_schedule_id = fields.Many2one('flight.schedule','Flight Schedule')
	flight_number = fields.Char('Flight Number')
	flight_order_number = fields.Char('Flight Order Number')
	location_id = fields.Many2one('route.route', 'Location')
	customer_id = fields.Many2one('res.partner', string='Customer')
	schedule_commercial_id = fields.Many2one('schedule.commercial','Schedule Commercial')
	flight_category = fields.Selection([('domestic','Domestic'),
		('international','International')],'Flight Category')
	flight_type = fields.Selection([('commercial','Commercial'),
		('noncommercial','Non-Commercial')], string='Flight Type')
	internal_flight_type_id = fields.Many2one('internal.flight.type','Internal Flight Type')
	schedule_date = fields.Date('Schedule Date')
	route_rotary_ids = fields.One2many('route.rotary','rotary_id', 'Route')
	flight_attendant_ids = fields.One2many('flight.attendant','rotary_id','Flight Attendant')
	is_instruction_flight = fields.Boolean('Is instruction Flight?')
	training_instructor_id = fields.Many2one('hr.employee','Training Instructor')
	brief_time = fields.Float(string='Brief/De Brief')
	cancel_reason_id = fields.Many2one('reason.reason', 'Cancel Reason')
	late_departure_id = fields.Many2one('reason.reason','Late Departure')
	total_late = fields.Float(string='Total Late (minutes)')
	aircraft_unserviceable_reason = fields.Char('Aircraft Unserviceable Reason')
	rtb = fields.Float(string='RTB')
	rtb_reason = fields.Text('RTB Reason')
	discrepancies_ids = fields.One2many('discrepancies.discrepancies','rotary_id',
		'Discrepancies')
	maintenance_rotary_ids = fields.One2many('maintenance.rotary','rotary_id',
	 'Maintenance Data')

	@api.model
	def create(self, vals):
		if vals.get('name', _('New')) == _('New'):
			vals['name'] = self.env['ir.sequence'].next_by_code('maintenance.log.rotary') or _('New')
		result = super(MaintenanceLogRotary, self).create(vals)
		return result

	
class RouteRotary(models.Model):
	_name ='route.rotary'
	rotary_id = fields.Many2one('maintenance.log.rotary')
	from_id = fields.Many2one('route.route','From')
	to_id = fields.Many2one('route.route','To')
	rotor_engage = fields.Float(string='Rotor Engage')
	lift_off = fields.Float(string='Lift OFF')
	landing = fields.Float(string='Landing')
	flight_hours = fields.Float(string='Flight Hours')
	dispatch = fields.Float(string='Dispatch')
	rotor_stop = fields.Float(string='Rotor Stop')
	block = fields.Float(string='Block')
	in_service = fields.Float(string='In Service')
	pax_no = fields.Float(string='PAX No')
	cargo = fields.Float(string='Cargo (Kgs/Lbs')
	sing_hoist_no = fields.Float(string='Sing/Hoist No')
	ldg = fields.Float(string='LDG')
	cycle_start1 = fields.Float(string='Cycle Start I')
	cycle_start2 = fields.Float(string='Cycle Start II')
	cycle_gg = fields.Float(string='GG')
	cycle_ft = fields.Float(string='FT')
	crew_id = fields.Many2one('hr.employee','Flight  Crew')
	crew_type_id = fields.Many2one('crew.type','Crew Type')
	qualification = fields.Char('Qualification')
	fml_no = fields.Char('FML Number')

class Discrepancies(models.Model):
	_name = 'discrepancies.discrepancies'
	rotary_id = fields.Many2one('maintenance.log.rotary')
	name = fields.Char('Discrepancies')
	action = fields.Text('Action')

class MaintenanceRotary(models.Model):
	_name = 'maintenance.rotary'
	rotary_id = fields.Many2one('maintenance.log.rotary')
	engine_oil1 = fields.Float('Engine Oil added I')
	engine_oil2 = fields.Float('Engine Oil added II')
	fuel_added = fields.Float('Fuel Added')
	fuel_total = fields.Float('Fuel Total')
	start_T4_engine1 = fields.Float('Indicated T4/TOT/ITT on engine 1')
	start_T4_engine2 = fields.Float('Indicated T4/TOT/ITT on engine 2')
	
	takeoff_ng_engine1 = fields.Float('Indicated Ng/N1 on engine 1')
	takeoff_ng_engine2 = fields.Float('Indicated Ng/N1 on engine 2')
	takeoff_T4_engine1 = fields.Float('T4/TOT/ITT on engine 1')
	takeoff_T4_engine2 = fields.Float('T4/TOT/ITT on engine 2')
	takeoff_torque_engine1 = fields.Float('Torque(%) on engine 1')
	takeoff_torque_engine2 = fields.Float('Torque(%) on engine 1')
	takeoff_ntl_engine1 = fields.Float('Ntl/N2 on engine 1')
	takeoff_ntl_engine2 = fields.Float('Ntl/N2 on engine 2')
	takeoff_oil_press_engine1 = fields.Float('Oil Press on engine 1')
	takeoff_oil_press_engine2 = fields.Float('Oil Press on engine 2')
	takeoff_oil_temp_engine1 = fields.Float('Oil Temp on engine 1')
	takeoff_oil_temp_engine2 = fields.Float('Oil Temp on engine 2')
	takeoff_xmsn_torque_engine1 = fields.Float('XMSN Torque on engine 1 (%)')
	takeoff_xmsn_torque_engine2 = fields.Float('XMSN Torque on engine 2 (%)')
	takeoff_xmsn_oil_engine1 = fields.Float('XMSN Oil on engine 1 (0c)')
	takeoff_xmsn_oil_engine2 = fields.Float('XMSN Oil on engine 2 (0c)')
	takeoff_nr_engine = fields.Float('NR (RPM)')
	takeoff_pitch_engine1 = fields.Float('Pitch on engine 1')
	takeoff_pitch_engine2 = fields.Float('Pitch on engine 2')
	takeoff_oat_engine1 = fields.Float('OAT on engine 1')
	takeoff_oat_engine2 = fields.Float('OAT on engine 2')
	takeoff_airspeed_engine = fields.Float('Airspeed on engine (knot)')
	takeoff_altitude_engine = fields.Float('Altitude on engine (feet)')

	airframe_bf_hours = fields.Float('Brought Forward Hours')
	airframe_bf_landing = fields.Float('Brought Forward Landing')
	airframe_today_hours = fields.Float('Today Hours')
	airframe_today_landing = fields.Float('Today Landing')
	airframe_total_hours = fields.Float('Total Hours')
	airframe_total_landing = fields.Float('Total Landing')

	sn_bf = fields.Float('Sn Brought Forward')
	sn_today = fields.Float('Sn Today')
	sn_total = fields.Float('Sn Total')

	esn1_bf_hours = fields.Float('Brought Forward Hours')
	esn1_bf_landing = fields.Float('Brought Forward Landing')
	esn1_today_hours = fields.Float('Today Hours')
	esn1_today_landing = fields.Float('Today Landing')
	esn1_total_hours = fields.Float('Total Hours')
	esn1_total_landing = fields.Float('Total Landing')
	
	esn2_bf_hours = fields.Float('Brought Forward Hours')
	esn2_bf_landing = fields.Float('Brought Forward Landing')
	esn2_today_hours = fields.Float('Today Hours')
	esn2_today_landing = fields.Float('Today Landing')
	esn2_total_hours = fields.Float('Total Hours')
	esn2_total_landing = fields.Float('Total Landing')
	
	
	
	
	
	
	
	
	
	
	
	
		
	
	
	
	
	
		
		
# -*- coding: utf-8 -*-
from odoo import fields, models,api, _
# import pytz
# from odoo.addons.mail.models.mail_template import format_tz
# from datetime import date, datetime, timedelta
# from odoo.exceptions import UserError, AccessError
import logging
_logger = logging.getLogger(__name__)

class MaintenanceLogFixWing(models.Model):
	_name = 'maintenance.log.fixwing'
	name = fields.Char('Log Number', index=True, default=lambda self: _('New')	)
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
	route_ids = fields.One2many('maintenance.route','fixwing_id','Route')
	flight_attendant_ids = fields.One2many('flight.attendant','fixwing_id','Flight Attendant')
	is_instruction_flight = fields.Boolean('Is instruction Flight?')
	training_instructor_id = fields.Many2one('hr.employee','Training Instructor')
	brief_time = fields.Float(string='Brief/De Brief')
	cancel_reason_id = fields.Many2one('reason.reason', 'Cancel Reason')
	late_departure_id = fields.Many2one('reason.reason','Late Departure')
	total_late = fields.Float(string='Total Late (minutes)')
	aircraft_unserviceable_reason = fields.Char('Aircraft Unserviceable Reason')
	rtb = fields.Float(string='RTB')
	rtb_reason = fields.Text('RTB Reason')
	corective_action_ids = fields.One2many('corrective.action','fixwing_id','Corrective Action')
	maintenance_ids = fields.One2many('maintenance.data','fixwing_id', 'Maintenance Data')

	@api.model
	def create(self, vals):
		if vals.get('name', _('New')) == _('New'):
			vals['name'] = self.env['ir.sequence'].next_by_code('maintenance.log.fixwing') or _('New')
		result = super(MaintenanceLogFixWing, self).create(vals)
		return result


class MaintenanceRoute(models.Model):
	_name ='maintenance.route'
	fixwing_id = fields.Many2one('maintenance.log.fixwing')
	from_id = fields.Many2one('route.route','From')
	to_id = fields.Many2one('route.route','To')
	take_off = fields.Float(string='Take OFF')
	landing = fields.Float(string='Landing')
	flight_hours = fields.Float(string='Flight Hours')
	block_off = fields.Float(string='Block OFF')
	block_on = fields.Float(string='Block ON')
	flight_time = fields.Float(string='Flight Time')
	flight_time_matrix = fields.Float(string='Flight Time Matrix')
	no_pax = fields.Float(string='No PAX')
	pax = fields.Float(string='PAX')
	lugg = fields.Float('Lugg')
	freight = fields.Float('Freight')
	total = fields.Float('Total')
	fuel_payload_available = fields.Float('Fuel Payload Available')
	fuel_uplift = fields.Float('Fuel Uplift (Lt/Gal)')
	fuel_total = fields.Float('Fuel Total(Lbs/Kg)')
	fuel_const = fields.Float('Fuel Const(Lbs/Kg)')
	fuel_rem = fields.Float('Fuel Rem (Lbs/Kg)')
	oil_added1 = fields.Float('Oil Added 1')
	oil_added2 = fields.Float('Oil added 2')
	oil_added3 = fields.Float('Oil Added 3')
	oil_added4 = fields.Float('Oil Added 4')
	crew_id = fields.Many2one('hr.employee','Flight  Crew')
	crew_type_id = fields.Many2one('crew.type','Crew Type')
	qualification = fields.Char('Qualification')
	fml_no = fields.Char('FML Number')


class MaintenanceData(models.Model):
	_name = 'maintenance.data'
	fixwing_id = fields.Many2one('maintenance.log.fixwing')
	engine_torque1 = fields.Float('Torque/Thrust/EPR (1)')
	engine_torque2 = fields.Float('Torque/Thrust/EPR (2)')
	engine_rpm_nl = fields.Float('RPM (NL/N1/NG)')
	engine_rpm_nl2 = fields.Float('RPM (NL/N2/NG)')
	engine_rpm_nh = fields.Float('RPM (NH/N2)')
	engine_np1 = fields.Float('NP1')
	engine_np2 = fields.Float('NP2')
	engine_itt1 = fields.Float('ITT/TGT/T5/EGT')
	engine_itt2 = fields.Float('ITT/TGT/T5/EGT')
	fuel_flow1 = fields.Float('Fuel Flow')
	fuel_flow2 = fields.Float('Fuel Flow')
	fuel_temp1 = fields.Float('Fuel Temperature')
	fuel_temp2 = fields.Float('Fuel Temperature')
	oil_temp1 = fields.Float('Oil Temperature')
	oil_temp2 = fields.Float('Oil Temperature')
	oil_preasure1 = fields.Float('Oil Preasure')	
	oil_preasure2 = fields.Float('Oil Preasure')
	oil_level1 = fields.Float('Oil Level')
	oil_level2 = fields.Float('Oil Level')
	vibration1 = fields.Float('Vibration')
	vibration2 = fields.Float('Vibration')
	c1_gw = fields.Float('C1/GW')
	c2_gw = fields.Float('C2/GW')
	c1_gw = fields.Text('C1/GW')

	airframe_brt_fwd_hours = fields.Float('Brt FWD (Hours)')
	airframe_brt_fwd_cycles = fields.Float('BRT FWD (Cycles)')
	airframe_brt_today_hours = fields.Float('Today (Hours)')
	airframe_brt_today_cycles = fields.Float('Today (Cycles)')
	airframe_brt_total_hours = fields.Float('Total (Hours)')
	airframe_brt_total_cycles = fields.Float('Total (Cycles)')

	engine1_brt_fwd_hours = fields.Float('Brt FWD (Hours)')
	engine1_brt_fwd_cycles = fields.Float('BRT FWD (Cycles)')
	engine1_brt_today_hours = fields.Float('Today (Hours)')
	engine1_brt_today_cycles = fields.Float('Today (Cycles)')
	engine1_brt_total_hours = fields.Float('Total (Hours)')
	engine1_brt_total_cycles = fields.Float('Total (Cycles)')

	engine2_brt_fwd_hours = fields.Float('Brt FWD (Hours)')
	engine2_brt_fwd_cycles = fields.Float('BRT FWD (Cycles)')
	engine2_brt_today_hours = fields.Float('Today (Hours)')
	engine2_brt_today_cycles = fields.Float('Today (Cycles)')
	engine2_brt_total_hours = fields.Float('Total (Hours)')
	engine2_brt_total_cycles = fields.Float('Total (Cycles)')

	apu_brt_fwd_hours = fields.Float('Brt FWD (Hours)')
	apu_brt_fwd_cycles = fields.Float('BRT FWD (Cycles)')
	apu_brt_today_hours = fields.Float('Today (Hours)')
	apu_brt_today_cycles = fields.Float('Today (Cycles)')
	apu_brt_total_hours = fields.Float('Total (Hours)')
	apu_brt_total_cycles = fields.Float('Total (Cycles)')

	propeller_brt_fwd_hours = fields.Float('Brt FWD (Hours)')
	propeller_brt_fwd_cycles = fields.Float('BRT FWD (Cycles)')
	propeller_brt_today_hours = fields.Float('Today (Hours)')
	propeller_brt_today_cycles = fields.Float('Today (Cycles)')
	propeller_brt_total_hours = fields.Float('Total (Hours)')
	propeller_brt_total_cycles = fields.Float('Total (Cycles)')


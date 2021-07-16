from odoo import fields, models,api, _
import pytz
from odoo.addons.mail.models.mail_template import format_tz
from datetime import date, datetime, timedelta
from odoo.exceptions import UserError, AccessError

class AircraftReliability(models.Model):
	_name = 'aircraft.reliability'
	name = fields.Many2one('aircraft.acquisition','Registration No')
	aircraft_type_id = fields.Many2one('aircraft.type', string='Aircraft Type')
	aircraft_type = fields.Selection('Aircraft Type', 
		related='name.aircraft_name.aircraft_categ',readonly=True)
	year = fields.Selection([(num, str(num)) for num in range(2015, (datetime.now().year)+5 )], 'Year')
	month = fields.Selection([('january','January'),('february','February'),('march','March'),
		('april','April'),('may','May'),('june','June'),('july','July'),('august','August'),
		('september','September'),('october','October'),('november','November'),('desember','Desember')])
	target = fields.Float(string='Target (%)')
	actual = fields.Float(string="Actual (%)")
	tanggal = fields.Date('Date')
	description = fields.Text('Description')

class AircraftInterruption(models.Model):
	_name = 'aircraft.interruption'
	name = fields.Many2one('aircraft.acquisition','Registration No')
	aircraft_type_id = fields.Many2one('aircraft.type', string='Aircraft Type')
	aircraft_type = fields.Selection('Aircraft Type', 
		related='name.aircraft_name.aircraft_categ',readonly=True)
	year = fields.Selection([(num, str(num)) for num in range(2015, (datetime.now().year)+5 )], 'Year')
	month = fields.Selection([('1','January'),('february','February'),('march','March'),
		('april','April'),('may','May'),('june','June'),('july','July'),('august','August'),
		('september','September'),('october','October'),('november','November'),('desember','Desember')])
	ddg = fields.Float('DDG (Times)')
	intermitent_failure = fields.Float('Intermitent Failure (Times)')
	reliability_issue = fields.Float('Reliability Issue (Times)')
	material = fields.Float('Material (Times)')
	crew_decision = fields.Float('Crew Decision (Times)')
	component_failure = fields.Float('Component Failure (Times)')

class AircraftOnGround(models.Model):
	_name = 'aircraft.onground'
	name = fields.Many2one('aircraft.acquisition','Registration No')
	aircraft_type_id = fields.Many2one('aircraft.type', string='Aircraft Type')
	aircraft_type = fields.Selection('Aircraft Type', 
		related='name.aircraft_name.aircraft_categ',readonly=True)
	year = fields.Selection([(num, str(num)) for num in range(2015, (datetime.now().year)+5 )], 'Year')
	month = fields.Selection([('1','January'),('february','February'),('march','March'),
		('april','April'),('may','May'),('june','June'),('july','July'),('august','August'),
		('september','September'),('october','October'),('november','November'),('desember','Desember')])
	aog = fields.Float(string='AOG (Days)')
	tanggal = fields.Date('Date')
	description = fields.Text('Description')

class AircraftUtilisation(models.Model):
	_name = 'aircraft.utilisation'
	name = fields.Many2one('aircraft.acquisition','Registration No')
	aircraft_type_id = fields.Many2one('aircraft.type', string='Aircraft Type')
	aircraft_type = fields.Selection('Aircraft Type', 
		related='name.aircraft_name.aircraft_categ',readonly=True)
	year = fields.Selection([(num, str(num)) for num in range(2015, (datetime.now().year)+5 )], 'Year')
	month = fields.Selection([('1','January'),('february','February'),('march','March'),
		('april','April'),('may','May'),('june','June'),('july','July'),('august','August'),
		('september','September'),('october','October'),('november','November'),('desember','Desember')])
	target = fields.Float(string='Target Utilisation (Hours)')
	actual = fields.Float(string="Actual Utilisation (Hours)")
	tanggal = fields.Date('Date')
	description = fields.Text('Description')
	

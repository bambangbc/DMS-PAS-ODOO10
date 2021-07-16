from odoo import fields, models,api, _
import pytz
from odoo.addons.mail.models.mail_template import format_tz
from datetime import date, datetime, timedelta
from odoo.exceptions import UserError, AccessError

class AircraftRental(models.Model):
	_name = 'aircraft.rental'
	acquisition_id = fields.Many2one('aircraft.acquisition','Registration No')
	aircraft_name = fields.Char(string='Aircraft Name',
	 related='acquisition_id.aircraft_name.name', readonly=True)
	aircraft_type = fields.Char(string='Aircraft Type', 
		related='acquisition_id.aircraft_type_id.name',readonly=True)
	lessor = fields.Char(string='Lessor', related='acquisition_id.lessor',readonly=True)	
	month = fields.Selection([('january','January'),('february','February'),('march','March'),
		('april','April'),('may','May'),('june','June'),('july','July'),('august','August'),
		('september','September'),('october','October'),('november','November'),('desember','Desember')])
	year = fields.Selection([(num, str(num)) for num in range(2000, (datetime.now().year)+1 )], 'Year')
	rent_amount = fields.Float('Rent ammount')
	rent_currency_id = fields.Many2one('res.currency',  'Rent Currency')
	#rent_payment = fields.Float('Rent Payment')
	#payment_currency_id = fields.Many2one('res.currency', 'Payment Currency')

class MaintenanceReserved(models.Model):
	_name = 'maintenance.reserved'
	acquisition_id = fields.Many2one('aircraft.acquisition','Registration No')
	aircraft_name = fields.Char(string='Aircraft Name',
	 related='acquisition_id.aircraft_name.name', readonly=True)
	aircraft_type = fields.Char(string='Aircraft Type', 
		related='acquisition_id.aircraft_type_id.name',readonly=True)
	month = fields.Selection([('january','January'),('february','February'),('march','March'),
		('april','April'),('may','May'),('june','June'),('july','July'),('august','August'),
		('september','September'),('october','October'),('november','November'),('desember','Desember')])
	year = fields.Selection([(num, str(num)) for num in range(2000, (datetime.now().year)+1 )], 'Year')
	airframe = fields.Float('Airframe')
	ldg = fields.Float('Ldg')
	engine1 = fields.Float('Engine#1')
	llp_engine1 = fields.Float('LLP Engine#1')
	engine2 = fields.Float('Engine#2')
	llp_engine2 = fields.Float('LLP Engine#2')
	propeller1 = fields.Float('Propeller#1')
	propeller2 = fields.Float('Propeller#2')
	rgb1 = fields.Float('RGB#1')
	rgb2 = fields.Float('RGB#2')

class ReservedClaimed(models.Model):
	_name = 'reserved.claimed'
	acquisition_id = fields.Many2one('aircraft.acquisition','Registration No')
	aircraft_name = fields.Char(string='Aircraft Name',
	 related='acquisition_id.aircraft_name.name', readonly=True)
	aircraft_type = fields.Char(string='Aircraft Type', 
		related='acquisition_id.aircraft_type_id.name',readonly=True)
	month = fields.Selection([('january','January'),('february','February'),('march','March'),
		('april','April'),('may','May'),('june','June'),('july','July'),('august','August'),
		('september','September'),('october','October'),('november','November'),('desember','Desember')])
	year = fields.Selection([(num, str(num)) for num in range(2000, (datetime.now().year)+1 )], 'Year')
	
	airframe = fields.Float('Airframe')
	ldg = fields.Float('Ldg')
	engine1 = fields.Float('Engine#1')
	llp_engine1 = fields.Float('LLP Engine#1')
	engine2 = fields.Float('Engine#2')
	llp_engine2 = fields.Float('LLP Engine#2')
	propeller1 = fields.Float('Propeller#1')
	propeller2 = fields.Float('Propeller#2')
	rgb1 = fields.Float('RGB#1')
	rgb2 = fields.Float('RGB#2')

class DeliverySchedule(models.Model):
	_name = 'delivery.schedule'
	name = fields.Many2one('aircraft.aircraft', 'Aircraft Name')
	aircraft_type = fields.Char(string='Aircraft Type', 
		related='name.aircraft_type_id.name',readonly=True)
	aircraft_category = fields.Char(string='Aircraft Category', 
		related='name.aircraft_categ_id.name',readonly=True)
	year = fields.Selection([(num, str(num)) for num in range(2000, (datetime.now().year)+1 )], 'Year')
	quantity = fields.Integer('Quantity Delivery')
	
class RedeliverySchedule(models.Model):
	_name = 'redelivery.schedule'
	name = fields.Many2one('aircraft.aircraft', 'Aircraft Name')
	aircraft_type = fields.Char(string='Aircraft Type', 
		related='name.aircraft_type_id.name',readonly=True)
	aircraft_category = fields.Char(string='Aircraft Category', 
		related='name.aircraft_categ_id.name',readonly=True)
	year = fields.Selection([(num, str(num)) for num in range(2000, (datetime.now().year)+1 )], 'Year')
	quantity = fields.Integer('Quantity Re-Delivery')

class FleetAssignment(models.Model):
	_name = 'fleet.assignment'
	name = fields.Many2one('aircraft.aircraft', 'Aircraft Name')
	aircraft_type = fields.Char(string='Aircraft Type', 
		related='name.aircraft_type_id.name',readonly=True)
	aircraft_category = fields.Char(string='Aircraft Category', 
		related='name.aircraft_categ_id.name',readonly=True)
	year = fields.Selection([(num, str(num)) for num in range(2000, (datetime.now().year)+1 )], 'Year')
	month = fields.Selection([('january','January'),('february','February'),('march','March'),
		('april','April'),('may','May'),('june','June'),('july','July'),('august','August'),
		('september','September'),('october','October'),('november','November'),('desember','Desember')])
	quantity = fields.Integer('Quantity')


	


	
	
	
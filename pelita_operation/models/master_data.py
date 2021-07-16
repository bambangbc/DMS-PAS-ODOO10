# -*- coding: utf-8 -*-
from odoo import fields, models,api, _
import ast
import math
# import pytz
# from odoo.addons.mail.models.mail_template import format_tz
# from datetime import date, datetime, timedelta
# from odoo.exceptions import UserError, AccessError

import logging
_logger = logging.getLogger(__name__)


GLOBAL_TYPE = [("vvip","VVIP"),("nonvvip","Non VVIP")]


class BaseOperation(models.Model):
    _name = "base.operation"
    _inherit = ["mail.thread", "ir.needaction_mixin"]
    _order = "code asc, name asc"
    
    name = fields.Char(string = 'Name',required=True, track_visibility='onchange')
    code = fields.Char(string='Code', track_visibility='onchange')
    description = fields.Text('Description')
    latitude = fields.Char(string='Latitude', track_visibility='onchange')
    longitude = fields.Char(string='Longitude', track_visibility='onchange')
    coordinate =  fields.Char('Coordinate')
    coordinate_map = fields.Char('MAP', compute='_get_coordinate')
    status = fields.Selection([('active','Active'),('nonactive','Non Active')], string='Status')
    active = fields.Boolean(string='Status', default=True, 
                            help="Set active to false to hide the tax without removing it.")
    google_map_base_ops = fields.Char(string="Map", track_visibility='onchange')

    @api.onchange('google_map_base_ops')
    def onchange_google_map_base_ops(self):
        if self.google_map_base_ops:
            dict_map = ast.literal_eval(self.google_map_base_ops)
            if dict_map and dict_map['position']:
                self.latitude = dict_map['position']['lat']
                self.longitude = dict_map['position']['lng']

    @api.depends('latitude','longitude')
    def _get_coordinate(self):
        for record in self:
            if record.latitude is False or record.longitude is False:
                record.latitude = record.longitude = 0.0
            record.coordinate_map = '{"position":{"lat":%s,"lng":%s},"zoom":18}'%(
                record.latitude,record.longitude)



class AreaOperation(models.Model):
    _name = 'area.operation'
    _inherit = ["mail.thread", "ir.needaction_mixin"]
    _order = "code asc, name asc"
    
    name = fields.Char(string = 'Name',required=True, track_visibility='onchange')
    code = fields.Char(string='Code', track_visibility='onchange')
    description = fields.Text('Description')
    coordinate_map = fields.Char('MAP', compute='_get_coordinate')
    coordinate = fields.Char('Coordinate')
    latitude = fields.Char(string='Latitude', track_visibility='onchange')
    longitude = fields.Char(string='Longitude', track_visibility='onchange')
    status = fields.Selection([('active','Active'),('nonactive','Non Active')], string='Status')
    google_map_area_ops = fields.Char(string="Map", track_visibility='onchange')

    @api.onchange('google_map_area_ops')
    def onchange_google_map_area_ops(self):
        if self.google_map_area_ops:
			dict_map = ast.literal_eval(self.google_map_area_ops)
			if dict_map and dict_map['position']:
				self.latitude = dict_map['position']['lat']
				self.longitude = dict_map['position']['lng']

    @api.depends('latitude','longitude')
    def _get_coordinate(self):
        for record in self:
			if record.latitude is False or record.longitude is False:
				record.latitude = record.longitude = 0.0
			record.coordinate_map = '{"position":{"lat":%s,"lng":%s},"zoom":18}'%(record.latitude,record.longitude)



class IrregularityOperation(models.Model):
    _name = 'irregularity.operation'
    
    name = fields.Char(string = 'Name',required=True)
    code = fields.Char(string='Code')
    description = fields.Text('Description')
    late_category = fields.Selection([('teknik','Operational Technical Factor'),
                                      ('nonteknik','Non Technical Factor'),
                                      ('weather','Weather Factor')], string='Late Category')
    status = fields.Selection([('active','Active'),('nonactive','Non Active')], string='Status')



class RouteRoute(models.Model):
    _name = 'route.route'
    
    name = fields.Char(string='Name')



class RouteOperation(models.Model):
    _name = 'route.operation'
    
    name = fields.Char(string='Name')
    from_route_id = fields.Many2one('area.operation','From') #remove
    to_route_id = fields.Many2one('area.operation','To') #remove
    distance_nm = fields.Float('Distance (NM)', required=True)
    distance_km = fields.Float('Distance (KM)', compute='_compute_total')
    complete_route = fields.Char(string='Complete Route', copy=False)
    from_area_id = fields.Many2one('area.operation', string='Area From')
    to_area_id = fields.Many2one('area.operation', string='Area To')
    
    @api.multi
    def _distance(self, origin, destination):
		lat1, lon1 = origin
		lat2, lon2 = destination
		radius = 3959 # km = 6371
		dlat = math.radians(lat2-lat1)
		dlon = math.radians(lon2-lon1)
		a = math.sin(dlat/2) * math.sin(dlat/2) + math.cos(math.radians(lat1)) \
		* math.cos(math.radians(lat2)) * math.sin(dlon/2) * math.sin(dlon/2)
		c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
		d = radius * c
		return d

    @api.depends('distance_nm')
    def _compute_total(self):
        for record in self:
            record.distance_km = record.distance_nm * 1.852

    @api.depends('from_area_id','to_area_id') #'from_route_id','to_route_id'
    def _compute_distance(self):
		for rec in self:
			lat1 = float(rec.from_area_id.latitude)
			lon1 = float(rec.from_area_id.longitude)
			lat2 = float(rec.to_area_id.latitude)
			lon2 = float(rec.to_area_id.longitude)
			rec.distance_nm = rec._distance((lat1, lon1),(lat2, lon2))
	
    @api.onchange('distance_nm') # if these fields are changed, call method
    def change_km(self):
		if self.distance_nm:
			self.distance_km = self.distance_nm * 1.852
            


class FlightHoursPrice(models.Model):
    _name = 'flight.hours.price'
    _inherit = ["mail.thread", "ir.needaction_mixin"]
    _order = "sk_date desc, name asc"
    
    name = fields.Char(string='Name', placeholder='SK Payment', track_visibility='onchange')
    sk_date = fields.Date(string='SK Date', track_visibility='onchange')
    payment_type = fields.Selection([('vvip','VVIP'),('nonvvip','Non VVIP')], 
                                    string='Payment Type', track_visibility='onchange')
    aircraft_categ = fields.Selection([('fixedwing','Fixed Wing'),('rotary','Rotary')])
    crew_type_id = fields.Many2one('crew.type','Crew Type')
    price = fields.Float(string='Price', track_visibility='onchange')
    remark = fields.Text('Remark')
    golongan_id = fields.Many2one('golongan.golongan','Golongan/Jabatan')


class Golongan(models.Model):
	_name = 'golongan.golongan'
	name = fields.Char(string='Name')


class Regulation(models.Model):
	_name = 'regulation.regulation'
	_inherit = ["mail.thread"]

	name = fields.Char(string='Number', 
                       default=lambda self: self.env['ir.sequence'].next_by_code(
                           'regulation.regulation'))
	aircraft_categ_id = fields.Many2one('aircraft.category', string='Aircraft Category')
	aircraft_categ = fields.Selection([('fixedwing','Fixed Wing'),('rotary','Rotary')], string="Aircraft Categ")
	min_flight_crew = fields.Selection([('1','One'),('2','Two'),
		('3','Three'),('minimum','Minimum')], string='Min Flight Crew')
	additional_flight_crew = fields.Selection([('nil','NIL'),('1','One'),('2','Two or More')],
		string='Additional Flight Crew')
	duty_time = fields.Float(string='Duty Time')
	flight_deck_duty_time = fields.Float(string='Flight Deck Duty Time')
	qualification = fields.Selection([('pic','PIC'),('foo','FOO'),('ame','AME'),
		('avi','AVI'),('hlo','HLO'),('fa','FA'),('sic','SIC')], string='Qualification')
	hour_per_day = fields.Float(string='Hour per Day')
	hour_per_week = fields.Float(string='Hour per Week')
	hour_per_month = fields.Float(string='Hour per Month')
	hour_per_threemonth =fields.Float(string='Hour per Three Month')
	hour_per_year = fields.Float(string='Hour per Year')
	rest_hour = fields.Float(string='Rest Hour')
	rest_night_duty_hour = fields.Float(string='Rest Night Duty Hour')
	qualification_id = fields.Many2one('hr.qualification', string='Qualification')

	@api.onchange('aircraft_categ')
	def onchange_aircraft_categ(self):
		if not self.aircraft_categ:
			return
		if self.name and self.name!='/':
			if self.aircraft_categ=='fixedwing':
				self.name = _("FW/") + self.name
			elif self.aircraft_categ=='rotary':
				self.name = _("RW/") + self.name
		else:
			self.name = self.env['ir.sequence'].next_by_code('regulation.regulation') or _('/')




class DutyTime(models.Model):
	_name= 'duty.time'
	flight_category = fields.Selection([('domestic','Domestic'),
		('international','International')],'Flight Category')
	before_value = fields.Float('Before Value')
	after_value = fields.Float('After Value')
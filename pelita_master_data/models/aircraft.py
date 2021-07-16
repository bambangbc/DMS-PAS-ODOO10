# -*- coding: utf-8 -*-
from odoo import fields, models,api, _
import pytz
from odoo.addons.mail.models.mail_template import format_tz
from datetime import date, datetime, timedelta
from odoo.exceptions import UserError, AccessError

import logging
_logger = logging.getLogger(__name__)


class AircraftAircraft(models.Model):
	_name = 'aircraft.aircraft'
	name = fields.Char(string = 'Name',required=True)
	aircraft_type_id = fields.Many2one('aircraft.type',string='Aircraft Type', required=True)
	aircraft_categ = fields.Selection([('fixedwing','Fixed Wing'),('rotary','Rotary')])
	aircraft_categ_id = fields.Many2one('aircraft.category', string='Aircraft Category')
	aircraft_code = fields.Char('Aircraft Code')
	#ownership = fields.Selection([('leasing','Leasing'),('owner','Owner')],string='Ownership')
	#date_manufacture = fields.Date(string='Date of Manufacture')
	available_seat = fields.Integer(string = 'Available Seat')
	aircraft_color = fields.Char(string = 'Aircraft Color')
	aircraft_status = fields.Selection([('active','Active'),('nonactive','Non Active')], string='Status')
	#engine_type_id = fields.Many2one('engine.type', string='Engine Type')
	#aircraft_lease_status = fields.Selection([('lessor','Lessor'),('startlease','Start Lease'),
	#		('termination','Normal Termination')], string='Aircraft Lease Status')
	active = fields.Boolean(string='Status', default=True,
                            help="Set active to false to hide the tax without removing it.")



class AircraftType(models.Model):
	_name = 'aircraft.type'
	name = fields.Char( string='Aircraft Type')
	#description = fields.Char(string='Description')
	propeller1 = fields.Char(string='Propeller#1 S/N')
	propeller2 = fields.Char(string='Propeller#2 S/N')
	rh_ldg = fields.Char(string='RH LDG S/N')
	lh_ldg = fields.Char(string='LH LDG S/N')
	n_ldg = fields.Char(string='N LDG S/N')
	apu = fields.Char(string='APU S/N')

	airframe = fields.Char(string='Airframe')
	airframe_tsn = fields.Float(string='Airframe TSN')
	airframe_csn = fields.Float(string='Airframe CSN')
	airframe_lastoh = fields.Date(string='Airframe Last OH')
	
	ldg = fields.Char(string='LDG')
	rh_ldg = fields.Char(string='RH LDG')
	rh_ldg_csn = fields.Float(string='RH LDG CSN')
	rh_ldg_lastoh = fields.Date(string='RH LDG Last OH')
	lh_ldg = fields.Char(string='LH LDG')
	lh_ldg_csn = fields.Float(string='LH LDG CSN')
	lh_ldg_lastoh = fields.Date(string='LH LDG Last OH')

	engine = fields.Char(string='Engine')
	engine1 = fields.Char(string='Engine#1')
	engine1_tsn = fields.Float(string='Engine#1 TSN')
	engine1_csn = fields.Float(string='Engine#1 CSN')
	engine1_tslsv = fields.Float(string='Engine#1 TSLSV')
	engine1_cslsv = fields.Float(string='Engine#1 CSLSV')
	engine1_lastoh = fields.Date(string='Engine#1 Last OH')
	
	engine2 = fields.Char(string='Engine#2')
	engine2_tsn = fields.Char(string='Engine#2 TSN')
	engine2_csn = fields.Float(string='Engine#2 CSN')
	engine2_tslsv = fields.Float(string='Engine#2 TSLSV')
	engine2_cslsv = fields.Float(string='Engine#2 CSLSV')
	engine2_lastoh = fields.Date(string='Engine#2 Last OH')
	
	propeller = fields.Char(string="Propeller")
	propeller1 = fields.Char(string='Propeller#1')
	propeller1_tsn = fields.Float(string='Propeller#1 TSN')
	propeller1_tslsv = fields.Float(string='Propeller#1 TSLSV')
	propeller1_lastoh =fields.Date(string='Propeller#1 Last OH')
	
	propeller2 = fields.Char(string='Propeller#2')
	propeller2_tsn = fields.Float(string='Propeller#2 TSN')
	propeller2_tslsv = fields.Float(string='Propeller#2 TSLSV')
	propeller2_lastoh =fields.Date(string='Propeller#2 Last OH')

	propeller_sn = fields.Char(string='Propeller S/N')
	propeller_tsn = fields.Float(string='Propeller TSN')
	propeller_csn = fields.Float(string='Propeller CSN')
	propeller_tslsv = fields.Float(string='Propeller TSLSV')
	propeller_lastoh =fields.Date(string='Propeller Last OH')


class AircraftCategory(models.Model):
	_name = 'aircraft.category'
	name = fields.Char( string='Aircraft Category')
	description = fields.Char(string='Description')

class EngineType(models.Model):
	_name = 'engine.type'
	name = fields.Char( string='Engine Name')
	category = fields.Selection([('fixedwing','Fixed Wing'),('rotary','Rotary')],
		'Category')
	ownership = fields.Selection([('leasing','Leasing'),('owner','Owner')],string='Ownership')
	delivery_date = fields.Date('Delivery date')
	date_manufacture = fields.Date('Date of Manufacture')
	propeller_type_id = fields.Many2one('propeller.type','Propeller Type')
	esn = fields.Char(string='ESN')
	rgb = fields.Char(string='RGB S/N')
	propeller = fields.Char(string='Propeller S/N')
	tsn = fields.Char(string='TSN')
	csn = fields.Char(string='CSN')
	tslsv = fields.Char(string='TSLSV')
	cslsv = fields.Char(string='CSLSV')
	lessor = fields.Char(string='Lessor')
	start_lease = fields.Date('Start Lease')
	normal_termination = fields.Date('Normal Termination')
	engine_lastoh = fields.Date(string='Last OH')
	engine_hsi = fields.Date(string='Engine#1 HSI')
	engine_tsn = fields.Float(string='TSN')
	engine_csn = fields.Float(string='Engine CSN')
	engine_tslsv = fields.Float(string='Engine TSLSV OH')
	engine_tslsv_hsi = fields.Float(string='Engine TSLSV HSI')
	engine_cslsv = fields.Float(string='Engine CSLSV OH')
	engine_cslsv_hsi = fields.Float(string='Engine CSLSV HSI')
	propeller_tsn = fields.Float(string='Propeller TSN')
	propeller_tslsv = fields.Float(string='Propeller TSLSV')
	propeller_lastoh =fields.Date(string='Propeller Last OH')
	
	
	

class PropellerType(models.Model):
	_name = 'propeller.type'
	name = fields.Char( string='Propeller Type')
	description = fields.Char(string='Description')

class DocumentDocument(models.Model):
	_name = 'document.document'
	name = fields.Char(string='Document Name')
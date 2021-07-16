# -*- coding: utf-8 -*-
from odoo import fields, models,api, _
import pytz
from odoo.addons.mail.models.mail_template import format_tz
from datetime import date, datetime, timedelta
from odoo.exceptions import UserError, AccessError

import logging
_logger = logging.getLogger(__name__)

class AircraftAcquisition(models.Model):
	_name = 'aircraft.acquisition'
	name = fields.Char(string='Registration No')
	aircraft_name = fields.Many2one('aircraft.aircraft', string='Aircraft Name')
	aircraft_type_id = fields.Many2one('aircraft.type', string='Aircraft Type')
	date_manufacture = fields.Date(string='Date of Manufacture')
	engine_type_id = fields.Many2one('engine.type', string='Engine Name')
	engine2_type_id = fields.Many2one('engine.type', string='Engine Name')
	
	propeller_type_id = fields.Many2one('propeller.type', string='Propeller Type')
	category = fields.Selection('Category' , related='aircraft_name.aircraft_categ')
	msn = fields.Char(string='MSN')
	esn1 = fields.Char(string='ESN#1')
	rgb1 = fields.Char(string='RGB#1 S/N')
	esn2 = fields.Char(string='ESN#2')
	rgb2 = fields.Char(string='RGB#2 S/N')

	propeller1 = fields.Char(string='Propeller#1 S/N')
	propeller2 = fields.Char(string='Propeller#2 S/N')
	rh_ldg = fields.Char(string='RH LDG S/N')
	lh_ldg = fields.Char(string='LH LDG S/N')
	n_ldg = fields.Char(string='N LDG S/N')
	apu = fields.Char(string='APU S/N')

	airframe = fields.Char(string='Airframe')
	airframe_tsn = fields.Float(string='Airframe TSN')
	airframe_csn = fields.Float(string='Airframe CSN')
	airframe_lastoh = fields.Date(string='Airframe Last Inspection')
	
	rh_ldg_csn = fields.Float(string='RH LDG CSN')
	rh_ldg_lastoh = fields.Date(string='RH LDG Last OH')
	lh_ldg_csn = fields.Float(string='LH LDG CSN')
	lh_ldg_lastoh = fields.Date(string='LH LDG Last OH')
	n_ldg_csn = fields.Float(string='N LDG CSN')
	n_ldg_lastoh = fields.Date(string='N LDG Last OH')


	#engine = fields.Char(string='Engine')
	#engine1 = fields.Char(string='Engine#1')
	engine1_tsn = fields.Float(string='Engine#1 TSN')
	engine1_csn = fields.Float(string='Engine#1 CSN')
	engine1_tslsv = fields.Float(string='Engine#1 TSLSV OH')
	engine1_tslsv_hsi = fields.Float(string='Engine#1 TSLSV HSI')
	engine1_cslsv = fields.Float(string='Engine#1 CSLSV OH')
	engine1_cslsv_hsi = fields.Float(string='Engine#1 CSLSV HSI')
	
	engine1_lastoh = fields.Date(string='Engine#1 Last OH')
	engine1_hsi = fields.Date(string='Engine#1 HSI')
	
	#engine2 = fields.Char(string='Engine#2')
	engine2_tsn = fields.Char(string='Engine#2 TSN')
	engine2_csn = fields.Float(string='Engine#2 CSN')
	engine2_tslsv = fields.Float(string='Engine#1 TSLSV OH')
	engine2_tslsv_hsi = fields.Float(string='Engine#1 TSLSV HSI')
	engine2_cslsv = fields.Float(string='Engine#1 CSLSV OH')
	engine2_cslsv_hsi = fields.Float(string='Engine#1 CSLSV HSI')
	engine2_lastoh = fields.Date(string='Engine#2 Last OH')
	engine2_hsi = fields.Date(string='Engine#2 HSI')
	
	propeller = fields.Char(string="Propeller S/N")
	propeller1 = fields.Char(string='Propeller#1 S/N')
	propeller1_tsn = fields.Float(string='Propeller#1 TSN')
	propeller1_tslsv = fields.Float(string='Propeller#1 TSLSV')
	propeller1_lastoh =fields.Date(string='Propeller#1 Last OH')
	
	propeller2 = fields.Char(string='Propeller#2 S/N')
	propeller2_tsn = fields.Float(string='Propeller#2 TSN')
	propeller2_tslsv = fields.Float(string='Propeller#2 TSLSV')
	propeller2_lastoh =fields.Date(string='Propeller#2 Last OH')

	#aircraft_lease_status = fields.Selection([('lessor','Lessor'),('startlease','Start Lease'),
	#	('termination','Normal Termination')], string='Aircraft Lease Status')
	ownership = fields.Selection([('leasing','Leasing'),('owner','Owned')],string='Ownership')
	delivery_date = fields.Date('Delivery Date')
	lessor = fields.Char(string='Lessor')
	start_lease = fields.Date('Start Lease')
	normal_termination = fields.Date('Normal Termination')
	engine_ownership = fields.Selection([('leasing','Leasing'),('owner','Owner')],string='Engine Ownership')

	engine_esn = fields.Char(string='Engine ESN')
	engine_rgb = fields.Char(string='Engine RGB S/N')

	propeller_sn = fields.Char(string='Propeller S/N')
	propeller_tsn = fields.Float(string='Propeller TSN')
	propeller_csn = fields.Float(string='Propeller CSN')
	propeller_tslsv = fields.Float(string='Propeller TSLSV')
	propeller_lastoh =fields.Date(string='Propeller Last OH')

	document_ids = fields.One2many('document.certificate','acquisition_id', 'Document Certificates')


class DocumentCertificate(models.Model):
	_name = 'document.certificate'
	acquisition_id = fields.Many2one('aircraft.acquisition','Document Certificates')
	document_id = fields.Many2one('document.document')
	file_data = fields.Binary()
	date_expired = fields.Date('Date Expired')

class EngineSpare(models.Model):
	_name = 'engine.spare'
	name = fields.Many2one('engine.type','Engine Spare')
	acquisition_id = fields.Many2one('aircraft.acquisition',
		string ='Engine Spare for')
	description = fields.Text('Description')
	date_pemasangan = fields.Date('Tanggal Pemasangan')
	date_penurunan = fields.Date('Tanggal Penurunan')
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

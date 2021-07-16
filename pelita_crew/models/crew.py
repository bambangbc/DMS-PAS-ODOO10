# -*- coding: utf-8 -*-
from odoo import fields, models,api, _
import pytz
from odoo.addons.mail.models.mail_template import format_tz
from datetime import date, datetime, timedelta
from odoo.exceptions import UserError, AccessError

import logging
_logger = logging.getLogger(__name__)

RATING_QUALIFICATION = [
	('captain','Captain'),
	('firstofficer','First Officer'),
    ('foo','Flight Operation Officer'),
	('fa','Flight Attendant'),
	('fa1','Flight Attendant 1'),
	('fa2','Flight Attendant 2')
]

class HrCrew(models.Model):
	_inherit = 'hr.employee'

	qualification_id = fields.Many2one('hr.qualification', string='Qualification')  #required=True,
	religion = fields.Selection([('islam','Islam'),('kristen','Kristen Protestan'),
		('katolik','Katolik'),('hindu','Hindu'),('budha','Budha')],'Religions')
	employee_no = fields.Char('Employee Number')
	date_employee = fields.Date('Date Employee')
	pilot_categ_id = fields.Many2one('pilot.category', string='Pilot Category')  #, required=True
	crew_categ_id = fields.Many2one('crew.category', string='Crew Category')
	crew_categ = fields.Selection([('fixedwing','Fixed Wing'),('rotary','Rotary Wing')], string="Crew Category") #required=True,
	license_no = fields.Char(string='License Number')
	instructor_id = fields.Many2one('hr.employee', string='Instructor')
	otr_no = fields.Char(string='OTR Number')
	ground_instructor = fields.Boolean(string='Ground Instructor')
	flight_instructor = fields.Boolean(string='Flight Instructor')
	simulator_instructor = fields.Boolean(string='Simulator Instructor')
	company_check_pilot = fields.Boolean(string='Company Check Pilot')
	place_of_birth = fields.Char(string='Place of Birth')
	flying_hours_ids = fields.One2many('flying.hours','crew_id', string='Flying Hours')
	duty_time_ids = fields.One2many('crew.duty.time','crew_id', string='Duty Time')
	rating_ids = fields.One2many('rating.qualification','employee_id')
	cv_ids = fields.One2many('hr.cv', 'employee_id')
	address = fields.Char(string='Home Address')
	work_address = fields.Char(string='Work Address')
	is_crew = fields.Boolean(string='Is a Crew', default=False)

	@api.onchange('category_ids')
	def _onchange_category_ids(self):
		if not self.category_ids:
			return
		list_tags = [tag.name for tag in self.category_ids]
		# for tag in self.category_ids:
		# 	list_tags.append(tag.name)
		if ('Crew' in list_tags) or ('Technician' in list_tags):
			self.is_crew = True
		else:
			self.is_crew = False

	
class HrCv(models.Model):
	_name = 'hr.cv'

	employee_id = fields.Many2one('hr.employee','Full Name')
	image = fields.Binary('Photo', related='employee_id.image')
	image_medium = fields.Binary('Medium-sized photo', related='employee_id.image_medium')
	image_smal = fields.Binary('Small-sized photo', related='employee_id.image_small')
	
	employee_no = fields.Char('Employee Number', related='employee_id.employee_no')
	qualification = fields.Char('Qualification', related='employee_id.qualification_id.name')
	marital = fields.Selection('Marital', related='employee_id.marital')
	place_of_birth = fields.Char('Place of Birth', related='employee_id.place_of_birth')
	birthday = fields.Date('Date of Birth', related='employee_id.birthday')
	gender = fields.Selection('Sex', related='employee_id.gender')
	religion = fields.Selection('Religion', related='employee_id.religion')
	work_email = fields.Char('Work Email',related='employee_id.work_email')
	#address = fields.Char('Address',related='employee_id.address_id.street')
	address = fields.Char('Address',related='employee_id.address')
	mobile_phone = fields.Char('Mobile Phone', related='employee_id.mobile_phone')
	home_phone = fields.Char('Home Phone', related='employee_id.work_phone')
	pilot_categ = fields.Char('Pilot Category',related='employee_id.pilot_categ_id.name')
	crew_categ = fields.Char('Crew Category', related='employee_id.crew_categ_id.name')
	license_no = fields.Char('License Number', related='employee_id.license_no')
	otr_no = fields.Char('OTR Number', related='employee_id.otr_no')
	instructor = fields.Char('Instructor',related='employee_id.instructor_id.name')
	date_employee =fields.Date('Date of Employee', related='employee_id.date_employee')
	education_ids = fields.One2many('hr.education','cv_id')
	carrier_ids = fields.One2many('hr.carrier','cv_id')
	train_ids = fields.One2many('hr.training','cv_id')
	document_ids = fields.One2many('hr.document','cv_id')



class HrEducation(models.Model):
	_name = 'hr.education'
	cv_id = fields.Many2one('hr.cv')
	name = fields.Char('Education Name')
	year = fields.Char('Year')
	location = fields.Char('Location')



class HrCarrier(models.Model):
	_name = 'hr.carrier'
	cv_id = fields.Many2one('hr.cv')
	name = fields.Char('Title')
	company_name = fields.Char('Company Name')
	year_from = fields.Char('Year From')
	year_until = fields.Char('Year Until')


class HrTraining(models.Model):
	_name = 'hr.training'

	cv_id = fields.Many2one('hr.cv')
	training_id = fields.Many2one('training.operation')
	date_training = fields.Date('Date')
	training_type = fields.Selection([('mandatory','Mandatory'),('nonmandatory',
		'Non Mandatory')],'Training Type')
	valid_from = fields.Date('Valid From')
	valid_to = fields.Date('Valid To')
	upload_certificate = fields.Binary()



class HrDocument(models.Model):
	_name = 'hr.document'

	cv_id = fields.Many2one('hr.cv')
	name = fields.Char('Document Name')
	date_doc = fields.Date('Date')
	next_due = fields.Date('Next Due')
	upload_doc = fields.Binary()



class RatingQualification(models.Model):
	_name = 'rating.qualification'

	employee_id = fields.Many2one('hr.employee','Crew')
	aircraft_id = fields.Many2one('aircraft.aircraft','Aircraft')
	rating_qualification = fields.Selection(RATING_QUALIFICATION,'Rating Qualification')
	# rating_qualification= fields.Selection([('captain','Captain'),
	# 	('firstofficer','First Officer'),('fa','Flight Attendant'),
	# 	('fa1','Flight Attendant 1'),('fa2','Flight Attendant 2')],'Rating Qualification')
	


class FlyingHours(models.Model):
	_name = 'flying.hours'

	crew_id = fields.Many2one('hr.employee','Crew')
	fml_id = fields.Many2one('flight.maintenance.log','FML Number',readonly=True)
	fl_acquisition_id = fields.Many2one(string='Register No',related='fml_id.fl_acquisition_id')
	date_flight = fields.Datetime(string='Date', copy=False) #,related='fml_id.date_lt', store=True
	qualification_id = fields.Many2one('hr.qualification','Qualification', readonly=True)
	flying_hours = fields.Float(string='Flying Hours (Matrix)',readonly=True)
	eta = fields.Datetime(string='ETA from FML', copy=False)



class CrewDutyTime(models.Model):
	_name = 'crew.duty.time'

	crew_id = fields.Many2one('hr.employee', string='Crew', required=True)
	fml_id = fields.Many2one('flight.maintenance.log', string='FML Number', readonly=True, required=True)
	fl_acquisition_id = fields.Many2one(string='Register No',related='fml_id.fl_acquisition_id')
	date_flight = fields.Datetime('Date', related='fml_id.etd')
	time_in = fields.Float('Time In',readonly=True)
	time_out = fields.Float('Time Out', readonly=True)
	login = fields.Float('Login',readonly=True)
	logout = fields.Float('Logout',readonly=True)
	duty_time = fields.Float('Duty Time', readonly=True)



class HrQualification(models.Model):
	_name = 'hr.qualification'

	name = fields.Char('Qualification Name')



class PilotCategory(models.Model):
	_name = 'pilot.category'

	name = fields.Char('Pilot Category Name')



class CrewCategory(models.Model):
	_name = 'crew.category'

	name = fields.Char('Crew Category')



class TrainingOperation(models.Model):
	_name = 'training.operation'

	name = fields.Char(string='Name')
	code = fields.Char(string='Code')
	description = fields.Text(string='Description')
	training_categ = fields.Selection([('aircraft_training','Aircraft Training'),
		('ground_training','Mandatory Ground Training')],string='Training Category')
	qualification = fields.Selection([('pic','PIC'),('foo','FOO'),('ame','AME'),
		('avi','AVI'),('hlo','HLO'),('fa','FA'),('sic','SIC')],string='Qualification')
	training_line_ids = fields.One2many('training.operation.lines','training_id')



class TrainingOperationLines(models.Model):
	_name='training.operation.lines'

	training_id = fields.Many2one('training.operation','Training Lines')
	dgca_categ = fields.Selection([('dgca','DGCA'),('customer','Customer'),
			('com','COM')],string= 'DGCA Req')
	aircraft_categ_id = fields.Many2one('aircraft.category',string='Aircraft Category')
	frequency = fields.Selection([('once','Once'),('month','Month')],string='Frequency')



class CrewSchedule(models.Model):
	_name = 'crew.schedule'

	@api.multi
	@api.depends('name','aircraft_id')
	def name_get(self):
		result = []
		for plan in self:
			name = "%s" % (_("[" + str(plan.aircraft_id.name) + "] " + str(plan.name)) or _(plan.name))
			result.append((plan.id, name))
		return result

	def _default_employee(self):
		return self.env.context.get('default_employee_id') or self.env['hr.employee'].search([('user_id', '=', self.env.uid)], limit=1)

	#name = fields.Char('Schedule Name')
	name = fields.Selection([('Flight Duty','Flight Duty'),
		('Flight Training','Flight Training'),('Ground Training','Ground Training'),
		('In Active','In Active'),('Leave(Cuti)','Leave(Cuti)'),
		('Medical (License/Hatpen)','Medical (License/Hatpen)'),('Medical(Office)','Medical(Office)'),
		('Office Duty','Office Duty'),('Permit(Izin)','Permit(Izin)'),('Sick','Sick'),
		('Simulator','Simulator')],string='Schedule Name')
	employee_id = fields.Many2one('hr.employee', string='Crew', index=True, default=_default_employee)
	user_id = fields.Many2one('res.users', string='User', related='employee_id.user_id', related_sudo=True, store=True, default=lambda self: self.env.uid, readonly=True)
	schedule_type_id = fields.Many2one('crew.schedule.type','Schedule Type')
	date_from = fields.Datetime('Date From')
	date_to = fields.Datetime('Date To')
	aircraft_id = fields.Many2one('aircraft.aircraft','Aircraft Name')
	# aircraft_type = fields.Char('Aircraft Type')
	etd = fields.Datetime('ETD (local time)')
	eta = fields.Datetime('ETA (local time)')
	flight_type = fields.Selection([('commercial','Commercial'),
		('noncommercial','Non-Commercial')], string='Flight Type')
	customer_id = fields.Many2one('res.partner', string='Customer')
	#location_id = fields.Many2one('route.route','Location')
	remark = fields.Text('Remark')
	regulation_ids = fields.One2many('regulation.regulation','schedule_id','Regulation')
	training_ids = fields.One2many('training.crew','crew_id')
	is_flight_duty = fields.Boolean('Flight Duty')
	is_flight_training = fields.Boolean('Flight Training')
	is_ground_training = fields.Boolean('Ground Training')
	is_inactive = fields.Boolean('Inactive')
	is_leave = fields.Boolean('Leave(Cuti)')
	is_medical_license = fields.Boolean('Medical (License/Hatpen)')
	is_medical_office = fields.Boolean('Medical (Office)')
	is_office_duty = fields.Boolean('Office Duty')
	is_permit = fields.Boolean('Permit(Izin)')
	is_sick = fields.Boolean('Sick')
	is_simulator = fields.Boolean('Simulator')


class CrewScheduleActual(models.Model):
	_name = 'crew.schedule.actual'

	@api.multi
	@api.depends('name','aircraft_id')
	def name_get(self):
		result = []
		for plan in self:
			name = "%s" % (_("[" + str(plan.aircraft_id.name) + "] " + str(plan.name)) or _(plan.name))
			result.append((plan.id, name))
		return result

	def _default_employee(self):
		return self.env.context.get('default_employee_id') or self.env['hr.employee'].search([('user_id', '=', self.env.uid)], limit=1)

	#name = fields.Char('Schedule Name')
	name = fields.Selection([('Flight Duty','Flight Duty'),
		('Flight Training','Flight Training'),('Ground Training','Ground Training'),
		('In Active','In Active'),('Leave(Cuti)','Leave(Cuti)'),
		('Medical (License/Hatpen)','Medical (License/Hatpen)'),('Medical(Office)','Medical(Office)'),
		('Office Duty','Office Duty'),('Permit(Izin)','Permit(Izin)'),('Sick','Sick'),
		('Simulator','Simulator')],string='Schedule Name', readonly=True)
	employee_id = fields.Many2one('hr.employee', string='Crew', index=True, default=_default_employee, readonly=True)
	user_id = fields.Many2one('res.users', string='User', related='employee_id.user_id', related_sudo=True, store=True,
							  default=lambda self: self.env.uid, readonly=True)
	fml_id = fields.Many2one('flight.maintenance.log', string='FML Number', readonly=True, index=True, ondelete='cascade')
	#crew_id = fields.Many2one('hr.employee','Crew')
	schedule_type_id = fields.Many2one('crew.schedule.type', string='Schedule Type', readonly=True)
	date_from = fields.Datetime('Date From', readonly=True)
	date_to = fields.Datetime('Date To', readonly=True)
	aircraft_id = fields.Many2one('aircraft.aircraft','Aircraft Name', readonly=True)
	# aircraft_type = fields.Char('Aircraft Type',readonly=True)
	etd = fields.Datetime('ETD (local time)', readonly=True)
	eta = fields.Datetime('ETA (local time)', readonly=True)
	flight_type = fields.Selection([('commercial','Commercial'),
		('noncommercial','Non-Commercial')], string='Flight Type', readonly=True)
	customer_id = fields.Many2one('res.partner', string='Customer',readonly=True)
	#location_id = fields.Many2one('route.route','Location')
	remark = fields.Text('Remark',readonly=True)
	
	

class TrainingCrew(models.Model):
	_name='training.crew'
	crew_id = fields.Many2one('crew.schedule')
	training_id = fields.Many2one('training.operation')
	date_expired = fields.Date('Date Expired')

class RegulationCrew(models.Model):
	_inherit = 'regulation.regulation'
	schedule_id = fields.Many2one('crew.schedule')


class ScheduleType(models.Model):
	_name = 'crew.schedule.type'
	name = fields.Char('Name')
	color_name = fields.Selection([
        ('red', 'Red'),
        ('blue', 'Blue'),
        ('lightgreen', 'Light Green'),
        ('lightblue', 'Light Blue'),
        ('lightyellow', 'Light Yellow'),
        ('magenta', 'Magenta'),
        ('lightcyan', 'Light Cyan'),
        ('black', 'Black'),
        ('lightpink', 'Light Pink'),
        ('brown', 'Brown'),
        ('violet', 'Violet'),
        ('lightcoral', 'Light Coral'),
        ('lightsalmon', 'Light Salmon'),
        ('lavender', 'Lavender'),
        ('wheat', 'Wheat'),
        ('ivory', 'Ivory')], string='Color in Report', required=True, default='red')
    
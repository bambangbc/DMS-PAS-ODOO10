# -*- coding: utf-8 -*-
from math import modf, ceil, floor
from odoo import fields, models,api, _
from datetime import date, datetime, timedelta
# import pytz
# from odoo.addons.mail.models.mail_template import format_tz
from odoo.exceptions import UserError, AccessError
#from odoo.addons.pelita_crew import RATING_QUALIFICATION #.models.crew

import logging
_logger = logging.getLogger(__name__)

UOM_OPTION = [('lbs','Lbs'),('kgs','Kgs')]

RATING_QUALIFICATION = {
    'captain': 'Captain', 'firstofficer': 'First Officer',
    'fa': 'Flight Attendant', 'fa1': 'Flight Attendant 1', 'fa2': 'Flight Attendant 2'
}

def float_round(num, places = 0, direction = floor):
    return direction(num * (10**places)) / float(10**places)


class FlightMaintainLog(models.Model):
    _name = "flight.maintenance.log"
    _description = "Flight Maintenance Log [FML Form]"
    _inherit = ["mail.thread","ir.needaction_mixin"]
    _order = "id desc, name desc"

    name = fields.Char('Maintenance Log Number', required=True, index=True, readonly=True, states={'draft': [('readonly', False)]}, default=lambda self: self.env['ir.sequence'].next_by_code('maintenance.rotary'))
    #default=lambda self: _('New')
    fl_acquisition_id = fields.Many2one('aircraft.acquisition', string="Registration No",
                track_visibility='onchange', copy=True, readonly=True,  required=True,
                states={'draft': [('readonly', False)]})
    aircraft_type = fields.Selection(string='Aircraft Type',
                related='fl_acquisition_id.aircraft_name.aircraft_categ', readonly=True)
    date_lt = fields.Date('Date (LT)', readonly=True, states={'draft': [('readonly', False)]})
    etd = fields.Datetime('ETD (Local Time)', readonly=True,
                          states={'draft': [('readonly', False)]}, track_visibility='onchange') #required=True,
    eta = fields.Datetime('ETA (Local Time)', readonly=True,
                          states={'draft': [('readonly', False)]}, track_visibility='onchange')
    flight_schedule_id = fields.Many2one('flight.schedule','Flight Schedule', readonly=True,
                states={'draft': [('readonly', False)]})
    flight_number = fields.Char('Flight Number', readonly=True,
                                states={'draft': [('readonly', False)]}, track_visibility='onchange')
    flight_order_number = fields.Char('Flight Order Number', readonly=True,
                                      states={'draft': [('readonly', False)]}, track_visibility='onchange')
    location_id = fields.Many2one('base.operation', 'Location', readonly=True, states={'draft': [('readonly', False)]})
    customer_id = fields.Many2one('res.partner', string='Customer', domain=[('customer','=',True)],
                                  readonly=True, states={'draft': [('readonly', False)]})
    schedule_commercial_id = fields.Many2one('schedule.commercial','Schedule Commercial', readonly=True,
                                             states={'draft': [('readonly', False)]})
    flight_category = fields.Selection([('domestic','Domestic'), ('international','International')],'Flight Category',
                                       readonly=True, states={'draft': [('readonly', False)]})
    flight_type = fields.Selection([('commercial','Commercial'), ('noncommercial','Non-Commercial')], string='Flight Type',
                                   readonly=True, states={'draft': [('readonly', False)]})
    internal_flight_type_id = fields.Many2one('internal.flight.type','Internal Flight Type', readonly=True,
                                              states={'draft': [('readonly', False)]}, required=True)
    schedule_date = fields.Date('Schedule Date',readonly=True, states={'draft': [('readonly', False)]})
    maintenance_rotary_ids = fields.One2many('maintenance.rotary', 'rotary_id', string='Maintenance Rotary',
                                             readonly=True, states={'draft': [('readonly', False)]})
    maintenance_fixed_ids = fields.One2many('maintenance.fixedwing','fixedwing_id', string='Maintenance Fixed Wing',
                                            readonly=True, states={'draft': [('readonly', False)]})
    cancel_reason_id = fields.Many2one('irregularity.operation', 'Cancel Reason', readonly=True,
                                       states={'draft': [('readonly', False)]})  #reason.reason
    late_departure_id = fields.Many2one('irregularity.operation','Late Departure', readonly=True,
                                        states={'draft': [('readonly', False)]})  #reason.reason
    total_late = fields.Float(string='Total Late (minutes)', readonly=True, states={'draft': [('readonly', False)]})
    aircraft_unserviceable_reason = fields.Char('Aircraft Unserviceable Reason', readonly=True,
                                                states={'draft': [('readonly', False)]})
    rtb = fields.Float(string='RTB', readonly=True, states={'draft': [('readonly', False)]})
    rtb_reason = fields.Text('RTB Reason',readonly=True, states={'draft': [('readonly', False)]})
    corective_action_ids = fields.One2many('corrective.action', 'fixedwing_id', string='Corrective Action',
                            readonly=True, states={'draft': [('readonly', False)]})
    discrepancies_ids = fields.One2many('discrepancies.discrepancies', 'rotary_id', string='Discrepancies',
                            readonly=True, states={'draft': [('readonly', False)]})
    regulation_id = fields.Many2one('regulation.regulation', string='Regulation', readonly=True, states={'draft': [('readonly', False)]})
    fl_hours_price_id = fields.Many2one('flight.hours.price','Flight Hours Price')
    state = fields.Selection([('draft', 'Draft'),('validated', 'Validated'),('cancel', 'Cancelled')],
            string='Status', readonly=True, copy=False, index=True, track_visibility='onchange', default='draft')
    note = fields.Text('Internal Note')
    create_uid = fields.Many2one('res.users', 'Created by')
    department_id = fields.Many2one('hr.department', string='Department', index=True,
                                    default=lambda self: self.env.user.partner_id.department_id.id, readonly=True)
    date_validate = fields.Datetime(string='Validation Date', readonly=True, index=True)

    _sql_constraints = [
        ('number_fml_company_uniq', 'unique (name)', 'Maintenance log number must be unique!'),
        ('fml_date_greater', 'check(eta >= etd)', 'Error! FML -ETD- must be lower than FML -ETA-.'),
    ]

    @api.onchange('name')
    def _onchange_name(self):
        warning = {}
        result = {}
        if not self.name:
            return
        if self.name:
            exist_fml = self.search([('name', 'like', '%'+ _(self.name) +'%')])
            if len(exist_fml) != 0:
                warning = {
                    'title': _('Warning!'),
                    'message': _('FML number already exists in the database, please input with another number.'),
                }
                self.name = _('') or str('') or False
        if warning:
            result['warning'] = warning
        return result

    @api.onchange('fl_acquisition_id')
    def _onchange_fl_acquisition_id(self):
        warning = {}
        result = {}
        if not self.fl_acquisition_id:
            return
        if self.fl_acquisition_id and self.aircraft_type=='rotary':
            if len(self.maintenance_rotary_ids) > 0 and len(self.maintenance_rotary_ids.rotary_crew_ids) > 0:
                for mtc_line1 in self.maintenance_rotary_ids:
                    for crw1 in mtc_line1.rotary_crew_ids:
                        if (mtc_line1.fl_acquisition_id.id!=self.fl_acquisition_id.id) and \
                                (crw1.aircraft_id.id != self.fl_acquisition_id.aircraft_name.id):
                            warning = {
                                'title': _('Warning!'),
                                'message': _('Daftar kru (Crew List) sudah ditetapkan sebelumnya, Untuk mengubah '
                                             'A/C Registration No. Anda harus menghapus Daftar Kru didalam FML Lines '
                                             'terlebih dulu, setelah itu Anda dapat melakukan perubahan yang anda inginkan.'),
                            }
                            self.fl_acquisition_id = False
            self.name = self.env['ir.sequence'].next_by_code('maintenance.rotary') or _('New')
        if self.fl_acquisition_id and self.aircraft_type == 'fixedwing':
            if len(self.maintenance_fixed_ids) > 0 and len(self.maintenance_fixed_ids.fixed_crew_ids) > 0:
                for mtc_line2 in self.maintenance_fixed_ids:
                    for crw2 in mtc_line2.fixed_crew_ids:
                        if (mtc_line2.fl_acquisition_id.id != self.fl_acquisition_id.id) and (crw2.aircraft_id.id != self.fl_acquisition_id.aircraft_name.id):
                            warning = {
                                'title': _('Warning!'),
                                'message': _('Daftar kru (Crew List) sudah ditetapkan sebelumnya, Untuk mengubah A/C Registration No. Anda harus menghapus Daftar Kru didalam FML Lines terlebih dulu, setelah itu Anda dapat melakukan perubahan yang anda inginkan.'),
                            }
                            self.fl_acquisition_id = False
            self.name = self.env['ir.sequence'].next_by_code('maintenance.fixedwing') or _('New')

        if warning:
            result['warning'] = warning
        return result

    @api.onchange('flight_schedule_id')
    def _onchange_flight_schedule_id(self):
        if not self.flight_schedule_id:
            return
        if self.flight_schedule_id:
            if self.flight_schedule_id.fl_acquisition_id.id != self.fl_acquisition_id.id:
                warning = {
                    'title': _('Warning!'),
                    'message': _('The selected flight schedule [FS] does not match the A/C Registration No.!'),
                }
                self.flight_schedule_id = False
                self.flight_number = _("")
                self.flight_order_number = _("")
                self.schedule_date = False
                self.flight_type = _("")
                self.flight_category = _("")
                self.internal_flight_type_id = False
                self.schedule_commercial_id = False
                self.regulation_id = False
                return {'warning': warning}
            else:
                self.flight_number = self.flight_schedule_id.name
                self.flight_order_number = self.flight_schedule_id.flight_order_no
                self.schedule_date = self.flight_schedule_id.date_schedule
                self.flight_type = self.flight_schedule_id.flight_type
                self.flight_category = self.flight_schedule_id.flight_category
                self.internal_flight_type_id = self.flight_schedule_id.internal_flight_type_id.id
                self.schedule_commercial_id = self.flight_schedule_id.schedule_commercial_id.id
                self.regulation_id = self.flight_schedule_id.regulation_id.id
        return {}

    @api.multi
    def action_validate(self):
        csa_obj = self.env['crew.schedule.actual']
        fh_obj = self.env['flying.hours']
        cdt_obj = self.env['crew.duty.time']
        dept_id = self.env['res.users'].browse(self.env.uid).partner_id.department_id.id
        for fml in self:
            dom = ['&', ('fml_id', '=', fml.id)] or []
            if not(fml.etd):
                raise UserError(_('ETD should not be empty, please check again...'))
            if not (fml.eta):
                raise UserError(_('ETA should not be empty, please check again...'))
            etd_date = datetime.strptime(fml.etd, '%Y-%m-%d %H:%M:%S') + timedelta(hours=7) - timedelta(hours=1)
            eta_date = datetime.strptime(fml.eta, '%Y-%m-%d %H:%M:%S') + timedelta(hours=7, minutes=30)
            time_in = etd_date.time().hour + etd_date.time().minute / 60.0
            time_out = eta_date.time().hour + eta_date.time().minute / 60.0
            duty_time = time_out - time_in
            if duty_time < 0:
                duty_time = duty_time + 24
            if fml.aircraft_type == 'rotary' or fml.fl_acquisition_id.category == 'rotary':
                for item in fml.maintenance_rotary_ids:
                    for crew in item.rotary_crew_ids:
                        csa = csa_obj.search(dom + [('employee_id', '=', crew.crew_id.id)])
                        fh = fh_obj.search(dom + [('crew_id', '=', crew.crew_id.id)])
                        cdt = cdt_obj.search(dom + [('crew_id', '=', crew.crew_id.id)])
                        csa_vals = {
                            'name': 'Flight Duty',
                            'fml_id': fml.id,
                            'employee_id': crew.crew_id.id,
                            'date_from': fml.etd,
                            'date_to': fml.eta,
                            'flight_type': fml.flight_type,
                            'customer_id': fml.customer_id.id,
                            'aircraft_id': fml.fl_acquisition_id.aircraft_name.id,
                            # 'aircraft_type': fml.aircraft_type,
                            'etd': fml.etd,
                            'eta': fml.eta,
                            'department_id': fml.department_id and fml.department_id.id or dept_id,
                        }
                        fh_vals = {
                            'fml_id': fml.id,
                            'crew_id': crew.crew_id.id,
                            'qualification_id': crew.crew_id.qualification_id.id,
                            'flying_hours': item.block_matrix,
                            'date_flight': datetime.combine(datetime.strptime(fml.date_lt, '%Y-%m-%d'), datetime.min.time()),
                            'eta': fml.eta,
                        }
                        cdt_vals = {
                            'fml_id': fml.id,
                            'crew_id': crew.crew_id.id,
                            'time_in': time_in,
                            'login': time_in,
                            'time_out': time_out,
                            'logout': time_out,
                            'duty_time': duty_time,
                            'date_flight': datetime.combine(datetime.strptime(fml.date_lt, '%Y-%m-%d'),
                                                            datetime.min.time()),
                        }
                        if not csa:
                            csa.create(csa_vals)
                            fh.create(fh_vals)
                            cdt.create(cdt_vals)
                        else:
                            csa.write(csa_vals)
                            fh.write(fh_vals)
                            cdt.write(cdt_vals)
                            for t in item.rotary_time_ids:
                                fh.write({'flying_hours': t.in_service})

            if fml.aircraft_type == 'fixedwing' or fml.fl_acquisition_id.category == 'fixedwing':
                for item in fml.maintenance_fixed_ids:
                    for crew in item.fixed_crew_ids:
                        csa = csa_obj.search(dom + [('employee_id', '=', crew.crew_id.id)])
                        fh = fh_obj.search(dom + [('crew_id', '=', crew.crew_id.id)])
                        cdt = cdt_obj.search(dom + [('crew_id', '=', crew.crew_id.id)])
                        csa_values = {
                            'name': 'Flight Duty',
                            'fml_id': fml.id,
                            'employee_id': crew.crew_id.id,
                            'date_from': fml.etd,
                            'date_to': fml.eta,
                            'flight_type': fml.flight_type,
                            'customer_id': fml.customer_id.id,
                            'aircraft_id': fml.fl_acquisition_id.aircraft_name.id,
                            # 'aircraft_type': fml.aircraft_type,
                            'etd': fml.etd,
                            'eta': fml.eta,
                            'department_id': fml.department_id and fml.department_id.id or dept_id,
                        }
                        fh_values = {
                            'fml_id': fml.id,
                            'crew_id': crew.crew_id.id,
                            'qualification_id': crew.crew_id.qualification_id.id,
                            'flying_hours': item.flight_hour_matrix,
                            'date_flight': datetime.combine(datetime.strptime(fml.date_lt, '%Y-%m-%d'),
                                                            datetime.min.time()),
                            'eta': fml.eta,
                        }
                        cdt_values = {
                            'fml_id': fml.id,
                            'crew_id': crew.crew_id.id,
                            'time_in': time_in,
                            'login': time_in,
                            'time_out': time_out,
                            'logout': time_out,
                            'duty_time': duty_time,
                            'date_flight': datetime.combine(datetime.strptime(fml.date_lt, '%Y-%m-%d'),
                                                            datetime.min.time()),
                        }
                        if not csa:
                            csa.create(csa_values)
                            fh.create(fh_values)# flight_time_matrix
                            cdt.create(cdt_values)
                        else:
                            csa.write(csa_values)
                            fh.write(fh_values)  # flight_time_matrix
                            cdt.write(cdt_values)
            self.write({'state': 'validated', 'date_validate': fields.Datetime.now()})
        return True
    
    @api.multi
    def action_set_to_draft(self):
        for fml in self:
            csa_related = self.env['crew.schedule.actual'].search([('fml_id', '=', fml.id)])
            fh_related = self.env['flying.hours'].search([('fml_id', '=', fml.id)])
            cdt_related = self.env['crew.duty.time'].search([('fml_id', '=', fml.id)])
            if csa_related:
                csa_related.unlink()
            if fh_related:
                fh_related.unlink()
            if cdt_related:
                cdt_related.unlink()
        return self.write({'state': 'draft', 'date_validate': False})

    @api.multi
    def action_cancel(self):
        return self.write({'state': 'cancel'})

    # @api.model
    # def create(self, vals):
    #     if vals.get('aircraft_type') == _('rotary'):
    #         vals['name'] = self.env['ir.sequence'].next_by_code('maintenance.rotary') or _('New')
    #     else:
    #         vals['name'] = self.env['ir.sequence'].next_by_code('maintenance.fixedwing') or _('New')
    #     return super(FlightMaintainLog, self).create(vals)




class FlightRotaryCrew(models.Model):
    _name = 'flight.rotary.crew'

    @api.depends('crew_id', 'rotary_id')
    def _compute_qualification(self):
        for rec in self:
            if rec.crew_id:
                rate_qua_id = self.env['rating.qualification'].search(
                    [('employee_id', '=', rec.crew_id.id),
                     ('aircraft_id', '=', rec.rotary_id.fl_acquisition_id.aircraft_name.id)],
                        limit=1)
                if rate_qua_id:
                    rec.qualification = RATING_QUALIFICATION[rate_qua_id.rating_qualification]

    @api.depends('brief_time', 'flt')
    def _compute_total(self):
        for record in self:
            record.total_time = record.brief_time + record.flt

    @api.depends('rotary_id.block_matrix')
    def _compute_flt(self):
        for record in self:
            record.flt = record.rotary_id.block_matrix

    rotary_id = fields.Many2one('maintenance.rotary', index=True, required=True, ondelete='cascade')
    crew_id = fields.Many2one('hr.employee', string='Flight  Crew', track_visibility='onchange', domain="[('crew_categ', '=', 'rotary')]", required=True)
    crew_type_id = fields.Many2one('crew.type', string='Function')
    type_duty_id = fields.Many2one('type.duty', string='Type Duty')
    qualification = fields.Char('Rating Qualification', compute='_compute_qualification', store=True)
    is_instructor = fields.Boolean('Is Instructor')
    payment_type = fields.Selection([('vvip','VVIP'),('nonvvip','Non VVIP'),('testflight','Test Flight'),('training','Training Flight')],'Type')
    brief_time = fields.Float(string='Brief/De Brief')
    flt = fields.Float(string='Flight Time', compute='_compute_flt', store=True)
    total_time = fields.Float(string='Total', compute='_compute_total', store=True)
    fl_hours_price_id = fields.Many2one('flight.hours.price', string='Flight Hours Price', required=True)
    aircraft_id = fields.Many2one('aircraft.aircraft', string="Aircraft")
    #related='rotary_id.fl_acquisition_id.aircraft_name.id',

    @api.onchange('aircraft_id')
    def _onchange_aircraft_id(self):
        self.aircraft_id = self.rotary_id.fl_acquisition_id.aircraft_name.id or False

    @api.model
    def create(self, vals):
        if vals.get('is_instructor', False) and (not vals.get('brief_time') or vals.get('brief_time') <= 0.0):
            crew_name = self.env['hr.employee'].browse(vals.get('crew_id')).name if vals.get('crew_id', False) else _("")
            raise UserError(_('Brief/De Brief should not be empty, please check again...\n"%s" ') % crew_name)
        return super(FlightRotaryCrew, self).create(vals)

    @api.model
    def write(self, val):
        if val.get('is_instructor', False) and (not val.get('brief_time') or val.get('brief_time') <= 0.0):
            crew_name = self.env['hr.employee'].browse(val.get('crew_id')).name if val.get('crew_id', False) else _("")
            raise UserError(_('Brief/De Brief should not be empty, please check again...\n"%s" ') % crew_name)
        return super(FlightRotaryCrew, self).write(val)

    @api.onchange('crew_id')
    def _onchange_crew_id(self):
        warning = {}
        result = {}
        if not self.crew_id:
            return
        if self.crew_id.rating_ids:
            aircraft_ids = [x.aircraft_id.id for x in self.crew_id.rating_ids]
            if (self.aircraft_id.id not in aircraft_ids) or (self.rotary_id.fl_acquisition_id.aircraft_name.id not in aircraft_ids):
                warning = {
                    'title': _('Warning!'),
                    'message': _("%s crew is not available for %s aircraft, please search for other crew.") % (self.crew_id.name,self.aircraft_id.name or self.rotary_id.fl_acquisition_id.aircraft_name.name),
                }
                self.crew_id = False
                return {'warning': warning}
        # if warning:
        #     result['warning'] = warning
        return result

    # @api.onchange('aircraft_id')
    # def _onchange_aircraft_id(self):
    #     domain = {}
    #     self.aircraft_id = self.rotary_id and self.rotary_id.fl_acquisition_id and \
    #                        self.rotary_id.fl_acquisition_id.aircraft_name.id
    #     if self.aircraft_id or self.rotary_id.fl_acquisition_id:
    #         aircraft_id = self.aircraft_id.id or self.rotary_id.fl_acquisition_id.aircraft_name.id
    #         rate_qua_ids = self.env['rating.qualification'].search([('aircraft_id', '=', aircraft_id)])
    #         if rate_qua_ids:
    #             emp_ids = []
    #             for rt_qua in self.env['rating.qualification'].browse(rate_qua_ids.ids):
    #                 if rt_qua.employee_id.id not in emp_ids:
    #                     emp_ids.append(rt_qua.employee_id.id)
    #             if emp_ids and len(emp_ids)>0:
    #                 self.crew_id = emp_ids[0] or False
    #                 domain = {'': [('id', 'in', tuple(emp_ids))]}
    #     res = {}
    #     if domain:
    #         res['domain'] = domain
    #     return res



class RotaryRoute(models.Model):
    _name = 'rotary.route'

    rotary_id = fields.Many2one('maintenance.rotary', index=True, required=True, ondelete='cascade')
    route_id = fields.Many2one('route.operation','Route')
    distance_nm = fields.Float('Distance (NM)', related='route_id.distance_nm')
    distance_km = fields.Float('Distance (KM)', related='route_id.distance_km')
    penumpang = fields.Integer('Jumlah Penumpang')
    cycle = fields.Integer('Cycle')
    ldg = fields.Float(string='LDG')
    cycle_start1 = fields.Float(string='Cycle Start I')
    cycle_start2 = fields.Float(string='Cycle Start II')
    cycle_gg = fields.Float(string='GG')
    cycle_ft = fields.Float(string='FT')
    cargo = fields.Float('Cargo')
    fuel_added = fields.Float('Fuel Added')
    fuel_total = fields.Float('Fuel Total')
    customer_id = fields.Many2one('res.partner', string='Customer', domain=[('customer','=',True)], track_visibility='onchange')

    

class RotaryTime(models.Model):
    _name = "rotary.time"

    @api.depends('lift_off','landing')
    def _compute_total(self):
        for record in self:
            if record.landing - record.lift_off < 0:
                record.in_service = record.landing - record.lift_off + 24
            else:
                record.in_service = record.landing - record.lift_off
            record.in_service_matrix = record.in_service

    rotary_id = fields.Many2one('maintenance.rotary', index=True, required=True, ondelete='cascade')
    lift_off = fields.Float(string='Lift OFF')
    landing = fields.Float(string='Landing')
    in_service = fields.Float(string='In Service', readonly=True, compute='_compute_total', store=True)
    in_service_matrix = fields.Float(string='In Service Matrix', readonly=True, compute='_compute_total', store=True)




class MaintenanceRotary(models.Model):
    _name = "maintenance.rotary"
    _description = "FML Lines - Mtc Rotary"

    @api.one
    @api.depends('rotary_route_ids.ldg','rotary_route_ids.cycle_start1','rotary_route_ids.cycle_start2',
                 'rotary_route_ids.cycle_gg','rotary_route_ids.cycle_ft','rotary_route_ids.cargo',
                 'rotary_route_ids.fuel_added','rotary_route_ids.fuel_total','rotary_route_ids.penumpang')
    def _compute_all_attribute(self):
        for mt_rot in self:
            ldg = c_start1 = c_start2 = c_gg = c_ft = pax_no = cargo = fuel_added = fuel_total = 0.0
            for record in mt_rot.rotary_route_ids:
                ldg += record.ldg
                c_start1 += record.cycle_start1
                c_start2 += record.cycle_start2
                c_gg += record.cycle_gg
                c_ft += record.cycle_ft
                pax_no += record.penumpang
                cargo += record.cargo
                fuel_added += record.fuel_added
                fuel_total += record.fuel_total
            mt_rot.ldg = ldg
            mt_rot.cycle_start1 = c_start1
            mt_rot.cycle_start2 = c_start2
            mt_rot.cycle_gg = c_gg
            mt_rot.cycle_ft = c_ft
            mt_rot.pax_no = pax_no
            mt_rot.cargo = cargo
            mt_rot.fuel_added = fuel_added
            mt_rot.fuel_total = fuel_total

    @api.one
    @api.depends('cargo', 'uom_cargo')
    def _compute_cargo_conversion(self):
        for record in self:
            if record.uom_cargo:
                if record.uom_cargo == 'lbs':
                    record.cargo_conversi_lbs = record.cargo
                    record.cargo_conversi_kgs = record.cargo * 0.454
                elif record.uom_cargo == 'kgs':
                    record.cargo_conversi_kgs = record.cargo
                    record.cargo_conversi_lbs = record.cargo * 2.205

    @api.one
    @api.depends('rotor_stop', 'rotor_engage')
    def _compute_block(self):
        for record in self:
            if record.rotor_stop or record.rotor_engage:
                if record.rotor_stop - record.rotor_engage < 0:
                    record.block = record.rotor_stop - record.rotor_engage + 24
                else:
                    record.block = record.rotor_stop - record.rotor_engage
                record.block_matrix = record.block

    @api.depends('fuel_total', 'fuel_added')
    def _compute_fuel_consumption(self):
        for record in self:
            record.fuel_consumption = record.fuel_total - record.fuel_added

    @api.depends('current_user')
    def _compute_otr_no(self):
        for record in self:
            if record.current_user:
                record.otr_no = record.current_user.otr_no

    @api.multi
    def _default_current_user(self):
        return self.env['hr.employee'].search([('user_id', '=', self.env.uid or self.env.user.id)], limit=1).id


    rotary_id = fields.Many2one('flight.maintenance.log', index=True, required=True, ondelete='cascade')
    aircraft_type = fields.Selection(string='Aircraft Type',related='rotary_id.aircraft_type',
                    readonly=True)
    rotary_crew_ids = fields.One2many('flight.rotary.crew','rotary_id','Flight Crews', copy=True)
    rotary_route_ids = fields.One2many('rotary.route','rotary_id','Route', copy=True)
    rotary_time_ids = fields.One2many('rotary.time','rotary_id','Time', copy=True)
    rotor_engage = fields.Float(string='Rotor Engage', copy=True) #, required=True
    flight_hours = fields.Float(string='Flight Hours', copy=True)
    dispatch = fields.Float(string='Dispatch', copy=True)
    rotor_stop = fields.Float(string='Rotor Stop', copy=True) #, required=True
    block = fields.Float(string='Block',readonly=True, compute='_compute_block', store=True)
    block_matrix = fields.Float(string='Block Matrix',readonly=True,
    	compute='_compute_block', store=True)
	#inservice = fields.Float(string='In Service')
    pax_no = fields.Float(string='PAX No',compute='_compute_all_attribute', store=True)
    cargo = fields.Float(string='Cargo (Kgs/Lbs)',compute='_compute_all_attribute', store=True)
    cargo_conversi_lbs = fields.Float('Cargo Konversi (Lbs)', compute='_compute_cargo_conversion')
    cargo_conversi_kgs = fields.Float('Cargo Konversi(Kgs)', compute='_compute_cargo_conversion')
    sing_hoist_no = fields.Float(string='Sing/Hoist No', copy=True)
    ldg = fields.Float(string='LDG',compute='_compute_all_attribute', store=True)
    cycle_start1 = fields.Float(string='Cycle Start I',compute='_compute_all_attribute', store=True)
    cycle_start2 = fields.Float(string='Cycle Start II',compute='_compute_all_attribute', store=True)
    cycle_gg = fields.Float(string='GG',compute='_compute_all_attribute', store=True)
    cycle_ft = fields.Float(string='FT',compute='_compute_all_attribute', store=True)
    qualification = fields.Char('Qualification', copy=True)
    fml_no = fields.Char('FML Number', copy=True)
    remark = fields.Text('Remark')
    oil_added1 = fields.Float('Oil Added 1', copy=True)
    oil_added2 = fields.Float('Oil Added 2', copy=True)
    fuel_added = fields.Float('Fuel Added',compute='_compute_all_attribute', store=True)
    fuel_total = fields.Float('Fuel Total',compute='_compute_all_attribute', store=True)
    fuel_consumption = fields.Float('Fuel Consumption', compute='_compute_fuel_consumption', store=True)
    uom_cargo = fields.Selection(UOM_OPTION,'Weight') #[('kgs','Kgs'),('lbs','Lbs')]
    uom_oil1 = fields.Selection([('ltr','Ltr'),('tin','Tin')],'Weight', default='ltr', copy=True)
    uom_oil2 = fields.Selection([('ltr','Ltr'),('tin','Tin')],'Weight', default='ltr', copy=True)
    uom_fuel_added = fields.Selection([('ltr','Ltr'),('lbs','Lbs')],'Weight', default='ltr', copy=True)
    uom_fuel_total = fields.Selection([('ltr','Ltr'),('lbs','Lbs')],'Weight', default='ltr', copy=True)
    current_user = fields.Many2one('hr.employee', string='Sign', default=_default_current_user)
    otr_no = fields.Char('OTR Number')
    fl_acquisition_id = fields.Many2one('aircraft.acquisition', string="Registration No")
    state = fields.Selection([('draft', 'Draft'), ('validated', 'Validated'), ('cancel', 'Cancelled')],
                             related='rotary_id.state', string='Status', readonly=True, copy=False, index=True,
                             store=True, default='draft')

    @api.onchange('fl_acquisition_id')
    def onchange_fl_acquisition_id(self):
        self.fl_acquisition_id = self.rotary_id and self.rotary_id.fl_acquisition_id and self.rotary_id.fl_acquisition_id.id

    @api.multi
    def action_duplicate_line(self, default=None):
        self.copy(default={'rotary_id': self.rotary_id.id})
        model_obj = self.env['ir.model.data']
        data_id = model_obj._get_id('pelita_operation', 'fml_form')
        view_id = model_obj.browse(data_id).res_id
        return {
            'type': 'ir.actions.act_window',
            'name': _('Flight Maintenance Log'),
            'res_model': 'flight.maintenance.log',
            'res_id': self.rotary_id.id,
            'view_type': 'form',
            'view_mode': 'form',
            'view_id': view_id,
            'target': 'current',
            'nodestroy': True,
        }

    # @api.model
    # def create(self, vals):
    #     if vals.get('rotor_engage', False):
    #         if isinstance(vals['rotor_engage'], float):
    #             real_engage_time = modf(vals['rotor_engage'])[1] + round(
    #                 modf(vals['rotor_engage'])[0] * 100.0) / 60.0
    #             vals.update({'rotor_engage': real_engage_time})
    #     if vals.get('rotor_stop', False):
    #         if isinstance(vals['rotor_stop'], float):
    #             real_stop_time = modf(vals['rotor_stop'])[1] + round(
    #                 modf(vals['rotor_stop'])[0] * 100.0) / 60.0
    #             vals.update({'rotor_stop': real_stop_time})
    #     return super(MaintenanceRotary, self).create(vals)
    # 
    # @api.multi
    # def write(self, values):
    #     if 'rotor_engage' in values and values.get('rotor_engage'):
    #         if isinstance(values['rotor_engage'], float):
    #             real_engage_time = modf(values['rotor_engage'])[1] + round(modf(values['rotor_engage'])[0] * 100.0) / 60.0
    #             values.update({'rotor_engage': real_engage_time})
    #     if 'rotor_stop' in values and values.get('rotor_stop'):
    #         if isinstance(values['rotor_stop'], float):
    #             real_stop_time = modf(values['rotor_stop'])[1] + round(modf(values['rotor_stop'])[0] * 100.0) / 60.0
    #             values.update({'rotor_stop': real_stop_time})
    #     return super(MaintenanceRotary, self).write(values)

    # @api.multi
    # def _check_float_time(self, time_input):
    #     if not time_input:
    #         return {}
    #     result = {}
    #     warning = {}
    #     separator_not_allowed = ["-",",","+","(",")","/","_","{","}","[","]","<",">",";","*","!","=","|","?"]
    #     if isinstance(time_input, int):
    #         warning['title'] = _("Incorrect !!!")
    #         warning['message'] = _("Wrong time format inputted.\nAllowed format: '21.30' or '14:30'")
    #         result = {'warning': warning}
    #     else:
    #         for separator in separator_not_allowed:
    #             if len(str(time_input).split(separator))>1:
    #                 warning['title'] = _("Incorrect !!!")
    #                 warning['message'] = _("Wrong time format inputted.\nAllowed format: '21.30' or '14:30'")
    #         if warning:
    #             result = {'warning': warning}
    #     return result
    
    # @api.multi
    # @api.onchange('rotor_engage')
    # def onchange_rotor_engage(self):
    #     if not self.rotor_engage:
    #         return {}
    #     vals = {}
    #     result = {}
    #     warning = {}
    #     separator_not_allowed = ["-",",","+","(",")","/","_","{","}","[","]","<",">",";","*","!","=","|","?"]
    #     if isinstance(self.rotor_engage, float):
    #         vals['rotor_engage'] = modf(self.rotor_engage)[1] + round(modf(self.rotor_engage)[0] * 100.0) / 60.0
    #     elif isinstance(self.rotor_engage, int):
    #         warning['title'] = _("Incorrect !!!")
    #         warning['message'] = _("Wrong time format inputted.\nAllowed format: '21.30' or '14:30'")
    #         result = {'warning': warning}
    #     else:
    #         for separator in separator_not_allowed:
    #             if len(str(self.rotor_engage).split(separator))>1:
    #                 warning['title'] = _("Incorrect !!!")
    #                 warning['message'] = _("Wrong time format inputted.\nAllowed format: '21.30' or '14:30'")
    #         if warning:
    #             result = {'warning': warning}
    #     
    #     self.update(vals)
    #     return result
    # 
    # @api.multi
    # @api.onchange('rotor_stop')
    # def onchange_rotor_stop(self):
    #     self._check_float_time(self.rotor_stop)
        



class Discrepancies(models.Model):
    _name = 'discrepancies.discrepancies'

    rotary_id = fields.Many2one('flight.maintenance.log')
    name = fields.Char('Discrepancies')
    action = fields.Text('Action')



class TypeDuty(models.Model):
    _name = 'type.duty'

    name = fields.Char('Name')



class FlightFixedCrew(models.Model):
    _name = 'flight.fixed.crew'

    @api.depends('crew_id', 'fixed_id')
    def _compute_qualification(self):
        for rec in self:
            if rec.crew_id:
                rate_qua_id = self.env['rating.qualification'].search(
                    [('employee_id', '=', rec.crew_id.id),
                     ('aircraft_id', '=', rec.fixed_id.fl_acquisition_id.aircraft_name.id)],
                        limit=1)
                if rate_qua_id:
                    # rec.qualification = rate_qua_id.rating_qualification
                    rec.qualification = RATING_QUALIFICATION[rate_qua_id.rating_qualification]

    @api.depends('brief_time', 'flt')
    def _compute_total(self):
        for record in self:
            record.total_time = record.brief_time + record.flt

    @api.depends('fixed_id.flt_time_mtx')  #fixed_id.flt_time_mtx #flight_time_matrix
    def _compute_flt(self):
        for record in self:
            record.flt = record.fixed_id.flt_time_mtx   #flight_time_matrix

    fixed_id = fields.Many2one('maintenance.fixedwing', index=True, required=True, ondelete='cascade')
    crew_id = fields.Many2one('hr.employee', string='Flight Crew', track_visibility='onchange', domain="[('crew_categ', '=', 'fixedwing')]", required=True)
    crew_type_id = fields.Many2one('crew.type','Function')
    qualification = fields.Char('Rating Qualification', compute='_compute_qualification', store=True)
    is_instructor = fields.Boolean('Is Instructor')
    payment_type = fields.Selection([('vvip','VVIP'),('nonvvip','Non VVIP'),('testflight','Test Flight'),('training','Training Flight')],'Type')
    type_duty_id = fields.Many2one('type.duty','Type Duty')
    brief_time = fields.Float('Brief/De Brief')
    flt = fields.Float('Flight Time', compute='_compute_flt', store=True)
    total_time = fields.Float(string= 'Total', compute='_compute_total', store=True)
    fl_hours_price_id = fields.Many2one('flight.hours.price','Flight Hours Price', required=True)
    aircraft_id = fields.Many2one('aircraft.aircraft', string="Aircraft")
    #related='fixed_id.fl_acquisition_id.aircraft_name.id',

    @api.onchange('aircraft_id')
    def _onchange_aircraft_id(self):
        self.aircraft_id = self.fixed_id.fl_acquisition_id.aircraft_name.id or False

    @api.onchange('crew_id')
    def _onchange_crew_id(self):
        warning = {}
        result = {}
        if not self.crew_id:
            return
        if self.crew_id.rating_ids:
            aircraft_ids = [x.aircraft_id.id for x in self.crew_id.rating_ids]
            if (self.aircraft_id.id not in aircraft_ids) or (self.fixed_id.fl_acquisition_id.aircraft_name.id not in aircraft_ids):
                warning = {
                    'title': _('Warning!'),
                    'message': _("%s crew is not available for %s aircraft, please search for other crew.") % (self.crew_id.name,self.aircraft_id.name or self.fixed_id.fl_acquisition_id.aircraft_name.name),
                }
                self.crew_id = False
                return {'warning': warning}
        if warning:
            result['warning'] = warning
        return result

    @api.onchange('is_instructor')
    def _onchange_is_instructor(self):
        self.brief_time = False

    @api.model
    def create(self, vals):
        if vals.get('is_instructor', False) and (not vals.get('brief_time') or vals.get('brief_time') <= 0.0):
            crew_name = self.env['hr.employee'].browse(vals.get('crew_id')).name if vals.get('crew_id', False) else _("")
            raise UserError(_('Brief/De Brief should not be empty, please check again...\n"%s" ') % crew_name)
        return super(FlightFixedCrew, self).create(vals)

    @api.model
    def write(self, values):
        if values.get('is_instructor', False) and (not values.get('brief_time') or values.get('brief_time') <= 0.0):
            crew_name = self.env['hr.employee'].browse(values.get('crew_id')).name if values.get('crew_id', False) else _("")
            raise UserError(_('Brief/De Brief should not be empty, please check again...\n"%s" ') % crew_name)
        return super(FlightFixedCrew, self).write(values)

    @api.onchange('brief_time','flt') # if these fields are changed, call method
    def onchange_brief_time(self):
        self.total_time = self.brief_time + self.flt

    @api.onchange('fixed_id.flt_time_mtx')   #fixed_id.flt_time_mtx #flight_time_matrix
    def onchange_fixed_id(self):
        if self.fixed_id:
            self.flt = self.fixed_id.flt_time_mtx   #flight_time_matrix



class MaintenanceFixedWing(models.Model):
    _name ='maintenance.fixedwing'

    @api.depends('landing', 'take_off')
    def _compute_flight_hours(self):
        for record in self:
            if record.landing or record.take_off:
                if (record.landing - record.take_off) < 0:
                    record.flight_hours = (record.landing - record.take_off) + 24
                else:
                    record.flight_hours = (record.landing - record.take_off)

    @api.depends('block_on', 'block_off')
    def _calculate_flt_time(self):
        for rec in self: #if record.block_on or record.block_off:  #record.fixedwing_id:
            fl_time = rec.block_on - rec.block_off
            if fl_time < 0.0:
                fl_time += 24
            rec.update({'flt_time': fl_time})

    @api.depends('flt_time')
    def _calculate_flt_time_mtx(self):
        for rec in self:
            rec.update({'flt_time_mtx': float(rec.flt_time)})

    @api.depends('flight_hours')
    def _compute_flight_hour_matrix(self):
        for record in self:
            if record.flight_hours:
                record.flight_hour_matrix = float(record.flight_hours)

    @api.depends('pax', 'lugg', 'freight')
    def _compute_total(self):
        for record in self:
            if record.pax or record.lugg or record.freight:
                record.total = record.pax + record.lugg + record.freight

    @api.multi
    def _default_current_user(self):
        return self.env['hr.employee'].search([('user_id', '=', self.env.uid or self.env.user.id)], limit=1).id

    fixedwing_id = fields.Many2one('flight.maintenance.log', string='Fixed Wing', index=True, required=True, ondelete='cascade')
    aircraft_type = fields.Selection(string='Aircraft Type',related='fixedwing_id.aircraft_type', readonly=True, store=True)
    fixed_crew_ids = fields.One2many('flight.fixed.crew','fixed_id','Flight Crews', copy=True)
    customer_id = fields.Many2one('res.partner', string='Customer', domain=[('customer','=',True)], track_visibility='onchange', copy=True)
    take_off = fields.Float(string='Take OFF', copy=True)
    landing = fields.Float(string='Landing', copy=True)
    flight_hours = fields.Float(string='Flight Hours', readonly=True,
                compute='_compute_flight_hours', store=True)
    block_off = fields.Float(string='Chock OFF', copy=True) #, required=True
    block_on = fields.Float(string='Chock ON', copy=True) #, required=True
    flight_time = fields.Float(string='Flight Time')  #compute='_compute_flight_time', store=True
    flt_time = fields.Float(string='Flight Time', compute='_calculate_flt_time', store=True)
    flight_time_matrix = fields.Float(string='Flight Time Matrix')  #compute='_compute_flight_time_matrix', store=True
    flt_time_mtx = fields.Float(string='Flight Time Matrix', compute='_calculate_flt_time_mtx', store=True)
    flight_hour_matrix = fields.Float(string='Flight Hour Matrix',
                compute='_compute_flight_hour_matrix', store=True)
    no_pax = fields.Float(string='No PAX', copy=True)
    pax = fields.Float(string='PAX', copy=True)
    lugg = fields.Float('Lugg', copy=True)
    freight = fields.Float('Freight', copy=True)
    total = fields.Float('Total', readonly=True, compute='_compute_total', store=True)
    fuel_payload_available = fields.Float('Payload Available', copy=True)
    fuel_uplift = fields.Float('Fuel Uplift (Lt/Gal)', copy=True)
    fuel_total = fields.Float('Fuel Total(Lbs/Kg)', copy=True)
    fuel_cons = fields.Float('Fuel Cons(Lbs/Kg)', copy=True)
    fuel_rem = fields.Float('Fuel Rem (Lbs/Kg)', copy=True)
    oil_added1 = fields.Float('Oil Added 1', copy=True)
    oil_added2 = fields.Float('Oil added 2', copy=True)
    oil_added3 = fields.Float('Oil Added 3', copy=True)
    oil_added4 = fields.Float('Oil Added 4', copy=True)
    fml_no = fields.Char('FML Number', copy=True)
    remark = fields.Text('Remark', copy=True)
    uom_pax = fields.Selection(UOM_OPTION,'Weight', default='lbs')
    uom_lugg = fields.Selection(UOM_OPTION,'Weight', default='lbs')
    uom_freight = fields.Selection(UOM_OPTION,'Weight', default='lbs')
    uom_uplift = fields.Selection([('ltr','Ltr'),('gal','Gal')],'Weight', default='ltr')
    uom_total = fields.Selection(UOM_OPTION,'Weight', default='lbs')
    uom_cons = fields.Selection(UOM_OPTION,'Weight', default='lbs')
    uom_rem = fields.Selection(UOM_OPTION,'Weight', default='lbs')
    uom_fuel_total = fields.Selection(UOM_OPTION,'Weight', default='lbs')
    current_user = fields.Many2one('hr.employee','Sign', default=_default_current_user)
    otr_no = fields.Char('OTR Number')
    fl_acquisition_id = fields.Many2one('aircraft.acquisition', string="Registration No")
    state = fields.Selection([('draft', 'Draft'), ('validated', 'Validated'), ('cancel', 'Cancelled')],
            related='fixedwing_id.state', string='Status', readonly=True, copy=False, index=True, store=True, default='draft')
    route_id = fields.Many2one('route.operation', copy=True)
    from_id = fields.Many2one('area.operation', string='From', readonly=True, related='route_id.from_area_id')
    to_id = fields.Many2one('area.operation', string='To', readonly=True, related='route_id.to_area_id')
    distance_nm = fields.Float(string='Distance (NM)', related='route_id.distance_nm')
    distance_km = fields.Float(string='Distance (KM)', related='route_id.distance_km')

    @api.onchange('fl_acquisition_id')
    def onchange_fl_acquisition_id(self):
        self.fl_acquisition_id = self.fixedwing_id and self.fixedwing_id.fl_acquisition_id and self.fixedwing_id.fl_acquisition_id.id

    @api.multi
    def action_duplicate_line(self, default=None):
        self.copy(default={'fixedwing_id': self.fixedwing_id.id})
        model_obj = self.env['ir.model.data']
        data_id = model_obj._get_id('pelita_operation', 'fml_form')
        view_id = model_obj.browse(data_id).res_id
        return {
            'type': 'ir.actions.act_window',
            'name': _('Flight Maintenance Log'),
            'res_model': 'flight.maintenance.log',
            'res_id': self.fixedwing_id.id,
            'view_type': 'form',
            'view_mode': 'form',
            'view_id': view_id,
            'target': 'current',
            'nodestroy': True,
        }

    # @api.onchange('block_on','block_off') # if these fields are changed, call method
    # def change_flight_time(self):
    #     if self.block_on or self.block_off:
    #         if self.block_on - self.block_off < 0:
    #             self.flight_time = (self.block_on - self.block_off) + 24
    #         else:
    #             self.flight_time = self.block_on - self.block_off
    #     	#self.flight_time = self.flight_hours + 0.16666667
    # @api.onchange('current_user') # if these fields are changed, call method
    # def change_otr_no(self):
	 #    for record in self:
		#     if record.current_user:
		# 		record.otr_no = record.current_user.otr_no
	# @api.onchange('landing','take_off') # if these fields are changed, call method
	# def change_flight_hours(self):
	# 	if self.landing or self.take_off:
	# 		if self.landing - self.take_off < 0:
	# 			self.flight_hours = self.landing - self.take_off + 24
	# 		else:
	# 			self.flight_hours = self.landing - self.take_off
			
	# @api.onchange('pax','lugg','freight') # if these fields are changed, call method
	# def change_total(self):
	# 	if self.pax or self.lugg or self.freight:
	# 		self.total = self.pax + self.lugg + self.freight



class CorrectiveAction(models.Model):
	_name = 'corrective.action'
	fixedwing_id = fields.Many2one('flight.maintenance.log')
	name = fields.Char('Name')
	action = fields.Char('Action')





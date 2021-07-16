# -*- coding: utf-8 -*-
import pytz
import datetime as dt
from datetime import date
from odoo.addons.mail.models.mail_template import format_tz
from odoo import fields, models, api, tools, SUPERUSER_ID, _
from datetime import date, datetime, timedelta
from odoo.exceptions import UserError, AccessError

import logging

_logger = logging.getLogger(__name__)

RATING_QUALIFICATION = {
    'captain': 'Captain', 'firstofficer': 'First Officer',
    'fa': 'Flight Attendant', 'fa1': 'Flight Attendant 1', 'fa2': 'Flight Attendant 2'
}


class ScheduleType(models.Model):
    _name = 'schedule.type'

    name = fields.Char('Schedule Type')


class FlightSchedule(models.Model):
    _name = 'flight.schedule'
    _inherit = ['mail.thread', 'ir.needaction_mixin']
    _order = 'id desc, name desc'

    name = fields.Char('Flight Number', copy=False, readonly=True, states={'draft': [('readonly', False)]},
                       default=lambda self: _('New'))
    # default=lambda self: self.env['ir.sequence'].next_by_code('flight.schedule.number')
    fl_acquisition_id = fields.Many2one('aircraft.acquisition', string="Registration Number", copy=False, 
                                        track_visibility='onchange', readonly=True, states={'draft': [('readonly', False)]})
    flight_order_no = fields.Char('Flight Order Number', copy=False, readonly=True,
                                  states={'draft': [('readonly', False)]},
                                  default=lambda self: _('/'))
    base_operation_id = fields.Many2one('base.operation', 'Base Operation', required=True, track_visibility='onchange',
                                        readonly=True, states={'draft': [('readonly', False)]})
    date_schedule = fields.Date(string='Date', readonly=True, states={'draft': [('readonly', False)]})
    aircraft_id = fields.Many2one('aircraft.aircraft', string='Aircraft Name',
                                  related='fl_acquisition_id.aircraft_name',
                                  readonly=True, states={'draft': [('readonly', False)]})
    type_aircraft = fields.Selection(string='Aircraft Category', related='fl_acquisition_id.category')
    etd = fields.Datetime('ETD (local time)', required=True, readonly=True, states={'draft': [('readonly', False)]})
    eta = fields.Datetime('ETA (local time)', required=True, readonly=True, states={'draft': [('readonly', False)]})
    customer_id = fields.Many2one('res.partner', string='Customer', domain=[('customer', '=', True)],
                                  track_visibility='onchange', required=True, readonly=True,
                                  states={'draft': [('readonly', False)]})
    schedule_commercial_id = fields.Many2one('schedule.commercial', string='Schedule Commercial', readonly=True,
                                             states={'draft': [('readonly', False)]})
    flight_category = fields.Selection([('domestic', 'Domestic'),
                                        ('international', 'International')], string='Flight Category', readonly=True,
                                       states={'draft': [('readonly', False)]})
    flight_type = fields.Selection([('commercial', 'Commercial'),
                                    ('noncommercial', 'Non-Commercial')], string='Flight Type', readonly=True,
                                   states={'draft': [('readonly', False)]})
    internal_flight_type_id = fields.Many2one('internal.flight.type', string='Internal Flight Type', readonly=True,
                                              states={'draft': [('readonly', False)]})
    crew_standby_ids = fields.One2many('hr.crews', 'crew_stb_id', string='Crew Stand by',
                                       track_visibility='onchange', readonly=True,
                                       states={'draft': [('readonly', False)], 'validated': [('readonly', False)]})
    crew_assignment_ids = fields.One2many('hr.crews', 'crew_assign_id', string='Crew Assignment',
                                          track_visibility='onchange', readonly=True,
                                          states={'draft': [('readonly', False)], 'validated': [('readonly', False)]})
    is_standby = fields.Boolean(string='Stand By', readonly=True, states={'draft': [('readonly', False)]})
    route_ids = fields.One2many('route.flight.operation', 'schedule_id', string="Route Lines",
                                readonly=True, states={'draft': [('readonly', False)]}, copy=True)
    state = fields.Selection([('draft', 'Draft'), ('validated', 'Validated'),
                              ('setcrew', 'Crew Set'), ('cancel', 'Cancelled')],
                             string='Status', readonly=True, copy=False, index=True,
                             track_visibility='onchange', default='draft')
    # sale_order_id = fields.Many2one('sale.order','Sales Order')
    start_date = fields.Datetime(string='Start', readonly=True, states={'draft': [('readonly', False)]})
    finish_date = fields.Datetime(string='Finish', readonly=True, states={'draft': [('readonly', False)]})
    regulation_id = fields.Many2one('regulation.regulation', string='Regulation', readonly=True,
                                    states={'draft': [('readonly', False)]})
    fl_hours_price_id = fields.Many2one('flight.hours.price', string='Flight Hours Price', readonly=True,
                                        states={'draft': [('readonly', False)]})
    aircraft_type_id = fields.Many2one('aircraft.type', string='Aircraft Type', readonly=True, store=False,
                                       states={'draft': [('readonly', False)]},
                                       related='fl_acquisition_id.aircraft_name.aircraft_type_id')
    assigned_technician_ids = fields.One2many('fs.assigned.technician', 'fl_schedule_id',
                                              string='Technician Assignment',
                                              readonly=True, states={'draft': [('readonly', False)],
                                                                     'validated': [('readonly', False)]})
    note = fields.Text('Internal Note')
    create_uid = fields.Many2one('res.users', 'Created by')
    reason_crew_allowed_ids = fields.One2many('fs.reason.crew.allowed', 'flt_schedule_id',
                                              string='Unregulated Crew', readonly=True)
    all_allowed = fields.Boolean(string='All Crew Allowed', readonly=True, default=False,
                                 states={'draft': [('readonly', False)], 'validated': [('readonly', False)]})

    _sql_constraints = [
        ('fs_no_company_uniq', 'unique (flight_order_no)', 'Flight Order Number must be unique!'),
        ('fs_date_greater', 'check(eta > etd)', 'Error! \nETD must be lower than ETA.'),
    ]

    @api.multi
    def action_set_to_draft(self):
        for schedule in self:
            fml_related = self.env['flight.maintenance.log'].search([('flight_schedule_id', '=', schedule.id)])
            if fml_related:
                for fml in fml_related:
                    if fml.state == 'validated':
                        raise UserError(_('Flight Schedules can not be set to draft because flight maintenance logs '
                                          '[FML:%s] have been validated') % fml.name)
                fml_related.action_set_to_draft()
                fml_related.unlink()
            for crew in schedule.crew_assignment_ids:
                crew.write({'allowed': False})
            unregulated_crew = self.env['fs.reason.crew.allowed'].search([('flt_schedule_id', '=', schedule.id)])
            if unregulated_crew:
                unregulated_crew.unlink()
        return self.write({'state': 'draft'})

    @api.onchange('fl_acquisition_id')
    def _onchange_fl_acquisition_id(self):
        self.type_aircraft = self.fl_acquisition_id.category or _("")

    @api.onchange('etd', 'eta')
    def _onchange_etd_eta(self):
        warning = {}
        result = {}
        if not self.etd:
            return
        if not self.eta:
            return
        if self.etd and self.eta and self.regulation_id:
            etd = datetime.strptime(self.etd, '%Y-%m-%d %H:%M:%S')
            eta = datetime.strptime(self.eta, '%Y-%m-%d %H:%M:%S')
            total_sec = (eta - etd).seconds
            current_hours = total_sec / 3600  # 1hour
            if current_hours > self.regulation_id.hour_per_day:
                warning = {
                    'title': _('Warning!'),
                    'message': _("Flight hours over Limit.\n [Flight Hour: %.2f <> Regulation(per Day): %.2f].") % (
                        current_hours, self.regulation_id.hour_per_day),
                }
                self.regulation_id = False
        if warning:
            result['warning'] = warning
        return result

    # @api.model
    # def create(self, vals):
    #     next_number = self.env['ir.sequence'].next_by_code('flight.schedule.number')
    #     if (not vals.get('name', False)) or (vals.get('name') == _('New')):
    #         vals['name'] = next_number or _('New')
    #     if (not vals.get('flight_order_no', False)) or (vals.get('flight_order_no') == _('/')):
    #         vals['flight_order_no'] = next_number or _('/')
    #     return super(FlightSchedule, self).create(vals)

    @api.multi
    def action_validate(self):
        # fml = self.env['flight.maintenance.log']
        for fs in self:
            if fs.name and fs.flight_order_no and fs.fl_acquisition_id:
                self.auto_create_fml()
            self.write({'state': 'validated'})
        return True

    @api.multi
    def action_cancel(self):
        for schedule in self:
            fml_related = self.env['flight.maintenance.log'].search([('flight_schedule_id', '=', schedule.id)])
            if fml_related:
                fml_related.action_cancel()
        return self.write({'state': 'cancel'})

    @api.onchange('regulation_id')
    def onchange_regulation_id(self):
        warning = {}
        result = {}
        if not self.regulation_id:
            return
        if self.etd and self.eta:
            etd = datetime.strptime(self.etd, '%Y-%m-%d %H:%M:%S') + timedelta(hours=7)
            eta = datetime.strptime(self.eta, '%Y-%m-%d %H:%M:%S') + timedelta(hours=7)
            total_sec = (eta - etd).seconds
            current_hours = total_sec / 3600  # 1hour
            if current_hours > self.regulation_id.hour_per_day:
                warning = {
                    'title': _('Warning!'),
                    'message': _("Flight hours over Limit.\n [Flight Hour: %.2f <> Regulation(per Day): %.2f].") % (
                        current_hours, self.regulation_id.hour_per_day),
                }
                self.regulation_id = False
        if warning:
            result['warning'] = warning
        return result

    @api.multi
    def auto_create_fml(self):
        dept_id = self.env['res.users'].browse(self.env.uid).partner_id.department_id.id
        for fs in self:
            self.env['flight.maintenance.log'].create({
                'fl_acquisition_id': fs.fl_acquisition_id and fs.fl_acquisition_id.id,
                'flight_schedule_id': fs.id,
                'flight_number': fs.name,
                'flight_order_number': fs.flight_order_no,
                'flight_category': fs.flight_category,
                'flight_type': fs.flight_type,
                'internal_flight_type_id': fs.internal_flight_type_id and fs.internal_flight_type_id.id,
                'schedule_commercial_id': fs.schedule_commercial_id and fs.schedule_commercial_id.id,
                'schedule_date': fs.date_schedule,
                'etd': fs.etd,
                'eta': fs.eta,
                'customer_id': fs.customer_id and fs.customer_id.id,
                'flight_category': fs.flight_category,
                'regulation_id': fs.regulation_id and fs.regulation_id.id,
                'location_id': fs.base_operation_id and fs.base_operation_id.id,
                'department_id': fs.department_id and fs.department_id.id or dept_id,
            })

    @api.multi
    def action_validation_crew_regulation(self):
        block_info, employee_block_ids, check_list = [], [], []
        fh_obj = self.env['flying.hours']
        for fs in self:
            # week_start = datetime.combine(date.fromordinal(etd.toordinal() - etd.weekday()), datetime.min.time())
            # week_end = datetime.combine(date.fromordinal(etd.toordinal() + (6 - etd.weekday())), datetime.min.time())
            # week_end = date.fromordinal(etd.toordinal() + (6 - etd.weekday())).strftime('%Y-%m-%d %H:%M:%S')
            etd = datetime.strptime(fs.etd, '%Y-%m-%d %H:%M:%S')  # + timedelta(hours=7)
            eta = datetime.strptime(fs.eta, '%Y-%m-%d %H:%M:%S')  # + timedelta(hours=7)
            week_start = date.fromordinal(etd.toordinal() - etd.weekday())
            week_end = datetime.combine(date.fromordinal(etd.toordinal() + (6 - etd.weekday())),
                                        datetime.min.time()) + timedelta(
                hours=23, minutes=59)
            first_dt_month = datetime(etd.year, etd.month, 1)
            end_dt_month = datetime(etd.year, etd.month + 1, 1, 23, 59) + timedelta(days=-1)
            first_dt_year = datetime(etd.year, 1, 1)
            end_dt_year = datetime(etd.year + 1, 1, 1, 23, 59) + timedelta(days=-1)
            diff_now = eta - etd
            total_sec = diff_now.seconds
            current_fly_hours = total_sec / 3600  # hour_dalam_day
            list_hours = [current_fly_hours]
            crew_and_techniciant_ids = [ca.crew_id.id for ca in fs.crew_assignment_ids if not ca.allowed]
            crew_and_techniciant_ids += [at.employee_id.id for at in fs.assigned_technician_ids]
            for emp_id in crew_and_techniciant_ids:
                self._cr.execute("""SELECT t.emp_id, c.name FROM employee_category_rel as t LEFT JOIN hr_employee_category as c 
                                ON t.category_id=c.id WHERE t.emp_id=%s and c.name IN %s """,
                                 (emp_id, tuple(['Crew', 'FOO'])))
                crew_foo_ids = [emp_id for emp_id, tags in self._cr.fetchall()]
                if crew_foo_ids:
                    employee_name = self.env['hr.employee'].browse(emp_id).name
                    # validation_Hour_per_Day
                    fly_hour_day_ids = fh_obj.search(['&', '&', ('crew_id', '=', emp_id),
                                                      ('date_flight', '=', dt.datetime.strftime(eta.date(),
                                                                                                tools.DEFAULT_SERVER_DATETIME_FORMAT)),
                                                      '|', ('eta', '>=', dt.datetime.strftime(etd,
                                                                                              tools.DEFAULT_SERVER_DATETIME_FORMAT)),
                                                      ('eta', '<=', dt.datetime.strftime(eta,
                                                                                         tools.DEFAULT_SERVER_DATETIME_FORMAT))])
                    total_hour_day = sum(list_hours + [x.flying_hours for x in fly_hour_day_ids])  # fly_hour_day_ids
                    if total_hour_day > self.regulation_id.hour_per_day:
                        check_list.append(False)
                        employee_block_ids.append(emp_id)
                        block_info.append("%s: Flying Hours: %.2f, Regulation(Hour per Day): %.2f" % (
                            employee_name, total_hour_day, self.regulation_id.hour_per_day))
                    # validasi_Hour_per_WEEK
                    fly_hour_week_ids = fh_obj.search(['&', '&', ('crew_id', '=', emp_id),
                                                       ('eta', '>=', dt.datetime.strftime(week_start,
                                                                                          tools.DEFAULT_SERVER_DATETIME_FORMAT)),
                                                       ('eta', '<=', dt.datetime.strftime(week_end,
                                                                                          tools.DEFAULT_SERVER_DATETIME_FORMAT))])
                    total_hour_week = sum(list_hours + [y.flying_hours for y in fly_hour_week_ids])
                    if total_hour_week > self.regulation_id.hour_per_week:
                        check_list.append(False)
                        employee_block_ids.append(emp_id)
                        block_info.append("%s: Flying Hours: %.2f, Regulation(Hour per Week): %.2f" % (
                            employee_name, total_hour_week, self.regulation_id.hour_per_week))
                    # validasi_crew_assign_per_month
                    fly_hour_month_ids = fh_obj.search(['&', '&', ('crew_id', '=', emp_id),
                                                        ('eta', '>=', dt.datetime.strftime(first_dt_month,
                                                                                           tools.DEFAULT_SERVER_DATETIME_FORMAT)),
                                                        ('eta', '<=', dt.datetime.strftime(end_dt_month,
                                                                                           tools.DEFAULT_SERVER_DATETIME_FORMAT))])
                    total_hour_month = sum(list_hours + [z.flying_hours for z in fly_hour_month_ids])
                    if total_hour_month > self.regulation_id.hour_per_month:
                        check_list.append(False)
                        employee_block_ids.append(emp_id)
                        block_info.append("%s: Flying Hours: %.2f, Regulation(Hour per Month): %.2f" % (
                            employee_name, total_hour_month, self.regulation_id.hour_per_month))
                    # validasi_Hour_per_Year
                    fly_hour_year_ids = fh_obj.search(['&', '&', ('crew_id', '=', emp_id),
                                                       ('eta', '>=', dt.datetime.strftime(first_dt_year,
                                                                                          tools.DEFAULT_SERVER_DATETIME_FORMAT)),
                                                       ('eta', '<=', dt.datetime.strftime(end_dt_year,
                                                                                          tools.DEFAULT_SERVER_DATETIME_FORMAT))])
                    total_hour_year = sum(list_hours + [a.flying_hours for a in fly_hour_year_ids])
                    if total_hour_year > self.regulation_id.hour_per_year:
                        check_list.append(False)
                        employee_block_ids.append(emp_id)
                        block_info.append("%s: Flying Hours: %.2f, Regulation(Hour per Year): %.2f" % (
                            employee_name, total_hour_year, self.regulation_id.hour_per_year))
                        # self.action_process_crew_approval([fs.id], emp_id, 'hour_per_year',
                        # 					total_hour_year, self.regulation_id.hour_per_year)
                        # raise UserError(_('Flight hours over Limit! [Hour per Year]\n\n[Flight hour(year): %.2f <> '
                        # 				'Regulation(year): %.2f].\nEmployee: %s') % (
                        # 	total_hour_year, self.regulation_id.hour_per_year, employee_name))
        return all(check_list), employee_block_ids, block_info

    @api.multi
    def action_process_crew_approval(self):
        self.ensure_one()
        ctx = dict(self.env.context or {})
        ir_model_data = self.env['ir.model.data']
        view_id = ir_model_data.get_object_reference('pelita_operation', 'view_flt_schedule_approve_crew_wzd')[1]
        check_list, employee_ids, block_info = self.action_validation_crew_regulation()
        ctx.update({
            'flt_schedule_ids': self._ids,
            'employee_ids': employee_ids,
            'description': block_info,
        })
        if (not check_list):
            return {
                'name': _('Approving Crew Unregulated'),
                'view_type': 'form',
                'view_mode': 'form',
                'res_model': 'flight.schedule.approve.crew',
                'type': 'ir.actions.act_window',
                'view_id': view_id,
                'domain': '[]',
                'context': ctx,
                'nodestroy': True,
                'target': 'new',
            }
        else:
            self.action_crew_schedule()

    @api.multi
    def action_crew_schedule(self):
        emp_obj = self.env['hr.employee']
        fml_obj = self.env['flight.maintenance.log']
        mtc_fw_obj = self.env['maintenance.fixedwing']
        mtc_rw_obj = self.env['maintenance.rotary']
        unregulated = self._context.get('unregulated', False)
        for schedule in self:
            if not schedule.route_ids:
                raise UserError(_('Route list can not be empty, please check again...'))
            if not schedule.crew_assignment_ids:
                raise UserError(_('List of assigned crews can not be empty, please check again...'))
            if not (schedule.etd):
                raise UserError(_('ETD should not be empty, please check again...'))
            if not (schedule.eta):
                raise UserError(_('ETA should not be empty, please check again...'))
            fml = fml_obj.search([('flight_schedule_id', '=', schedule.id)], limit=1)
            # self.action_validation_crew_regulation()  #validation_regulation
            if len(fml):  # autocreate FML lines (RW or FW) and Crew Schedule
                curr_usr_id = emp_obj.search([('user_id', '=', self.env.uid or self.env.user.id)], limit=1).id or False
                if fml.aircraft_type == 'rotary':  # ROTARY  # fixed_crew_ids #flight.fixed.crew
                    rw_route_vals, all_rw_crew, cycle_route = [], {}, {}
                    for route in schedule.route_ids:  # all_rw_crew = {route_id: [crew_id,crew_id,crew_id]}
                        crew_this_route = []
                        if len(all_rw_crew.keys()) > 0:
                            for rt_id in all_rw_crew.keys():
                                if route.route_id.id == rt_id:
                                    crew_this_route += all_rw_crew[route.route_id.id]
                        rw_crew_vals = []
                        for ca in schedule.crew_assignment_ids:  # (ca.crew_id.id not in all_rw_crew)
                            if (not ca.is_standby) and (ca.route_id.id == route.route_id.id) and \
                                    (ca.crew_id.id not in crew_this_route):
                                emp_data = {
                                    'crew_id': ca.crew_id.id,
                                    'crew_type_id': ca.crew_type_id.id,
                                    'fl_hours_price_id': ca.fl_hours_price_id.id,
                                    'aircraft_id': schedule.fl_acquisition_id.aircraft_name.id,
                                }
                                if unregulated:
                                    if ca.allowed:
                                        rw_crew_vals.append((0, 0, emp_data))
                                        if ca.route_id.id not in all_rw_crew.keys():
                                            all_rw_crew[ca.route_id.id] = [ca.crew_id.id]
                                        else:
                                            all_rw_crew[ca.route_id.id].append(ca.crew_id.id)
                                else:
                                    rw_crew_vals.append((0, 0, emp_data))
                                    if ca.route_id.id not in all_rw_crew.keys():
                                        all_rw_crew[ca.route_id.id] = [ca.crew_id.id]
                                    else:
                                        all_rw_crew[ca.route_id.id].append(ca.crew_id.id)
                        for at in schedule.assigned_technician_ids:
                            if (at.route_id.id == route.route_id.id) and (at.employee_id.id not in crew_this_route):
                                rw_crew_vals.append((0, 0, {
                                    'crew_id': at.employee_id.id,
                                    'fl_hours_price_id': at.fl_hours_price_id.id,  # schedule.fl_hours_price_id.id,
                                    'aircraft_id': schedule.fl_acquisition_id.aircraft_name.id,
                                }))
                                if at.route_id.id not in all_rw_crew.keys():
                                    all_rw_crew[at.route_id.id] = [at.employee_id.id]
                                else:
                                    all_rw_crew[at.route_id.id].append(at.employee_id.id)
                        if route.cycle not in cycle_route.keys():
                            cycle_route[route.cycle] = {
                                'current_user': curr_usr_id, #SUPERUSER_ID,
                                'rotary_id': fml.id,
                                'fl_acquisition_id': schedule.fl_acquisition_id.id,
                                'rotary_crew_ids': rw_crew_vals,  # [(0,0,{}),(0,0,{})]
                                'rotary_route_ids': [(0, 0,
                                                      {'route_id': route.route_id.id,
                                                       'customer_id': route.customer_id.id})],
                            }
                        else:
                            cycle_route[route.cycle]['rotary_crew_ids'] += rw_crew_vals
                            cycle_route[route.cycle]['rotary_route_ids'] += [(0, 0,
                                                                              {'route_id': route.route_id.id,
                                                                               'customer_id': route.customer_id.id})]

                    if len(cycle_route):
                        for vals in cycle_route.values():
                            mtc_rw_obj.create(vals)
                    if len(all_rw_crew.values()):
                        for rw_crew_ids in all_rw_crew.values():
                            for crew_id in rw_crew_ids:
                                self.auto_create_crew_schedule(crew_id, schedule)
                else:  # FIXEDWING
                    mtc_fw_vals, all_fw_crew = [], {}
                    for item in schedule.route_ids:  # fixed_crew_ids #flight.fixed.crew
                        crew_this_route = []
                        if len(all_fw_crew.keys()) > 0:
                            for rt_id in all_fw_crew.keys():
                                if item.route_id.id == rt_id:
                                    crew_this_route += all_fw_crew[item.route_id.id]
                        fw_crew_vals = []
                        for ca in schedule.crew_assignment_ids:  # (ca.crew_id.id not in all_fw_crew)
                            if (not ca.is_standby) and (ca.route_id.id == item.route_id.id) and \
                                    (ca.crew_id.id not in crew_this_route):
                                emp_data = {
                                    'crew_id': ca.crew_id.id,
                                    'crew_type_id': ca.crew_type_id.id,
                                    'fl_hours_price_id': ca.fl_hours_price_id.id,  # schedule.fl_hours_price_id.id,
                                    'aircraft_id': schedule.fl_acquisition_id.aircraft_name.id,
                                }
                                if unregulated:
                                    if ca.allowed:
                                        fw_crew_vals.append((0, 0, emp_data))
                                        if ca.route_id.id not in all_fw_crew.keys():
                                            all_fw_crew[ca.route_id.id] = [ca.crew_id.id]
                                        else:
                                            all_fw_crew[ca.route_id.id].append(ca.crew_id.id)
                                else:
                                    fw_crew_vals.append((0, 0, emp_data))
                                    if ca.route_id.id not in all_fw_crew.keys():
                                        all_fw_crew[ca.route_id.id] = [ca.crew_id.id]
                                    else:
                                        all_fw_crew[ca.route_id.id].append(ca.crew_id.id)
                        for at in schedule.assigned_technician_ids:
                            if (at.route_id.id == item.route_id.id) and (at.employee_id.id not in crew_this_route):
                                fw_crew_vals.append((0, 0, {
                                    'crew_id': at.employee_id.id,
                                    'fl_hours_price_id': at.fl_hours_price_id.id,  # schedule.fl_hours_price_id.id,
                                    'aircraft_id': schedule.fl_acquisition_id.aircraft_name.id,
                                }))
                                if at.route_id.id not in all_fw_crew.keys():
                                    all_fw_crew[at.route_id.id] = [at.employee_id.id]
                                else:
                                    all_fw_crew[at.route_id.id].append(at.employee_id.id)
                        mtc_fw_vals.append({
                            'fixedwing_id': fml.id,
                            'route_id': item.route_id.id,
                            'from_id': item.from_area_id.id,
                            'to_id': item.to_area_id.id,
                            'customer_id': item.customer_id.id,
                            'fl_acquisition_id': schedule.fl_acquisition_id.id,
                            'fixed_crew_ids': fw_crew_vals,
                            'current_user': curr_usr_id, #SUPERUSER_ID,
                        })

                    if len(mtc_fw_vals):
                        # raise UserError(_('Result: %s\n%s\n%s') % (fw_crew_vals,all_fw_crew,mtc_fw_vals))
                        for vals in mtc_fw_vals:
                            mtc_fw_obj.create(vals)
                    if len(all_fw_crew.values()):
                        for fw_crew_ids in all_fw_crew.values():
                            for crew_id in fw_crew_ids:
                                self.auto_create_crew_schedule(crew_id, schedule)

            self.write({'state': 'setcrew'})
        return True

    @api.multi
    def auto_create_crew_schedule(self, crew_id, schedule):
        dept_id = self.env['res.users'].browse(self.env.uid).partner_id.department_id.id
        return self.env['crew.schedule'].create({
            'name': 'Flight Duty',
            'employee_id': crew_id,
            'date_from': schedule.etd,
            'date_to': schedule.eta,
            'flight_type': schedule.flight_type,
            'customer_id': schedule.customer_id.id,
            'aircraft_id': schedule.fl_acquisition_id.aircraft_name.id,
            'etd': schedule.etd,
            'eta': schedule.eta,
            'department_id': schedule.department_id and schedule.department_id.id or dept_id,
        })

        # @api.onchange('all_allowed')
        # def onchange_all_allowed(self):
        # 	vals = self.all_selected_onchange(self.all_allowed, self.crew_assignment_ids)
        # 	if vals:
        # 		for k, v in vals['value'].iteritems():
        # 			setattr(self, k, v)
        #
        # @api.multi
        # def all_selected_onchange(self, all_allowed, line_ids):
        # 	if line_ids:
        # 		for index in range(len(line_ids)):
        # 			if line_ids[index][0] in (0, 1, 4):
        # 				if line_ids[index][2]:
        # 					line_ids[index][2].update({'allowed': all_allowed})
        # 				else:
        # 					if line_ids[index][0] == 4:
        # 						line_ids[index][0] = 1
        # 					line_ids[index][2] = {'allowed': all_allowed}
        # 		return {'value': {'crew_assignment_ids': line_ids}}

        # @api.multi #gak_jadi
        # def action_view_related_fml(self):
        # 	fs_ids = self.mapped('fml_ids')
        # 	action = self.env.ref('pelita_operation.fml_action').read()[0]
        # 	if len(fs_ids) > 1:
        # 		action['domain'] = [('id', 'in', fs_ids.ids)]
        # 	elif len(fs_ids) == 1:
        # 		action['views'] = [(self.env.ref('pelita_operation.fml_form').id, 'form')]
        # 		action['res_id'] = fs_ids.ids[0]
        # 	else:
        # 		action = {'type': 'ir.actions.act_window_close'}
        # 	return action


class ScheduleCommercial(models.Model):
    _name = 'schedule.commercial'

    name = fields.Char('Name')


class RouteFlightOperation(models.Model):
    _name = 'route.flight.operation'
    schedule_id = fields.Many2one('flight.schedule')
    route_id = fields.Many2one('route.operation')
    from_route = fields.Char('From', related='route_id.from_route_id.name')
    to_route = fields.Char('To', related='route_id.to_route_id.name')
    distance_nm = fields.Float('Distance (NM)', related='route_id.distance_nm')
    distance_km = fields.Float('Distance (KM)', related='route_id.distance_km')
    customer_id = fields.Many2one('res.partner', string='Customer', domain=[('customer', '=', True)],
                                  track_visibility='onchange')
    cycle = fields.Selection([('c1', 'First Cycle'), ('c2', 'Second Cycle'),
                              ('c3', 'Third Cycle'), ('c4', 'Fourth Cycle'), ('c5', 'Fifth Cycle'),
                              ], string='Cycle', copy=True)


class InternalFlightType(models.Model):
    _name = 'internal.flight.type'
    name = fields.Char('Name')


class HrCrews(models.Model):
    _name = 'hr.crews'
    _description = "Flight Schedule Crew"

    @api.depends('crew_id')
    def _compute_type(self):
        for record in self:
            if record.crew_id:
                rate_qua_id = self.env['rating.qualification'].search(
                    [('employee_id', '=', record.crew_id.id),
                     ('aircraft_id', '=', record.crew_assign_id.fl_acquisition_id.aircraft_name.id)],
                    limit=1)
                if rate_qua_id:
                    record.qualification = RATING_QUALIFICATION[rate_qua_id.rating_qualification]
                if record.crew_id.crew_categ == 'fixedwing':
                    record.crew_type = 'Fixed Wing'
                elif record.crew_id.crew_categ == 'rotary':
                    record.crew_type = 'Rotary Wing'

    # employee_id = fields.Many2one('hr.employee',string='Crew', track_visibility='onchange')
    crew_id = fields.Many2one('hr.employee', string='Crew', track_visibility='onchange')
    crew_stb_id = fields.Many2one('flight.schedule', string='Crew Stand By', ondelete='cascade', index=True)
    crew_assign_id = fields.Many2one('flight.schedule', string='Crew Assigntment', index=True, ondelete='cascade')
    crew_type = fields.Char('Crew Type', track_visibility='onchange', compute='_compute_type', readonly=True)
    category = fields.Char('category')
    qualification = fields.Char(string='Qualification', compute='_compute_type')
    is_standby = fields.Boolean(string='Crew StandBy')
    route_id = fields.Many2one('route.operation', string='Route')
    crew_type_id = fields.Many2one('crew.type', string='Function')
    fl_hours_price_id = fields.Many2one('flight.hours.price', string='Flight Hours Price')
    allowed = fields.Boolean(string='Allowed', default=False)

    @api.multi
    @api.onchange('crew_assign_id')
    def _onchange_crew_assign_id(self):
        domain = {}
        list_crew, list_route = [], []
        now = datetime.today().strftime('%Y-%m-%d')
        cv = self.env['hr.cv'].search([])
        for rec in cv:  # employee_id
            if rec.employee_id.crew_categ == self.crew_assign_id.fl_acquisition_id.category:
                for rating in rec.employee_id.rating_ids:
                    if rating.aircraft_id.id == self.crew_assign_id.fl_acquisition_id.aircraft_name.id:
                        for item in rec.train_ids:
                            if item.valid_to > now:
                                for doc in rec.document_ids:
                                    if doc.next_due > now:
                                        list_crew.append(rec.employee_id.id)
        for record in self:
            if record.crew_assign_id.route_ids:
                for route in record.crew_assign_id.route_ids:
                    if route.route_id:
                        list_route.append(route.route_id.id)
        domain.update({
            'crew_id': [('id', 'in', list_crew)],
            'route_id': [('id', 'in', list_route)],
        })
        return {'domain': domain}

    @api.multi
    @api.onchange('crew_id')  # if these fields are changed, call method
    def _onchange_crew_id(self):
        if self.crew_id:
            rate_qua_id = self.env['rating.qualification'].search(
                [('employee_id', '=', self.crew_id.id),
                 ('aircraft_id', '=', self.crew_assign_id.fl_acquisition_id.aircraft_name.id)],
                limit=1)
            if rate_qua_id:
                self.qualification = RATING_QUALIFICATION[rate_qua_id.rating_qualification]
            elif self.crew_id and self.crew_id.qualification_id:
                self.qualification = self.crew_id.qualification_id.name
                
            if self.crew_id.crew_categ == 'fixedwing':
                self.crew_type = 'Fixed Wing'
            elif self.crew_id.crew_categ == 'rotary':
                self.crew_type = 'Rotary Wing'


class CrewType(models.Model):
    _name = "crew.type"
    _description = "Crew Type"

    name = fields.Char('Crew Type')


class FlightAttendant(models.Model):
    _name = "flight.attendant"
    _description = "Flight Attendant"

    fixwing_id = fields.Many2one('maintenance.fixedwing')
    rotary_id = fields.Many2one('maintenance.rotary')
    crew_id = fields.Many2one('hr.employee', 'Flight Attendant/Other Crew')
    crew_type_id = fields.Many2one('crew.type', 'Crew Type')
    qualification = fields.Char('Qualification')


class ReasonReason(models.Model):
    _name = "reason.reason"
    _description = "Reason"

    name = fields.Char('Name')


class FSTechnicianAssignment(models.Model):
    _name = "fs.assigned.technician"
    _description = "Assigned Technician"

    fl_schedule_id = fields.Many2one('flight.schedule', 'Flight Schedule', ondelete='cascade', index=True)
    employee_id = fields.Many2one('hr.employee', string='Technician', ondelete='set null', index=True)
    route_id = fields.Many2one('route.operation', string='Route')
    fl_hours_price_id = fields.Many2one('flight.hours.price', string='Flight Hours Price')

    @api.multi
    @api.onchange('fl_schedule_id')
    def _onchange_fl_schedule_id(self):
        domain = {}
        list_tech, list_route = [], []
        self._cr.execute("""SELECT t.emp_id, c.name FROM employee_category_rel as t LEFT JOIN hr_employee_category as c 
				ON t.category_id=c.id WHERE c.name like %s """, ('%Technician%',))
        emp_ids = [emp_id for emp_id, tags in self._cr.fetchall()]
        for rec in self.env['hr.employee'].browse(emp_ids):
            if rec.crew_categ == self.fl_schedule_id.fl_acquisition_id.category:
                for rating in rec.rating_ids:
                    if rating.aircraft_id.id == self.fl_schedule_id.fl_acquisition_id.aircraft_name.id:
                        list_tech.append(rec.id)
        for record in self:
            if record.fl_schedule_id.route_ids:
                for route in record.fl_schedule_id.route_ids:
                    if route.route_id:
                        list_route.append(route.route_id.id)
        domain.update({
            'employee_id': [('id', 'in', list_tech)],
            'route_id': [('id', 'in', list_route)],
        })
        return {'domain': domain}


class FSReasonCrewAllowed(models.Model):
    _name = "fs.reason.crew.allowed"

    flt_schedule_id = fields.Many2one('flight.schedule', 'Flight Schedule', ondelete='cascade', index=True)
    crew_id = fields.Many2one('hr.employee', string='Crew', ondelete='set null', index=True)
    reason = fields.Text(string="Reason", help="Reason to Approve Flying Crew")
    approved_id = fields.Many2one('res.users', string='Approved by', default=lambda self: self.env.user)

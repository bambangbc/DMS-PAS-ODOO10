# -*- coding: utf-8 -*-
# © 2017 Ibrohim Binladin | ibradiiin@gmail.com | +62-838-7190-9782
from odoo import api, fields, models, _
from odoo.osv import expression
from odoo.exceptions import UserError
import logging
_logger = logging.getLogger(__name__)


class BaseOperation(models.Model):
    _inherit = 'base.operation'

    active = fields.Boolean(string='Status', default=True,
                            help="Set active to false to hide the tax without removing it.")



class AreaOperation(models.Model): #CITY-kota-Area
    _inherit = 'area.operation'

    active = fields.Boolean(string='Status', default=True,
                            help="Set active to false to hide the tax without removing it.")
    name = fields.Char(string='Area Name', required=True, track_visibility='onchange')
    code = fields.Char(string='Area Code', required=True, track_visibility='onchange')

    _sql_constraints = [
        ('area_code_uniq', 'unique (code)', 'The code of the area operation must be unique!')
    ]

    @api.multi
    def name_get(self):
        result = []
        for area in self:
            name = "%s" % (str(area.name) or _(''))
            if area.code:
                name = "%s" % (_("[" + str(area.code) + "] " + str(area.name)) or _(''))
            result.append((area.id, name))
        return result

    @api.model
    def name_search(self, name, args=None, operator='ilike', limit=100):
        args = args or []
        domain = []
        if name:
            domain = ['|', ('code', '=ilike', name + '%'), ('name', operator, '%' + name + '%')]
            if operator in expression.NEGATIVE_TERM_OPERATORS:
                domain = ['&', '!'] + domain[1:]
        area_ops = self.search(domain + args, limit=limit)
        return area_ops.name_get()



class IrregularityOperation(models.Model):
    _inherit = 'irregularity.operation'

    active = fields.Boolean(string='Status', default=True,
                            help="Set active to false to hide the tax without removing it.")



class RouteOperation(models.Model):
    _name = "route.operation"
    _inherit = ['route.operation', 'mail.thread', 'ir.needaction_mixin']

    @api.one
    @api.depends('from_area_id.name', 'to_area_id.name','route_line_ids.name')
    def _compute_flight_route(self):
        list_area = []
        if self.from_area_id:
            list_area.append(self.from_area_id.name)
        if self.route_line_ids:
            for rol in self.route_line_ids:
                list_area.append(rol.name.name)
        if self.to_area_id:
            list_area.append(self.to_area_id.name)
        self.flight_route = '%s' % (' >> '.join(list_area) or _(''))

    @api.one
    @api.depends('route_line_ids.name','from_area_id.name', 'to_area_id.name')
    def _compute_name(self):
        deskripsi = []
        if self.from_area_id:
            deskripsi.append(self.from_area_id.code)
        if self.route_line_ids:
            for rol in self.route_line_ids:
                if rol.name and rol.name.code:
                    deskripsi.append(rol.name.code)
        if self.to_area_id:
            deskripsi.append(self.to_area_id.code)
        self.name = '%s' % (' - '.join(deskripsi) or _(''))

    @api.one
    @api.depends('from_area_id.name', 'to_area_id.name', 'route_line_ids.name')
    def _compute_complete_route(self):
        ctx = dict(self._context)
        complete_txt = []
        if self.from_area_id:
            complete_txt.append(self.from_area_id.with_context(ctx).name_get()[0][1])
        if self.route_line_ids:
            for rol in self.route_line_ids:
                complete_txt.append(rol.with_context(ctx).name_get()[0][1])
        if self.to_area_id:
            complete_txt.append(self.to_area_id.with_context(ctx).name_get()[0][1])
        self.complete_route = '%s' % (' >> '.join(complete_txt) or _(''))

    name = fields.Char(string='Route Name', required=True, compute='_compute_name',
                       track_visibility='onchange', copy=False, index=True)
    description = fields.Text('Description')
    from_area_id = fields.Many2one('area.operation','Area From', required=True, track_visibility='onchange')
    to_area_id = fields.Many2one('area.operation','Area To', required=True, track_visibility='onchange')
    product_tmpl_id = fields.Many2one('product.template', string='Product Template')
    route_status = fields.Selection(related='product_tmpl_id.route_status', store=True, readonly=True)
    route_line_ids = fields.One2many('route.operation.line', 'route_opt_id', 
                                     string='Flight Route', copy=True, track_visibility='onchange')
    active = fields.Boolean(string='Status', default=True,
                            help="Set active to false to hide the tax without removing it.")
    flight_route = fields.Char('Flight Route', compute='_compute_flight_route', store=False)
    product_tmpl_ok = fields.Boolean('Auto Created Product?', copy=False, default=False)
    status = fields.Selection([('validated', 'Validated'), ('invalid', 'Invalid')],
                                    string='Route Status', readonly=True)
    insert_area_id = fields.Many2one('area.operation', 'Route')
    complete_route = fields.Char(string='Complete Route', compute='_compute_complete_route', copy=False, index=True, store=True)

    _sql_constraints = [
        ('route_ops_name_uniq', 'unique (name)', 'Name of route operation must be unique!')
    ]

    @api.multi
    def name_get(self):
        result = []
        for route in self:
            name = "%s" % (str(route.name) or _(''))
            result.append((route.id, name))
        return result

    @api.model
    def name_search(self, name, args=None, operator='ilike', limit=100):
        args = args or []
        domain = []
        if name:
            domain = ['|', '|', ('complete_route', operator, '%' + name + '%'),
                      ('from_area_id.code', operator, '%' + name + '%'),
                      ('to_area_id.code', operator, '%' + name + '%')]
            if operator in expression.NEGATIVE_TERM_OPERATORS:
                domain = ['&', '!'] + domain[1:]
        route_ops = self.search(domain + args, limit=limit)
        return route_ops.name_get()

    @api.model
    def create(self, vals):
        route_ops = super(RouteOperation, self).create(vals)
        if (vals.get('name') or route_ops.name) and (vals.get('route_line_ids') or route_ops.route_line_ids):
            if vals.get('product_tmpl_ok', False):
                categ_id = self.env['product.category'].search(['|',('name', 'like', '%Route%'),
                                                                ('name', 'like', '%Flight Route%')], limit=1) or False
                uom_ids = self.env['product.uom'].search(
                        ['|', ('name', 'like', '%Hour%'), ('name', 'like', '%Hour(s)%')], limit=1)
                product_tmpl_id = self.env['product.template'].create({
                        'name': vals.get('name') or route_ops.name,
                        'type': 'service',
                        'categ_id': categ_id.id or 1,
                        'sale_ok': True,
                        'purchase_ok': False,
                        'uom_id': uom_ids and uom_ids.id or 1,
                        'uom_po_id': uom_ids and uom_ids.id or 1,
                        'flight_route_ok': True,
                        'description_sale': route_ops.name or str(''),     #description,
                        'route_status': 'validated',
                })
                if product_tmpl_id:
                    route_ops.write({'product_tmpl_id': product_tmpl_id.id})
        return route_ops

    @api.multi
    def write(self, vals):  #[(0, 0, {'name': self.from_area_id.id})]
        result = super(RouteOperation, self).write(vals)
        for route in self:
            if route.product_tmpl_id and route.product_tmpl_ok:
                if ('active' in vals or not vals.get('active')):  #route.active
                    route.product_tmpl_id.write({'active': route.active})
                if ('name' in vals or vals.get('name')):
                    route.product_tmpl_id.write({'name': vals.get('name')})
                if route.product_tmpl_id.description_sale != route.name:
                    route.product_tmpl_id.write({'description_sale': route.name})
        return result

    @api.multi
    def unlink(self):
        for route_ops in self:
            if route_ops.product_tmpl_id:
                route_ops.product_tmpl_id.unlink()
        return super(RouteOperation, self).unlink()

    @api.multi
    def action_route_status(self):
        for route_ops in self:
            if route_ops.product_tmpl_id:
                if self._context.get('action')=='validated':
                    route_ops.product_tmpl_id.write({'route_status': 'validated'})
                elif self._context.get('action')=='invalid':
                    route_ops.product_tmpl_id.write({'route_status': 'invalid'})
            else:
                if self._context.get('action')=='validated':
                    route_ops.write({'status': 'validated'})
                elif self._context.get('action')=='invalid':
                    route_ops.write({'status': 'invalid'})
        return True



class RouteOperationLines(models.Model):
    _name = "route.operation.line"
    _description = "Flight Route"
    _order = "sequence, id"

    route_opt_id = fields.Many2one('route.operation', string='Route Operation', index=True)
    name = fields.Many2one('area.operation','Route', required=True)
    additional_info = fields.Selection([('helipad','Helipad'),('fuel','Fuel Refill'),('fuelman','Fuel Man')], string='Additional Information')
    add_need_id = fields.Many2one('additional.flight.needs', string='Additional Information')
    flight_requisition_id = fields.Many2one('flight.requisition', string='Flight Requisition', index=True)
    sequence = fields.Integer(string='Urutan', default=1)



class FlightRequisition(models.Model):
    _name = "flight.requisition"
    _inherit = ['flight.requisition', 'mail.thread', 'ir.needaction_mixin']
    _order = 'id desc, name desc'

    name = fields.Char(string='Number', required=True, copy=False, readonly=True,
            states={'draft': [('readonly', False)]}, index=True, default=lambda self: _('New'))
    route_operation_id = fields.Many2one('route.operation', string='Route',
            readonly=True, states={'draft': [('readonly', False)]}, track_visibility='onchange')  #required=True,
    date_from = fields.Datetime(string='Date of Flight(From)', readonly=True, copy=True,
            states={'draft': [('readonly', False)]})
    date_to = fields.Datetime(string='Date of Flight (To)', readonly=True, copy=True,
            states={'draft': [('readonly', False)]})
    etd = fields.Datetime('ETD', readonly=True, copy=True, states={'draft': [('readonly', False)]}, help="Estimasi Time Departure")
    state = fields.Selection([('draft', 'Draft'),('validated', 'Validated'),('cancel', 'Cancelled')],
            string='Status', readonly=True, copy=False, index=True, track_visibility='onchange', default='draft')
    date_request = fields.Datetime(string='Date Request', readonly=True, copy=False,
            states={'draft': [('readonly', False)]})
    aircraft_id = fields.Many2one('aircraft.acquisition', 'Aircraft', required=True,
            readonly=True, states={'draft': [('readonly', False)]}, track_visibility='onchange')
    customer_id = fields.Many2one('res.partner', string='Customer', domain=[('customer','=',True)],
            readonly=True, states={'draft': [('readonly', False)]}, track_visibility='onchange')
    base_operation_id = fields.Many2one('base.operation', 'Base Operation', required=True,
            readonly=True, states={'draft': [('readonly', False)]})
    creator_id = fields.Many2one('res.users', string='Creator', index=True, track_visibility='onchange',
                              default=lambda self: self.env.user, readonly=True)
    route_line_ids = fields.One2many('route.operation.line', 'flight_requisition_id', string='Flight Route', copy=True)
    note = fields.Text('Internal Note')
    order_line_id = fields.Many2one('sale.order.line', 'Sales Order Line')
    order_id = fields.Many2one('sale.order', related='order_line_id.order_id', string='Sales Order', store=False,
                               readonly=True)
    requisition_route_ids = fields.One2many('flight.requisition.route.line', 'flight_requisition_id', string='Flight Route',
                                            copy=True, readonly=True, states={'draft': [('readonly', False)]})
    department_id = fields.Many2one('hr.department', string='Department', index=True, 
                                 default=lambda self: self.env.user.partner_id.department_id.id, readonly=True)

    @api.model
    def create(self, vals):
        if vals.get('name', _('New')) == _('New'):
            vals['name'] = self.env['ir.sequence'].next_by_code('flight.requisition') or _('New')
        result = super(FlightRequisition, self).create(vals)
        return result

    @api.multi
    def action_set_to_draft(self):
        return self.write({'state': 'draft'})

    @api.multi
    def action_validate(self):
        return self.write({'state': 'validated'})

    @api.multi
    def action_cancel(self):
        return self.write({'state': 'cancel'})



class FlightSchedule(models.Model):
    _name = 'flight.schedule'
    _inherit = ['flight.schedule', 'mail.thread', 'ir.needaction_mixin']
    _order = 'id desc, name desc'

    order_line_id = fields.Many2one('sale.order.line', 'Sales Order Line')
    order_id = fields.Many2one('sale.order', related='order_line_id.order_id', string='Sales Order', store=False, readonly=True)
    assigned_technician_ids = fields.One2many('fs.assigned.technician', 'fl_schedule_id', string='Technician Assignment',
                readonly=True, states={'draft': [('readonly', False)], 'validated': [('readonly', False)]})
    contract_id = fields.Many2one('account.analytic.account', 'Contract Ref#', readonly=True,
                    states={'draft': [('readonly', False)]}, copy=False, domain=[('state','!=','cancel')])
    sale_id = fields.Many2one('sale.order', related='contract_id.order_id', string='Sales Order', store=False,
                               readonly=True)
    type_flight = fields.Selection([('vvip', 'VVIP'), ('nonvvip', 'Non VVIP')], string='Type of Flight')
    create_uid = fields.Many2one('res.users', string='Created by', index=True, default=lambda self: self.env.user, readonly=True)
    department_id = fields.Many2one('hr.department', string='Department', index=True,
                                    default=lambda self: self.env.user.partner_id.department_id.id, readonly=True)
    write_uid = fields.Many2one('res.users', string='Validator / Written by', readonly=True)

    @api.multi
    @api.onchange('contract_id')
    def onchange_contract_id_warning(self):
        warning = {}
        result = {}
        if not self.contract_id:
            self.contract_id = False
            return

        if self.contract_id.date_end < fields.Datetime.now():
            warning = {
                'title': _('Warning!'),
                'message': _('The contract has expired.'),
            }
            self.contract_id = False
        if warning:
            result['warning'] = warning
        return result




class RouteFlightOperation(models.Model):
    _inherit = 'route.flight.operation'

    from_area_id = fields.Many2one('area.operation', related='route_id.from_area_id', string='Area From', store=False, readonly=True)
    to_area_id = fields.Many2one('area.operation', related='route_id.to_area_id', string='Area To', store=False, readonly=True)
    aircraft_categ = fields.Selection(string='Aircraft Category',
                                      related='schedule_id.fl_acquisition_id.aircraft_name.aircraft_categ')



class HrCrews(models.Model):
    _inherit = 'hr.crews'

    employee_id = fields.Many2one('hr.employee',string='Crew', ondelete='set null',
            domain="[('category_ids', 'ilike', 'crew')]", track_visibility='onchange')



class FlightMaintenanceLog(models.Model):
    _inherit = "flight.maintenance.log"

    aircraft_type = fields.Selection(string='Aircraft Type', store=True,
            related='fl_acquisition_id.aircraft_name.aircraft_categ', readonly=True)

    @api.multi
    def action_validate(self):
        result = super(FlightMaintenanceLog, self).action_validate()
        for fml in self:
            if (fml.eta > fields.Datetime.now()) or (fml.eta > fml.date_validate):
                error_msg = (
                    _('Validation error: try validating FML [%s] before any flight.') % fml.name)
                _logger.error(error_msg)
                raise UserError(_('You can not validate FML documents before the flight arrival date (ETA)'))
        return result
    


class FlightHoursPrice(models.Model):
    _inherit = 'flight.hours.price'

    qualification_id = fields.Many2one('hr.qualification', 'Qualification')


class MaintenanceRotary(models.Model):
    _inherit = 'maintenance.rotary'

    @api.one
    @api.depends('rotary_route_ids.route_id')
    def _compute_complete_route(self):
        rute_lengkap = []
        if self.rotary_route_ids:
            seq = 0
            for rute in self.rotary_route_ids: #.sorted()
                if seq==0:
                    if rute.route_id and rute.route_id.from_area_id:
                        rute_lengkap.append(rute.route_id.from_area_id.code)
                    if rute.route_id and rute.route_id.route_line_ids:
                        for rol in rute.route_id.route_line_ids:
                            if rol.name and rol.name.code:
                                rute_lengkap.append(rol.name.code)
                    if rute.route_id and rute.route_id.to_area_id:
                        rute_lengkap.append(rute.route_id.to_area_id.code)
                else:
                    if rute.route_id and rute.route_id.from_area_id and rute.route_id.from_area_id.code!=rute_lengkap[-1:][0]:
                        # raise UserError(_('Result: %s; %s;...') % (rute_lengkap[-1:][0],rute.route_id.from_area_id.code))
                        rute_lengkap.append(rute.route_id.from_area_id.code)
                    if rute.route_id and rute.route_id.route_line_ids:
                        for rol in rute.route_id.route_line_ids:
                            if rol.name and rol.name.code:
                                rute_lengkap.append(rol.name.code)
                    if rute.route_id and rute.route_id.to_area_id:
                        rute_lengkap.append(rute.route_id.to_area_id.code)
                seq += 1
        self.complete_route = '%s' % (' - '.join(rute_lengkap) or _(''))

    complete_route = fields.Char(string='Complete Route', compute='_compute_complete_route', copy=False, store=True)



class FlightRequsitionRouteLines(models.Model):
    _name = "flight.requisition.route.line"
    _description = "Flight Requisition Route Line"
    _order = "sequence, id"

    flight_requisition_id = fields.Many2one('flight.requisition', string='Flight Requisition', index=True, required=True, ondelete='cascade')
    name = fields.Many2one('area.operation', string='Area', required=True)
    add_need_id = fields.Many2one('additional.flight.needs', string='Additional Information')
    sequence = fields.Integer(string='Urutan', default=1)



class AdditionalFlightNeeds(models.Model):
    _name = "additional.flight.needs"

    name = fields.Char(string='Needs', required=True)
    active = fields.Boolean(string='Status', default=True,
                            help="Set active to false to hide the tax without removing it.")


class CrewSchedule(models.Model):
    _inherit = 'crew.schedule'
    

    department_id = fields.Many2one('hr.department', string='Department', index=True,
                                    default=lambda self: self.env.user.partner_id.department_id.id, readonly=True)
    # department_id = fields.Many2one(related='employee_id.department_id', string='Department', store=True, readonly=True)


class CrewScheduleActual(models.Model):
    _inherit = 'crew.schedule.actual'
    
    department_id = fields.Many2one('hr.department', string='Department', index=True,
                                    default=lambda self: self.env.user.partner_id.department_id.id, readonly=True)
    # department_id = fields.Many2one(related='employee_id.department_id', string='Department', store=True, readonly=True)


# class HrEmployee(models.Model):
#     _inherit = 'hr.employee'
# 
#     @api.model
#     def create(self, vals):
#         if vals.get('department_id', False) and vals.get('user_id', False):
#             self.env['res.users'].sudo().with_context(self._context).search([('id', '=', vals['user_id'])]).write(
#                 {'department_id': vals['department_id']})
#         return super(HrEmployee, self).create(vals)
# 
#     @api.multi
#     def write(self, vals):
#         for employee in self:
#             usr_id = employee.user_id and employee.user_id.id or False
#             if vals.get('department_id', False) and (vals.get('user_id', False) or employee.user_id):
#                 if vals.get('user_id', False):
#                     usr_id = vals['user_id']
#                 self.env['res.users'].sudo().with_context(self._context).search([('id', '=', usr_id)]).write(
#                     {'department_id': vals['department_id']})
#         return super(HrEmployee, self).write(vals)

    
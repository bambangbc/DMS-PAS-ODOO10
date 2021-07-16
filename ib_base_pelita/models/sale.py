# -*- coding: utf-8 -*-
# © 2017 Ibrohim Binladin | ibradiiin@gmail.com | +62-838-7190-9782
import datetime as dt
from odoo import api, fields, models, _
from datetime import datetime
from odoo.osv import expression
import odoo.addons.decimal_precision as dp
from odoo.exceptions import UserError
from odoo.tools import float_is_zero, DEFAULT_SERVER_DATETIME_FORMAT
#from odoo.addons.pelita_crew import GLOBAL_TYPE #.models.master_data
import logging
_logger = logging.getLogger(__name__)

GLOBAL_TYPE = [('vvip','VVIP'),('nonvvip','Non VVIP')]


class SalesOrder(models.Model):
    _inherit = 'sale.order'

    @api.model
    def _default_division(self):
        user = self.env['res.users'].browse(self._uid)
        return user.division_id and user.division_id.id

    @api.model
    def _default_main_business_unit(self):
        return self.env.user.main_business_unit.id


    trx_type_id = fields.Many2one('sale.trx.type', string="Sales Type",
                readonly=True, copy=False, states={'draft': [('readonly', False)], 'sent': [('readonly', False)]})
    date_departure = fields.Datetime(string='Date From', readonly=True, copy=False,
                states={'draft': [('readonly', False)], 'sent': [('readonly', False)]}) #Departure
    date_arrival = fields.Datetime(string='Date To', readonly=True, copy=False,
                states={'draft': [('readonly', False)], 'sent': [('readonly', False)]}) #Arrival
    type_sales = fields.Boolean(default=False, string="Sales", help="Klik disini (tandai cek list) jika tipe penjualan bukan sewa pesawat.")
    partner_payer_id = fields.Many2one('res.partner', string='Payer', readonly=True,
            states={'draft': [('readonly', False)], 'sent': [('readonly', False)]})
    sales_off = fields.Many2one('sale.sales.office', string='Sales Off', readonly=True,
            states={'draft': [('readonly', False)], 'sent': [('readonly', False)]})
    area_id = fields.Many2one('sale.sales.area', string='Sales Area', readonly=True,
            states={'draft': [('readonly', False)], 'sent': [('readonly', False)]})
    dist_channel_id = fields.Many2one('sale.distribution.channel', string='Distribution Channel', readonly=True,
            states={'draft': [('readonly', False)], 'sent': [('readonly', False)]})
    division_id = fields.Many2one('sale.division', string='Division', readonly=True,
            states={'draft': [('readonly', False)], 'sent': [('readonly', False)]}, default=_default_division)
    business_unit_id = fields.Many2one('pelita.business.unit', string='BOD Subordination', readonly=True,
            states={'draft': [('readonly', False)], 'sent': [('readonly', False)]},
            default=_default_main_business_unit)
    quotation_number = fields.Char(string="Quotation Number", copy=False, index=True)
    approved_by = fields.Many2one('res.users', string='Approved by')

    # @api.multi
    # @api.onchange('fl_acquisition_id')
    # def onchange_fleet_acquisition_id(self):
    #     if not self.fl_acquisition_id:
    #         self.update({
    #             'aircraft_id': False,
    #         })
    #         return
    #     self.update({'aircraft_id': self.fl_acquisition_id.aircraft_name and self.fl_acquisition_id.aircraft_name.id})

    @api.model
    def create(self, vals):
        result = super(SalesOrder, self).create(vals)
        if vals.get('project_id', False) and vals['project_id']:  #result.project_id or
            contract = self.env['account.analytic.account'].browse(vals['project_id'])
            contract.write({'order_id': result.id, 'partner_id': result.partner_id and result.partner_id.id,
                            'date_start': vals['date_order'] or result.date_order or fields.Datetime.now(),
                            'date_end': vals['validity_date'] or result.validity_date})
        return result

    @api.multi
    def action_confirm(self):
        for order in self:
            order.state = 'sale'
            order.confirmation_date = fields.Datetime.now()
            if self.env.context.get('send_email'):
                self.force_quotation_send()
            order.order_line._action_procurement_create()
            order._action_autocreate_fr_fs()
            #order.order_line.action_availability_aircraft('reserved')
            order.order_line._action_confirm_aircraft()
            # if order.project_id:
            #     order.project_id.action_validate()
        if self.env['ir.values'].get_default('sale.config.settings', 'auto_done_setting'):
            self.action_done()
        return True

    @api.multi
    @api.onchange('partner_id')
    def onchange_partner_id(self):
        if not self.partner_id:
            self.update({
                'partner_invoice_id': False,
                'partner_shipping_id': False,
                'payment_term_id': False,
                'fiscal_position_id': False,
                'partner_payer_id': False,
                'sales_off': False,
                'area_id': False,
                'dist_channel_id': False,
                'division_id': False,
                'team_id': False,
            })
            return

        addr = self.partner_id.address_get(['delivery', 'invoice','payer'])
        values = {
            'pricelist_id': self.partner_id.property_product_pricelist and self.partner_id.property_product_pricelist.id or False,
            'payment_term_id': self.partner_id.property_payment_term_id and self.partner_id.property_payment_term_id.id or False,
            'partner_invoice_id': addr['invoice'],
            'partner_shipping_id': addr['delivery'],
            'partner_payer_id': addr['payer'] or False,
            'sales_off': self.partner_id.sale_office_id and self.partner_id.sale_office_id.id or False,
            'area_id': self.partner_id.sales_area_id and self.partner_id.sales_area_id.id or False,
            'dist_channel_id': self.partner_id.dist_channel_id and self.partner_id.dist_channel_id.id or False,
            'division_id': self.partner_id.division_id and self.partner_id.division_id.id or False,
            'team_id': self.partner_id.team_id and self.partner_id.team_id.id or False,
        }
        if self.env.user.company_id.sale_note:
            values['note'] = self.with_context(lang=self.partner_id.lang).env.user.company_id.sale_note
        if self.partner_id.user_id:
            values['user_id'] = self.partner_id.user_id.id
        if self.partner_id.team_id:
            values['team_id'] = self.partner_id.team_id.id
        self.update(values)

    @api.multi
    def _action_autocreate_fr_fs(self):
        for order in self:
            if (order.trx_type_id.code != 'PLT' or order.trx_type_id.name != 'Longterm') and (not order.type_sales):
                for line in order.order_line: #flight_route_ok
                    if (not line.base_ops_id) and line.product_id.aircraft_ok:
                        raise UserError(_('Basic operations can not be empty.\n[%s]') % (line.name,))
                    if (not line.fleet_acquisition_id) and line.product_id.aircraft_ok:
                        raise UserError(_('Fleet Acquisition (A/C Reg.Code) can not be empty.\n[%s]') % (line.name,))
                    if line.product_id.aircraft_ok and (not line.arrival or not line.departure):
                        raise UserError(_('Departure and Arrival Date can not be empty.\n[%s]') % (line.name,))
                    if line.route_opt_id and line.product_id.aircraft_ok:
                        dept_id = self.env['hr.department'].search(['|',('name', 'like', '%Operation%'),
                                                                    ('name', 'like', '%OPS%')], limit=1)
                        requisition_routes = [] #fl_routes  #'additional_info': rute_line.additional_info
                        if line.route_opt_id and line.route_opt_id.from_area_id:
                            requisition_routes.append((0, 0, {'name': line.route_opt_id.from_area_id.id}))
                        if line.route_opt_id and line.route_opt_id.route_line_ids:
                            for rute_line in line.route_opt_id.route_line_ids:
                                requisition_routes.append((0, 0, {
                                    'name': rute_line.name and rute_line.name.id,
                                    'add_need_id': rute_line.add_need_id.id}))
                        if line.route_opt_id and line.route_opt_id.to_area_id:
                            requisition_routes.append((0, 0, {'name': line.route_opt_id.to_area_id.id}))
                        flight_request = self.env['flight.requisition'].create({ #autoCreate FR
                            'customer_id': order.partner_id and order.partner_id.id,
                            'date_request': line.departure or order.date_order or fields.Datetime.now(),
                            'date_from': line.departure,
                            'date_to': line.arrival,
                            'state': 'draft',
                            'aircraft_id': line.fleet_acquisition_id and line.fleet_acquisition_id.id or False,
                            'base_operation_id': line.base_ops_id and line.base_ops_id.id or False,
                            'route_operation_id': line.route_opt_id and line.route_opt_id.id or False,
                            'order_line_id': line.id,
                            'etd': line.etd,
                            'requisition_route_ids': requisition_routes,
                            'department_id': dept_id.id or False,
                        })
                        if flight_request:
                            self._cr.execute("INSERT INTO sale_order_line_flight_request_rel (order_line_id,flight_request_id) "
                                             "VALUES (%s,%s)", (line.id,flight_request.id))
                            msg_fr = _("Flight Requisition has been created from %s ") % (order.name,)
                            flight_request.message_post(body=msg_fr)
                        routes = []
                        if line.route_opt_id:
                            routes.append((0, 0, {'route_id': line.route_opt_id.id}))
                        flight_schedule = self.env['flight.schedule'].create({  #autoCreate FS
                            'base_operation_id': line.base_ops_id and line.base_ops_id.id or False,
                            'customer_id': order.partner_id and order.partner_id.id or False,
                            'fl_acquisition_id': line.fleet_acquisition_id and line.fleet_acquisition_id.id or False,
                            'order_line_id': line.id,
                            'state': 'draft',
                            'route_ids': routes,
                            'date_schedule': order.date_order or fields.Datetime.now(),
                            'etd': line.etd or line.departure or fields.Datetime.now(),
                            'eta': line.arrival or fields.Datetime.now(),
                            'aircraft_id': line.fleet_acquisition_id.aircraft_name and line.fleet_acquisition_id.aircraft_name.id,
                            'aircraft_type_id': line.fleet_acquisition_id.aircraft_name.aircraft_type_id and 
                                                line.fleet_acquisition_id.aircraft_name.aircraft_type_id.id,
                            'type_aircraft': line.fleet_acquisition_id.category or _(""),
                            'department_id': dept_id.id or False,
                        })
                        if flight_schedule:
                            self._cr.execute("INSERT INTO sale_order_line_flight_schedule_rel (order_line_id,flight_schedule_id) "
                                             "VALUES (%s,%s)", (line.id,flight_schedule.id))
                            msg_fs = _("Flight Schedule has been created from %s ") % (order.name,)
                            flight_schedule.message_post(body=msg_fs)
        return True

    @api.multi
    def unlink(self):
        for order in self:
            if order.state not in ('draft', 'cancel'):
                raise UserError(_('You can not delete a sent quotation or a sales order! Try to cancel it before.'))
            for line in order.order_line:
                if line.flight_requisition_ids:
                    for fl_request in line.flight_requisition_ids:
                        if fl_request.state not in ('draft', 'cancel'):
                            raise UserError(_('You can not delete a flight requisition or a sales order! Try to cancel it (FR) before.'))
                        fl_request.unlink()
                if line.flight_schedule_ids:
                    for fl_schedule in line.flight_schedule_ids:
                        if fl_schedule.state not in ('draft', 'cancel'):
                            raise UserError(_('You can not delete a flight schedule or a sales order! Try to cancel it (FS) before.'))
                        fl_schedule.unlink()
                if line.product_id.product_tmpl_id.log_availability:
                    for log in line.product_id.product_tmpl_id.log_availability:
                        if log.order_id.id == order.id:
                            log.unlink()
        return super(SalesOrder, self).unlink()

    @api.multi
    def action_cancel(self):
        for order in self:
            for line in order.order_line:
                for fl_request in line.flight_requisition_ids:
                    if fl_request.state != 'cancel':
                        fl_request.write({'state': 'cancel'})
                for fl_schedule in line.flight_schedule_ids:
                    if fl_schedule.state != 'cancel':
                        fl_schedule.write({'state': 'cancel'})
                if line.product_id.product_tmpl_id.log_availability:
                    self._cr.execute("SELECT id FROM product_log_availability WHERE order_id=%s AND "
                            "state!=%s ", (order.id, 'cancel'))
                    results = self._cr.fetchone()
                    if results:
                        self._cr.execute("UPDATE product_log_availability SET state='cancel' WHERE id=%s", (results[0],))
                        self._cr.execute("UPDATE product_template SET availability_of_aircraft='available' WHERE id=%s",
                                         (line.product_id.product_tmpl_id.id,))
                    # for log in line.product_id.product_tmpl_id.log_availability:
                        # if log.order_id.id == order.id and log.state != 'cancel':
                            # log.action_cancel()
            # if order.project_id:
            #     order.project_id.action_cancel()
        return self.write({'state': 'cancel'})

    @api.multi
    def action_draft(self):
        for order in self:
            for line in order.order_line:
                for fl_request in line.flight_requisition_ids:
                    if fl_request.state == 'cancel':
                        fl_request.write({'state': 'draft'})
                for fl_schedule in line.flight_schedule_ids:
                    if fl_schedule.state == 'cancel':
                        fl_schedule.write({'state': 'draft'})
                if line.product_id.product_tmpl_id.log_availability:
                    self._cr.execute("SELECT id FROM product_log_availability WHERE order_id=%s AND "
                        "state=%s ", (order.id, 'cancel'))
                    results = self._cr.fetchone()
                    if results:
                        self._cr.execute("UPDATE product_log_availability SET state='active' WHERE id=%s", (results[0],))
                        self._cr.execute("UPDATE product_template SET availability_of_aircraft='reserved' WHERE id=%s",
                                         (line.product_id.product_tmpl_id.id,))
                #     for log in line.product_id.product_tmpl_id.log_availability:
                #         if log.order_id.id == order.id and log.state == 'cancel':
                #             log.action_active()
            if order.project_id:
                order.project_id.action_set_to_draft()
        orders = self.filtered(lambda s: s.state in ['cancel', 'sent'])
        orders.write({
            'state': 'draft',
            'procurement_group_id': False,
        })
        orders.mapped('order_line').mapped('procurement_ids').write({'sale_line_id': False})



class SalesOrderLine(models.Model):
    _inherit = 'sale.order.line'

    @api.depends('flight_schedule_ids')
    def _get_crew_technician_set(self):
        for line in self:
            total_crew_set = technician_set = 0
            if line.flight_schedule_ids:
                for fl_schedule in line.flight_schedule_ids:
                    if fl_schedule.crew_assignment_ids:
                        total_crew_set = len(fl_schedule.crew_assignment_ids)
                    if fl_schedule.assigned_technician_ids:
                        technician_set = len(fl_schedule.assigned_technician_ids)
            line.update({'crew_set': total_crew_set, 'technician_set': technician_set})

    @api.depends('product_id')
    def _get_acquisition_id(self):
        for sol in self:
            acquisition = self.env['aircraft.acquisition'].search(
                [('product_tmpl_id', '=', sol.product_id.product_tmpl_id.id)], limit=1)
            if acquisition:
                sol.fleet_acquisition_id = acquisition.id

    @api.multi
    def write(self, values):
        result = super(SalesOrderLine, self).write(values)
        product_logs = self.env['product.log.availability']
        # if ('etd' in values) or ('arrival' in values):
        for line in self:
            type_sales = ('type_sales' in values) and values['type_sales'] or line.type_sales
            product = ('product_id' in values) and self.env['product.product'].browse(values['product_id']) or line.product_id
            if (not type_sales) and product.product_tmpl_id.log_availability:
                log_id = product_logs.search([('order_line_id', '=', line.id),('order_id','=',line.order_id.id)], limit=1).id
                for logs in product_logs.browse(log_id):
                    if ('etd' in values):
                        logs.write({'start_date': values['etd']})
                    if ('arrival' in values):
                        logs.write({'end_date': values['arrival']})
        return result

    @api.depends('qty_invoiced', 'qty_delivered', 'product_uom_qty', 'order_id.state')
    def _get_to_invoice_qty(self):
        for line in self:
            if line.order_id.state in ['sale', 'done']:
                if line.product_id.invoice_policy == 'order':
                    line.qty_to_invoice = line.product_uom_qty - line.qty_invoiced
                else:
                    line.qty_to_invoice = line.qty_delivered - line.qty_invoiced
            else:
                line.qty_to_invoice = 0

    @api.depends('invoice_lines.invoice_id.state', 'invoice_lines.quantity')
    def _get_invoice_qty(self):
        for line in self:
            qty_invoiced = 0.0
            for invoice_line in line.invoice_lines:
                if invoice_line.invoice_id.state != 'cancel':
                    if invoice_line.invoice_id.type == 'out_invoice':
                        qty_invoiced += invoice_line.uom_id._compute_quantity(invoice_line.quantity, line.product_uom)
                    elif invoice_line.invoice_id.type == 'out_refund':
                        qty_invoiced -= invoice_line.uom_id._compute_quantity(invoice_line.quantity, line.product_uom)
            line.qty_invoiced = qty_invoiced


    route_opt_id = fields.Many2one('route.operation', string='Route', change_default=True, ondelete='set null',
                    domain=[('active', '=', True),('status','=','validated')])
    etd = fields.Datetime(string='ETD', copy=False)
    departure = fields.Datetime(string='Departure', copy=False)
    arrival = fields.Datetime(string='Arrival', copy=False)
    conformance = fields.Datetime(string='Conformance', copy=False)
    non_conformance = fields.Datetime(string='Non Conformance', copy=False)
    type_sales = fields.Boolean(default=False, string="Non Aircraft Service")
    # fl_acquisition_id = fields.Many2one('aircraft.acquisition', string="Fleet Acquisition", copy=False)
    fleet_acquisition_id = fields.Many2one('aircraft.acquisition', 'A/C Reg.Code', compute='_get_acquisition_id', store=True)
    craft_name = fields.Char(related='fleet_acquisition_id.aircraft_name.name', string="Aircraft Name", readonly=True, store=False)
    craft_type = fields.Many2one('aircraft.type', related='fleet_acquisition_id.aircraft_name.aircraft_type_id',
                string='Aircraft Type', store=False, readonly=True)
    craft_categ = fields.Selection(related='fleet_acquisition_id.aircraft_name.aircraft_categ',
                                   string='Aircraft Category', store=False, readonly=True)
    craft_availseat = fields.Integer(related='fleet_acquisition_id.aircraft_name.available_seat',
                string='Available Seat', readonly=True, store=False)
    craft_color = fields.Char(related='fleet_acquisition_id.aircraft_name.aircraft_color',
                string='Aircraft Color', readonly=True, store=False)
    craft_status = fields.Selection(related='fleet_acquisition_id.product_tmpl_id.aircraft_state',
                store=False, readonly=True)
    craft_reg_code = fields.Char(related='fleet_acquisition_id.name', string='Registration Code',
                readonly=True, store=False)
    craft_ownership = fields.Selection(related='fleet_acquisition_id.ownership', store=False, readonly=True)
    # Base Operation required=True,
    base_ops_id = fields.Many2one('base.operation', string="Base Operation")
    base_code = fields.Char(string="Code", related='base_ops_id.code', readonly=True)
    base_desc = fields.Text(string="Description", related='base_ops_id.description', readonly=True)
    base_coordinate = fields.Char(string="Coordinate", related='base_ops_id.coordinate', readonly=True)
    # Area  required=True,
    area_ops_id = fields.Many2one('area.operation', string="Area Operation")
    area_code = fields.Char(string="Code", related='area_ops_id.code', readonly=True)
    area_desc = fields.Text(string='Description', related='area_ops_id.description', readonly=True)
    area_coordinate = fields.Char(string="Coordinate", related='area_ops_id.coordinate', readonly=True)
    pass_qty = fields.Integer('Passenger')
    pass_cargo = fields.Integer('Cargo (Max Weight)')
    pass_ticket = fields.Selection(GLOBAL_TYPE, string='Ticket')
    crew_set = fields.Integer(compute="_get_crew_technician_set", string="Crew Set", readonly=True, copy=False)
    technician_set = fields.Integer(compute="_get_crew_technician_set", string="Technician Set", readonly=True, copy=False)
    fuel_consump = fields.Float(string="Fuels Consumption")
    flight_requisition_ids = fields.Many2many('flight.requisition', 'sale_order_line_flight_request_rel', 'order_line_id',
                    'flight_request_id', string='Flight Requisition', copy=False)
    flight_schedule_ids = fields.Many2many('flight.schedule', 'sale_order_line_flight_schedule_rel', 'order_line_id',
                    'flight_schedule_id', string='Flight Schedule', copy=False)
    product_uom_qty = fields.Float(string='Quantity', digits=dp.get_precision('Stock Weight'), required=True, default=1.0)
    qty_delivered = fields.Float(string='Delivered', copy=False, digits=dp.get_precision('Stock Weight'), default=0.0)
    qty_to_invoice = fields.Float( compute='_get_to_invoice_qty', string='To Invoice', store=True, readonly=True,
        digits=dp.get_precision('Stock Weight'))
    qty_invoiced = fields.Float(compute='_get_invoice_qty', string='Invoiced', store=True, readonly=True,
        digits=dp.get_precision('Stock Weight'))

    _sql_constraints = [
        ('eta_greater_than_etd', 'check(arrival > departure)', 'Error! \nDeparture [ETD] must be lower than Arrival [ETA]'),
    ]


    @api.onchange('type_sales')
    def onchange_type_sales(self):
        self.type_sales = self.order_id and self.order_id.type_sales

    @api.onchange('arrival')
    def _onchange_arrival(self):
        if self.departure and self.arrival and (self.arrival < self.departure):
            self.arrival = False or _("")
            warning_datetime = {
                'title': _('Departure and Arrival configuration errors!'),
                'message': _(
                    'Departure [ETD] must be lower than Arrival [ETA].'),
            }
            return {'warning': warning_datetime}

    @api.onchange('fleet_acquisition_id')
    def onchange_fleet_acquisition_id(self):
        acquisition = self.env['aircraft.acquisition'].search(
            [('product_tmpl_id', '=', self.product_id.product_tmpl_id.id)], limit=1)
        if self.product_id.aircraft_ok and self.fleet_acquisition_id and (self.fleet_acquisition_id.id != acquisition.id):
            self.fleet_acquisition_id = self.fleet_acquisition_id and self.fleet_acquisition_id.id
            raise UserError(_("Anda tidak bisa mengubah 'Aircraft Registration Code' yang tidak sesuai dengan kolom Product [%s].") % self.product_id.name)
        if self.fleet_acquisition_id:
            self.pass_qty = self.fleet_acquisition_id.aircraft_name and self.fleet_acquisition_id.aircraft_name.available_seat
                ##or self.craft_name and self.craft_name.available_seat or 0 #int()

    @api.onchange('etd')
    def onchange_etd(self):
        self.departure = self.etd
        self.arrival = self.etd

    # @api.multi
    # def action_availability_aircraft(self, action):
    #     aa = self.env['aircraft.acquisition']
    #     for line in self:
    #         if line.product_id and line.product_id.product_tmpl_id:
    #             acquisition = aa.search([('product_tmpl_id','=', line.product_id.product_tmpl_id.id)], limit=1)
    #             if acquisition:
    #                 if action=='reserved':
    #                     acquisition.with_context(action='reserved').action_set_availability()
    #                 elif action=='available':
    #                     acquisition.with_context(action='available').action_set_availability()
    #     return True

    @api.multi
    def _action_confirm_aircraft(self):
        pla_values = {}
        pla = self.env['product.log.availability']
        for line in self:
            if (not line.order_id.project_id) and (line.order_id.trx_type_id.code == 'PLT' or line.order_id.trx_type_id.name == 'Longterm'):
                raise UserError(_("Contract contract reference number can not be empty if type of sales order is 'long term'."))
            if (not line.type_sales) and line.product_id.aircraft_ok:
                pla_values = {
                    'product_tmpl_id': line.product_id.product_tmpl_id and line.product_id.product_tmpl_id.id,
                    'order_line_id': line.id,
                    'start_date': line.departure or fields.Datetime.now(),
                    'end_date': line.arrival or fields.Datetime.now(),
                    'order_id': line.order_id and line.order_id.id,
                    'sales_type': line.order_id and line.order_id.trx_type_id and line.order_id.trx_type_id.id,
                }
                if line.order_id.trx_type_id:
                    if (line.order_id.trx_type_id.code == 'PLT' or line.order_id.trx_type_id.name == 'Longterm'):
                        pla_values['start_date'] = line.order_id.project_id and line.order_id.project_id.date_start
                        pla_values['end_date'] = line.order_id.project_id and line.order_id.project_id.date_end
                pla_records = pla.search([('order_line_id', '=', line.id),('state','=','active'),
                                      ('product_tmpl_id', '=', line.product_id.product_tmpl_id.id)], limit=1)
                if not pla_records:
                    pla.create(pla_values)
                else:
                    # pla_records.write(pla_values)
                    pla_records.unlink()
                    pla.create(pla_values)
                # line.product_id.product_tmpl_id.button_update()
        return True

    @api.multi
    @api.onchange('product_id')
    def product_id_change(self):
        if not self.product_id:
            return {'domain': {'product_uom': []}}
        vals = {}
        domain = {'product_uom': [('category_id', '=', self.product_id.uom_id.category_id.id)]}
        if not self.product_uom or (self.product_id.uom_id.id != self.product_uom.id):
            vals['product_uom'] = self.product_id.uom_id
            vals['product_uom_qty'] = 1.0

        product = self.product_id.with_context(
            lang=self.order_id.partner_id.lang,
            partner=self.order_id.partner_id.id,
            quantity=vals.get('product_uom_qty') or self.product_uom_qty,
            date=self.order_id.date_order,
            pricelist=self.order_id.pricelist_id.id,
            uom=self.product_uom.id,
            etd=self.etd or False,
        )

        result = {'domain': domain}
        title = False
        message = False
        warning = {}
        if (not self.type_sales) and product.product_tmpl_id.log_availability:
            # raise UserError(_('Error 1.'))
            for log in product.product_tmpl_id.log_availability.sorted():
                if log.state=='active' and self.etd < log.end_date:
                    # raise UserError(_('Error 2.'))
                    end_dt = datetime.strptime(log.end_date, DEFAULT_SERVER_DATETIME_FORMAT)
                    end_dt = end_dt + dt.timedelta(hours=7)
                    end_dt_str = end_dt.strftime('%A, %B %d, %Y at %H:%M hours')
                    etd_dt = datetime.strptime(self.etd, DEFAULT_SERVER_DATETIME_FORMAT)
                    etd_dt = etd_dt + dt.timedelta(hours=7)
                    etd_str = etd_dt.strftime('%A, %B %d, %Y at %H:%M hours')
                    warning['title'] = _('Warning!')
                    warning['message'] = _('The aircraft is not available in your ETD [%s].\nBecause status of aircraft is active until %s') % (etd_str,end_dt_str)
                    result = {'warning': warning}
                    self.product_id = False
                    return result
        if self.type_sales and self.product_id.aircraft_ok:
            result = {'warning': {
                'title': _('Warning!'),
                'message': _('The type of sales you choose is non aircraft service. Choose a product with a non-aircraft type.'),
            }}
            self.product_id = False
            return result
        # if self.product_id.aircraft_ok and (self.product_id.product_tmpl_id.aircraft_state == 'unserviceable' and self.product_id.product_tmpl_id.availability_of_aircraft == 'reserved'):
        #     result = {'warning': {
        #         'title': _('Warning!'),
        #         'message': _('The aircraft is not available.'),
        #     }}
        #     self.product_id = False
        #     return result
        if product.sale_line_warn != 'no-message':
            title = _("Warning for %s") % product.name
            message = product.sale_line_warn_msg
            warning['title'] = title
            warning['message'] = message
            result = {'warning': warning}
            if product.sale_line_warn == 'block':
                self.product_id = False
                return result

        name = product.name_get()[0][1]
        if product.description_sale:
            name += '\n' + product.description_sale
        vals['name'] = name

        self._compute_tax_id()

        acquisition = self.env['aircraft.acquisition'].search([('product_tmpl_id', '=', self.product_id.product_tmpl_id.id)], limit=1)
        if acquisition:
            vals['fleet_acquisition_id'] = acquisition.id

        if self.order_id.pricelist_id and self.order_id.partner_id:
            vals['price_unit'] = self.env['account.tax']._fix_tax_included_price(self._get_display_price(product),
                                                                                 product.taxes_id, self.tax_id)
        self.update(vals)

        return result

    @api.multi
    def invoice_line_create(self, invoice_id, qty):
        precision = self.env['decimal.precision'].precision_get('Product Unit of Measure')
        for line in self:
            if not float_is_zero(qty, precision_digits=precision):
                vals = line._prepare_invoice_line(qty=qty)
                vals.update({'invoice_id': invoice_id, 'sale_line_ids': [(6, 0, [line.id])]})
                self.env['account.invoice.line'].create(vals)
                if line.product_id.product_tmpl_id.log_availability:
                    for log in line.product_id.product_tmpl_id.log_availability:
                        if log.order_id.id == line.order_id.id and log.state=='active':
                            log.action_done()



class SaleTransactionType(models.Model):
    _name = 'sale.trx.type'

    name = fields.Char(string='Sales Type', required=True)
    code = fields.Char(string='Code')
    active = fields.Boolean(string='Status', default=True,
                            help="Set active to false to hide the tax without removing it.")

    @api.model
    def name_search(self, name, args=None, operator='ilike', limit=100):
        args = args or []
        domain = []
        if name:
            domain = ['|', ('code', '=ilike', name + '%'), ('name', operator, '%' + name + '%')]
            if operator in expression.NEGATIVE_TERM_OPERATORS:
                domain = ['&', '!'] + domain[1:]
        sales_type = self.search(domain + args, limit=limit)
        return sales_type.name_get()

    @api.multi
    @api.depends('name', 'code')
    def name_get(self):
        result = []
        for type in self:
            name = "%s" % (str(type.name) or _(''))
            if type.code:
                name = "%s" % (_("[" + str(type.code) + "] " + str(type.name)) or _(''))
            result.append((type.id, name))
        return result



class SalesArea(models.Model):
    _name = 'sale.sales.area'

    name = fields.Char(string='Sales Area', required=True)
    code = fields.Char(string='Sales Area Code')
    active = fields.Boolean(string='Status', default=True,
                            help="Set active to false to hide the tax without removing it.")

    @api.model
    def name_search(self, name, args=None, operator='ilike', limit=100):
        args = args or []
        domain = []
        if name:
            domain = ['|', ('code', '=ilike', name + '%'), ('name', operator, '%' + name + '%')]
            if operator in expression.NEGATIVE_TERM_OPERATORS:
                domain = ['&', '!'] + domain[1:]
        sales_area = self.search(domain + args, limit=limit)
        return sales_area.name_get()

    @api.multi
    @api.depends('name', 'code')
    def name_get(self):
        result = []
        for sa in self:
            name = "%s" % (str(sa.name) or _(''))
            if sa.code:
                name = "%s" % (_("[" + str(sa.code) + "] " + str(sa.name)) or _(''))
            result.append((sa.id, name))
        return result



class DiscountChannel(models.Model):
    _name = 'sale.distribution.channel'

    name = fields.Char(string='Distribution Channel', required=True)
    code = fields.Char(string='Code')
    active = fields.Boolean(string='Status', default=True,
                            help="Set active to false to hide the tax without removing it.")

    @api.model
    def name_search(self, name, args=None, operator='ilike', limit=100):
        args = args or []
        domain = []
        if name:
            domain = ['|', ('code', '=ilike', name + '%'), ('name', operator, '%' + name + '%')]
            if operator in expression.NEGATIVE_TERM_OPERATORS:
                domain = ['&', '!'] + domain[1:]
        dist_channel = self.search(domain + args, limit=limit)
        return dist_channel.name_get()

    @api.multi
    @api.depends('name', 'code')
    def name_get(self):
        result = []
        for dist_channel in self:
            name = "%s" % (str(dist_channel.name) or _(''))
            if dist_channel.code:
                name = "%s" % (_("[" + str(dist_channel.code) + "] " + str(dist_channel.name)) or _(''))
            result.append((dist_channel.id, name))
        return result



class SaleSalesOffice(models.Model):
    _name = 'sale.sales.office'

    name = fields.Char(string='Sales Off', required=True)
    code = fields.Char(string='Code')
    active = fields.Boolean(string='Status', default=True,
                            help="Set active to false to hide the tax without removing it.")

    @api.model
    def name_search(self, name, args=None, operator='ilike', limit=100):
        args = args or []
        domain = []
        if name:
            domain = ['|', ('code', '=ilike', name + '%'), ('name', operator, '%' + name + '%')]
            if operator in expression.NEGATIVE_TERM_OPERATORS:
                domain = ['&', '!'] + domain[1:]
        sales_off = self.search(domain + args, limit=limit)
        return sales_off.name_get()

    @api.multi
    @api.depends('name', 'code')
    def name_get(self):
        result = []
        for sales_off in self:
            name = "%s" % (str(sales_off.name) or _(''))
            if sales_off.code:
                name = "%s" % (_("[" + str(sales_off.code) + "] " + str(sales_off.name)) or _(''))
            result.append((sales_off.id, name))
        return result


class SaleReport(models.Model):
    _inherit = "sale.report"

    trx_type_id = fields.Many2one('sale.trx.type', string="Sales Type", readonly=True,  ondelete='set null', required=False)
    sales_off = fields.Many2one('sale.sales.office', string='Sales Off', ondelete='set null', readonly=True, required=False)
    area_id = fields.Many2one('sale.sales.area', string='Sales Area', ondelete='set null', readonly=True, required=False)
    division_id = fields.Many2one('sale.division', string='Division', ondelete='set null', readonly=True, required=False)
    business_unit_id = fields.Many2one('pelita.business.unit', string='Business Unit', ondelete='set null',  readonly=True, required=False)

    def _select(self):
        select_str = super(SaleReport, self)._select()
        select_str += """,
                    s.sales_off,
                    s.area_id,
                    s.trx_type_id,
                    s.division_id,
                    s.business_unit_id
        """
        return select_str
        #s.aircraft_id,
        #s.dist_channel_id,
        #s.fl_acquisition_id,

    def _group_by(self):
        group_by_str = super(SaleReport, self)._group_by()
        group_by_str += """,
                    s.sales_off,
                    s.area_id,
                    s.trx_type_id,
                    s.division_id,
                    s.business_unit_id
        """
        return group_by_str
        # s.dist_channel_id,
        # s.aircraft_id,
        # s.fl_acquisition_id,



    # @api.multi
    # def generate_jasper_report_attachment(self):
    #     attachment_id = False
    #     attachment_obj = self.env['ir.attachment']
    #     for record in self:
    #         ir_actions_report = self.env['ir.actions.report.xml']
    #         matching_reports = ir_actions_report.search([('name', '=', 'Sales Order'),('report_name','=','sale.order.pdf')])
    #         if matching_reports:
    #             report = ir_actions_report.browse(matching_reports.id)
    #             report_service = 'report.' + report.report_name
    #             service = odoo.netsvc.LocalService(report_service)
    #             (result, format) = service.create({'model': self._name})
    #             eval_context = {'time': time, 'object': record}
    #             if not report.attachment or not eval(report.attachment, eval_context):
    #                 # no auto-saving of report as attachment, need to do it manually
    #                 result = base64.b64encode(result)
    #                 #file_name = re.sub(r'[^a-zA-Z0-9_-]', '_', 'Sales Order')
    #                 file_name = _(record.name) + _(".pdf")
    #                 attachment_id = attachment_obj.create({
    #                     'name': file_name,
    #                     'datas': result,
    #                     'datas_fname': file_name,
    #                     'res_model': self._name,
    #                     'res_id': record.id,
    #                     'type': 'binary'
    #                 })
    #     return attachment_id
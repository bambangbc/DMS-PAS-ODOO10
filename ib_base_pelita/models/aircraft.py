# -*- coding: utf-8 -*-
# © 2017 Ibrohim Binladin | ibradiiin@gmail.com | +62-838-7190-9782

from psycopg2 import OperationalError

from odoo import api, fields, models, registry, _
#from odoo.exceptions import UserError, AccessError
import logging
_logger = logging.getLogger(__name__)

AIRCRAFT_TYPE = {'fixedwing': 'Fixed Wing', 'rotary': 'Rotary'}


class AircraftAircraft(models.Model):
    _inherit = 'aircraft.aircraft'

    active = fields.Boolean(string='Status', default=True,
                            help="Set active to false to hide the tax without removing it.")
    aircraft_color = fields.Char(string='Aircraft Color', help="Choose your color")



class ProductTemplate(models.Model):
    _inherit = 'product.template'

    @api.one
    @api.depends('log_availability.state', 'log_availability.end_date', 'log_availability.sales_type')
    def _compute_aircraft_status(self):
        log_pool = self.env['product.log.availability']
        for product_tmpl in self:
            logs = log_pool.search([('product_tmpl_id', '=', product_tmpl.id),('state', '=', 'active')])
            if not logs:
                product_tmpl.availability_of_aircraft = 'available'
            else:
                product_tmpl.availability_of_aircraft = 'reserved'
            # if product_tmpl.log_availability:
            #     for log in product_tmpl.log_availability:
            #         if log.end_date < fields.Datetime.now(): #log.action_done()
            #             log_pool.action_done([log.id])
            #         elif log.order_id.state == 'cancel': #log.action_cancel()
            #             log_pool.action_cancel([log.id])
            #         elif log.sales_type and (log.sales_type.code == 'PLT' or log.sales_type.name == 'Longterm') \
            #             and log.order_id.project_id and log.end_date == log.order_id.project_id.date_end and \
            #             log.end_date > fields.Datetime.now():
            #             log_pool.action_active([log.id])  #log.action_active()
            #         elif log.order_line_id.arrival and log.end_date == log.order_line_id.arrival and \
            #             log.end_date > fields.Datetime.now():
            #             log_pool.action_active([log.id])

    aircraft_state = fields.Selection([('serviceable', 'Serviceable'),
        ('unserviceable', 'Unserviceable')], string='Aircraft Status', readonly=True, default='serviceable')
    availability_aircraft = fields.Selection(
        [('available', 'Available'),('reserved', 'Reserved')],
        string='Availability of Aircraft', readonly=True)
    aircraft_ok = fields.Boolean('Is Aircraft', copy=False, readonly=True, default=False)
    flight_route_ok = fields.Boolean('Is Flight Route', copy=False, readonly=True, default=False)
    route_status = fields.Selection([('validated', 'Validated'), ('invalid', 'Invalid')],
                string='Route Status', readonly=True)
    availability_of_aircraft = fields.Selection([('available', 'Available'),('reserved', 'Reserved')
        ], string='Availability of Aircraft', readonly=True, default='available')
    #compute='_compute_aircraft_status', store=True,
    log_availability = fields.One2many('product.log.availability', 'product_tmpl_id',
                            string='Log Availability Lines', copy=True)

    @api.multi
    def button_update(self):
        log_pool = self.env['product.log.availability']
        for product_tmpl in self:
            logs = log_pool.search([('product_tmpl_id', '=', product_tmpl.id), ('state', '=', 'active')])
            if not logs:
                product_tmpl.availability_of_aircraft = 'available'
            else:
                product_tmpl.availability_of_aircraft = 'reserved'
        return True


class AircraftAcquisition(models.Model):
    _inherit = 'aircraft.acquisition'

    name = fields.Char(string='Registration No', required=True, index=True)
    aircraft_name = fields.Many2one('aircraft.aircraft', string='Aircraft Name', required=True,
                    ondelete='set null', index=True)
    company_id = fields.Many2one('res.company', 'Company',
                    default=lambda self: self.env['res.company']._company_default_get('aircraft.acquisition'))
    product_tmpl_id = fields.Many2one('product.template', string='Product')
    availability_aircraft = fields.Selection(related='product_tmpl_id.availability_aircraft', store=False, readonly=True)
    aircraft_state = fields.Selection(related='product_tmpl_id.aircraft_state', store=False, readonly=True)
    aircraft_ok = fields.Boolean(related='product_tmpl_id.aircraft_ok', store=False, readonly=True)
    # product_tmpl_ok = fields.Boolean('Auto Created Product?', copy=False, readonly=True, default=True)

    _sql_constraints = [
        ('reg_number_company_uniq', 'unique (name,company_id)', 'Aircraft registration number must be unique per company!')
    ]

    # @api.depends('name', 'aircraft_name')
    @api.multi
    def name_get(self):
        result = []
        for acquisition in self:
            name = "%s" % (acquisition.name or _(''))
            if acquisition.aircraft_name:
                name = "[%s] %s" % (name,acquisition.aircraft_name.name)
            if self._context.get('show_complete'):
                name += "\n"
                if acquisition.aircraft_name.aircraft_categ:
                    name += "Category: %s" % (AIRCRAFT_TYPE[acquisition.aircraft_name.aircraft_categ])
                if acquisition.aircraft_name.aircraft_type_id:
                    name += " | Type: %s" % (acquisition.aircraft_name.aircraft_type_id.name,)
                if acquisition.ownership or acquisition.aircraft_name.available_seat or acquisition.aircraft_name.aircraft_color:
                    name += "\n"
                    if acquisition.ownership:
                        name += "Ownership: %s" % (str(acquisition.ownership).title(),)
                    if acquisition.aircraft_name.available_seat:
                        name += " | Seat: %s" % (str(acquisition.aircraft_name.available_seat),)
                    if acquisition.aircraft_name.aircraft_color:
                        name += " | Color: %s" % (acquisition.aircraft_name.aircraft_color,)
            result.append((acquisition.id, name))
        return result

    @api.model
    def name_search(self, name, args=None, operator='ilike', limit=100):
        args = args or []
        domain = []
        if name:
            domain = ['|', ('name', operator, '%' + name + '%'), ('aircraft_name.name', operator, '%' + name + '%')]
        acquisition = self.search(domain + args, limit=limit)
        return acquisition.name_get()

    @api.multi
    def action_set_availability(self):
        for acquisition in self:
            if acquisition.product_tmpl_id:
                if self._context.get('action')=='available':
                    acquisition.product_tmpl_id.write({'availability_aircraft': 'available'})
                elif self._context.get('action')=='reserved':
                    acquisition.product_tmpl_id.write({'availability_aircraft': 'reserved'})
        return True

    @api.model
    def create(self, vals):
        acquisition = super(AircraftAcquisition, self).create(vals)
        product_categ = self.env['product.category']
        if ('aircraft_name' in vals) and vals.get('aircraft_name'): #('product_tmpl_ok' in vals) and vals['product_tmpl_ok'] and
            aircraft = self.env['aircraft.aircraft'].browse(vals.get('aircraft_name'))
            exist_categ = product_categ.search([('name', 'like', '%' + str(aircraft.aircraft_categ).title() + '%')], limit=1)
            if not exist_categ:
                parent_categ = product_categ.search([('name', 'like', '%PAS%')], limit=1)
                categ_id = product_categ.create({'name': str(aircraft.aircraft_categ).title(),  'type': 'normal',
                                                 'parent_id': parent_categ and parent_categ.id}).id
            else:
                categ_id = exist_categ.id or False
            if (vals.get('name') or acquisition.name):  #aircraft.aircraft_code: aircraft.name and
                uom_ids = self.env['product.uom'].search(['|',('name','like','%Hour%'),('name','like','%Hour(s)%')], limit=1)
                product_tmpl_id = self.env['product.template'].create({
                    'name': aircraft.name,
                    'default_code': vals.get('name') or acquisition.name,  #aircraft.aircraft_code,
                    'type': 'service',
                    'categ_id': categ_id or 1,
                    'sale_ok': True,
                    'purchase_ok': False,
                    'uom_id': uom_ids and uom_ids.id or 1,
                    'uom_po_id': uom_ids and uom_ids.id or 1,
                    'aircraft_ok': True,
                    'aircraft_state': 'serviceable',
                    'availability_aircraft': 'available',
                })
                if product_tmpl_id:
                    acquisition.write({'product_tmpl_id': product_tmpl_id.id})
        return acquisition

    @api.multi
    def write(self, vals):
        product_categ = self.env['product.category']
        for fa in self:
            if fa.product_tmpl_id: #and fa.product_tmpl_ok:
                aircraft_reg_code = ('name' in vals and vals.get('name')) or fa.name
                if (fa.product_tmpl_id.default_code != aircraft_reg_code):
                    fa.product_tmpl_id.write({'default_code': aircraft_reg_code})
                if ('aircraft_name' in vals or vals.get('aircraft_name')):
                    aircraft = self.env['aircraft.aircraft'].browse(vals.get('aircraft_name'))
                    if (fa.product_tmpl_id.name != aircraft.name):
                        fa.product_tmpl_id.write({'name': aircraft.name})
                    if fa.aircraft_name.aircraft_categ: #('aircraft_categ' in vals)
                        if fa.product_tmpl_id.categ_id.name != aircraft.aircraft_categ:
                            exist_categ = product_categ.search([('name', 'like', '%' + str(aircraft.aircraft_categ).title() + '%')], limit=1)
                            if not exist_categ:
                                categ_id = product_categ.create({'name': str(aircraft.aircraft_categ).title(), 'type': 'normal'}).id
                            else:
                                categ_id = exist_categ.id
                            fa.product_tmpl_id.write({'categ_id': categ_id})
                    if (aircraft.active or not aircraft.active):  ##and not vals.get('active'):
                        fa.product_tmpl_id.write({'active': aircraft.active})
        return super(AircraftAcquisition, self).write(vals)

    @api.multi
    def unlink(self):
        for acquisition in self:
            if acquisition.product_tmpl_id:
                acquisition.product_tmpl_id.unlink()
        return super(AircraftAcquisition, self).unlink()



class LogFlightAvailability(models.Model):
    _name = 'product.log.availability'
    _description = "Log Availability of Aircraft"
    _order = 'end_date desc, id desc'

    product_tmpl_id = fields.Many2one('product.template', string='Product', ondelete='cascade', index=True)
    order_line_id = fields.Many2one('sale.order.line', string='Order Lines', ondelete='restrict', index=True)
    order_id = fields.Many2one('sale.order', related='order_line_id.order_id', string='Order', store=True, readonly=True)
    fleet_acquisition_id = fields.Many2one('aircraft.acquisition', related='order_line_id.fleet_acquisition_id',
                    string='A/C Reg.Code', store=False, readonly=True)
    sales_type = fields.Many2one('sale.trx.type', related='order_line_id.order_id.trx_type_id', store=True, readonly=True)
    start_date = fields.Datetime(string='Start Date / Departure', readonly=True, copy=False)
    end_date = fields.Datetime(string='Expired Date / Arrival', readonly=True, copy=False)
    state = fields.Selection([('active', 'Active'),('done', 'Done'),('cancel', 'Cancelled')],
                             string='Log Status', readonly=True, default='active')

    @api.multi
    def action_active(self):
        return self.write({'state': 'active'})

    @api.multi
    def action_done(self):
        return self.write({'state': 'done'})

    @api.multi
    def action_cancel(self):
        return self.write({'state': 'cancel'})

    @api.multi
    def run(self, autocommit=False):
        for log in self:
            if log.state not in ("cancel", "done"):
                try:
                    if log.end_date < fields.Datetime.now():
                        if log.order_id.state not in ('draft','cancel'):
                            log.write({'state': 'done'})
                        else:
                            if log.order_id.state == 'cancel':
                                log.write({'state': 'cancel'})
                    else:
                        if log.order_id.state not in ('draft', 'cancel'):
                            for sol in log.order_id.order_line:
                                if sol.product_id.product_tmpl_id.id == log.product_tmpl_id.id:
                                    log.write({'state': 'active'})
                        else:
                            log.write({'state': 'cancel'})
                    if autocommit:
                        self.env.cr.commit()
                except OperationalError:
                    if autocommit:
                        self.env.cr.rollback()
                        continue
                    else:
                        raise
        return True

    ### Scheduler ###
    @api.model
    def run_log_scheduler(self, use_new_cursor=False):
        try:
            if use_new_cursor:
                cr = registry(self._cr.dbname).cursor()
                self = self.with_env(self.env(cr=cr))  # TDE FIXME
            LogAircraftSudo = self.env['product.log.availability'].sudo()
            OrderSudo = self.env['sale.order'].sudo()
            active_orders = OrderSudo.search([('state', '!=', 'cancel')])
            # Run active logs
            logs = LogAircraftSudo.search([('state', '=', 'active'), ('order_id', 'in', active_orders.ids)])
            while logs:
                logs.run(autocommit=use_new_cursor)
                if use_new_cursor:
                    self.env.cr.commit()
        finally:
            if use_new_cursor:
                try:
                    self.env.cr.close()
                except Exception:
                    pass
        return {}


class ProductProduct(models.Model):
    _inherit = 'product.product'

    @api.multi
    def button_update(self):
        log_pool = self.env['product.log.availability']
        product_tmpl = self.env['product.template']
        for product in self:
            logs = log_pool.search([('product_tmpl_id', '=', product.product_tmpl_id.id), ('state', '=', 'active')])
            if not logs:
                product_tmpl.write({'availability_of_aircraft': 'available'})
            else:
                product_tmpl.write({'availability_of_aircraft': 'reserved'})
        return True



# -*- coding: utf-8 -*-
# © 2017 Ibrohim Binladin | ibradiiin@gmail.com | +62-838-7190-9782
from odoo import api, fields, models, _
import time
import logging
_logger = logging.getLogger(__name__)


class MaintenanceRequest(models.Model):

    _inherit = 'maintenance.request'

    fl_acquisition_id = fields.Many2one('aircraft.acquisition', string="Fleet Acquisition",
                                        required=True, track_visibility='onchange', copy=False)
    aircraft_id = fields.Many2one('aircraft.aircraft', related='fl_acquisition_id.aircraft_name',
                                  string='Aircraft', store=True, readonly=True)
    aircraft_state = fields.Selection([('serviceable', 'Serviceable'),('unserviceable', 'Unserviceable')],
                    string='Aircraft Status', readonly=True, track_visibility='onchange', copy=False, default='unserviceable')
    finished_date = fields.Date('Finished Date', index=True, copy=False)
    maintenance_type = fields.Selection([('scheduled', 'Scheduled'), ('unScheduled', 'Unscheduled')],
                                        string='Maintenance Type', default="scheduled")
    reason_maintenance = fields.Text(string='Reason of Maintenance', required=True)
    department_id = fields.Many2one(related='owner_user_id.department_id', string='Department', store=True, readonly=True)
    date_finished = fields.Datetime('Finished Date', index=True, copy=False)

    @api.model
    def create(self, vals):
        result = super(MaintenanceRequest, self).create(vals)
        if result.fl_acquisition_id and result.fl_acquisition_id.product_tmpl_id:
            result.fl_acquisition_id.product_tmpl_id.write({'aircraft_state': vals.get('aircraft_state')})
        return result

    @api.multi
    def write(self, vals):
        result = super(MaintenanceRequest, self).write(vals)
        for request in self:
            if 'aircraft_state' in vals and vals.get('aircraft_state') and request.fl_acquisition_id:
                request.fl_acquisition_id.product_tmpl_id.write({'aircraft_state': vals.get('aircraft_state')})
        return result

    @api.multi
    def action_set_serviceable(self):
        return self.write({'aircraft_state': 'serviceable'})

    @api.multi
    def action_set_unserviceable(self):
        return self.write({'aircraft_state': 'unserviceable'})



#
# class SaleOrderLines(models.Model):
# 	_inherit = 'sale.order.line'


# -*- coding: utf-8 -*-
# © 2017 Ibrohim Binladin | ibradiiin@gmail.com | +62-838-7190-9782

from odoo import api, fields, models, _
from odoo.exceptions import UserError
import logging
_logger = logging.getLogger(__name__)


class ApprovingCrewUnregulated(models.TransientModel):
    _name = "flight.schedule.approve.crew"
    _description = "Approve Crew Unregulated in the Flight Schedule"

    @api.model
    def _get_information(self):
        context = self._context or {}
        result = _("")
        if context.get('description', False):
            for val in context['description']:
                result += val + _("\n")
        return result

    @api.model
    def _get_employee_ids(self):
        context = dict(self._context or {})
        res = []
        if context.get('employee_ids', []):
            res.append((6, 0, context['employee_ids']))
        return res

    reason = fields.Text(string="Reason", help="Reason to Approve Flying Crew")
    information = fields.Text(string="Information", default=_get_information)
    employee_ids = fields.Many2many('hr.employee', 'approve_unregulated_crew_hr_employee_rel', 'wizard_id', 'employee_id',
        default=_get_employee_ids,
        string='Employee')

    @api.multi
    def action_approve(self):
        context = dict(self._context or {})
        flt_schedules = self.env['flight.schedule'].browse(context.get('flt_schedule_ids', []))
        reason_allowed = self.env['fs.reason.crew.allowed']
        flt_schedule_to_set = self.env['flight.schedule']
        for wzd in self:
            for schedule in flt_schedules:
                if wzd.reason and (wzd.employee_ids or context.get('employee_ids', [])):
                    employee_ids = [e.id for e in wzd.employee_ids] or context['employee_ids']
                    for employee_id in employee_ids:
                        reason_allowed.create({
                            'flt_schedule_id': schedule.id,
                            'crew_id': employee_id, #context['employee_id'],
                            'reason': wzd.reason,
                            'approved_id': self._uid,
                        })
                        self.env['hr.crews'].search([
                            ('crew_assign_id', '=', schedule.id), ('crew_id', '=', employee_id)
                        ]).write({'allowed': True})  #context['employee_id']
                    flt_schedule_to_set += schedule
        if flt_schedule_to_set:
            return flt_schedule_to_set.with_context({'unregulated': True}).action_crew_schedule()
        return {'type': 'ir.actions.act_window_close'}






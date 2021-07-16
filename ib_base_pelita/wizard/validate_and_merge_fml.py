# -*- coding: utf-8 -*-
import time
from odoo import api, fields, models, _
from odoo.exceptions import UserError
import odoo.addons.decimal_precision as dp


class FSMakeMergeFML(models.TransientModel):
    _name = "flight.schedule.make.merge.fml"
    _description = "Flight Schedule Make Merge FML"

    def _check_flight_schedule_list(self):
        self._context.get('active_ids', [])
        if self._context.get('active_model', '') == 'flight.schedule':
            ids = self._context.get('active_ids', [])
            fs_obj = self.env['flight.schedule']
            if len(ids) > 1:
                schedules = fs_obj.read(ids, ['state','company_id','picking_type_id','invoice_method'])
                for fs in schedules:
                    if fs['state'] in ('cancel',):
                        raise UserError(_('Warning'), _("At least one of the selected flight schedule is %s! \nFlight Schedule status allowed is Draft or Validated.") % fs['state'])
                    if (fs['company_id'] != schedules[0]['company_id']):
                        raise UserError(_('Warning'), _('Not all Purchase Order are at the same company!'))
        return {}


    @api.model
    def fields_view_get(self, view_id=None, view_type='form', toolbar=False, submenu=False):
        res = super(FSMakeMergeFML, self).fields_view_get(view_id=view_id, view_type=view_type,
                                                            toolbar=toolbar, submenu=submenu)
        self._check_flight_schedule_list()
        return res

    @api.multi
    def create_invoices(self):
        fs_obj = self.env['flight.schedule']
        flight_schedule = fs_obj.browse(self._context.get('active_ids', []))

        for fs in flight_schedule:
            if fs.state=='draft':
                fs.action_validate()
            elif fs.state=='validated':
                fs.action_crew_schedule()


        if self._context.get('open_fml', False):
            return flight_schedule.action_view_related_fml()
        return {'type': 'ir.actions.act_window_close'}



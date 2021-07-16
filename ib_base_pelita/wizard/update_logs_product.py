# -*- coding: utf-8 -*-
# © 2017 Ibrohim Binladin | ibradiiin@gmail.com | +62-838-7190-9782
import logging
import threading

from odoo import api, models, tools, registry, _

_logger = logging.getLogger(__name__)


class UpdateProductLogs(models.TransientModel):
    _name = 'product.template.update.logs'
    _description = 'Update log schedulers'

    @api.multi
    def _update_product_logs(self):
        with api.Environment.manage():
            # As this function is in a new thread, i need to open a new cursor, because the old one may be closed
            new_cr = registry(self._cr.dbname).cursor()
            self = self.with_env(self.env(cr=new_cr))  # TDE FIXME
            scheduler_cron = self.sudo().env.ref('ib_base_pelita.ir_cron_product_log_scheduler_act')
            # Avoid to run the scheduler multiple times in the same time
            try:
                with tools.mute_logger('odoo.sql_db'):
                    self._cr.execute("SELECT id FROM ir_cron WHERE id = %s FOR UPDATE NOWAIT", (scheduler_cron.id,))
            except Exception:
                _logger.info('Attempt to run product logs scheduler aborted, as already running')
                self._cr.rollback()
                self._cr.close()
                return {}

            LogAircraft = self.env['product.log.availability']
            for company in self.env.user.company_ids:
                LogAircraft.run_log_scheduler(use_new_cursor=self._cr.dbname, company_id=company.id)
            # close the new cursor
            self._cr.close()
            return {}

    @api.multi
    def update_log_availability(self):
        threaded_update_logs = threading.Thread(target=self._update_product_logs, args=())
        threaded_update_logs.start()
        return {'type': 'ir.actions.act_window_close'}





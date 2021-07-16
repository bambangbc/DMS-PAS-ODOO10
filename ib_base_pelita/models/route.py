# -*- coding: utf-8 -*-
# © 2017 Ibrohim Binladin | ibradiiin@gmail.com | +62-838-7190-9782
from odoo import api, fields, models, _
import logging
_logger = logging.getLogger(__name__)


class RouteOperation(models.Model):
    _name = "route.operation"
    #
    # @api.one
    # @api.depends('route_line_ids.name','from_area_id.name', 'to_area_id.name')
    # def _compute_complete_route(self):
    #     deskripsi = []
    #     if self.from_area_id:
    #         deskripsi.append(self.from_area_id.code)
    #     if self.route_line_ids:
    #         for rol in self.route_line_ids:
    #             if rol.name and rol.name.code:
    #                 deskripsi.append(rol.name.code)
    #     if self.to_area_id:
    #         deskripsi.append(self.to_area_id.code)
    #     self.name = '%s' % (' - '.join(deskripsi) or _(''))

    complete_route = fields.Char(string='Complete Route', track_visibility='onchange', copy=False, index=True)
    # compute='_compute_complete_route', store=True,




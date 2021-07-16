# -*- coding: utf-8 -*-
from odoo import http

# class Pelita(http.Controller):
#     @http.route('/pelita/pelita/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/pelita/pelita/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('pelita.listing', {
#             'root': '/pelita/pelita',
#             'objects': http.request.env['pelita.pelita'].search([]),
#         })

#     @http.route('/pelita/pelita/objects/<model("pelita.pelita"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('pelita.object', {
#             'object': obj
#         })
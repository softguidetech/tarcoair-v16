# -*- coding: utf-8 -*-
# from odoo import http


# class Fleet-extension(http.Controller):
#     @http.route('/fleet-extension/fleet-extension/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/fleet-extension/fleet-extension/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('fleet-extension.listing', {
#             'root': '/fleet-extension/fleet-extension',
#             'objects': http.request.env['fleet-extension.fleet-extension'].search([]),
#         })

#     @http.route('/fleet-extension/fleet-extension/objects/<model("fleet-extension.fleet-extension"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('fleet-extension.object', {
#             'object': obj
#         })

# -*- coding: utf-8 -*-
# from odoo import http


# class RgbRestrictCustomer(http.Controller):
#     @http.route('/rgb_restrict_customer/rgb_restrict_customer', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/rgb_restrict_customer/rgb_restrict_customer/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('rgb_restrict_customer.listing', {
#             'root': '/rgb_restrict_customer/rgb_restrict_customer',
#             'objects': http.request.env['rgb_restrict_customer.rgb_restrict_customer'].search([]),
#         })

#     @http.route('/rgb_restrict_customer/rgb_restrict_customer/objects/<model("rgb_restrict_customer.rgb_restrict_customer"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('rgb_restrict_customer.object', {
#             'object': obj
#         })

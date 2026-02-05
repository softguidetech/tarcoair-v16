# -*- coding: utf-8 -*-

from odoo import fields, models


class ResPartner(models.Model):
    _inherit = "res.partner"

    airline_root = fields.Char(string="Root", help="Airline customer root / reference.")



from odoo import models, fields, api, _
from odoo.exceptions import AccessError


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    @api.model
    def create(self, vals):
        user = self.env.user
        if user.has_group('tarcoair_extension.group_product_creation'):
            return super(ProductTemplate, self).create(vals)
        else:
            raise AccessError("You do not have permission to create products.")


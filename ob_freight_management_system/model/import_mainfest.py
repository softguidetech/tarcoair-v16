

from odoo import fields, models


class ImportMainefest(models.Model):
    _name = 'import.main'

    name = fields.Char('Owner Of Operation',required=True)
    registration = fields.Char(string='Registration',required=True)
    point_of_loading = fields.Many2one('freight.port',string='Point of Loading')
    point_of_unloading = fields.Many2one('freight.port',string='Point of Unloading')
    flight_no = fields.Char('Flight Number',required=True)
    flight_date = fields.Date('Flight Date',required=True)
    entering_date = fields.Datetime('Entering Stock Date',required=True)
    line_ids = fields.One2many('import.main.line','import_ma_id',)
    total_weight = fields.Float(string='Total Weight',compute='_total_weight')
    state = fields.Selection([('draft', 'Draft'), ('submit', 'Submitted'),
                              ('confirm', 'Confirmed'),
                              ('invoice', 'Invoiced'), ('done', 'Done'),
                              ('cancel', 'Cancel')], default='draft')
    clearance_count = fields.Integer(compute='compute_count')
    
    def _total_weight(self):
        for rec in self:
            total = 0
            for i in rec.line_ids:
                total+=i.net_weight
            rec.total_weight = total
    
    def create_custom_clearance(self):
        """Create custom clearance"""
        clearance = self.env['custom.clearance'].create({
            'name': 'CC - ' + self.name,
            'import_main_id': self.id,
            'date': self.entering_date,
            'loading_port_id': self.point_of_loading.id,
            'discharging_port_id': self.dpoint_of_unloading.id,
            # 'line_ids': [(6, 0, self.line_ids.ids)]
            # 'agent_id': self.agent_id.id,
        })
        result = {
            'name': 'action.name',
            'type': 'ir.actions.act_window',
            'views': [[False, 'form']],
            'target': 'current',
            'res_id': clearance.id,
            'res_model': 'custom.clearance',
        }
        # self.clearance = True
        return result
        
    # @api.depends('name')
    def compute_count(self):
        """Compute custom clearance and account move's count"""
        for rec in self:
            if rec.env['custom.clearance'].search([('import_main_id', '=', rec.id)]):
                rec.clearance_count = rec.env['custom.clearance'].search_count(
                    [('import_main_id', '=', rec.id)])
            else:
                rec.clearance_count = 0
            

            
class ImportMainfestLine(models.Model):
    _name = 'import.main.line'
    
    import_ma_id = fields.Many2one('import.main',string='Import')
    number = fields.Char('AWB Number',required=True)
    n_of_p = fields.Char('Number of Pices',required=True)
    cargo_type_id = fields.Many2one('cargo.type',string='Cargo Type')
    net_weight = fields.Float('Net Weight/KG',required=True)
    des_of_goods = fields.Char('Description of Goods',required=True)
    shipper = fields.Char('Shipper',required=True)
    consignee = fields.Many2one('res.partner',string="Consignee",required=True)
    origin = fields.Char('Origin')
    destination = fields.Char('Destination')
    scc = fields.Char('SCC')
    custom_status = fields.Char('Custom Status')
    mft_remarks = fields.Char('MFT Remarks')
    
# Copyright 2020 Openindustry.it SAS
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from odoo import models, fields, exceptions, api, _


class Picking(models.Model):
    _inherit = "stock.picking"

    project_id = fields.Many2one('project.project', 'Project')

    @api.constrains('origin')
    def _check_project_from_origin(self):
        for record in self:
            if record.origin:
                obj_sale_ids = self.env['sale.order'].search([('name', 'like', record.origin)])
                if obj_sale_ids:
                    for obj_sale in obj_sale_ids:
                        record.project_id = obj_sale.project_id.id
                obj_purchase_ids = self.env['purchase.order'].search([('project_id', '=', record.origin)])
                if obj_purchase_ids:
                    for obj_purchase in obj_purchase_ids:
                        record.project_id = obj_purchase.project_id.id


class ProductProduct(models.Model):
    _inherit = "product.product"

    resource_type = fields.Selection([
        ('equipment', 'Equipment'),
        ('material', 'Material'),
        ('space', 'Spaces'),
        ('user', 'Human'),
        ('other', 'Others')], string='Type resource')

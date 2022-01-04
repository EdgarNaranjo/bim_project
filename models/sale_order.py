# Copyright 2020 Openindustry.it SAS
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from odoo import models, fields, exceptions, api, _
from odoo.exceptions import UserError


class SaleOrder(models.Model):
    _inherit = "sale.order"

    # @api.constrains('state', 'order_line')
    # def _check_state_quotation(self):
    #     for record in self:
    #         if not record.order_line:
    #             raise UserError(_("The quotation must contain at least one line. Contact Admin user!"))
    #         else:
    #             if record.state == 'sale':
    #                 pass


class ChapterSaleBim(models.Model):
    _name = "chapter.sale.bim"
    _description = "Chapter Sale Bim"

    name = fields.Char('Chapter', index=True, required=True)


class DepartureSaleBim(models.Model):
    _name = "departure.sale.bim"
    _description = "Departure Sale Bim"

    name = fields.Char('Departure', index=True, required=True)
    parent_id = fields.Many2one('departure.sale.bim', 'Parent Departure', index=True, ondelete='cascade')
    child_id = fields.One2many('departure.sale.bim', 'parent_id', 'Child Departures')


class ResourceSaleBim(models.Model):
    _name = "resource.sale.bim"
    _description = "Resource Sale Bim"

    name = fields.Char('Resource', index=True, required=True)
    departure_id = fields.Many2one('departure.sale.bim', 'Departure', index=True)
    chapter_id = fields.Many2one('chapter.sale.bim', 'Chapter', index=True)





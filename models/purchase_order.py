# Copyright 2020 Openindustry.it SAS
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from odoo import models, fields, exceptions, api, _


class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    project_id = fields.Many2one('project.project', 'Project')

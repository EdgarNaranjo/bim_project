# Copyright 2020 Openindustry.it SAS
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from odoo import models, fields, exceptions, api, _


class Users(models.Model):
    _inherit = "res.users"

    is_bim = fields.Boolean('Bim User', help="Check bim user")


class Groups(models.Model):
    _inherit = "res.groups"

    is_bim = fields.Boolean('Bim User', help="Check bim user")

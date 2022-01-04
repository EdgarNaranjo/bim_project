# Part of Odoo. See LICENSE file for full copyright and licensing details.
from collections import defaultdict
from datetime import datetime
from random import randint
import pytz

from odoo import api, fields, models
from odoo.tools.misc import DEFAULT_SERVER_DATETIME_FORMAT


class ResourceResource(models.Model):
    _inherit = 'resource.resource'

    resource_type = fields.Selection([
        ('equipment', 'Equipment'),
        ('material', 'Material'),
        ('space', 'Spaces'),
        ('user', 'Human'),
        ('other', 'Others')], string='Type', required=True)
    resource_ids = fields.Many2many('resource.calendar', relation='resource_calendar_bim_rel', column1='resource_id', column2='calendar_id', string='Calendar Work')

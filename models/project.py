# Copyright 2020 Openindustry.it SAS
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from odoo import models, fields, exceptions, api, _


class Project(models.Model):
    _inherit = "project.project"

    def _get_company_currency(self):
        self.currency_id = self.env.user.company_id.currency_id

    doc_count = fields.Integer(compute='_compute_attached_docs_count', string="Number of documents attached")
    street = fields.Char()
    zip = fields.Char(change_default=True)
    city = fields.Char()
    state_id = fields.Many2one("res.country.state", string='State', ondelete='restrict', domain="[('country_id', '=?', country_id)]")
    country_id = fields.Many2one('res.country', string='Country', ondelete='restrict')
    count_sale = fields.Integer('Count quotation', compute='_calc_count_sale')
    count_meeting = fields.Integer('Count meeting', compute='_calc_count_meeting')
    count_purchase = fields.Integer('Count purchase', compute='_calc_count_purchase')
    count_picking = fields.Integer('Count picking', compute='_calc_count_picking')
    currency_id = fields.Many2one('res.currency', compute='_get_company_currency', readonly=True, string="Currency", help='Utility field to express amount currency')
    amount_total = fields.Float('Amount Total', compute='_call_amount_sale_project')
    date_awarded = fields.Date('Date awarded')

    def _calc_count_picking(self):
        for obj_proj in self:
            obj_picking_ids = self.env['stock.picking'].search([('project_id', '=', obj_proj.id), ('picking_type_id.code', '=', 'outgoing')])
            obj_proj.count_picking = len(obj_picking_ids) if obj_picking_ids else 0

    def _calc_count_purchase(self):
        for obj_proj in self:
            obj_purchase_ids = self.env['purchase.order'].search([('project_id', '=', obj_proj.id)])
            obj_proj.count_purchase = len(obj_purchase_ids) if obj_purchase_ids else 0

    def _call_amount_sale_project(self):
        for record in self:
            sum_val = 0
            obj_sale_ids = self.env['sale.order'].search([('project_id', '=', record.id)])
            if obj_sale_ids:
                for obj_sale in obj_sale_ids:
                    sum_val += obj_sale.amount_total
            record.amount_total = sum_val

    def _calc_count_sale(self):
        for obj_proj in self:
            obj_sale_ids = self.env['sale.order'].search([('project_id', '=', obj_proj.id)])
            obj_proj.count_sale = len(obj_sale_ids) if obj_sale_ids else 0

    def _calc_count_meeting(self):
        for obj_proj in self:
            obj_meeting_ids = self.env['calendar.event'].search([('project_id', '=', obj_proj.id)])
            obj_proj.count_meeting = len(obj_meeting_ids) if obj_meeting_ids else 0

    def _compute_attached_docs_count(self):
        Attachment = self.env['ir.attachment']
        for project in self:
            project.doc_count = Attachment.search_count(['|', '&', ('res_model', '=', 'project.project'), ('res_id', '=', project.id), '&', ('res_model', '=', 'project.task'), ('res_id', 'in', project.task_ids.ids)])

    def attachment_tree_view(self):
        action = self.env['ir.actions.act_window']._for_xml_id('base.action_attachment')
        action['domain'] = str(['|', '&', ('res_model', '=', 'project.project'), ('res_id', 'in', self.ids), '&', ('res_model', '=', 'project.task'), ('res_id', 'in', self.task_ids.ids)])
        action['context'] = "{'default_res_model': '%s','default_res_id': %d}" % (self._name, self.id)
        return action

    def schedule_meeting(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Meeting',
            'res_model': 'calendar.event',
            'view_mode': 'calendar,tree',
            'domain': [('project_id', '=', self.id)],
            'context': ({'default_project_id': self.id})
        }

    def quotation_project(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Quotations',
            'res_model': 'sale.order',
            'view_mode': 'tree,form',
            'domain': [('project_id', '=', self.id)],
            'context': ({'default_project_id': self.id})
        }

    def purchase_project(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'RFQ',
            'res_model': 'purchase.order',
            'view_mode': 'tree,form',
            'domain': [('project_id', '=', self.id)],
            'context': ({'default_project_id': self.id})
        }

    def picking_project(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Delivery',
            'res_model': 'stock.picking',
            'view_mode': 'tree,form',
            'domain': [('picking_type_id.code', '=', 'outgoing'), ('project_id', '=', self.id)],
            'context': ({'default_project_id': self.id})
        }



# Copyright 2020 Openindustry.it SAS
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from odoo import models, fields, exceptions, api, _
from odoo.exceptions import UserError


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
    amount_m2 = fields.Float('Amount m2', compute='_call_amount_sale_project')
    amount_bidding = fields.Float('Amount bidding')
    amount_awarded = fields.Float('Amount awarded')
    date_awarded = fields.Date('Date awarded')
    date_contract = fields.Date('Date contract')
    date_init_real = fields.Date('Date init real')
    date_finish_real = fields.Date('Date finish real')
    area = fields.Float('Area (m2)')
    expedient = fields.Char('Expedient')
    code = fields.Char('Code')
    department_id = fields.Many2one('hr.department', 'Department', domain="['|', ('company_id', '=', False), ('company_id', '=', company_id)]")
    currency_project_id = fields.Many2one('res.currency', string='Currency', help="Forces all moves for this account to have this account currency.", tracking=True)
    calendar_id = fields.Many2one('resource.calendar', 'Calendar Work')

    @api.model
    def create(self, vals):
        vals['code'] = self.env['ir.sequence'].next_by_code('project.project')
        request = super(Project, self).create(vals)
        request.message_post(body=_("Project id %s") % request.code)
        return request

    def _calc_count_picking(self):
        for obj_proj in self:
            obj_picking_ids = self.env['stock.picking'].search([('project_id', '=', obj_proj.id), ('picking_type_id.code', '=', 'outgoing')])
            obj_proj.count_picking = len(obj_picking_ids) if obj_picking_ids else 0

    def _calc_count_purchase(self):
        for obj_proj in self:
            obj_purchase_ids = self.env['purchase.order'].search([('project_id', '=', obj_proj.id)])
            obj_proj.count_purchase = len(obj_purchase_ids) if obj_purchase_ids else 0

    @api.depends('amount_total', 'amount_m2', 'area')
    def _call_amount_sale_project(self):
        for record in self:
            sum_val = 0
            obj_sale_ids = self.env['sale.order'].search([('project_id', '=', record.id), ('state', 'in', ['sale', 'done'])])
            if obj_sale_ids:
                for obj_sale in obj_sale_ids:
                    sum_val += obj_sale.amount_total
            record.amount_total = sum_val
            record.amount_m2 = record.amount_total / record.area if record.area else 0

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


class Task(models.Model):
    _inherit = "project.task"

    def _get_company_currency(self):
        self.currency_id = self.env.user.company_id.currency_id

    @api.depends('cost_ids')
    def _compute_count_resource(self):
        for record in self:
            record.count_resource = len(record.cost_ids) if record.cost_ids else False

    direct_cost = fields.Float('Direct Cost')
    total_quotation = fields.Float('Total Quotation')
    currency_id = fields.Many2one('res.currency', compute='_get_company_currency', readonly=True, string="Currency", help='Utility field to express amount currency')
    cost_ids = fields.One2many('cost.task.bim', 'task_id', 'Cost Task')
    code = fields.Char('Code')
    count_day = fields.Float('Duration (days)', help='Duration planned')
    count_real_day = fields.Float('Duration real (days)', help='Duration real')
    date_init_real = fields.Datetime('Date init real')
    date_finish_real = fields.Datetime('Date finish real')
    count_resource = fields.Integer('Resources', compute='_compute_count_resource')

    @api.model
    def create(self, vals):
        vals['code'] = self.env['ir.sequence'].next_by_code('project.task')
        if vals['parent_id']:
            vals['code'] = 'SUB' + self.env['ir.sequence'].next_by_code('project.task')
        request = super(Task, self).create(vals)
        request.message_post(body=_("Task id %s") % request.code)
        return request

    @api.constrains('planned_date_begin', 'planned_date_end', 'date_init_real', 'date_finish_real')
    def check_duration_project(self):
        for record in self:
            if record.planned_date_begin and record.planned_date_end:
                record.count_day = (record.planned_date_end - record.planned_date_begin).days
            if record.date_init_real and record.date_finish_real:
                record.count_real_day = (record.date_finish_real - record.date_init_real).days

    def resource_project(self):
        list_id = []
        for record in self:
            list_id = [item.item_id.resource_id.id for item in record.cost_ids]
        form_view_ref = self.env.ref('bim_project.resource_resource_with_employee_form_view_bim_inherit2', False)
        tree_view_ref = self.env.ref('bim_project.resource_resource_tree_view_bim_inherit2', False)
        return {
            'type': 'ir.actions.act_window',
            'name': 'Resource',
            'res_model': 'resource.resource',
            'view_mode': 'tree,kanban,form',
            'views': [(tree_view_ref.id, 'tree'), (form_view_ref.id, 'form')],
            'domain': [('id', 'in', list_id)],
        }
        pass


class CostTaskBim(models.Model):
    _name = "cost.task.bim"
    _description = "Cost Task"
    _rec_name = 'item_id'

    def _get_company_currency(self):
        self.currency_id = self.env.user.company_id.currency_id

    item_id = fields.Many2one('item.cost.task.bim', 'Resources')
    task_type = fields.Selection([
        ('fix', 'Fixed'),
        ('daily', 'Daily'),
        ('unit', 'Unit')], string='Type', required=True)
    value_unit = fields.Float('Cost')
    quantity = fields.Float('Quantity')
    subtotal_value = fields.Float('Subtotal')
    currency_id = fields.Many2one('res.currency', compute='_get_company_currency', readonly=True, string="Currency", help='Utility field to express amount currency')
    task_id = fields.Many2one('project.task', 'Task')


class ItemCostTaskBim(models.Model):
    _name = "item.cost.task.bim"
    _description = "Item Cost Task"
    _rec_name = 'resource_id'

    resource_id = fields.Many2one('resource.resource', 'Resources')


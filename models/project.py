# Copyright 2020 Openindustry.it SAS
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from odoo import models, fields, exceptions, api, _


class Project(models.Model):
    _name = "project.project"

    doc_count = fields.Integer(compute='_compute_attached_docs_count', string="Number of documents attached")

    def _compute_attached_docs_count(self):
        Attachment = self.env['ir.attachment']
        for project in self:
            project.doc_count = Attachment.search_count(['|', '&', ('res_model', '=', 'project.project'), ('res_id', '=', project.id), '&', ('res_model', '=', 'project.task'), ('res_id', 'in', project.task_ids.ids)])

    def attachment_tree_view(self):
        action = self.env['ir.actions.act_window']._for_xml_id('base.action_attachment')
        action['domain'] = str(['|', '&', ('res_model', '=', 'project.project'), ('res_id', 'in', self.ids), '&', ('res_model', '=', 'project.task'), ('res_id', 'in', self.task_ids.ids)])
        action['context'] = "{'default_res_model': '%s','default_res_id': %d}" % (self._name, self.id)
        return action

# Copyright 2020 Openindustry.it SAS
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from odoo import models, fields, exceptions, api, _
from datetime import datetime, timedelta, date
import logging
_logger = logging.getLogger(__name__)


class Meeting(models.Model):
    _inherit = 'calendar.event'

    project_id = fields.Many2one('project.project', 'Project')


class MailActivity(models.Model):
    _inherit = 'mail.activity'

    def _default_attendance_ids(self):
        list_attendance = []
        task_filter = []
        if self.env.user.partner_id:
            owner_partner = self.env.user.partner_id
            list_attendance.append(owner_partner.id)
        obj_task_ids = self.env['project.task'].search([('user_ids', '!=', False)])
        if self.env.context.get('default_res_model'):
            default_model = self._context['default_res_model']
            if default_model == 'project.project':
                task_filter = obj_task_ids.filtered(lambda e: e.project_id.id == self._context['default_res_id'])
            if default_model == 'project.task':
                task_filter = obj_task_ids.filtered(lambda e: e.id == self._context['default_res_id'])
        if task_filter:
            list_users = [task.user_ids for task in task_filter]
            for users in list_users:
                list_attendance += [user.partner_id.id for user in users]
        return list_attendance

    attendance_ids = fields.Many2many('res.partner', relation='mail_project_partner_rel', column1='mail_id', column2='partner_id', string='Assignees', default=_default_attendance_ids)

    def show_obj_id(self, dict_meet):
        dict_meet['project_id'] = ''
        obj_id = self._context['default_res_id']
        if obj_id:
            if self.env.context.get('default_res_model'):
                default_model = self._context['default_res_model']
                if default_model == 'project.project':
                    dict_meet['project_id'] = obj_id
                if default_model == 'project.task':
                    obj_task_id = self.env['project.task'].search([('id', '=', obj_id)], limit=1)
                    dict_meet['project_id'] = obj_task_id.project_id.id if obj_task_id.project_id else False
        return dict_meet

    def action_create_bim_event(self):
        create_even = self.env['calendar.event']
        create_attendee = self.env['calendar.attendee']
        dict_meet = {
            'name': '',
            'partner_ids': self.attendance_ids,
            'allday': 'True',
            'user_id': self.user_id.id if self.user_id else False,
            'project_id': False,
            'attendee_ids': False,
            'alarm_ids': [alarm.id for alarm in self.env['calendar.alarm'].search([('alarm_type', '=', 'notification')], limit=1) if alarm]
        }
        summary = self.summary if self.summary else ''
        dict_meet['name'] = self.activity_type_id.name + ': ' + summary
        self.show_obj_id(dict_meet)
        if len(dict_meet) > 0:
            # eliminar los que tengan valor False
            dict_meet = dict(filter(lambda x: x[1] != False, dict_meet.items()))
            ok_create_even = create_even.create(dict_meet)
            if ok_create_even:
                date_tmp = (self.date_deadline - date.today()).days
                dict_update = {
                    'start': ok_create_even.start + timedelta(days=date_tmp),
                    'stop': ok_create_even.stop + timedelta(days=date_tmp),
                }
                ok_create_even.write(dict_update)
                _logger.info("Create Event '%s'" % ok_create_even.name)
                for attendance in dict_meet['partner_ids']:
                    create_attendee.create({'event_id': ok_create_even.id, 'partner_id': attendance.id})
        obj_activity_ids = self.env['mail.activity'].search([('summary', 'like', summary)])
        if obj_activity_ids and len(obj_activity_ids) > 1:
            activity_filters = obj_activity_ids.filtered(lambda e: e.summary == summary)
            if activity_filters:
                for act_fil in activity_filters:
                    act_fil.unlink()

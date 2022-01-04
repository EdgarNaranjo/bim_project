# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
from odoo import api, fields, models, _
from odoo.exceptions import UserError
from odoo.tools.misc import format_date
import os
import csv
import base64
from datetime import datetime, timedelta, date
import xlrd

from dateutil.relativedelta import relativedelta
from itertools import chain

# try:
#     import ftplib
# except ImportError:
#     raise ImportError('This module needs pysftp to automaticly write backups to the FTP through SFTP. Please install pysftp on your system. (sudo pip install pysftp)')
#
# try:
#     import urllib.request as urllib2
# except ImportError:
#     raise ImportError("This module needs urllib2. (sudo pip install urllib2)")
#
# try:
#     import ssl
# except ImportError:
#     ssl = None

import logging
_logger = logging.getLogger(__name__)


class IrAttachment(models.Model):
    _inherit = 'ir.attachment'

    models_id = fields.Many2one('bim.models.import', 'Report Balance', index=True)


class BimModelsImport(models.Model):
    _name = 'bim.models.import'
    _inherit = ['portal.mixin', 'mail.thread', 'mail.activity.mixin', 'utm.mixin']
    _description = 'Bim Models'
    _order = 'create_date desc'

    name = fields.Char('Document Name', default=lambda self: _('New'), copy=False)
    type_file = fields.Selection([
        ('excel', 'Excel'),
        ('xml', 'XML'),
        ('bc3', 'BC3'),
        ('other', 'Other'),
    ], string='Type file', index=True, track_visibility='onchange')
    state = fields.Selection([
        ('draft', 'To import'),
        ('pend', 'Imported'),
        ('done', 'Saved'),
        ('cancel', 'Cancelled'),
    ], string='Status', default="draft", index=True, track_visibility='onchange')
    date_import = fields.Datetime(string='Import Date', required=True, readonly=True, index=True, copy=False, default=fields.Datetime.now)
    attachment_count = fields.Integer(compute='_compute_todo_attachment')
    attachment_ids = fields.One2many('ir.attachment', 'models_id', 'Attachments')
    origin = fields.Char('Origin')

    @api.model
    def create(self, vals):
        if vals.get('name', _('New')) == _('New'):
            seq_date = None
            vals['name'] = self.env['ir.sequence'].next_by_code('bim.models.import', sequence_date=seq_date) or _('New')
        request = super(BimModelsImport, self).create(vals)
        request.message_post(body=_("Import %s en odoo") % request.name)
        return request

    @api.ondelete(at_uninstall=False)
    def _unlink_except_draft_or_cancel(self):
        for bim in self:
            if bim.state not in ('draft', 'cancel'):
                raise UserError(_('You can not delete a saved Models import. You must first cancel it.'))

    def import_files(self):
        self.ensure_one()
        action = self.env["ir.actions.actions"]._for_xml_id("bim_project.action_calendar_event")
        # action['context'] = {
        #     'default_activity_type_id': self.activity_type_id.id,
        #     'default_res_id': self.env.context.get('default_res_id'),
        #     'default_res_model': self.env.context.get('default_res_model'),
        #     'default_name': self.summary or self.res_name,
        #     'default_description': self.note and tools.html2plaintext(self.note).strip() or '',
        #     'default_activity_ids': [(6, 0, self.ids)],
        # }
        self.state = 'pend'
        return action

    def save_files(self):
        for record in self:
            record.state = 'done'

    def cancel_model(self):
        for record in self:
            record.state = 'cancel'

    # def _create_file(self, name):
    #     today = datetime.today().strftime("%d-%m-%Y:%H:%M")
    #     obj_connection_id = self.env['media.setting'].search([('active', '=', True)])
    #     if obj_connection_id:
    #         obj_connect = obj_connection_id[0]
    #         url_route = obj_connect.url_output
    #         _logger.info('RUTA OUT')
    #     if url_route:
    #         if not os.path.exists(url_route):
    #             os.makedirs(url_route)
    #         if os.path.exists(url_route):
    #             ruta = os.path.join(url_route, name + '_' + today)
    #             archivo_txt = ruta + '.csv'
    #             return archivo_txt

    # def _create_content(self, file, balance):
    #     if balance.type_report not in ['balance', 'pl']:
    #         file.writerow(['Sociedad', 'Año', 'Mes', 'Elemento Pep', 'Número de Cuenta', 'Centro de Coste', 'Sociedad GL', 'Flujo', 'Importe'])
    #     else:
    #         file.writerow(['Sociedad', 'Año', 'Mes', 'Elemento Pep', 'Número de Cuenta', 'Centro de Coste', 'Sociedad GL', 'Importe'])
    #     if balance.report_lines:
    #         for line in balance.report_lines:
    #             if balance.type_report not in ['balance', 'pl']:
    #                 if line.type_flow:
    #                     keys_list = LIST_FLOW.keys()
    #                     if line.type_flow in keys_list:
    #                         for key in keys_list:
    #                             if key == line.type_flow:
    #                                 value_flow = LIST_FLOW.get(key)
    #                     file.writerow([line.name_company or '', line.year_now or '', line.month_now or '', line.pep_element or '', line.account_number or '', line.cost_center or '', line.company_gl or '', value_flow or '', line.amount_total or ''])
    #             else:
    #                 file.writerow([line.name_company or '', line.year_now or '', line.month_now or '', line.pep_element or '', line.account_number or '', line.cost_center or '', line.company_gl or '', line.amount_total or ''])
    #     return file

    # def _create_attachment(self, ruta_file, balance):
    #     contenido_pdf = file_get_contents(ruta_file)
    #     bin_data = base64.b64encode(contenido_pdf)
    #     attachment = {
    #         'name': ruta_file.split('/')[-1],
    #         'datas': bin_data,
    #         'res_id': balance.id,
    #         'models_id': balance.id,
    #     }
    #     obj_att = self.env['ir.attachment'].create(attachment)
    #     return obj_att

    # def prepare_sent(self):
    #     for balance in self:
    #         if not balance.report_lines:
    #             self._cr.execute(
    #                 """ SELECT * FROM account_balance_insert_select(""" + str(balance.id) + """ ,'""" + datetime.strftime(balance.start_date, "%Y-%m-%d") + """','""" + datetime.strftime(balance.end_date, "%Y-%m-%d") + """','""" + balance.type_report + """',""" + str(balance.create_uid.id) + """,""" + str(balance.write_uid.id) + """)""")
    #             self._prepared_files(balance)
    #         else:
    #             self._prepared_files(balance)
    #     return False

    # def _prepared_files(self, balance):
    #     if balance.type_report == 'balance':
    #         budget_name = "BALANCE"
    #     elif balance.type_report == 'pl':
    #         budget_name = "PL"
    #     else:
    #         budget_name = "Assets"
    #     if budget_name and balance.report_lines:
    #         obj_create_file = self._create_file(budget_name)
    #         if obj_create_file:
    #             with open(obj_create_file, 'w') as t_csv:
    #                 out_file = csv.writer(t_csv, delimiter=';')
    #                 obj_content = self._create_content(out_file, balance)
    #                 if obj_content:
    #                     _logger.info("Contenido generado")
    #                     t_csv.close()
    #                     create_attach = self._create_attachment(obj_create_file, balance)
    #                     if create_attach:
    #                         _logger.info("Attachment creado")
    #                         os.remove(obj_create_file)
    #             balance.message_post(body=_("Generado fichero csv para: %s") % balance.name)
    #             balance.state = 'pend'
    #     return False

    # def sent_server(self):
    #     all_ok = False
    #     for report_base in self:
    #         if report_base.attachment_ids:
    #             last_file = report_base.attachment_ids[:1]
    #             obj_connection_id = self.env['media.setting'].search([('active', '=', True)])
    #             if obj_connection_id:
    #                 obj_connect = obj_connection_id[0]
    #                 url_output = obj_connect.url_output
    #                 url_server_input = obj_connect.url_server_input
    #                 # create url o read
    #                 if not os.path.exists(url_output):
    #                     os.makedirs(url_output)
    #                 if os.path.exists(url_output):
    #                     ruta = os.path.join(url_output, last_file.name)
    #                     with open(ruta, 'wb') as fw_f:
    #                         fw_f.write(base64.b64decode(last_file.datas))
    #                     fw_f.close()
    #                     test_conection = obj_connect.test_connection00(obj_connect)
    #                     if test_conection[0]:
    #                         _logger.info("Connection sucessful at CRON!!")
    #                         ftp = test_conection[1]
    #                         if ftp:
    #                             ftp.cwd('/' + str(url_server_input))
    #                             _logger.info("Listo para escribir en Media Pro")
    #                             upload_sucessfull = obj_connect.upload(ftp, ruta)
    #                             if upload_sucessfull:
    #                                 _logger.info("Documento subido a Media Pro satisfactoriamente")
    #                                 report_base.message_post(body=_("Enviado fichero a servidor MediaPro: %s") % last_file.name)
    #                                 os.remove(ruta)
    #                     # borrar del server
    #                     all_ok = True
    #         if all_ok:
    #             report_base.state = 'send'
    #             return True

    def action_view_attachments(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Modelos Adjuntos',
            'res_model': 'ir.attachment',
            'view_mode': 'kanban,tree,form',
            'view_type': 'form',
            'domain': [('id', 'in', self.attachment_ids.ids)]
        }

    def _compute_todo_attachment(self):
        for obj_media in self:
            obj_media.attachment_count = len(obj_media.attachment_ids)

    # def _compute_todo_move_line(self):
    #     for obj_media in self:
    #         list_mapped = [line.account_number for line in obj_media.report_lines]
    #         obj_read_book = self.env['account.move.line'].search([('parent_state', '=', 'posted'), ('account_id.account_related', 'in', list_mapped)])
    #         if obj_media.type_report == 'pl':
    #             book_filtered = obj_read_book.filtered(lambda e: obj_media.start_date <= e.date <= obj_media.end_date)
    #         else:
    #             book_filtered = obj_read_book.filtered(lambda e: e.date <= obj_media.end_date)
    #     if book_filtered:
    #         obj_media.line_count = len(book_filtered)
    #     else:
    #         obj_media.line_count = 0

    # def action_view_move_line(self):
    #     for obj_media in self:
    #         list_mapped = [line.account_number for line in obj_media.report_lines]
    #         obj_read_book = self.env['account.move.line'].search([('parent_state', '=', 'posted'), ('account_id.account_related', 'in', list_mapped)])
    #         if obj_media.type_report == 'pl':
    #             book_filtered = obj_read_book.filtered(lambda e: obj_media.start_date <= e.date <= obj_media.end_date)
    #         else:
    #             book_filtered = obj_read_book.filtered(lambda e: e.date <= obj_media.end_date)
    #         if book_filtered:
    #             return {
    #                 'type': 'ir.actions.act_window',
    #                 'name': 'Apuntes contables',
    #                 'res_model': 'account.move.line',
    #                 'view_mode': 'tree,form',
    #                 'view_type': 'form',
    #                 'domain': [('id', 'in', book_filtered.ids)]
    #             }


# def file_get_contents(filename, use_include_path=0, context=None, offset=-1, maxlen=-1):
#     if (filename.find('://') > 0):
#         ret = urllib2.urlopen(filename).read()
#         if (offset > 0):
#             ret = ret[offset:]
#         if (maxlen > 0):
#             ret = ret[:maxlen]
#         return ret
#     else:
#         fp = open(filename, 'rb')
#         try:
#             if (offset > 0):
#                 fp.seek(offset)
#             ret = fp.read(maxlen)
#             return ret
#         finally:
#             fp.close()

# class ReportAccount(models.Model):
#     _name = 'account.report'
#     _description = 'Account Report'
#     _order = 'create_date desc'
#     _inherit = ['mail.activity.mixin', 'mail.thread']
#
#     name = fields.Char('Document Name', default="Nuevo Reporte", copy=False)
#     state = fields.Selection([
#         ('draft', 'Draft'),
#         ('done', 'Done'),
#     ], string='Status', index=True, defaulf='draft')
#     attachment_ids = fields.Many2many('ir.attachment', 'attact_efirm_rel', 'efirm_id', 'attach_id', ondelete="cascade", string='Attachments')
#     move_id = fields.Many2one('account.move', 'Asiento Contable', index=True)
#
#     @api.model
#     def create(self, vals):
#         request = super(ReportAccount, self).create(vals)
#         if request.name == "Nuevo Reporte":
#             sequence_name = self.env['ir.sequence'].next_by_code('report.balance') or "Nuevo Reporte"
#             request.name = 'PAYROL' + sequence_name
#             request.message_post(body=_("Creado PAYROL: %s") % request.name)
#         request.state = 'draft'
#         return request
#
#     def generated_report_account(self):
#         ok_generated = False
#         obj_move = self.env['account.move'].create({'ref': 'Asiento: Nomina (excel)'})
#         create_move_line = self.env['account.move.line']
#         if obj_move:
#             dict_move_line = {
#                 'account_id': '',
#                 'name': False,
#                 'project_account_id': False,
#                 'debit': 0,
#                 'credit': 0,
#                 'move_id': obj_move[0].id if obj_move else False
#             }
#             for report_base in self:
#                 if report_base.attachment_ids:
#                     obj_connection_id = self.env['media.setting'].search([('active', '=', True)])
#                     if obj_connection_id:
#                         obj_connect = obj_connection_id[0]
#                         url_route = obj_connect.other_url_input
#                         _logger.info('RUTA IN')
#                         if url_route:
#                             if not os.path.exists(url_route):
#                                 os.makedirs(url_route)
#                             if os.path.exists(url_route):
#                                 for attach in report_base.attachment_ids:
#                                     archivo_excel = os.path.join(url_route, attach.name)
#                                     with open(archivo_excel, 'wb') as fw_f:
#                                         fw_f.write(base64.b64decode(attach.datas))
#                                     fw_f.close()
#                                     if archivo_excel:
#                                         wb = xlrd.open_workbook(archivo_excel)
#                                         hoja = wb.sheet_by_index(1)
#                                         total_filas = hoja.nrows
#                                         if total_filas % 2 != 0:
#                                             raise UserError(_("No se puede crear una entrada de diario no balanceada...,\n"
#                                               "Total de lineas: %s") % str(total_filas))
#                                         if type(hoja.cell_value(rowx=0, colx=1)) not in [int, float]:
#                                             raise UserError(_('El excel no cumple con el formato especificado \n La cabecera debe contener caracteres numéricos.'))
#                                         else:
#                                             obj_account_id = self.env['account.account'].search([('deprecated', '=', False)])
#                                             list_account = [float(account.code) for account in obj_account_id]
#                                             list_excel = hoja.col_values(colx=3)
#
#                                             if not any(excel for excel in list_excel if excel in list_account):
#                                                 raise UserError(_('No existen "account mapped" en odoo correspondientes con las líneas del excel.'))
#                                             else:
#                                                 for i in range(hoja.nrows):
#                                                     line = hoja.row(i)
#                                                     # lines
#                                                     obj_account_id = self.env['account.account'].search([('code', 'like', str(int(line[3].value)).strip())])
#                                                     obj_project_id = self.env['account.analytic.account'].search([('name', 'like', line[19].value.strip())])
#                                                     if obj_account_id:
#                                                         account = obj_account_id[0]
#                                                         dict_move_line['account_id'] = account.id
#                                                         dict_move_line['name'] = line[7].value
#                                                         dict_move_line['project_account_id'] = obj_project_id[0].id if obj_project_id else False
#                                                         dict_move_line['debit'] = line[5].value
#                                                         dict_move_line['credit'] = line[6].value
#                                                         obj_lines = create_move_line.with_context(check_move_validity=False).create(dict_move_line)
#                                                         if obj_lines:
#                                                             ok_generated = True
#                                     if ok_generated:
#                                         report_base.message_post(body=_("Generado Asiento Contable con Ref: Asiento: Nomina (excel) en estado: Borrador"))
#                                         report_base.move_id = obj_move.id
#                                         report_base.state = 'done'

class ModelsWizard(models.TransientModel):
    _name = 'models.wizard'
    _description = 'Models Wizard'

    type_file = fields.Selection([
        ('excel', 'Excel'),
        ('xml', 'XML'),
        ('other', 'Other'),
    ], string='Type file', index=True, track_visibility='onchange')
    attachment_ids = fields.Many2many('ir.attachment', relation='models_attachment_rel', column1='models_id', column2='attachment_id', string='Attachments')

#     def set_non_active(self):
#         for obj_ufv in self:
#             if obj_ufv.ufv_ids:
#                 for line in obj_ufv.ufv_ids:
#                     line.write({'active': False})
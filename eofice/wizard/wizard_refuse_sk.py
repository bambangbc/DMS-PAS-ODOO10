from odoo import api, fields, models, _
from odoo.addons import decimal_precision as dp
from odoo.exceptions import UserError
from datetime import datetime
from datetime import date


class RefuseSk(models.TransientModel):
    _name = "refuse.sk"
    _description = "Refuse Surat Keluar"

    note = fields.Text('Catatan')

    @api.multi
    def refuse(self):
        sk = self.env['surat.keluar'].browse(self.env.context['active_id'])

        ##### mengirim email ke email tujuan ####

        #### Search Employee ####

        emp_obj = self.env['hr.employee']
        emp_src = emp_obj.sudo().search([('user_id', '=', sk.user_id.id)])

        #### search email company ####
        com_obj = self.env['res.company']
        com_src = com_obj.sudo().search([], limit=1)
        for comp in com_src:
            for send in emp_src:
                if send.work_email != False:
                    body_html = '<p>Kepada '+str(sk.user_id.name)+',</p> \n'+'<p> Surat Keluar yang anda buat dengan nomor '+str(
                        sk.name)+' Dengan Perihal '+str(sk.perihal)+' Mohon Untuk Segera Di tindak lanjuti karna ada beberapa catatan diantaranya '+str(self.note)
                    mail = self.env['mail.mail']
                    notif_mail = mail.sudo().create({'subject': 'Surat Keluar perihal '+str(sk.perihal),
                                                     'email_from': comp.email,
                                                     'email_to': send.work_email,
                                                     #'email_cc'     :
                                                     'auto_delete': True,
                                                     'type': 'notification',
                                                     #'recipient_ids' : [(6, 0, [gr.partner_id.id])],
                                                     'notification': True,
                                                     'body_html': body_html,
                                                     })
                    # _logger.info("created due date invoice alert to %s" % (gr.partner_id.email) )

        ##### Email Checker and Signer #####
        ck = 0
        count = 1
        if sk.state == 'checker1':
            ck = 1
        elif sk.state == 'checker2':
            ck = 2
        elif sk.state == 'checker3':
            ck = 3
        elif sk.state == 'checker4':
            ck = 4
        elif sk.state == 'checker5':
            ck = 5
        elif sk.state == 'signer':
            ck = 6
        while count < ck:
            #### Search Employee ####
            if count == 1 and sk.template.checker1 == True:
                emp_obj = self.env['hr.employee']
                emp_src = emp_obj.sudo().search(
                    [('user_id', '=', sk.template.user_id1.id)])

                #### search email company ####
                com_obj = self.env['res.company']
                com_src = com_obj.sudo().search([], limit=1)
                for comp in com_src:
                    for send in emp_src:
                        if emp_src != False:
                            body_html = '<p>Kepada '+str(send.user_id.name)+',</p> \n'+'<p> Surat Keluar yang di buat oleh '+str(sk.user_id.name)+' dengan nomor '+str(
                                sk.name)+' Dengan Perihal '+str(sk.perihal)+' Mohon Untuk Segera Di tindak lanjuti karna ada beberapa catatan diantaranya '+str(self.note)
                            mail = self.env['mail.mail']
                            notif_mail = mail.sudo().create({'subject': 'Surat Keluar perihal '+str(sk.perihal),
                                                             'email_from': comp.email,
                                                             'email_to': send.work_email,
                                                             #'email_cc'     :
                                                             'auto_delete': True,
                                                             'type': 'notification',
                                                             #'recipient_ids' : [(6, 0, [gr.partner_id.id])],
                                                             'notification': True,
                                                             'body_html': body_html,
                                                             })

            elif count == 2 and sk.template.checker2 == True:
                emp_obj = self.env['hr.employee']
                emp_src = emp_obj.sudo().search(
                    [('user_id', '=', sk.template.user_id2.id)])

                #### search email company ####
                com_obj = self.env['res.company']
                com_src = com_obj.sudo().search([], limit=1)
                for comp in com_src:
                    for send in emp_src:
                        if emp_src != False:
                            body_html = '<p>Kepada '+str(send.user_id.name)+',</p> \n'+'<p> Surat Keluar yang di buat oleh '+str(sk.user_id.name)+' dengan nomor '+str(
                                sk.name)+' Dengan Perihal '+str(sk.perihal)+' Mohon Untuk Segera Di tindak lanjuti karna ada beberapa catatan diantaranya '+str(self.note)
                            mail = self.env['mail.mail']
                            notif_mail = mail.sudo().create({'subject': 'Surat Keluar perihal '+str(sk.perihal),
                                                             'email_from': comp.email,
                                                             'email_to': send.work_email,
                                                             #'email_cc'     :
                                                             'auto_delete': True,
                                                             'type': 'notification',
                                                             #'recipient_ids' : [(6, 0, [gr.partner_id.id])],
                                                             'notification': True,
                                                             'body_html': body_html,
                                                             })

            elif count == 3 and sk.template.checker3 == True:
                emp_obj = self.env['hr.employee']
                emp_src = emp_obj.sudo().search(
                    [('user_id', '=', sk.template.user_id3.id)])

                #### search email company ####
                com_obj = self.env['res.company']
                com_src = com_obj.sudo().search([], limit=1)
                for comp in com_src:
                    for send in emp_src:
                        if emp_src != False:
                            body_html = '<p>Kepada '+str(send.user_id.name)+',</p> \n'+'<p> Surat Keluar yang di buat oleh '+str(sk.user_id.name)+' dengan nomor '+str(
                                sk.name)+' Dengan Perihal '+str(sk.perihal)+' Mohon Untuk Segera Di tindak lanjuti karna ada beberapa catatan diantaranya '+str(self.note)
                            mail = self.env['mail.mail']
                            notif_mail = mail.sudo().create({'subject': 'Surat Keluar perihal '+str(sk.perihal),
                                                             'email_from': comp.email,
                                                             'email_to': send.work_email,
                                                             #'email_cc'     :
                                                             'auto_delete': True,
                                                             'type': 'notification',
                                                             #'recipient_ids' : [(6, 0, [gr.partner_id.id])],
                                                             'notification': True,
                                                             'body_html': body_html,
                                                             })

            elif count == 4 and sk.template.checker4 == True:
                emp_obj = self.env['hr.employee']
                emp_src = emp_obj.sudo().search(
                    [('user_id', '=', sk.template.user_id4.id)])

                #### search email company ####
                com_obj = self.env['res.company']
                com_src = com_obj.sudo().search([], limit=1)
                for comp in com_src:
                    for send in emp_src:
                        if emp_src != False:
                            body_html = '<p>Kepada '+str(send.user_id.name)+',</p> \n'+'<p> Surat Keluar yang di buat oleh '+str(sk.user_id.name)+' dengan nomor '+str(
                                sk.name)+' Dengan Perihal '+str(sk.perihal)+' Mohon Untuk Segera Di tindak lanjuti karna ada beberapa catatan diantaranya '+str(self.note)
                            mail = self.env['mail.mail']
                            notif_mail = mail.sudo().create({'subject': 'Surat Keluar perihal '+str(sk.perihal),
                                                             'email_from': comp.email,
                                                             'email_to': send.work_email,
                                                             #'email_cc'     :
                                                             'auto_delete': True,
                                                             'type': 'notification',
                                                             #'recipient_ids' : [(6, 0, [gr.partner_id.id])],
                                                             'notification': True,
                                                             'body_html': body_html,
                                                             })

            elif count == 5 and sk.template.checker5 == True:
                emp_obj = self.env['hr.employee']
                emp_src = emp_obj.sudo().search(
                    [('user_id', '=', sk.template.user_id5.id)])

                #### search email company ####
                com_obj = self.env['res.company']
                com_src = com_obj.sudo().search([], limit=1)
                for comp in com_src:
                    for send in emp_src:
                        if emp_src != False:
                            body_html = '<p>Kepada '+str(send.user_id.name)+',</p> \n'+'<p> Surat Keluar yang di buat oleh '+str(sk.user_id.name)+' dengan nomor '+str(
                                sk.name)+' Dengan Perihal '+str(sk.perihal)+' Mohon Untuk Segera Di tindak lanjuti karna ada beberapa catatan diantaranya '+str(self.note)
                            mail = self.env['mail.mail']
                            notif_mail = mail.sudo().create({'subject': 'Surat Keluar perihal '+str(sk.perihal),
                                                             'email_from': comp.email,
                                                             'email_to': send.work_email,
                                                             #'email_cc'     :
                                                             'auto_delete': True,
                                                             'type': 'notification',
                                                             #'recipient_ids' : [(6, 0, [gr.partner_id.id])],
                                                             'notification': True,
                                                             'body_html': body_html,
                                                             })

            elif count == 6 and sk.template.signer6 == True:
                emp_obj = self.env['hr.employee']
                emp_src = emp_obj.sudo().search(
                    [('user_id', '=', sk.template.user_id6.id)])

                #### search email company ####
                com_obj = self.env['res.company']
                com_src = com_obj.sudo().search([], limit=1)
                for comp in com_src:
                    for send in emp_src:
                        if emp_src != False:
                            body_html = '<p>Kepada '+str(send.user_id.name)+',</p> \n'+'<p> Surat Keluar yang di buat oleh '+str(sk.user_id.name)+' dengan nomor '+str(
                                sk.name)+' Dengan Perihal '+str(sk.perihal)+' Mohon Untuk Segera Di tindak lanjuti karna ada beberapa catatan diantaranya '+str(self.note)
                            mail = self.env['mail.mail']
                            notif_mail = mail.sudo().create({'subject': 'Surat Keluar perihal '+str(sk.perihal),
                                                             'email_from': comp.email,
                                                             'email_to': send.work_email,
                                                             #'email_cc'     :
                                                             'auto_delete': True,
                                                             'type': 'notification',
                                                             #'recipient_ids' : [(6, 0, [gr.partner_id.id])],
                                                             'notification': True,
                                                             'body_html': body_html,
                                                             })

            count = count + 1
        send = self.env['mail.mail'].sudo().process_email_queue()
        if sk.note :
            note = self.env.user.name+" "+str(datetime.now())+" "+"("+sk.state+")"+"<p>"+self.note+"</p>"+"<p><br></p>"+sk.note
        else :
            note = self.env.user.name+" "+str(datetime.now())+" "+"("+sk.state+")"+"<p>"+self.note+"</p>"
        sk_create = sk.update({'note': note, 'state': 'draft'})


class RefuseSk(models.TransientModel):
    _name = "refuse.memo"
    _description = "Refuse Memorandum"

    note = fields.Text('Catatan')

    @api.multi
    def refuse(self):
        sk = self.env['surat.memorandum'].browse(self.env.context['active_id'])

        ##### mengirim email ke email tujuan ####

        #### Search Employee ####

        emp_obj = self.env['hr.employee']
        emp_src = emp_obj.sudo().search([('user_id', '=', sk.user_id.id)])

        #### search email company ####
        com_obj = self.env['res.company']
        com_src = com_obj.sudo().search([], limit=1)
        for comp in com_src:
            for send in emp_src:
                if send.work_email != False:
                    body_html = '<p>Kepada '+str(sk.user_id.name)+',</p> \n'+'<p> Memorandum yang anda buat dengan nomor '+str(sk.name)+' Dengan Perihal '+str(
                        sk.perihal)+' Mohon Untuk Segera Di tindak lanjuti karna ada beberapa catatan diantaranya '+str(self.note)
                    mail = self.env['mail.mail']
                    notif_mail = mail.sudo().create({'subject': 'Memorandum perihal '+str(sk.perihal),
                                                     'email_from': comp.email,
                                                     'email_to': send.work_email,
                                                     #'email_cc'     :
                                                     'auto_delete': True,
                                                     'type': 'notification',
                                                     #'recipient_ids' : [(6, 0, [gr.partner_id.id])],
                                                     'notification': True,
                                                     'body_html': body_html,
                                                     })
                    # _logger.info("created due date invoice alert to %s" % (gr.partner_id.email) )

        ##### Email Checker and Signer #####
        ck = 0
        count = 1
        if sk.state == 'checker1':
            ck = 1
        elif sk.state == 'checker2':
            ck = 2
        elif sk.state == 'checker3':
            ck = 3
        elif sk.state == 'checker4':
            ck = 4
        elif sk.state == 'checker5':
            ck = 5
        elif sk.state == 'signer':
            ck = 6
        while count < ck:
            #### Search Employee ####
            if count == 1 and sk.template.checker1 == True:
                emp_obj = self.env['hr.employee']
                emp_src = emp_obj.sudo().search(
                    [('user_id', '=', sk.template.user_id1.id)])

                #### search email company ####
                com_obj = self.env['res.company']
                com_src = com_obj.sudo().search([], limit=1)
                for comp in com_src:
                    for send in emp_src:
                        if emp_src != False:
                            body_html = '<p>Kepada '+str(send.user_id.name)+',</p> \n'+'<p> Memorandum yang di buat oleh '+str(sk.user_id.name)+' dengan nomor '+str(
                                sk.name)+' Dengan Perihal '+str(sk.perihal)+' Mohon Untuk Segera Di tindak lanjuti karna ada beberapa catatan diantaranya '+str(self.note)
                            mail = self.env['mail.mail']
                            notif_mail = mail.sudo().create({'subject': 'Memorandum perihal '+str(sk.perihal),
                                                             'email_from': comp.email,
                                                             'email_to': send.work_email,
                                                             #'email_cc'     :
                                                             'auto_delete': True,
                                                             'type': 'notification',
                                                             #'recipient_ids' : [(6, 0, [gr.partner_id.id])],
                                                             'notification': True,
                                                             'body_html': body_html,
                                                             })

            elif count == 2 and sk.template.checker2 == True:
                emp_obj = self.env['hr.employee']
                emp_src = emp_obj.sudo().search(
                    [('user_id', '=', sk.template.user_id2.id)])

                #### search email company ####
                com_obj = self.env['res.company']
                com_src = com_obj.sudo().search([], limit=1)
                for comp in com_src:
                    for send in emp_src:
                        if emp_src != False:
                            body_html = '<p>Kepada '+str(send.user_id.name)+',</p> \n'+'<p> Memorandum yang di buat oleh '+str(sk.user_id.name)+' dengan nomor '+str(
                                sk.name)+' Dengan Perihal '+str(sk.perihal)+' Mohon Untuk Segera Di tindak lanjuti karna ada beberapa catatan diantaranya '+str(self.note)
                            mail = self.env['mail.mail']
                            notif_mail = mail.sudo().create({'subject': 'Memorandum perihal '+str(sk.perihal),
                                                             'email_from': comp.email,
                                                             'email_to': send.work_email,
                                                             #'email_cc'     :
                                                             'auto_delete': True,
                                                             'type': 'notification',
                                                             #'recipient_ids' : [(6, 0, [gr.partner_id.id])],
                                                             'notification': True,
                                                             'body_html': body_html,
                                                             })

            elif count == 3 and sk.template.checker3 == True:
                emp_obj = self.env['hr.employee']
                emp_src = emp_obj.sudo().search(
                    [('user_id', '=', sk.template.user_id3.id)])

                #### search email company ####
                com_obj = self.env['res.company']
                com_src = com_obj.sudo().search([], limit=1)
                for comp in com_src:
                    for send in emp_src:
                        if emp_src != False:
                            body_html = '<p>Kepada '+str(send.user_id.name)+',</p> \n'+'<p> Memorandum yang di buat oleh '+str(sk.user_id.name)+' dengan nomor '+str(
                                sk.name)+' Dengan Perihal '+str(sk.perihal)+' Mohon Untuk Segera Di tindak lanjuti karna ada beberapa catatan diantaranya '+str(self.note)
                            mail = self.env['mail.mail']
                            notif_mail = mail.sudo().create({'subject': 'Memorandum '+str(sk.perihal),
                                                             'email_from': comp.email,
                                                             'email_to': send.work_email,
                                                             #'email_cc'     :
                                                             'auto_delete': True,
                                                             'type': 'notification',
                                                             #'recipient_ids' : [(6, 0, [gr.partner_id.id])],
                                                             'notification': True,
                                                             'body_html': body_html,
                                                             })

            elif count == 4 and sk.template.checker4 == True:
                emp_obj = self.env['hr.employee']
                emp_src = emp_obj.sudo().search(
                    [('user_id', '=', sk.template.user_id4.id)])

                #### search email company ####
                com_obj = self.env['res.company']
                com_src = com_obj.sudo().search([], limit=1)
                for comp in com_src:
                    for send in emp_src:
                        if emp_src != False:
                            body_html = '<p>Kepada '+str(send.user_id.name)+',</p> \n'+'<p> Memorandum yang di buat oleh '+str(sk.user_id.name)+' dengan nomor '+str(
                                sk.name)+' Dengan Perihal '+str(sk.perihal)+' Mohon Untuk Segera Di tindak lanjuti karna ada beberapa catatan diantaranya '+str(self.note)
                            mail = self.env['mail.mail']
                            notif_mail = mail.sudo().create({'subject': 'Memorandum perihal '+str(sk.perihal),
                                                             'email_from': comp.email,
                                                             'email_to': send.work_email,
                                                             #'email_cc'     :
                                                             'auto_delete': True,
                                                             'type': 'notification',
                                                             #'recipient_ids' : [(6, 0, [gr.partner_id.id])],
                                                             'notification': True,
                                                             'body_html': body_html,
                                                             })

            elif count == 5 and sk.template.checker5 == True:
                emp_obj = self.env['hr.employee']
                emp_src = emp_obj.sudo().search(
                    [('user_id', '=', sk.template.user_id5.id)])

                #### search email company ####
                com_obj = self.env['res.company']
                com_src = com_obj.sudo().search([], limit=1)
                for comp in com_src:
                    for send in emp_src:
                        if emp_src != False:
                            body_html = '<p>Kepada '+str(send.user_id.name)+',</p> \n'+'<p> Memorandum yang di buat oleh '+str(sk.user_id.name)+' dengan nomor '+str(
                                sk.name)+' Dengan Perihal '+str(sk.perihal)+' Mohon Untuk Segera Di tindak lanjuti karna ada beberapa catatan diantaranya '+str(self.note)
                            mail = self.env['mail.mail']
                            notif_mail = mail.sudo().create({'subject': 'Memorandum perihal '+str(sk.perihal),
                                                             'email_from': comp.email,
                                                             'email_to': send.work_email,
                                                             #'email_cc'     :
                                                             'auto_delete': True,
                                                             'type': 'notification',
                                                             #'recipient_ids' : [(6, 0, [gr.partner_id.id])],
                                                             'notification': True,
                                                             'body_html': body_html,
                                                             })

            elif count == 6 and sk.template.signer6 == True:
                emp_obj = self.env['hr.employee']
                emp_src = emp_obj.sudo().search(
                    [('user_id', '=', sk.template.user_id6.id)])

                #### search email company ####
                com_obj = self.env['res.company']
                com_src = com_obj.sudo().search([], limit=1)
                for comp in com_src:
                    for send in emp_src:
                        if emp_src != False:
                            body_html = '<p>Kepada '+str(send.user_id.name)+',</p> \n'+'<p> Memorandum yang di buat oleh '+str(sk.user_id.name)+' dengan nomor '+str(
                                sk.name)+' Dengan Perihal '+str(sk.perihal)+' Mohon Untuk Segera Di tindak lanjuti karna ada beberapa catatan diantaranya '+str(self.note)
                            mail = self.env['mail.mail']
                            notif_mail = mail.sudo().create({'subject': 'Memorandum perihal '+str(sk.perihal),
                                                             'email_from': comp.email,
                                                             'email_to': send.work_email,
                                                             #'email_cc'     :
                                                             'auto_delete': True,
                                                             'type': 'notification',
                                                             #'recipient_ids' : [(6, 0, [gr.partner_id.id])],
                                                             'notification': True,
                                                             'body_html': body_html,
                                                             })

            count = count + 1
        send = self.env['mail.mail'].sudo().process_email_queue()
        if sk.note :
            note = self.env.user.name+" "+str(datetime.now())+" "+"("+sk.state+")"+"<p>"+self.note+"</p>"+"<p><br></p>"+sk.note
        else :
            note = self.env.user.name+" "+str(datetime.now())+" "+"("+sk.state+")"+"<p>"+self.note+"</p>"
        sk_create = sk.update({'note': note, 'state': 'draft'})

from odoo import models, api, fields
from odoo.exceptions import UserError, AccessError, ValidationError

import time
from datetime import datetime, timedelta
from dateutil import relativedelta

from odoo.addons.muk_dms.models import dms_base

class EarlyWarningSystem(models.Model):
	_name = 'ews.dms'
	_description = 'Ews berfungsi untuk memberikan notif ketika ada file yang sudah mendekati expiration'

	name = fields.Char('Nama', required=True)
	warning = fields.Integer("Warning/Hari", required=True)

class File(dms_base.DMSModel):
    _inherit = 'muk_dms.file'

    active_ews = fields.Boolean('Active Ews')
    number_email = fields.Integer(string='number')
    project = fields.Boolean('Create Project')

    @api.multi
    def write(self,vals):
    	if 'expiration' in vals :
    		vals['active_ews'] = False
        nameold = False
        namenew = False
        expold = False
        expnew = False
        picold = False
        picnew = False
        ewsold = False
        ewsnew = False
        contentold = False
        contentnew = False
        directoryold = False
        directorynew = False
        if 'name' in vals :
            nameold = self.name
            namenew = vals['name']
        if 'expiration' in vals :
            expold = self.expiration
            expnew = vals['expiration']
        if 'pic' in vals :
            picold = self.pic.name
            picnew = vals['pic']
        if 'ews' in vals :
            eswold = self.ews.name
            ewsnew = vals['ews']
        if 'content' in vals :
            contentold = self.content
            contentnew = vals['content']
        if 'directory' in vals :
            directoryold = self.directory.name
            directorynew = vals['directory']
        writelog = self.env['audit.log'].sudo().create({'name':self.name,
                                                        'date':str(datetime.today()),
                                                        'method':'Write',
                                                        'user_id':self.env.user.id,
                                                        'name_old':nameold,
                                                        'name_new':namenew,
                                                        'exp_old':expold,
                                                        'exp_new':expnew,
                                                        'pic_old':picold,
                                                        'pic_new':picnew,
                                                        'ews_old':ewsold,
                                                        'ews_new':ewsnew,
                                                        'content_old':contentold,
                                                        'content_new':contentnew,
                                                        'directory_old':directoryold,
                                                        'directory_new':directorynew})
        #import pdb;pdb.set_trace()
    	return super(File, self).write(vals)

    @api.multi
    def early_warning_system(self):
    	date_now = datetime.today()
    	file_obj = self.env['muk_dms.file']
    	file_src = file_obj.search([('expiration','!=',False)])

    	com_obj = self.env['res.company']
    	com_src = com_obj.search([],limit=1)

    	for exp in file_src :
    		if exp.expiration <= str(date_now + relativedelta.relativedelta(days=exp.ews.warning))[:10] :
    			if exp.project == False :
    				project = self.env['project.project'].create({'name':'Perpanjang'+str(exp.name),
    															'user_id':exp.pic.user_id.id})
    			num = exp.number_email + 1
    			exp.write({'active_ews':True,'number_email':num,'project':True})
    			if num <= 3 :
    				for comp in com_src :
    					body_html 	= '<p>Kepada '+str(exp.pic.name)+',</p> \n'+'<p> Segera Perpanjang '+str(exp.name)+', Karna expiration akan habis pada tanggal'+str(exp.expiration)
    					mail		= self.env['mail.mail']
    					notif_mail	= mail.create({'subject'	:'EWS Perpanjang Surat',
    												'email_from' : comp.email,
    												'email_to'   : exp.pic.work_email,
    												'auto_delete': True,
    												'type'       : 'notification',
    												'notification': True,
    												'body_html'  : body_html,	
    												})
    				send = self.env['mail.mail'].process_email_queue()	



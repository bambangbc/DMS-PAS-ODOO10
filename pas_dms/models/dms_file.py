import os
import re
import json
import base64
import logging
import mimetypes

from odoo import _
from odoo import models, api, fields
from odoo.tools import ustr
from odoo.tools.mimetypes import guess_mimetype
from odoo.exceptions import ValidationError, AccessError

from odoo.addons.muk_dms.models import dms_base


class File(dms_base.DMSModel):
    _inherit = 'muk_dms.file'
    
    #----------------------------------------------------------
    # Database
    #----------------------------------------------------------
    
    expiration = fields.Date(string="Expiration")
    pic = fields.Many2one('hr.employee','PIC')
    ews = fields.Many2one('ews.dms','Template Ews')
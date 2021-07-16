# -*- coding: utf-8 -*-
{
    'name': "dms-V10",
    'summary': "Document Management System",
    'description': """
    """,
    'author': "Bambang Bagus Candra(bambangbaguscandra@gmail.com),Nendi Apandi(nendi_apandi@yahoo.com) ",
    'website': "",
    'support': '',
    'category': 'DMS',
    'version': '1.0',
    'depends': ['document','muk_dms','muk_dms_access','muk_dms_file',  'mail','hr','project'],
    'data': [
        'views/dms_file_view.xml',
        'views/ews_view.xml',
        'data/data.xml',
        'security/ir.model.access.csv',
        'views/auditlog_view.xml'
    ],
    'installable': True,
    'auto_install': False,
    'application': True,
}
# -*- encoding: utf-8 -*-
##############################################################################
#                                                                            #
#   --- Deby Wahyu Kurdian ---                                               #
#                                                                            #
##############################################################################

{
    'name': 'Pelita Reporting [Custom Module]',
    'version':'1.0',
    'category': 'Reporting',
    'description': """
        Reporting Module for Pelita Air (with JasperReports)
    """,
    'author': 'Deby Wahyu Kurdian | 085655647406 | deby.wahyu.kurdian@gmail.com',
    'website': '',
    'depends':[
        'base',
        'sale',
        'jasper_reports',
        'maintenance',
        'pelita_equipment',
        'pelita_master_data',
        'pelita_sale',
        'ib_base_pelita',
        'ib_pelita_report',
    ],
    'data':[
        'wizard/wizard_report_flight_time_fw_rw_view.xml',
        'wizard/wizard_report_flight_time_fw_rw_view_02.xml',
        'views/report_moy.xml',
    ],
    'installable': True,
    'auto_install': False,
}

# -- coding: utf-8 --
# This module and its content is copyright of Technaureus Info Solutions Pvt. Ltd.
# - © Technaureus Info Solutions Pvt. Ltd 2021. All rights reserved.


{
    'name': 'Odoo Quotation and Order Enhancement',
    'version': '14.0.0.6',
    'category': 'sale',
    'sequence': 1,
    'author': 'Technaureus Info Solutions Pvt. Ltd.',
    'summary': 'Unit Discount and Delivery Date in Sale order report',
    'description': """Unit Discount and Delivery Date in Sale order report
    """,
    'website': 'http://www.technaureus.com',
    'depends': ['sale'],
    'demo': [],
    'data': ['views/sale_report_unit_discount.xml'],
    'installable': True,
    'application': True,
    'auto_install': False
}

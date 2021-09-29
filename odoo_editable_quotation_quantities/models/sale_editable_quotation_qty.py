# -*- coding: utf-8 -*-
# This module and its content is copyright of Technaureus Info Solutions Pvt. Ltd.
# - © Technaureus Info Solutions Pvt. Ltd 2021. All rights reserved.

from odoo import api, fields, models
from ast import literal_eval


class SaleOtherInfo(models.Model):
    _inherit = "sale.order"

    quotation_quantity = fields.Boolean(string="Editable Quotation Quantities", default=False)

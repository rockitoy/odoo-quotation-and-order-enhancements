# -*- coding: utf-8 -*-
# This module and its content is copyright of Technaureus Info Solutions Pvt. Ltd.
# - © Technaureus Info Solutions Pvt. Ltd 2021. All rights reserved.

from odoo import api, fields, models, _


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    @api.onchange('product_uom', 'product_uom_qty')
    def product_uom_change(self):
        normal_uom = self.product_id.uom_id
        normal_unit_price = self.price_unit
        if not self.product_uom or not self.product_id:
            self.price_unit = 0.0
            return
        if self.order_id.pricelist_id and self.order_id.partner_id:
            product = self.product_id.with_context(
                lang=self.order_id.partner_id.lang,
                partner=self.order_id.partner_id,
                quantity=self.product_uom_qty,
                date=self.order_id.date_order,
                pricelist=self.order_id.pricelist_id.id,
                uom=self.product_uom.id,
                fiscal_position=self.env.context.get('fiscal_position')
            )
            # uom_factor = self.product_uom._compute_price(self.price_unit, self.product_uom)
            # uom_factor = self.product_uom._compute_price(normal_unit_price, normal_uom)
            account_tax =self.env['account.tax']._fix_tax_included_price_company(
                    self._get_display_price(product), product.taxes_id, self.tax_id, self.company_id)
            if normal_unit_price == account_tax:
                return super(SaleOrderLine, self).product_uom_change()
            else:
                self.price_unit = self.env['account.tax']._fix_tax_included_price_company(self.price_unit,
                                                                                          product.taxes_id, self.tax_id,
                                                                                          self.company_id)

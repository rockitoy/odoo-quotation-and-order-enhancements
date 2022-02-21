# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
from odoo import api, fields, models, _
from odoo.exceptions import UserError


class SaleOrderOption(models.Model):
    _inherit = "sale.order.option"

    customer_lead = fields.Float(
        'Lead Time', required=True, default=0.0,
        help="Number of days between the order confirmation and the shipping of the products to the customer")
    margin = fields.Monetary("Margin", compute="_compute_margin", store=True)
    margin_percent = fields.Float("Margin (%)", compute="_compute_margin", store=True)
    purchase_price = fields.Float(
        string='Cost', compute="_compute_purchase_price",
        digits='Product Price', store=True, readonly=False,
        groups="base.group_user")
    currency_id = fields.Many2one(related='order_id.currency_id', depends=['order_id.currency_id'], store=True,
                                  string='Currency', readonly=True)
    company_id = fields.Many2one(related='order_id.company_id', string='Company', store=True, readonly=True, index=True)
    price_total = fields.Float('Total', compute='_compute_amount', compute_sudo=True, digits=0)
    price_subtotal = fields.Monetary(compute='_compute_amount', string='Subtotal', readonly=True, store=True)
    tax_id = fields.Many2many('account.tax', string='Taxes')
    product_id = fields.Many2one('product.product', 'Product', required=False, domain=[('sale_ok', '=', True)])
    uom_id = fields.Many2one('uom.uom', 'Unit of Measure ',  required=False, domain="[('category_id', '=', product_uom_category_id)]")
    display_type = fields.Selection([
        ('line_section', "Section"),
        ('line_note', "Note")], default=False, help="Technical field for UX purpose.")

    _sql_constraints = [
        ('optional_vals_unique',
         "CHECK(display_type IS NOT NULL OR (product_id IS NOT NULL AND uom_id IS NOT NULL))",
         "Missing required product and UoM on accountable sale quote line."),

        ('optional_vals_unique_null',
         "CHECK(display_type IS NULL OR (product_id IS NULL AND quantity = 0 AND uom_id IS NULL))",
         "Forbidden product, unit price, quantity, and UoM on non-accountable sale quote line"),
    ]

    @api.onchange('product_id', 'uom_id', 'quantity')
    def _onchange_product_id(self):
        if not self.product_id:
            if self.display_type == 'line_section' or self.display_type == 'line_note':
                print("ok")
            else:
                return
        product = self.product_id.with_context(
            lang=self.order_id.partner_id.lang,
            partner=self.order_id.partner_id,
            quantity=self.quantity,
            date=self.order_id.date_order,
            pricelist=self.order_id.pricelist_id.id,
            uom=self.uom_id.id,
            fiscal_position=self.env.context.get('fiscal_position')
        )
        self.name = product.get_product_multiline_description_sale()
        self.uom_id = self.uom_id or product.uom_id
        # To compute the discount a so line is created in cache
        values = self._get_values_to_add_to_order()
        new_sol = self.env['sale.order.line'].new(values)
        new_sol._onchange_discount()
        self.discount = new_sol.discount
        if self.order_id.pricelist_id and self.order_id.partner_id:
            self.price_unit = new_sol._get_display_price(product)

    @api.depends('product_id', 'company_id', 'currency_id', 'uom_id')
    def _compute_purchase_price(self):
        for line in self:
            if not line.product_id:
                line.purchase_price = 0.0
                continue
            line = line.with_company(line.company_id)
            product = line.product_id
            product_cost = product.standard_price
            if not product_cost:
                # If the standard_price is 0
                # Avoid unnecessary computations
                # and currency conversions
                if not line.purchase_price:
                    line.purchase_price = 0.0
                continue
            fro_cur = product.cost_currency_id
            to_cur = line.currency_id or line.order_id.currency_id
            if line.uom_id and line.uom_id != product.uom_id:
                product_cost = product.uom_id._compute_price(
                    product_cost,
                    line.product_uom,
                )
            line.purchase_price = fro_cur._convert(
                from_amount=product_cost,
                to_currency=to_cur,
                company=line.company_id or self.env.company,
                date=line.order_id.date_order or fields.Date.today(),
                round=False,
            ) if to_cur and product_cost else product_cost
            # The pricelist may not have been set, therefore no conversion
            # is needed because we don't know the target currency..

    @api.depends('quantity', 'discount', 'price_unit', 'tax_id')
    def _compute_amount(self):
        """
        Compute the amounts of the SO line.
        """
        for line in self:
            price = line.price_unit * (1 - (line.discount or 0.0) / 100.0)
            taxes = line.tax_id.compute_all(price, line.order_id.currency_id, line.quantity,
                                            product=line.product_id, partner=line.order_id.partner_shipping_id)
            line.update({
                # 'price_tax': sum(t.get('amount', 0.0) for t in taxes.get('taxes', [])),
                'price_total': round(taxes['total_included'], 2),
                'price_subtotal': round(taxes['total_excluded']),
            })
            if self.env.context.get('import_file', False) and not self.env.user.user_has_groups(
                    'account.group_account_manager'):
                line.tax_id.invalidate_cache(['invoice_repartition_line_ids'], [line.tax_id.id])

    @api.depends('price_subtotal', 'quantity', 'purchase_price')
    def _compute_margin(self):
        for line in self:
            line.margin = line.price_subtotal - (line.purchase_price * line.quantity)
            line.margin_percent = line.price_subtotal and line.margin / line.price_subtotal

    @api.model
    def create(self, values):
        if values.get('display_type', self.default_get(['display_type'])['display_type']):
            values.update(name=values.get('name'), product_id=False, price_unit=0, uom_id=False, quantity=0, order_id=values.get('order_id'))
        return super(SaleOrderOption, self).create(values)

    def write(self, values):
        if 'display_type' in values and self.filtered(lambda line: line.display_type != values.get('display_type')):
            raise UserError(
                _("You cannot change the type of a sale quote line. Instead you should delete the current line and create a new line of the proper type."))
        return super(SaleOrderOption, self).write(values)





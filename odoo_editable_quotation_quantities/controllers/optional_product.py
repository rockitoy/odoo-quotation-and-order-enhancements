# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
import base64
import datetime
import json
import os
import logging
import pytz
import requests
import werkzeug.urls
import werkzeug.utils
import werkzeug.wrappers

from itertools import islice
from werkzeug import urls
from xml.etree import ElementTree as ET

import odoo

from odoo import http, models, fields, _
from odoo.http import request
from odoo.tools import OrderedSet
from odoo.addons.http_routing.models.ir_http import slug, slugify, _guess_mimetype
from odoo.addons.web.controllers.main import Binary
from odoo.addons.portal.controllers.portal import pager as portal_pager
from odoo.addons.portal.controllers.web import Home

logger = logging.getLogger(__name__)

class Website(Home):

    @http.route('/get_all_options', type='http', auth="public", website=True, sitemap=True)
    def get_all_options(self, **kw):
        option_list = []
        options = request.env['sale.order.option'].sudo().search([])
        if options:
            for option in options:
                data = {
                    "id": option.id,
                    "name": option.name
                }
                option_list.append(data)
            return json.dumps(option_list)

    @http.route('/update_option_qty', type='http', auth="public", website=True, sitemap=True)
    def update_option_qty(self, **kw):
        qty = kw.get('qty')
        option = request.env['sale.order.option'].sudo().browse(int(kw.get('op_id')))
        if int(qty) <= 0 and option:
            option.unlink()
            return "fail"
        elif option and qty > 0:
            option.update({
                "quantity": int(qty)
            })
            return str(option.price_subtotal)


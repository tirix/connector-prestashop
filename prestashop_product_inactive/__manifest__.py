# -*- coding: utf-8 -*-
# Copyright 2019 Akretion
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "PrestaShop Product Inactive",
    "version": "12.0.1.0.0",
    "license": "AGPL-3",
    "depends": [
        "connector_prestashop",
    ],
    "author": "Akretion,"
              "Odoo Community Association (OCA)",

    "website": "https://github.com/OCA/connector-prestashop",
    "category": "Connector",
    'demo': [
    ],
    'data': [
        'data/cron.xml',
    ],
    'installable': True,
    "application": False,
}

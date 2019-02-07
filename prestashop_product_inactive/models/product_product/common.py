# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models


class PrestashopProductCombination(models.Model):
    _name = 'prestashop.product.combination'
    _inherit = [
        'prestashop.product.combination',
        'prestashop.inactive.product.mixin',
    ]

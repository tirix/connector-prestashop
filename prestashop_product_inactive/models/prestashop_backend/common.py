# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, models


class PrestashopBackend(models.Model):
    _inherit = 'prestashop.backend'

    @api.model
    def _scheduler_inactive_deleted_products(self, domain=None):
        self.search(domain or []).inactive_deleted_products()

    def inactive_deleted_products(self):
        for backend in self:
            combinations = self.env['prestashop.product.combination'].search(
                [('active', '=', True), ('backend_id', '=', backend.id)],
                order='prestashop_id asc')
            limit_low = 0
            limit_top = 1500
            while combinations[limit_low:limit_top]:
                combinations[limit_low:limit_top].with_delay().\
                    inactive_records(backend)
                limit_low += 1500
                limit_top += 1500

            products = self.env['prestashop.product.template'].search(
                [('active', '=', True), ('backend_id', '=', backend.id)],
                order='prestashop_id asc')
            limit_low = 0
            limit_top = 1500
            while products[limit_low:limit_top]:
                products[limit_low:limit_top].with_delay().\
                    inactive_records(backend)
                limit_low += 1500
                limit_top += 1500

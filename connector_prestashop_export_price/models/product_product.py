# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.addons.component.core import Component
from odoo.addons.connector.components.mapper import only_create
from odoo.addons.queue_job.job import job
from odoo import models


class PrestashopProductCombination(models.Model):
    _inherit = 'prestashop.product.combination'

    def _get_price(self, pricelist):
        self.ensure_one()
        if not pricelist:
            return False
        template_price = pricelist.get_product_price(
            self.main_template_id.odoo_id, 1, False)
        combination_full_price = pricelist.get_product_price(
            self.odoo_id, 1, False)
        combination_extra = combination_full_price - template_price
        return combination_extra


class ProductCombinationMapper(Component):
    _inherit = 'prestashop.product.combination.mapper'

    @only_create
    def specific_price(self, record):
        return super().specific_price(record)

class PriceExporter(Component):
    _name = 'prestashop.product.price.exporter'
    _inherit = 'prestashop.template.price.exporter'
    _apply_on = [
        'prestashop.product.combination'
    ]
    _usage = 'price.exporter'

    def get_datas(self, binding):
        datas = {}
        pricelist_id = binding.backend_id.pricelist_id.id
        combination_price = self._get_price(pricelist_id)
        datas['pricecombinationwithouttax'] = combination_price
        datas['id_combination'] = binding.prestashop_id
        datas['key'] = binding.backend_id.webservice_key
        return datas


class PrestashopProductProductListener(Component):
    _name = 'prestashop.product.product.listener'
    _inherit = 'base.event.listener'
    _apply_on = ['product.product']

    def on_product_price_changed(self, product):
        if not product.sale_ok:
            return
        if not self.env.context.get('current_backend_only'):
            product = product.sudo()
        for binding in product.prestashop_combinations_bind_ids:
            binding.with_context(force_company=binding.company_id.id).with_delay().export_product_price()

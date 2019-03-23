# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).#############

from odoo.addons.component.core import Component
from odoo.addons.connector.components.mapper import only_create
from odoo.addons.queue_job.job import job
from odoo import models
import requests


class PrestashopProductTemplate(models.Model):
    _inherit = 'prestashop.product.template'

    def _get_price(self, pricelist):
        self.ensure_one()
        if not pricelist:
            return False
        price = pricelist.get_product_price(self.odoo_id, 1, False)
        print(price)
        return price


class ProductQtyMixin(models.AbstractModel):
    _inherit = 'prestashop.product.qty.mixin'

    @job(default_channel='root.prestashop_export')
    def export_product_price(self):
        """ Export the price of a product. """
        self.ensure_one()
        backend = self.backend_id
        with backend.work_on(self._name) as work:
            exporter = work.component(usage='price.exporter')
            return exporter.run(self)


class TemplateMapper(Component):
    _inherit = 'prestashop.product.template.mapper'

    @only_create
    def list_price(self, record):
        return super().list_price(record)


class PriceExporter(Component):
    _name = 'prestashop.template.price.exporter'
    _inherit = 'prestashop.exporter'
    _apply_on = [
        'prestashop.product.template'
    ]
    _usage = 'price.exporter'

    def get_datas(self, binding):
        datas = {}
        pricelist = binding.backend_id.pricelist_id
        new_price = binding._get_price(pricelist)
        datas['pricewithouttax'] = new_price
        datas['id_product'] = binding.prestashop_id
        datas['key'] = binding.backend_id.webservice_key
        return datas

    def update_price(self, url, datas):
        req = requests.post(url, data=datas)
        return req.text

    def run(self, record):
        datas = self.get_datas(record)
        url = record.backend_id.location + '/updateprice.php'
        res = self.update_price(url, datas)

class PrestashopProductTemplateListener(Component):
    _name = 'prestashop.product.template.listener'
    _inherit = 'base.event.listener'
    _apply_on = ['product.template']

    def on_product_price_changed(self, template):
        if not template.sale_ok:
            return
        if not self.env.context.get('current_backend_only'):
            template = template.sudo()
        for binding in template.prestashop_bind_ids:
            binding.with_context(force_company=binding.company_id.id).with_delay().export_product_price()

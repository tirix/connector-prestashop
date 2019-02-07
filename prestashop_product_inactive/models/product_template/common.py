# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, models
from odoo.addons.queue_job.job import job


class InactiveProductMixin(models.AbstractModel):
    _name = 'prestashop.inactive.product.mixin'

    @job(default_channel='root.prestashop')
    @api.multi
    def inactive_records(self, backend):
        prestashop_ids = self.mapped('prestashop_id')
        with backend.work_on(self._name) as work:
            adapter = work.component(usage='backend.adapter')
            filters = {
                'filter[id]': [min(prestashop_ids), max(prestashop_ids)],
            }
            existing_prestashop_ids = adapter.search(filters)
            to_unactive = list(
                set(prestashop_ids) - set(existing_prestashop_ids)
            )
            bindings = self.search(
                [('prestashop_id', 'in', to_unactive),
                 ('backend_id', '=', backend.id)])
            odoo_records = bindings.mapped('odoo_id')
            odoo_records.write({'active': False})
            bindings.write({'active': False})


class PrestashopProductTemplate(models.Model):
    _name = 'prestashop.product.template'
    _inherit = [
        'prestashop.product.template',
        'prestashop.inactive.product.mixin',
    ]

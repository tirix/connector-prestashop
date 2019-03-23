# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, models, _


class PrestashopBackend(models.Model):
    _inherit = 'prestashop.backend'

    @api.onchange('pricelist_id')
    def onchange_pricelist_id(self):
        warning = {
            'title': _('Warning'),
            'message': _('If you change the pricelist of the backend, '
                         'the price of all the products will be updated '
                         'in Prestashop.')
        }
        return {'warning': warning}

    def update_all_prices(self):
        """ Update the prices of all the products linked to the
        backend. """
        for backend in self:
            session = ConnectorSession(cr, uid, context=context)
            template_bindings = self.search(
                'prestashop.product.template',
                [('backend_id', '=', backend.id), ('sale_ok', '=', True)])
            combination_bindings = self.search(
                'prestashop.product.combination',
                [('backend_id', '=', backend.id)])
            for product_bind in template_bindings:
                product_bind.with_delay().export_product_price()
            for combination_bind in combination_bindings:
                combination_bind.with_delay().export_product_price()

    def write(self, vals):
        if 'pricelist_id' in vals:
            self.update_all_prices()
        return super().write(vals)


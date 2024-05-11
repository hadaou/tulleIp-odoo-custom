from odoo import fields, models, api
from odoo.osv import expression
import logging

_logger = logging.getLogger(__name__)


class ProductProduct(models.Model):
    _inherit = 'product.product'

    internal_code = fields.Char(
        related='product_tmpl_id.internal_code',
        string="Internal Code",
        readonly=True,  # Typically, related fields are readonly.
        store=True,  # Important as it allows searches on this field.
        # Optional but recommended for optimizing searches on this field.
        index=True,
    )
    x_barcode_length = fields.Integer(compute='_compute_barcode_length',string="Barcode Length", store=True)


    @api.depends('barcode')  # Correct dependency
    def _compute_barcode_length(self):
        for record in self:
            if record.barcode and isinstance(record.barcode, str):
                record.x_barcode_length = len(record.barcode)
            else:
                record.x_barcode_length = 0

    @api.model
    def _name_search(self, name, args=None, operator='ilike', limit=100, name_get_uid=None, order=None):
        if args is None:
            args = []
        domain = []
        _logger.info('Searching for product with name:', name)
        # Search for a product with an exact match on 'internal_code'.
        if name:
            domain = ['|', '|', '|', ('name', operator, name), ('default_code', operator, name),
                      ('barcode', operator, name), ('internal_code', operator, name)]
        product_ids = self._search(expression.AND([domain, args]),
                                   limit=limit, access_rights_uid=name_get_uid,order=order)
        return product_ids

    @api.model_create_multi
    def create(self, vals_list):
        records = super(ProductProduct, self).create(vals_list)
        for record in records:
            if record.internal_code:
                record.barcode = record.internal_code + str(record.id)
        return records

    @api.onchange('categ_id')
    def _onchange_categ_id_product(self):
        self.product_tmpl_id.onchange_categ_id()
from odoo import api, models, fields, _
from odoo.exceptions import ValidationError


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    # This field gets the image from the related product category
    category_image = fields.Binary(
        related='categ_id.cat_image_thumb', readonly=True, string="Category Image", store=True)

    p_image_thumb = fields.Image(
        "Image thumb", related="image_1920", max_width=None, max_height=64, store=True)

    internal_code = fields.Char(
        string="Internal Code",
        index=True
    )

    @api.model_create_multi
    def create(self, vals_list):
        records = super(ProductTemplate, self).create(vals_list)
        for record in records:
            if record.internal_code:
                record.barcode = record.internal_code + str(record.id)
        return records

    def write(self, vals):
        if 'internal_code' in vals:
            for record in self:
                record.barcode = vals['internal_code']
        return super(ProductTemplate, self).write(vals)

    @api.constrains('internal_code')
    def _check_internal_code_uniqueness(self):
        for template in self:
            if template.internal_code and self.search_count([('internal_code', '=', template.internal_code), ('id', '!=', template.id)]) > 0:
                raise ValidationError(_("The internal code must be unique."))

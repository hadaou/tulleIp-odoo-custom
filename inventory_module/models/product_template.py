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
        result = super(ProductTemplate, self).write(vals)
        if 'internal_code' in vals:
            for record in self:
                record.barcode = vals['internal_code']
        if 'categ_id' in vals:
            self._update_categories_based_on_categ_id()
        return result


    @api.constrains('internal_code')
    def _check_internal_code_uniqueness(self):
        for template in self:
            if template.internal_code and self.search_count([('internal_code', '=', template.internal_code), ('id', '!=', template.id)]) > 0:
                raise ValidationError(_("The internal code must be unique."))

    """
    when product's category is changed then update 
    the pos_categ_ids and public_categ_ids on the product.template based on the corresponding 
    pos_categ_ids and pulbic_categ_ids from the product.category
    """
    def _update_categories_based_on_categ_id(self):
        """Updates both public and POS categories based on the current 'categ_id'."""
        for record in self:
            record._update_public_categories()
            record._update_pos_categories()

    def _update_public_categories(self):
        """Update public categories based on the selected product category."""
        self.public_categ_ids = [(6, 0, self.categ_id.public_categ_ids.ids)]

    def _update_pos_categories(self):
        """Update POS categories based on the selected product category, or create them based on public categories."""
        pos_category_ids = self.categ_id.pos_categ_ids.ids or []
        if not pos_category_ids:
            pos_category_ids = self._create_pos_categories_based_on_public_cats()
        self.pos_categ_ids = [(6, 0, pos_category_ids)]

    def _create_pos_categories_based_on_public_cats(self):
        """Create POS categories based on public category names if they do not exist."""
        pos_category_ids = []
        for public_cat in self.public_categ_ids:
            pos_category = self.env['pos.category'].search([('name', '=', public_cat.name)], limit=1)
            if not pos_category:
                pos_category = self.env['pos.category'].create({'name': public_cat.name})
            pos_category_ids.append(pos_category.id)
        return pos_category_ids

    @api.onchange('categ_id')
    def onchange_categ_id(self):
        """Handles changes to the product category triggered by UI actions."""
        self._update_categories_based_on_categ_id()

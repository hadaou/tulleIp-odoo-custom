from odoo import api, models, fields, _
from odoo.exceptions import UserError
from io import BytesIO
import requests
import base64
import logging

_logger = logging.getLogger(__name__)


class ProductCategory(models.Model):
    _inherit = 'product.category'

    # New field for storing the image itself
    cat_image = fields.Binary(
        string='Image', compute='_compute_cat_image', store=True, inverse='_set_cat_image')

    # New field for storing the URL of the image
    cat_image_url = fields.Char("Image URL")

    cat_image_thumb = fields.Image(
        "Image thumb", related="cat_image", max_width=None, max_height=64, store=True)

    child_count = fields.Integer(
        'Child Count', compute='_compute_child_count', search='child_count', store=True)

    category_group_id = fields.Many2one(
        'product.category.group',
        string='Category Group', help='Group under which this category falls.', store=True
    )

    product_tag_ids = fields.Many2many(
        'product.tag', string='Product Tags', store=True)

    attribute_line_ids = fields.One2many(
        'product.category.attribute.line', 'category_id', 'Product cat Attributes', store=True)

    public_categ_ids = fields.Many2many(
        'product.public.category', string='Public Categories', store=True)

    def action_add_product(self):
        self.ensure_one()

        # Create a new wizard
        wizard = self.env['inventory.add_product_wizard'].create({
            'category_id': self.id,
            'attribute_line_ids': [(0, 0, {
                'attribute_id': line.attribute_id.id,
                'value_ids': [(6, 0, line.value_ids.ids)]
            }) for line in self.attribute_line_ids],
            'product_tag_ids': [(6, 0, self.product_tag_ids.ids)],
            'public_categ_ids': [(6, 0, self.public_categ_ids.ids)]
        })

        # Return an action to open the wizard in form view
        return {
            'name': f'Adding new Product to {self.name}',
            'type': 'ir.actions.act_window',
            'res_model': 'inventory.add_product_wizard',
            'res_id': wizard.id,
            'view_mode': 'form',
            'target': 'new',
        }

    @api.depends('cat_image_url')
    def _compute_cat_image(self):
        for record in self:
            if record.cat_image_url:
                try:
                    if record.cat_image_url.startswith('http://') or record.cat_image_url.startswith('https://'):
                        # Fetch image from URL
                        response = requests.get(
                            record.cat_image_url, timeout=15)
                        response.raise_for_status()
                        image_content = BytesIO(response.content).read()
                    else:
                        # Load image from local file
                        with open(record.cat_image_url, 'rb') as image_file:
                            image_content = image_file.read()

                    # Convert the image content to base64 format and store it
                    record.cat_image = base64.b64encode(image_content)
                except Exception as e:
                    _logger.error("Error fetching image: %s", e)
                    raise UserError(
                        _("There was an error fetching the image. Please ensure the URL or file path is correct and accessible."))

    def _set_cat_image(self):
        for record in self:
            # This might look redundant, but it ensures the value is written to the database.
            record.cat_image = record.cat_image

    @api.depends('child_id')
    def _compute_child_count(self):
        for rec in self:
            rec.child_count = len(rec.child_id)

    @api.model_create_multi
    def create(self, vals_list):
        records = super().create(vals_list)
        for record in records:
            record._update_public_category_image()
        return records

    def write(self, vals):
        result = super().write(vals)
        for record in self:
            record._update_public_category_image()
        return result

    def _update_public_category_image(self):
        for public_category in self.public_categ_ids:
            public_category.image_1920 = self.cat_image


class ProductCategoryAttributeLine(models.TransientModel):
    _name = 'product.category.attribute.line'
    _description = 'Product Category Attribute Line'

    category_id = fields.Many2one(
        'product.category', ondelete='cascade')

    attribute_id = fields.Many2one('product.attribute', required=True)

    value_ids = fields.Many2many('product.attribute.value',
                                 'product_cat_attr_line_product_attr_value_rel',
                                 'product_category_attribute_line_id',
                                 'attribute_value_id',
                                 string='Attribute Values', domain="[('attribute_id', '=', attribute_id)]")
    value_count = fields.Integer(compute='_compute_value_count')

    @api.depends('value_ids')
    def _compute_value_count(self):
        for record in self:
            record.value_count = len(record.value_ids)

    @api.onchange('attribute_id')
    def _onchange_attribute_id(self):
        return {'domain': {'value_ids': [('attribute_id', '=', self.attribute_id.id)]}}

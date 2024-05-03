from odoo import api, fields, models
import logging
_logger = logging.getLogger(__name__)


class AddProductWizard(models.TransientModel):
    _name = 'inventory.add_product_wizard'
    _description = 'Wizard to Add New Product with a Default Code'

    # Define the fields that will appear on the wizard
    vendor_id = fields.Many2one('res.partner', string='Vendor')

    product_code = fields.Char(string='Product Code',
                               help="Enter the unique code for the new product.")
    company_id = fields.Many2one(
        'res.company', 'Company',
        default=lambda self: self.env.company.id, index=1)
    currency_id = fields.Many2one(
        'res.currency', 'Currency',
        default=lambda self: self.env.company.currency_id.id,
        required=True)
    product_name = fields.Char(string='Product Name')

    product_price = fields.Float(string='Product Price')

    rent_ok = fields.Boolean(string='Can be Rented')

    product_daily_rental_price = fields.Float(string='Rental Price')

    p_image = fields.Binary(
        string='Image', store=True)

    p_image_thumb = fields.Image(
        "Image thumb", related="p_image", max_width=None, max_height=64, store=True)

    category_id = fields.Many2one(
        'product.category', string='Product Category')

    product_tag_ids = fields.Many2many(
        'product.tag', string='Product Tags')

    attribute_line_ids = fields.One2many(
        'inventory.add_product_wizard.attribute.line', 'wizard_id', 'Product Attributes', copy=True)

    public_categ_ids = fields.Many2many(
        'product.public.category', string='Public Categories')

    pos_categ_ids = fields.Many2many(
        'pos.category', string='POS Category',
        help="Category used in the Point of Sale.")

    def action_add_product(self):
        """Method to create a new product and open the form view."""
        self._create_product()
        # Close the wizard
        return {}

    def action_add_product_then_add_details(self):
        """Method to create a new product and open the form view."""
        product = self._create_product()

        # Return an action to open the newly created product in form view
        return {
            'name': 'New Product',
            'type': 'ir.actions.act_window',
            'res_model': 'product.template',
            'view_mode': 'form',
            'view_id': False,
            'res_id': product.id,
            'target': 'current'
        }

    def _create_product(self):
        """Method to create a new product with the supplied product code."""
        self.ensure_one()

        if self.vendor_id:
            vendor_id_str = str(self.vendor_id.id).zfill(4)
            internal_code = self.product_code + vendor_id_str
        else:
            internal_code = self.product_code

        # Initialize an empty list to collect POS category IDs
        pos_category_ids = []

        # Iterate over each selected public category
        for public_cat in self.public_categ_ids:
            # Search for an existing POS category with the same name
            pos_category = self.env['pos.category'].search([('name', '=', public_cat.name)], limit=1)

            # If the POS category does not exist, create a new one
            if not pos_category:
                pos_category = self.env['pos.category'].create({'name': public_cat.name})

            # Append the POS category ID to the list
            pos_category_ids.append(pos_category.id)

        # Use the (6, 0, pos_category_ids) command to set the pos_categ_ids field
        pos_categ_ids = [(6, 0, pos_category_ids)]

        # Create a new product using the provided code
        product_vals = {
            'name': self.product_name,
            'internal_code': internal_code,
            # Set the product's category to the passed category ID
            'categ_id': self.category_id.id,
            'product_tag_ids': [(6, 0, self.product_tag_ids.ids)],
            'public_categ_ids': [(6, 0, self.public_categ_ids.ids)],
            'image_1920': self.p_image,
            'available_in_pos': True,
            'list_price': self.product_price,
            'pos_categ_ids': pos_categ_ids,
            'rent_ok': self.rent_ok,
            'detailed_type': 'product'
        }
        product = self.env['product.template'].create(product_vals)

        # Create attribute lines for the product
        for line in self.attribute_line_ids:
            self.env['product.template.attribute.line'].create({
                'product_tmpl_id': product.id,
                'attribute_id': line.attribute_id.id,
                'value_ids': [(6, 0, line.value_ids.ids)],
            })

        if self.vendor_id:
            # Create a new supplierinfo record for the product
            supplierinfo_vals = {
                'product_tmpl_id': product.id,
                'partner_id': self.vendor_id.id,
                'product_code': self.product_code,
            }
            self.env['product.supplierinfo'].create(supplierinfo_vals)

        if self.rent_ok and self.product_daily_rental_price > 0.0:
            pricing_period_any = self.env['sale.temporal.recurrence'].search([('name', 'ilike', 'any')])
            if pricing_period_any:
                pricing_period_any_id = pricing_period_any.id
            else:
                pricing_period_any_id = 1

            # Crate a new daily pricing record in product_pricing table.
            self.env['product.pricing'].create({
                'product_template_id': product.id,
                'recurrence_id': pricing_period_any_id,
                'price': self.product_daily_rental_price,
            })

        # Return an action to open the newly created product in form view
        return product


class AddProductWizardAttributeLine(models.TransientModel):
    _name = 'inventory.add_product_wizard.attribute.line'
    _description = 'Inventory Add Product Wizard Attribute Line'
    _order = 'sequence, attribute_id, id'
    sequence = fields.Integer("Sequence", default=10)
    wizard_id = fields.Many2one(
        'inventory.add_product_wizard', ondelete='cascade')
    attribute_id = fields.Many2one('product.attribute', required=True)
    value_ids = fields.Many2many('product.attribute.value',
                                 'inv_add_product_wizard_attr_line_product_attr_value_rel',
                                 'wizard_attribute_line_id', 'attribute_value_id',
                                 string='Attribute Values',
                                 domain="[('attribute_id', '=', attribute_id)]")
    value_count = fields.Integer(compute='_compute_value_count')

    @api.depends('value_ids')
    def _compute_value_count(self):
        for record in self:
            record.value_count = len(record.value_ids)

from odoo import models, fields

class CategoryGroup(models.Model):
    _name = 'product.category.group'
    _description = 'Category Group'

    name = fields.Char(
        string='Category Group Name',
        required=True,
    )

    # If you want to show all product categories under a particular category group, you can use a One2many field
    category_ids = fields.One2many(
        'product.category',
        'category_group_id',
        string='Product Categories'
    )
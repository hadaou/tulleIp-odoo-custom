{
    'name': "TulleIP Inventory Module",
    'summary': "TulleIP Custom Inventory Management Features",
    'version': '17.0.0.7',
    'sequence': 10,
    'depends': ['product', 'sale','sale_renting', 'purchase', 'stock', 'website_sale'],
    'author': "Haitham Daou",
    "category": "Customizations",
    'description': """
        Long description of the module's purpose.
    """,
    'data': [
        # list of XML or CSV files with data
        'views/product_template_views.xml',
        'views/product_product_views.xml',
        'views/product_category_views.xml',
        'wizards/add_product_wizard_views.xml',
        'security/ir.model.access.csv',
        'views/product_category_menu.xml',
        'views/product_attribute_views.xml',
        'reports/product_product_template.xml'
    ],
    'application': False,
    'installable': True,
    'license': 'LGPL-3',
}

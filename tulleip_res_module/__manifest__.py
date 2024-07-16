{
    'name': "TulleIP Resource Module",
    'summary': "Custom module for managing governorates, districts, and subdivisions in TulleIP",
    'version': '17.0.0.8',
    'sequence': 11,
    'depends': ['base'],
    'author': "Haitham Daou",
    'category': "Customizations",
    'description': """
        TulleIP Resource Module

        This module provides custom functionalities for managing governorates, districts, and their subdivisions
        (villages and areas) within the TulleIP system. It includes:

        - A new model for governorates
        - A new model for districts, linked to governorates
        - A new model for subdivisions, classified as villages or areas
        - Integration with the existing res.partner model to associate partners with multiple districts
        - User-friendly views for managing governorates, districts, and subdivisions

        Key Features:
        - Create and manage governorates with relevant details like code and country
        - Create and manage districts with relevant details like postal code, population, and area
        - Define and categorize subdivisions (villages and areas) under each district
        - Associate partners with multiple districts for enhanced data organization

        This module aims to improve data structure and accessibility within the TulleIP system, 
        providing a robust framework for geographical and administrative management.
    """,
    'data': [
        'views/x_res_district_views.xml',
        'views/x_res_governorate_views.xml',
        'views/x_res_subdivision_views.xml',
        'views/x_res_menus.xml',
        'security/ir.model.access.csv'
    ],
    'application': False,
    'installable': True,
    'license': 'LGPL-3',
}

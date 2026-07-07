# -*- coding: utf-8 -*-
{
    'name': 'Custom Product Attribution System',
    'version': '1.0',
    'category': 'Sales/Product',
    'summary': 'Category-based attribute inheritance and hybrid EAV models.',
    'description': """
        Milestone 1: Category-Based Attribute Inheritance & Hybrid EAV models.
    """,
    'depends': ['product', 'sale'],
    'data': [
        'security/security_groups.xml',
        'security/ir.model.access.csv',
        'views/product_attribute_views.xml',
        'views/product_attribute_set_views.xml',
        'views/product_category_views.xml',
        'views/product_template_views.xml',
        'views/pim_export_views.xml',
        'views/res_config_settings_views.xml',
    ],
    'application': True,
    'assets': {
        'web.assets_backend': [
            'odoo_product_attribution_system/static/src/components/dynamic_attribute_value_field.js',
            'odoo_product_attribution_system/static/src/components/dynamic_attribute_value_field.xml',
        ],
    },
    'demo': [
        'data/demo_data.xml',
    ],
    'installable': True,
    'application': False,
    'license': 'LGPL-3',
}

# -*- coding: utf-8 -*-
from odoo import fields, models

class ProductAttribute(models.Model):
    _inherit = 'product.attribute'

    value_type = fields.Selection([
        ('text', 'Text'),
        ('integer', 'Integer'),
        ('float', 'Float'),
        ('date', 'Date'),
        ('boolean', 'Boolean'),
        ('selection', 'Selection'),
    ], string='Value Type', default='text', required=True)

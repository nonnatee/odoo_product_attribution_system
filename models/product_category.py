# -*- coding: utf-8 -*-
from odoo import api, fields, models
from odoo.exceptions import ValidationError


class ProductCategory(models.Model):
    _inherit = 'product.category'

    attribute_ids = fields.Many2many(
        'product.attribute',
        'product_category_product_attribute_rel',
        'category_id',
        'attribute_id',
        string='Attributes',
    )

    attribute_set_ids = fields.Many2many(
        'product.attribute.set',
        'product_category_attribute_set_rel',
        'category_id',
        'set_id',
        string='Attribute Sets',
    )

    all_inherited_attribute_ids = fields.Many2many(
        'product.attribute',
        compute='_compute_all_inherited_attribute_ids',
        string='All Inherited Attributes',
        store=False,
    )

    @api.depends('attribute_ids', 'attribute_set_ids.attribute_line_ids.attribute_id', 'parent_id.all_inherited_attribute_ids')
    def _compute_all_inherited_attribute_ids(self):
        """Recursively aggregate attributes from this category, its sets, and parent categories."""
        for category in self:
            visited = {category.id}
            attrs = category.attribute_ids
            if category.attribute_set_ids:
                attrs |= category.attribute_set_ids.mapped('attribute_line_ids.attribute_id')
            parent = category.parent_id
            while parent and parent.id not in visited:
                visited.add(parent.id)
                attrs |= parent.attribute_ids
                if parent.attribute_set_ids:
                    attrs |= parent.attribute_set_ids.mapped('attribute_line_ids.attribute_id')
                parent = parent.parent_id
            category.all_inherited_attribute_ids = attrs

    @api.constrains('parent_id')
    def _check_category_recursion(self):
        if not self._check_recursion():
            raise ValidationError('Error! You cannot create recursive categories.')

    def write(self, vals):
        res = super().write(vals)
        if any(f in vals for f in ('attribute_ids', 'attribute_set_ids', 'parent_id')):
            # Sync product templates under this category and all subcategories
            descendants = self.search([('id', 'child_of', self.ids)])
            templates = self.env['product.template'].search([
                ('categ_id', 'in', descendants.ids),
            ])
            templates._sync_custom_values()
        return res


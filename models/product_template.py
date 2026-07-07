# -*- coding: utf-8 -*-
from odoo import api, fields, models


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    custom_value_ids = fields.One2many(
        'product.template.custom.value',
        'product_tmpl_id',
        string='Custom Attribute Values',
    )

    attribute_set_ids = fields.Many2many(
        'product.attribute.set',
        'product_template_attribute_set_rel',
        'tmpl_id',
        'set_id',
        string='Attribute Sets',
    )

    all_inherited_attribute_ids = fields.Many2many(
        'product.attribute',
        compute='_compute_all_inherited_attribute_ids',
        string='All Inherited Attributes',
    )

    @api.depends('categ_id.all_inherited_attribute_ids', 'attribute_set_ids.attribute_line_ids.attribute_id')
    def _compute_all_inherited_attribute_ids(self):
        for template in self:
            attrs = self.env['product.attribute']
            if template.categ_id:
                attrs |= template.categ_id.all_inherited_attribute_ids
            if template.attribute_set_ids:
                attrs |= template.attribute_set_ids.mapped('attribute_line_ids.attribute_id')
            template.all_inherited_attribute_ids = attrs

    def _get_attribute_default_value(self, attribute):
        """Resolves default value for a given attribute based on template sets and category sets hierarchy."""
        self.ensure_one()
        # 1. Check template-specific sets
        for set_rec in self.attribute_set_ids:
            line = set_rec.attribute_line_ids.filtered(lambda l: l.attribute_id == attribute)
            if line:
                return line[0]

        # 2. Check category hierarchy sets
        if self.categ_id:
            visited = {self.categ_id.id}
            curr_categ = self.categ_id
            while curr_categ:
                for set_rec in curr_categ.attribute_set_ids:
                    line = set_rec.attribute_line_ids.filtered(lambda l: l.attribute_id == attribute)
                    if line:
                        return line[0]

                curr_categ = curr_categ.parent_id
                if curr_categ and curr_categ.id in visited:
                     break
                if curr_categ:
                     visited.add(curr_categ.id)
        return None

    def _sync_custom_values(self):
        """Ensure that all inherited attributes have a custom value record, applying defaults.
        
        This creates missing records but never deletes existing ones to prevent data loss.
        """
        CustomValue = self.env['product.template.custom.value']
        for template in self:
            existing_attrs = template.custom_value_ids.mapped('attribute_id')
            inherited_attrs = template.all_inherited_attribute_ids
            missing_attrs = inherited_attrs - existing_attrs

            if missing_attrs:
                vals_list = []
                for attr in missing_attrs:
                    vals = {
                        'product_tmpl_id': template.id,
                        'attribute_id': attr.id,
                    }
                    default_line = template._get_attribute_default_value(attr)
                    if default_line:
                        vals.update({
                            'value_text': default_line.value_text,
                            'value_integer': default_line.value_integer,
                            'value_float': default_line.value_float,
                            'value_date': default_line.value_date,
                            'value_boolean': default_line.value_boolean,
                            'value_selection_id': default_line.value_selection_id.id,
                        })
                    vals_list.append(vals)
                if vals_list:
                    CustomValue.create(vals_list)

    @api.onchange('categ_id', 'attribute_set_ids')
    def _onchange_custom_attributes_sync(self):
        """When category or sets change in the UI, dynamically add new custom value lines
        pre-populated with default values."""
        active_attrs = self.env['product.attribute']
        if self.categ_id:
            active_attrs |= self.categ_id.all_inherited_attribute_ids
        if self.attribute_set_ids:
            active_attrs |= self.attribute_set_ids.mapped('attribute_line_ids.attribute_id')

        existing_attrs = self.custom_value_ids.mapped('attribute_id')
        missing_attrs = active_attrs - existing_attrs

        new_lines = []
        for attr in missing_attrs:
            vals = {
                'attribute_id': attr.id,
                'product_tmpl_id': self._origin.id or self.id,
            }
            default_line = self._get_attribute_default_value(attr)
            if default_line:
                vals.update({
                    'value_text': default_line.value_text,
                    'value_integer': default_line.value_integer,
                    'value_float': default_line.value_float,
                    'value_date': default_line.value_date,
                    'value_boolean': default_line.value_boolean,
                    'value_selection_id': default_line.value_selection_id.id,
                })
            new_line = self.env['product.template.custom.value'].new(vals)
            new_lines.append(new_line)

        if new_lines:
            combined = self.custom_value_ids
            for line in new_lines:
                combined += line
            self.custom_value_ids = combined

    @api.model_create_multi
    def create(self, vals_list):
        templates = super().create(vals_list)
        templates._sync_custom_values()
<<<<<<< Updated upstream
=======
        templates._evaluate_set_value_rules()
        templates._sync_external_product_categories()
>>>>>>> Stashed changes
        return templates

    def write(self, vals):
        res = super().write(vals)
        if any(f in vals for f in ('categ_id', 'attribute_set_ids')):
            self._sync_custom_values()
<<<<<<< Updated upstream
=======
            self._evaluate_set_value_rules()
        if 'categ_id' in vals:
            self._sync_external_product_categories()
>>>>>>> Stashed changes
        return res

    def _sync_external_product_categories(self):
        for template in self:
            if not template.categ_id:
                continue
            
            # 1. POS Category Sync
            if hasattr(template, 'pos_categ_id'):
                target_pos_id = template.categ_id.pos_categ_id.id if (
                    template.categ_id.sync_to_pos and template.categ_id.pos_categ_id
                ) else False
                template.sudo().write({'pos_categ_id': target_pos_id})
                
            # 2. eCommerce Category Sync
            if hasattr(template, 'public_categ_ids'):
                mapped_public_categ_ids = self.env['product.category'].search([
                    ('public_categ_id', '!=', False)
                ]).mapped('public_categ_id')
                
                to_remove = template.public_categ_ids & mapped_public_categ_ids
                if to_remove:
                    template.sudo().write({'public_categ_ids': [(3, c.id) for c in to_remove]})
                
                if template.categ_id.sync_to_website and template.categ_id.public_categ_id:
                    template.sudo().write({'public_categ_ids': [(4, template.categ_id.public_categ_id.id)]})


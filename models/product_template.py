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

    def _evaluate_set_value_rules(self):
        for template in self:
            sets = template.attribute_set_ids
            if template.categ_id:
                curr = template.categ_id
                visited = {curr.id}
                while curr:
                    sets |= curr.attribute_set_ids
                    curr = curr.parent_id
                    if curr and curr.id in visited:
                        break
                    if curr:
                        visited.add(curr.id)

            rules = sets.mapped('rule_ids').filtered(lambda r: r.action_type == 'set_value')
            changed = True
            iterations = 0
            while changed and iterations < 10:
                changed = False
                iterations += 1
                for rule in rules:
                    trigger_line = template.custom_value_ids.filtered(lambda l: l.attribute_id == rule.attribute_id)
                    if not trigger_line:
                        continue
                    trigger_line = trigger_line[0]

                    condition_met = False
                    val_type = trigger_line.value_type

                    if val_type == 'selection':
                        if trigger_line.value_selection_id in rule.condition_value_selection_ids:
                            condition_met = True
                    elif val_type == 'boolean':
                        if trigger_line.value_boolean == rule.condition_value_boolean:
                            condition_met = True
                    else:
                        cur_val = ''
                        if val_type == 'text':
                            cur_val = trigger_line.value_text or ''
                        elif val_type == 'integer':
                            cur_val = str(trigger_line.value_integer) if trigger_line.value_integer else ''
                        elif val_type == 'float':
                            cur_val = str(trigger_line.value_float) if trigger_line.value_float else ''
                        elif val_type == 'date':
                            cur_val = str(trigger_line.value_date) if trigger_line.value_date else ''

                        if rule.condition_value_text and cur_val == rule.condition_value_text:
                            condition_met = True

                    if condition_met:
                        target_line = template.custom_value_ids.filtered(lambda l: l.attribute_id == rule.target_attribute_id)
                        if target_line:
                            target_line = target_line[0]
                            t_type = target_line.value_type
                            old_val = False
                            new_val = False

                            if t_type == 'text':
                                old_val = target_line.value_text
                                new_val = rule.action_value_text
                                if old_val != new_val:
                                    target_line.value_text = new_val
                                    changed = True
                            elif t_type == 'integer':
                                old_val = target_line.value_integer
                                new_val = rule.action_value_integer
                                if old_val != new_val:
                                    target_line.value_integer = new_val
                                    changed = True
                            elif t_type == 'float':
                                old_val = target_line.value_float
                                new_val = rule.action_value_float
                                if old_val != new_val:
                                    target_line.value_float = new_val
                                    changed = True
                            elif t_type == 'date':
                                old_val = target_line.value_date
                                new_val = rule.action_value_date
                                if old_val != new_val:
                                    target_line.value_date = new_val
                                    changed = True
                            elif t_type == 'boolean':
                                old_val = target_line.value_boolean
                                new_val = rule.action_value_boolean
                                if old_val != new_val:
                                    target_line.value_boolean = new_val
                                    changed = True
                            elif t_type == 'selection':
                                old_val = target_line.value_selection_id
                                new_val = rule.action_value_selection_id
                                if old_val != new_val:
                                    target_line.value_selection_id = new_val
                                    changed = True

    @api.model_create_multi
    def create(self, vals_list):
        templates = super().create(vals_list)
        templates._sync_custom_values()
        templates._evaluate_set_value_rules()
        return templates

    def write(self, vals):
        res = super().write(vals)
        if any(f in vals for f in ('categ_id', 'attribute_set_ids')):
            self._sync_custom_values()
            self._evaluate_set_value_rules()
        return res


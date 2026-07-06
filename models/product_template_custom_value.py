# -*- coding: utf-8 -*-
from odoo import api, fields, models
from odoo.exceptions import ValidationError


class ProductTemplateCustomValue(models.Model):
    _name = 'product.template.custom.value'
    _description = 'Product Template Custom Attribute Value'
    _order = 'attribute_id'

    product_tmpl_id = fields.Many2one(
        'product.template',
        string='Product Template',
        required=True,
        ondelete='cascade',
    )
    attribute_id = fields.Many2one(
        'product.attribute',
        string='Attribute',
        required=True,
        ondelete='cascade',
    )
    value_type = fields.Selection(
        related='attribute_id.value_type',
        store=True,
        readonly=True,
        string='Value Type',
    )

    # EAV typed value fields
    value_text = fields.Text(string='Text Value')
    value_integer = fields.Integer(string='Integer Value')
    value_float = fields.Float(string='Float Value')
    value_date = fields.Date(string='Date Value')
    value_boolean = fields.Boolean(string='Boolean Value')
    value_selection_id = fields.Many2one(
        'product.attribute.value',
        string='Selection Value',
        domain="[('attribute_id', '=', attribute_id)]",
    )

    # Consolidated display field (read-only, for search and list display)
    display_value = fields.Char(
        string='Display Value',
        compute='_compute_display_value',
        store=True,
    )

    # Boolean: is this attribute currently inherited from the product's category?
    is_inherited = fields.Boolean(
        string='Is Inherited',
        compute='_compute_is_inherited',
        store=False,
    )

    is_visible = fields.Boolean(
        string='Is Visible',
        compute='_compute_is_visible_and_readonly',
        store=False,
    )

    is_readonly = fields.Boolean(
        string='Is Readonly',
        compute='_compute_is_visible_and_readonly',
        store=False,
    )

    _sql_constraints = [
        ('uniq_product_attribute',
         'unique(product_tmpl_id, attribute_id)',
         'An attribute custom value line must be unique per product template!'),
    ]

    @api.constrains('value_selection_id', 'attribute_id')
    def _check_selection_value(self):
        for rec in self:
            if rec.value_selection_id and rec.value_selection_id.attribute_id != rec.attribute_id:
                raise ValidationError(
                    "The selection value must belong to the same attribute!"
                )

    @api.depends(
        'value_type', 'value_text', 'value_integer', 'value_float',
        'value_date', 'value_boolean', 'value_selection_id',
    )
    def _compute_display_value(self):
        for rec in self:
            if rec.value_type == 'text':
                rec.display_value = rec.value_text or ''
            elif rec.value_type == 'integer':
                rec.display_value = str(rec.value_integer) if rec.value_integer else ''
            elif rec.value_type == 'float':
                rec.display_value = str(rec.value_float) if rec.value_float else ''
            elif rec.value_type == 'date':
                rec.display_value = str(rec.value_date) if rec.value_date else ''
            elif rec.value_type == 'boolean':
                rec.display_value = 'Yes' if rec.value_boolean else 'No'
            elif rec.value_type == 'selection':
                rec.display_value = rec.value_selection_id.name if rec.value_selection_id else ''
            else:
                rec.display_value = ''

    @api.depends('attribute_id', 'product_tmpl_id.all_inherited_attribute_ids')
    def _compute_is_inherited(self):
        for rec in self:
            if rec.product_tmpl_id:
                rec.is_inherited = rec.attribute_id in rec.product_tmpl_id.all_inherited_attribute_ids
            else:
                rec.is_inherited = False

    @api.depends(
        'attribute_id',
        'product_tmpl_id.attribute_set_ids.rule_ids',
        'product_tmpl_id.categ_id.attribute_set_ids.rule_ids',
        'product_tmpl_id.custom_value_ids.value_text',
        'product_tmpl_id.custom_value_ids.value_integer',
        'product_tmpl_id.custom_value_ids.value_float',
        'product_tmpl_id.custom_value_ids.value_date',
        'product_tmpl_id.custom_value_ids.value_boolean',
        'product_tmpl_id.custom_value_ids.value_selection_id',
    )
    def _compute_is_visible_and_readonly(self):
        for rec in self:
            rec.is_visible = True
            rec.is_readonly = False
            if not rec.product_tmpl_id:
                continue

            sets = rec.product_tmpl_id.attribute_set_ids
            if rec.product_tmpl_id.categ_id:
                curr = rec.product_tmpl_id.categ_id
                visited = {curr.id}
                while curr:
                    sets |= curr.attribute_set_ids
                    curr = curr.parent_id
                    if curr and curr.id in visited:
                        break
                    if curr:
                        visited.add(curr.id)

            rules = sets.mapped('rule_ids').filtered(lambda r: r.target_attribute_id == rec.attribute_id)

            for rule in rules:
                trigger_line = rec.product_tmpl_id.custom_value_ids.filtered(lambda l: l.attribute_id == rule.attribute_id)
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
                    if rule.action_type == 'hide':
                        rec.is_visible = False
                    elif rule.action_type == 'readonly':
                        rec.is_readonly = True

    @api.onchange('value_text', 'value_integer', 'value_float', 'value_date', 'value_boolean', 'value_selection_id')
    def _onchange_values_evaluate_rules(self):
        for rec in self:
            if not rec.product_tmpl_id:
                continue

            sets = rec.product_tmpl_id.attribute_set_ids
            if rec.product_tmpl_id.categ_id:
                curr = rec.product_tmpl_id.categ_id
                visited = {curr.id}
                while curr:
                    sets |= curr.attribute_set_ids
                    curr = curr.parent_id
                    if curr and curr.id in visited:
                        break
                    if curr:
                        visited.add(curr.id)

            rules = sets.mapped('rule_ids').filtered(lambda r: r.action_type == 'set_value' and r.attribute_id == rec.attribute_id)
            for rule in rules:
                condition_met = False
                val_type = rec.value_type

                if val_type == 'selection':
                    if rec.value_selection_id in rule.condition_value_selection_ids:
                        condition_met = True
                elif val_type == 'boolean':
                    if rec.value_boolean == rule.condition_value_boolean:
                        condition_met = True
                else:
                    cur_val = ''
                    if val_type == 'text':
                        cur_val = rec.value_text or ''
                    elif val_type == 'integer':
                        cur_val = str(rec.value_integer) if rec.value_integer else ''
                    elif val_type == 'float':
                        cur_val = str(rec.value_float) if rec.value_float else ''
                    elif val_type == 'date':
                        cur_val = str(rec.value_date) if rec.value_date else ''

                    if rule.condition_value_text and cur_val == rule.condition_value_text:
                        condition_met = True

                if condition_met:
                    target_line = rec.product_tmpl_id.custom_value_ids.filtered(lambda l: l.attribute_id == rule.target_attribute_id)
                    if target_line:
                        target_line = target_line[0]
                        t_type = target_line.value_type
                        if t_type == 'text':
                            target_line.value_text = rule.action_value_text
                        elif t_type == 'integer':
                            target_line.value_integer = rule.action_value_integer
                        elif t_type == 'float':
                            target_line.value_float = rule.action_value_float
                        elif t_type == 'date':
                            target_line.value_date = rule.action_value_date
                        elif t_type == 'boolean':
                            target_line.value_boolean = rule.action_value_boolean
                        elif t_type == 'selection':
                            target_line.value_selection_id = rule.action_value_selection_id

    def write(self, vals):
        res = super().write(vals)
        templates = self.mapped('product_tmpl_id')
        if templates:
            templates._evaluate_set_value_rules()
        return res

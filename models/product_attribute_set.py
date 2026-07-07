# -*- coding: utf-8 -*-
from odoo import api, fields, models
from odoo.exceptions import ValidationError


class ProductAttributeSet(models.Model):
    _name = 'product.attribute.set'
    _description = 'Product Attribute Set'
    _order = 'name'

    name = fields.Char(string='Name', required=True)
    attribute_line_ids = fields.One2many(
        'product.attribute.set.line',
        'set_id',
        string='Attributes',
        copy=True,
    )
    rule_ids = fields.One2many(
        'product.attribute.set.rule',
        'set_id',
        string='Rules',
        copy=True,
    )


class ProductAttributeSetLine(models.Model):
    _name = 'product.attribute.set.line'
    _description = 'Product Attribute Set Line'
    _order = 'attribute_id'

    set_id = fields.Many2one(
        'product.attribute.set',
        string='Attribute Set',
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

    is_required = fields.Boolean(string='Required', default=False)

    # Default typed value fields
    value_text = fields.Text(string='Default Text Value')
    value_integer = fields.Integer(string='Default Integer Value')
    value_float = fields.Float(string='Default Float Value')
    value_date = fields.Date(string='Default Date Value')
    value_boolean = fields.Boolean(string='Default Boolean Value')
    value_selection_id = fields.Many2one(
        'product.attribute.value',
        string='Default Selection Value',
        domain="[('attribute_id', '=', attribute_id)]",
    )

    # Consolidated display field (read-only, for search and list display)
    display_value = fields.Char(
        string='Default Value',
        compute='_compute_display_value',
        store=True,
    )

    _sql_constraints = [
        ('uniq_set_attribute',
         'unique(set_id, attribute_id)',
         'An attribute can only be defined once per attribute set!'),
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


class ProductAttributeSetRule(models.Model):
    _name = 'product.attribute.set.rule'
    _description = 'Product Attribute Set Rule'

    set_id = fields.Many2one(
        'product.attribute.set',
        string='Attribute Set',
        required=True,
        ondelete='cascade',
    )
    attribute_id = fields.Many2one(
        'product.attribute',
        string='Trigger Attribute',
        required=True,
        ondelete='cascade',
    )
    value_type = fields.Selection(
        related='attribute_id.value_type',
        string='Trigger Value Type',
        readonly=True,
    )

    # Condition Trigger Values
    condition_value_selection_ids = fields.Many2many(
        'product.attribute.value',
        'product_attribute_set_rule_trigger_val_rel',
        'rule_id',
        'value_id',
        string='Trigger Selection Values',
        domain="[('attribute_id', '=', attribute_id)]",
    )
    condition_value_boolean = fields.Boolean(string='Trigger Boolean Value')
    condition_value_text = fields.Char(string='Trigger String Value')

    action_type = fields.Selection([
        ('hide', 'Hide Target Attribute'),
        ('readonly', 'Disable Target Attribute (Readonly)'),
        ('set_value', 'Force Target Attribute Value'),
    ], string='Action', default='hide', required=True)

    target_attribute_id = fields.Many2one(
        'product.attribute',
        string='Target Attribute',
        required=True,
        ondelete='cascade',
    )
    target_value_type = fields.Selection(
        related='target_attribute_id.value_type',
        string='Target Value Type',
        readonly=True,
    )

    # Action values for 'set_value'
    action_value_text = fields.Text(string='Action Text Value')
    action_value_integer = fields.Integer(string='Action Integer Value')
    action_value_float = fields.Float(string='Action Float Value')
    action_value_date = fields.Date(string='Action Date Value')
    action_value_boolean = fields.Boolean(string='Action Boolean Value')
    action_value_selection_id = fields.Many2one(
        'product.attribute.value',
        string='Action Selection Value',
        domain="[('attribute_id', '=', target_attribute_id)]",
    )

    @api.constrains('attribute_id', 'target_attribute_id', 'set_id')
    def _check_attributes_in_set(self):
        for rec in self:
            set_attrs = rec.set_id.attribute_line_ids.mapped('attribute_id')
            if rec.attribute_id not in set_attrs:
                raise ValidationError("The trigger attribute must belong to the attribute set!")
            if rec.target_attribute_id not in set_attrs:
                raise ValidationError("The target attribute must belong to the attribute set!")
            if rec.attribute_id == rec.target_attribute_id:
                raise ValidationError("The trigger attribute and target attribute cannot be the same!")

    @api.constrains('action_value_selection_id', 'target_attribute_id')
    def _check_action_selection_value(self):
        for rec in self:
            if rec.action_value_selection_id and rec.action_value_selection_id.attribute_id != rec.target_attribute_id:
                raise ValidationError("The action selection value must belong to the target attribute!")


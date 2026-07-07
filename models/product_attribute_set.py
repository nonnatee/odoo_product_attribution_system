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

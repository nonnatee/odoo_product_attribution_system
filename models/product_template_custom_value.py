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

    def write(self, vals):
        for rec in self:
            if rec.product_tmpl_id._is_write_locked():
                raise ValidationError(
                    f"Product '{rec.product_tmpl_id.name}' is Approved and locked. Custom values cannot be modified."
                )
        return super().write(vals)

    def unlink(self):
        for rec in self:
            if rec.product_tmpl_id._is_write_locked():
                raise ValidationError(
                    f"Product '{rec.product_tmpl_id.name}' is Approved and locked. Custom values cannot be deleted."
                )
        return super().unlink()

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

    is_required = fields.Boolean(
        string='Required',
        compute='_compute_is_required',
        store=False,
    )

    @api.depends('attribute_id', 'product_tmpl_id.attribute_set_ids', 'product_tmpl_id.categ_id')
    def _compute_is_required(self):
        for rec in self:
            if rec.attribute_id.is_required:
                rec.is_required = True
                continue
            
            is_req = False
            template = rec.product_tmpl_id
            if template:
                for set_rec in template.attribute_set_ids:
                    line = set_rec.attribute_line_ids.filtered(lambda l: l.attribute_id == rec.attribute_id)
                    if line and line[0].is_required:
                        is_req = True
                        break
                
                if not is_req and template.categ_id:
                    visited = {template.categ_id.id}
                    curr_categ = template.categ_id
                    while curr_categ:
                        for set_rec in curr_categ.attribute_set_ids:
                            line = set_rec.attribute_line_ids.filtered(lambda l: l.attribute_id == rec.attribute_id)
                            if line and line[0].is_required:
                                is_req = True
                                break
                        if is_req:
                            break
                        curr_categ = curr_categ.parent_id
                        if curr_categ and curr_categ.id in visited:
                            break
                        if curr_categ:
                            visited.add(curr_categ.id)
            rec.is_required = is_req


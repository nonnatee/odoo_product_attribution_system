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

    pim_state = fields.Selection([
        ('draft', 'Draft'),
        ('enriching', 'Enriching'),
        ('approved', 'Approved'),
    ], string='PIM Stage', default='draft', required=True)

    pim_completeness = fields.Integer(
        string='Completeness Score (%)',
        compute='_compute_pim_completeness',
        store=False,
    )

    pim_asset_ids = fields.One2many(
        'product.pim.asset',
        'product_tmpl_id',
        string='PIM Digital Assets',
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

    @api.depends(
        'name', 'description_sale', 'image_1920', 'categ_id',
        'custom_value_ids.is_required', 'custom_value_ids.value_text',
        'custom_value_ids.value_integer', 'custom_value_ids.value_float',
        'custom_value_ids.value_date', 'custom_value_ids.value_boolean',
        'custom_value_ids.value_selection_id'
    )
    def _compute_pim_completeness(self):
        for template in self:
            total = 4
            filled = 0
            if template.name:
                filled += 1
            if template.description_sale:
                filled += 1
            if template.image_1920:
                filled += 1
            if template.categ_id and template.categ_id != self.env.ref('product.product_category_all', raise_if_not_found=False):
                filled += 1
            
            required_lines = template.custom_value_ids.filtered(lambda l: l.is_required)
            for line in required_lines:
                total += 1
                is_line_filled = False
                if line.value_type == 'text' and line.value_text:
                    is_line_filled = True
                elif line.value_type == 'integer' and line.value_integer:
                    is_line_filled = True
                elif line.value_type == 'float' and line.value_float:
                    is_line_filled = True
                elif line.value_type == 'date' and line.value_date:
                    is_line_filled = True
                elif line.value_type == 'boolean':
                    is_line_filled = True
                elif line.value_type == 'selection' and line.value_selection_id:
                    is_line_filled = True
                
                if is_line_filled:
                    filled += 1
            
            template.pim_completeness = int((filled / total) * 100) if total > 0 else 100

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
        templates._sync_external_product_categories()
        return templates

    def _is_write_locked(self):
        self.ensure_one()
        if self.pim_state != 'approved':
            return False
        
        bypass_enabled = self.env['ir.config_parameter'].sudo().get_param('odoo_product_attribution_system.pim_lock_bypass')
        if bypass_enabled:
            is_manager = self.env.user.has_group('odoo_product_attribution_system.group_pim_manager')
            if is_manager:
                return False
        return True

    def write(self, vals):
        # Enforce PIM workflow edit lock on Approved state
        from odoo.exceptions import ValidationError
        if 'pim_state' not in vals:
            for rec in self:
                if rec._is_write_locked():
                    raise ValidationError(
                        f"Product '{rec.name}' is in 'Approved' state and locked for editing. "
                        "Please transition back to 'Enriching' to modify specifications."
                    )
        res = super().write(vals)
        if any(f in vals for f in ('categ_id', 'attribute_set_ids')):
            self._sync_custom_values()
            self._evaluate_set_value_rules()
        if 'categ_id' in vals:
            self._sync_external_product_categories()
        return res

    def action_pim_draft(self):
        for rec in self:
            rec.write({'pim_state': 'draft'})

    def action_pim_enriching(self):
        for rec in self:
            rec.write({'pim_state': 'enriching'})

    def action_pim_approve(self):
        from odoo.exceptions import ValidationError
        if not self.env.user.has_group('odoo_product_attribution_system.group_pim_manager'):
            raise ValidationError("Only PIM Managers are authorized to approve product specifications.")

        for rec in self:
            if rec.pim_completeness < 100:
                raise ValidationError(
                    f"Cannot approve '{rec.name}'. The product completeness score is only {rec.pim_completeness}%. "
                    "Please fill all required core fields and specifications before approving."
                )
            rec.write({'pim_state': 'approved'})

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


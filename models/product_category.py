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

    # POS and eCommerce mapping fields
    sync_to_pos = fields.Boolean(string='Sync to POS', default=False)
    sync_to_website = fields.Boolean(string='Sync to eCommerce', default=False)
    pos_categ_id = fields.Many2one('pos.category', string='POS Category', readonly=True, ondelete='set null')
    public_categ_id = fields.Many2one('product.public.category', string='eCommerce Category', readonly=True, ondelete='set null')

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

    @api.model_create_multi
    def create(self, vals_list):
        records = super().create(vals_list)
        for record in records:
            record._sync_to_external_channels()
        return records

    def write(self, vals):
        res = super().write(vals)
        if any(f in vals for f in ('name', 'parent_id', 'sync_to_pos', 'sync_to_website')):
            for record in self:
                record._sync_to_external_channels()
        if any(f in vals for f in ('attribute_ids', 'attribute_set_ids', 'parent_id')):
            descendants = self.search([('id', 'child_of', self.ids)])
            templates = self.env['product.template'].search([
                ('categ_id', 'in', descendants.ids),
            ])
            templates._sync_custom_values()
        return res

    def unlink(self):
        pos_categ_model = self.env.get('pos.category')
        public_categ_model = self.env.get('product.public.category')
        
        pos_categs_to_unlink = self.env['pos.category']
        public_categs_to_unlink = self.env['product.public.category']
        
        for record in self:
            if pos_categ_model and record.pos_categ_id:
                pos_categs_to_unlink |= record.pos_categ_id
            if public_categ_model and record.public_categ_id:
                public_categs_to_unlink |= record.public_categ_id
                
        res = super().unlink()
        
        if pos_categs_to_unlink:
            try:
                pos_categs_to_unlink.unlink()
            except Exception:
                pass
        if public_categs_to_unlink:
            try:
                public_categs_to_unlink.unlink()
            except Exception:
                pass
        return res

    def _sync_to_external_channels(self):
        self.ensure_one()
        pos_categ_model = self.env.get('pos.category')
        public_categ_model = self.env.get('product.public.category')
        
        # 1. POS category sync
        if pos_categ_model:
            if self.sync_to_pos:
                pos_parent_id = False
                if self.parent_id and self.parent_id.sync_to_pos and self.parent_id.pos_categ_id:
                    pos_parent_id = self.parent_id.pos_categ_id.id
                
                vals = {
                    'name': self.name,
                    'parent_id': pos_parent_id,
                }
                
                if not self.pos_categ_id:
                    pos_categ = pos_categ_model.create(vals)
                    self.sudo().write({'pos_categ_id': pos_categ.id})
                else:
                    self.pos_categ_id.write(vals)
            else:
                if self.pos_categ_id:
                    pos_to_del = self.pos_categ_id
                    self.sudo().write({'pos_categ_id': False})
                    try:
                        pos_to_del.unlink()
                    except Exception:
                        pass
                        
        # 2. eCommerce category sync
        if public_categ_model:
            if self.sync_to_website:
                public_parent_id = False
                if self.parent_id and self.parent_id.sync_to_website and self.parent_id.public_categ_id:
                    public_parent_id = self.parent_id.public_categ_id.id
                    
                vals = {
                    'name': self.name,
                    'parent_id': public_parent_id,
                }
                
                if not self.public_categ_id:
                    public_categ = public_categ_model.create(vals)
                    self.sudo().write({'public_categ_id': public_categ.id})
                else:
                    self.public_categ_id.write(vals)
            else:
                if self.public_categ_id:
                    public_to_del = self.public_categ_id
                    self.sudo().write({'public_categ_id': False})
                    try:
                        public_to_del.unlink()
                    except Exception:
                        pass

        # Re-evaluate direct descendants to propagate parent linkages
        child_categs = self.search([('parent_id', '=', self.id)])
        for child in child_categs:
            if child.sync_to_pos or child.sync_to_website:
                child._sync_to_external_channels()


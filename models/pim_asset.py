# -*- coding: utf-8 -*-
from odoo import fields, models

class ProductPimAsset(models.Model):
    _name = 'product.pim.asset'
    _description = 'Product PIM Digital Asset'
    _order = 'id desc'

    name = fields.Char(string='Asset Title', required=True)
    product_tmpl_id = fields.Many2one(
        'product.template',
        string='Product Template',
        required=True,
        ondelete='cascade',
    )
    asset_type = fields.Selection([
        ('manual', 'User Manual'),
        ('datasheet', 'Product Datasheet'),
        ('image', 'High-Res Image'),
        ('video', 'Video Link'),
        ('other', 'Other Document'),
    ], string='Asset Type', default='manual', required=True)
    
    attachment_id = fields.Many2one(
        'ir.attachment',
        string='File Attachment',
    )
    video_url = fields.Char(string='Video URL')
    description = fields.Text(string='Description')

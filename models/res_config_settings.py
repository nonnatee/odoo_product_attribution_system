# -*- coding: utf-8 -*-
from odoo import fields, models

class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    pim_lock_bypass = fields.Boolean(
        string="Allow Lock Bypass",
        config_parameter='odoo_product_attribution_system.pim_lock_bypass',
        help="Allow PIM Managers to edit Approved products without changing the state."
    )

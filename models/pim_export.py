# -*- coding: utf-8 -*-
import csv
import json
import io
import base64
from odoo import api, fields, models
from odoo.exceptions import ValidationError

class PimExportProfile(models.Model):
    _name = 'pim.export.profile'
    _description = 'PIM Multi-Channel Export Profile'
    _order = 'name'

    name = fields.Char(string='Profile Name', required=True)
    export_format = fields.Selection([
        ('csv', 'CSV Format'),
        ('json', 'JSON Format'),
    ], string='Export Format', default='csv', required=True)
    
    mapping_ids = fields.One2many(
        'pim.export.mapping',
        'profile_id',
        string='Field Mappings',
        copy=True,
    )

    def action_generate_export(self):
        self.ensure_one()
        if not self.mapping_ids:
            raise ValidationError("Please define at least one field mapping before exporting.")

        # Filter only approved products for feed generation
        products = self.env['product.template'].search([('pim_state', '=', 'approved')])
        if not products:
            raise ValidationError("No products are in the 'Approved' state to export.")

        if self.export_format == 'csv':
            return self._generate_csv_export(products)
        else:
            return self._generate_json_export(products)

    def _generate_csv_export(self, products):
        output = io.StringIO()
        writer = csv.writer(output, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        
        # Write headers
        headers = self.mapping_ids.mapped('target_header')
        writer.writerow(headers)
        
        # Write product rows
        for product in products:
            row = []
            for mapping in self.mapping_ids:
                row.append(self._get_mapped_value(product, mapping))
            writer.writerow(row)
            
        file_data = output.getvalue().encode('utf-8')
        output.close()
        
        return self._create_download_attachment(file_data, f"{self.name.replace(' ', '_')}.csv", 'text/csv')

    def _generate_json_export(self, products):
        data_list = []
        for product in products:
            item = {}
            for mapping in self.mapping_ids:
                item[mapping.target_header] = self._get_mapped_value(product, mapping)
            data_list.append(item)
            
        file_data = json.dumps(data_list, indent=4).encode('utf-8')
        
        return self._create_download_attachment(file_data, f"{self.name.replace(' ', '_')}.json", 'application/json')

    def _get_mapped_value(self, product, mapping):
        if mapping.source_type == 'field':
            if not mapping.field_name:
                return ''
            try:
                val = getattr(product, mapping.field_name)
                if isinstance(val, models.BaseModel):
                    # For Many2one, return display name, otherwise comma-separated names
                    return ', '.join(val.mapped('display_name')) if val else ''
                elif isinstance(val, bool):
                    return 'true' if val else 'false'
                return str(val) if val is not None else ''
            except AttributeError:
                return ''
        elif mapping.source_type == 'attribute':
            if not mapping.attribute_id:
                return ''
            line = product.custom_value_ids.filtered(lambda l: l.attribute_id == mapping.attribute_id)
            return line[0].display_value if line else ''
        return ''

    def _create_download_attachment(self, file_data, filename, mimetype):
        attachment = self.env['ir.attachment'].create({
            'name': filename,
            'type': 'binary',
            'datas': base64.b64encode(file_data),
            'mimetype': mimetype,
        })
        return {
            'type': 'ir.actions.act_url',
            'url': f'/web/content/{attachment.id}?download=true',
            'target': 'self',
        }


class PimExportMapping(models.Model):
    _name = 'pim.export.mapping'
    _description = 'PIM Export Mapping Line'
    _order = 'id'

    profile_id = fields.Many2one(
        'pim.export.profile',
        string='Export Profile',
        required=True,
        ondelete='cascade',
    )
    target_header = fields.Char(string='Column/Header Name', required=True)
    source_type = fields.Selection([
        ('field', 'Standard Product Field'),
        ('attribute', 'Custom Attribute EAV'),
    ], string='Source Type', default='field', required=True)
    
    field_name = fields.Char(string='Standard Field Technical Name')
    attribute_id = fields.Many2one(
        'product.attribute',
        string='Custom Attribute',
    )

    @api.constrains('source_type', 'field_name', 'attribute_id')
    def _check_source_config(self):
        for rec in self:
            if rec.source_type == 'field' and not rec.field_name:
                raise ValidationError("Technical Field Name is required for standard product field mappings.")
            if rec.source_type == 'attribute' and not rec.attribute_id:
                raise ValidationError("Custom Attribute is required for attribute mappings.")

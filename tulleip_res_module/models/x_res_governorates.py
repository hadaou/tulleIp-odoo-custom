from odoo import models, fields

class Governorate(models.Model):
    _name = 'x_res.governorate'
    _description = 'Governorate'

    name = fields.Char(string='Governorate Name', required=True)
    arabic_name = fields.Char(string='Arabic Name')
    country_id = fields.Many2one('res.country', string='Country', required=True)
    district_ids = fields.One2many('x_res.district', 'governorate_id', string='Districts')

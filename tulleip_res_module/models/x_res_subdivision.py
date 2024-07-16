from odoo import models, fields

class Subdivision(models.Model):
    _name = 'x_res.subdivision'
    _description = 'Subdivision (Village or Area)'

    name = fields.Char(string='Subdivision Name', required=True)
    arabic_name = fields.Char(string='Arabic Name')
    district_id = fields.Many2one('x_res.district', string='District', required=True)



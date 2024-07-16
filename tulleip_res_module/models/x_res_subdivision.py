from odoo import models, fields


class Subdivision(models.Model):
    _name = 'res.subdivision'
    _description = 'Subdivision (Village or Area)'

    name = fields.Char(string='Area', required=True)
    district_id = fields.Many2one('x_res.district', string='District', required=True)


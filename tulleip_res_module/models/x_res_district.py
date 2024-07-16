from odoo import api, fields, models

import logging

_logger = logging.getLogger(__name__)


class District(models.Model):
    _name = 'x_res.district'
    _description = 'District'

    name = fields.Char(string='District Name', required=True)
    arabic_name = fields.Char(string='Arabic Name')
    country_id = fields.Many2one('res.country', string='Country', required=True)
    subdivision_ids = fields.One2many('x_res.subdivision', 'district_id', string='Subdivisions')

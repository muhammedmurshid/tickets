from odoo import models, fields, api


class ServiceTypes(models.Model):
    _name = 'service.type'
    _description = 'Service Type'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(string='Service Type', required=True)
    assign_to = fields.Many2one('res.users', string='Assign To', required=True)

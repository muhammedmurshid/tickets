from odoo import models, fields, api


class ServiceTypes(models.Model):
    _name = 'service.type'
    _description = 'Service Type'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(string='Service Type', required=True)
    assign_to = fields.Many2one('res.users', string='Assign To', required=True)
    assign_to_users = fields.Many2many('res.users', string='Assign To Users')
    stress_days = fields.Integer(string='Stress Days')

    def print_current_users(self):

        for k in self.assign_to_users.ids:
            print(k, 'ooooo')
            print(self.env.user.id, 'user')
            if k == self.env.user.id:
                print('same')
            else:
                print('not same')


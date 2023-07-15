from odoo import api, fields, models


class MyTasks(models.Model):
    _name = 'my.tasks'
    _description = 'Tasks'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(string='Name')
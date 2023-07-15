from odoo import api, fields, models


class UserServiceForm(models.Model):
    _name = 'user.service.form'
    _description = 'Form'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Many2one('res.users', string='Name', default=lambda self: self.env.user, readonly=True)
    date = fields.Datetime(string='Date', default=fields.Datetime.now, readonly=True)
    type = fields.Many2one('service.type', string='Type')
    description = fields.Text(string='Description')
    priority = fields.Selection([
        ('low', 'Low'), ('medium', 'Medium'), ('high', 'High')], string='Priority', default='low')
    dead_line = fields.Datetime(string='Dead Line')
    attachment_file = fields.Binary(string='Attachment')
    note = fields.Text(string='Note')
    task_worker_id = fields.Many2one('res.users', string='Task Worker', compute='_compute_type', store=True)
    rating = fields.Selection([
        ('nil', 'Nil'), ('one', 'One'), ('two', 'Two'), ('three', 'Three')
    ], string='Rating')
    state = fields.Selection([
        ('draft', 'Draft'), ('in_progress', 'In Progress'), ('on_hold', 'On Hold'), ('completed', 'Completed'),
        ('cancelled', 'Cancelled')
    ])

    @api.depends('type')
    def _compute_type(self):
        print('oo')
        self.task_worker_id = self.type.assign_to.id

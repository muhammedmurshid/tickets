from odoo import models, fields, api, _


class AddToToDoActivity(models.TransientModel):
    _name = 'add.to.do.activity'
    _description = 'Add To Do Activity'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(string='Name')
    assign_to = fields.Many2one('res.users', string='Assign To', required=True)
    parent_id = fields.Many2one('project.tickets', string='Parent')
    deadline = fields.Date(string='Deadline')

    def action_add_to_to_do(self):
        record = self.env['project.tickets'].search([('id', '=', self.parent_id.id)])
        print(record.type.name, 'record', record.date, 'date')
        self.env['to_do.tasks'].sudo().create({
            'name': self.name,
            'assigned_to': self.assign_to.id,
            'description': record.description,
            'dead_line': self.deadline,
            'ticket_id': record.id
        })
        to_do = self.env['to_do.tasks'].sudo().search([('ticket_id', '=', record.id)])
        to_do.write({
            'state': 'task_sent',
        })
        # to_do.activity_schedule('to_do.activity_to_do_activity_custom', user_id=self.assign_to.id,
        #                        note=f'You have new work scheduled.')
        record.update({
            'state': 'to_do',
            'added_to_do': True
        })

from odoo import models, fields, api, _


class ProjectTickets(models.Model):
    _name = 'project.tickets'
    _description = 'Ticket'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Many2one('res.users', string='Name', default=lambda self: self.env.user, readonly=True)
    reference_no = fields.Char(string="Service Ticket", readonly=True, required=True,
                               copy=False, default='New')
    date = fields.Datetime(string='Date', default=fields.Datetime.now, readonly=True)
    type = fields.Many2one('service.type', string='Type')
    description = fields.Text(string='Description')
    priority = fields.Selection([
        ('low', 'Low'), ('medium', 'Medium'), ('high', 'High')], string='Priority', default='low')
    dead_line = fields.Datetime(string='Dead Line')
    attachment_file = fields.Binary(string='Attachment')
    note = fields.Text(string='Note')
    task_worker_id = fields.Many2one('res.users', string='Task Worker')
    rating = fields.Selection([
        ('nil', 'Nil'), ('one', 'One'), ('two', 'Two'), ('three', 'Three')
    ], string='Rating')
    state = fields.Selection([
        ('draft', 'Draft'), ('in_progress', 'In Progress'), ('on_hold', 'On Hold'), ('completed', 'Completed'),
        ('cancelled', 'Cancelled')
    ], string='Status', default='draft', compute='_compute_status', store=True)
    status = fields.Selection([
        ('draft', 'Draft'), ('in_progress', 'In Progress'), ('on_hold', 'On Hold'), ('completed', 'Completed'),
        ('cancelled', 'Cancelled')
    ], string='Status', default='draft')
    solution_taken = fields.Text(string='Solution Taken')

    @api.depends('type', 're_assign_id')
    def get_batch_head(self):
        print('kkkll')
        user_crnt = self.env.user.id

        res_user = self.env['res.users'].search([('id', '=', self.env.user.id)])
        if res_user.has_group('tickets.tickets_worker'):
            print('same')
            if self.task_worker_id.id == self.env.user.id:
                self.make_visible_head_batch = False
            else:
                print('not same')
                self.make_visible_head_batch = True

    make_visible_head_batch = fields.Boolean(string="User", default=True, compute='get_batch_head', store=True)

    @api.model
    def create(self, vals):
        if vals.get('reference_no', _('New')) == _('New'):
            vals['reference_no'] = self.env['ir.sequence'].next_by_code(
                'project.tickets') or _('New')
        res = super(ProjectTickets, self).create(vals)
        return res

    @api.depends('status')
    def _compute_status(self):
        if self.status == 'draft':
            self.state = 'draft'
        elif self.status == 'in_progress':
            self.state = 'in_progress'
        elif self.status == 'on_hold':
            self.state = 'on_hold'
        elif self.status == 'completed':
            self.state = 'completed'
        elif self.status == 'cancelled':
            self.state = 'cancelled'

    @api.depends('name')
    def _compute_check_same_user(self):
        self.check_same_user_id = self.name.id
        # if self.name == self.env.user:
        #     print('same')
        #     self.check_same_user_id = False
        # else:
        #     self.check_same_user_id = True
        #     print('not same')

    check_same_user_id = fields.Integer(compute='_compute_check_same_user', store=True, string='Check Same User')

    @api.onchange('type')
    def _compute_type(self):

        print('oo')
        self.task_worker_id = self.type.assign_to.id
        self.re_assign_id = self.type.assign_to.id

    def in_progress(self):
        self.message_post(body="Changed State Draft to In Progress")
        self.state = 'in_progress'

    def on_hold(self):
        self.message_post(body="Changed State In Progress to On Hold")

        self.state = 'on_hold'

    def completed(self):
        self.message_post(body="Changed State On Hold to Completed")
        self.state = 'completed'

    def cancelled(self):
        self.message_post(body="Cancelled")
        self.state = 'cancelled'

    reassign_check = fields.Boolean(string='check re')
    re_assign_id = fields.Many2one('res.users', string='Re Assign To')
    done_check = fields.Boolean(string='check done')

    def reassign(self):
        self.reassign_check = True
        self.done_check = True
        self.dd = self.re_assign_id

    @api.onchange('re_assign_id')
    def _compute_reassign(self):
        self.task_worker_id = self.re_assign_id

    dd = fields.Many2one('res.users', string='dd')

    def ensure_one_open_todo(self):
        if self.re_assign_id:
            if self.re_assign_id.id != self.dd.id:
                self.message_post(body="Reeeeee")
            else:
                print('koll')
        # self.task_worker_id = self.re_assign_id
        print('ensure_one_open_todo')

    def done(self):
        ss = self.re_assign_id.name
        message = "Re Assign To: %s" % ss
        if self.re_assign_id:
            if self.re_assign_id.id != self.dd.id:
                self.message_post(body=message)
            else:
                print('koll')
        self.reassign_check = False
        self.done_check = False

    # def write(self, vals):
    #     print('write')
    #     if self.re_assign_id:
    #         self.ensure_one_open_todo()
    #     # if self.re_assign_id:
    #     #     self.task_worker_id = self.re_assign_id
    #     return super(ProjectTickets, self).write(vals)

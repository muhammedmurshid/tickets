from odoo import models, fields, api, _
from datetime import datetime


class ProjectTickets(models.Model):
    _name = 'project.tickets'
    _description = 'Ticket'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'type'

    name = fields.Many2one('res.users', string='Name', default=lambda self: self.env.user, readonly=True)
    reference_no = fields.Char(string="Service Ticket", readonly=True, required=True,
                               copy=False, default='New')
    date = fields.Datetime(string='Date', default=fields.Datetime.now, readonly=True)
    type = fields.Many2one('service.type', string='Type', required=True)
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
        ('draft', 'Draft'), ('sent', 'Ticket Sent'), ('in_progress', 'In Progress'), ('on_hold', 'On Hold'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled')
    ], string='Status', default='draft', compute='_compute_status', store=True)
    status = fields.Selection([
        ('draft', 'Draft'), ('in_progress', 'In Progress'), ('on_hold', 'On Hold'), ('completed', 'Completed'),
        ('cancelled', 'Cancelled')
    ], string='Status', default='draft')
    solution_taken = fields.Text(string='Solution Taken')
    purchase = fields.Boolean(string='Purchase')
    product = fields.Char(string='Product')
    director_id = fields.Many2one('hr.employee', string='Director', domain=[('department_id.name', '=', 'DIRECTORS')])
    purchase_assign_id = fields.Many2one('res.users', string='Assign to')
    product_price = fields.Float(string='Product Price')
    currency_id = fields.Many2one('res.currency', default=lambda self: self.env.user.company_id.currency_id,
                                  string='Currency')

    @api.onchange('purchase_assign_id')
    def get_assign_purchase(self):
        self.task_worker_id = self.purchase_assign_id.id

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

    @api.depends('make_visible_user')
    def get_user(self):
        print('kkkll')
        user_crnt = self.env.user.id

        res_user = self.env['res.users'].search([('id', '=', self.env.user.id)])
        if res_user.has_group('tickets.tickets_worker'):
            self.make_visible_user = False

        else:
            self.make_visible_user = True

    make_visible_user = fields.Boolean(string="User", default=True, compute='get_user')

    def action_confirm(self):
        self.state = 'sent'
        ss = self.env['project.tickets'].search([])
        self.activity_schedule('tickets.mail_activity_type_tickets_id', user_id=self.task_worker_id.id,
                               note=f'Please Check Tickets {self.task_worker_id.name}')
        # current = self.purchase_assign_id

    @api.model
    def create(self, vals):
        ss = self.env['project.tickets'].search([])
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
        ss = self.env['project.tickets'].search([])
        self.message_post(body="Changed State Draft to In Progress")
        self.state = 'in_progress'
        activity_id = self.env['mail.activity'].search([('res_id', '=', self.id), ('user_id', '=', self.env.user.id), (
            'activity_type_id', '=', self.env.ref('tickets.mail_activity_type_tickets_id').id)])
        activity_id.action_feedback(feedback=f'In Progress')
        other_activity_ids = self.env['mail.activity'].search([('res_id', '=', self.id), (
            'activity_type_id', '=', self.env.ref('tickets.mail_activity_type_tickets_id').id)])
        other_activity_ids.unlink()

    def on_hold(self):
        self.message_post(body="Changed State In Progress to On Hold")

        self.state = 'on_hold'

    def completed(self):
        self.message_post(body="Changed State On Hold to Completed")
        self.state = 'completed'
        print('check email')

        main_content = {
            'subject': 'Product Purchased Successfully',
            'body_html': f"<p>Hello {self.director_id.name}, {self.product} purchased successfully...."
                         f"The total price of the product, including all applicable charges, is {self.product_price}</p>",
            'email_to': self.director_id.work_email,
            # 'attachment_ids': attachment

        }
        self.env['mail.mail'].sudo().create(main_content).send()

    @api.depends('current_user_id')
    def get_current_user(self):
        self.current_user_id = self.env.user.id

    current_user_id = fields.Many2one('res.users', compute='get_current_user', string='Current User')

    @api.depends('check_two_users_same')
    def check_two_users_are_same(self):
        if self.current_user_id == self.create_uid:
            self.check_two_users_same = True
        else:
            self.check_two_users_same = False

    check_two_users_same = fields.Boolean(compute='check_two_users_are_same', string='Same User')

    @api.depends('check_worker_users_same', 'task_worker_id')
    def check_workers_are_same(self):
        if self.current_user_id == self.task_worker_id:
            self.check_worker_users_same = True
        else:
            self.check_worker_users_same = False

    check_worker_users_same = fields.Boolean(compute='check_workers_are_same', string='Same User')

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
        activity_id = self.env['mail.activity'].search(
            [('res_id', '=', self.id), ('user_id', '=', self.env.user.id), (
                'activity_type_id', '=', self.env.ref('tickets.mail_activity_type_tickets_id').id)])
        activity_id.action_feedback(feedback=f'In Progress')
        other_activity_ids = self.env['mail.activity'].search([('res_id', '=', self.id), (
            'activity_type_id', '=', self.env.ref('tickets.mail_activity_type_tickets_id').id)])
        other_activity_ids.unlink()

    re_ass_tree_check = fields.Boolean(string='check tree reassign', default=False)

    def admin_due_tickets(self):
        print('hhhi')
        ss = self.env['project.tickets'].search([])
        current_datetime = datetime.now()

        for i in ss:
            if i.dead_line:
                if current_datetime > i.dead_line:
                    if i.state in 'sent' or i.state in 'in_progress':
                        users = ss.env.ref('tickets.tickets_admin').users
                        for rec in users:
                            i.activity_schedule('tickets.mail_activity_type_tickets_id', user_id=rec.id,
                                                note=f'Due Tickets')

            else:
                print('not due')

    @api.onchange('purchase')
    def onchange_purchase_director(self):
        if self.purchase == False:
            self.director_id = False

    def admin_due_tickets_remove(self):
        print('hhhi')
        ss = self.env['project.tickets'].search([])
        current_datetime = datetime.now()

        for i in ss:
            if i.state in 'completed' or i.state in 'cancelled' or i.state in 'on_hold':
                activity_id = self.env['mail.activity'].search(
                    [('res_id', '=', self.id), ('user_id', '=', self.env.user.id), (
                        'activity_type_id', '=', self.env.ref('tickets.mail_activity_type_tickets_id').id)])
                activity_id.action_feedback(feedback=f'In Progress')
                other_activity_ids = self.env['mail.activity'].search([('res_id', '=', self.id), (
                    'activity_type_id', '=', self.env.ref('tickets.mail_activity_type_tickets_id').id)])
                other_activity_ids.unlink()

            else:
                print('not due')

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
                self.re_ass_tree_check = True
                ss = self.env['project.tickets'].search([])
                users = ss.env.ref('tickets.tickets_worker').users
                for j in users:
                    print(j.id, 'ooooo')
                    print(self.task_worker_id.id, 'jjjoop')
                    if self.re_assign_id.id == j.id:
                        self.activity_schedule('tickets.mail_activity_type_tickets_id', user_id=j.id,
                                               note=f'Re Assigned {self.env.user.name}')

                        print(j.name, 'jjjj')
                    else:
                        print('not same')
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


class RemoveRefusedLeaves(models.Model):
    _inherit = 'hr.leave'

    def compute_remove_state(self):
        print('hi leaves')
        # aa = self.env['hr.leave'].search([])
        # for rec in aa:
        #     print(rec.state, 'this state')
        #     if rec.state == 'refused':
        #         rec.unlink()
        #         print(rec.holiday_status_id.name, 'this')
        #     else:
        #         print('not')

    # def action_refuse(self):
    #     self.unlink()




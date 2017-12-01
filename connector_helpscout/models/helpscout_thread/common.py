# -*- coding: utf-8 -*-
# Copyright 2017 LasLabs Inc.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import models, fields
from odoo.addons.component.core import Component


class MailMessage(models.Model):

    _inherit = 'mail.message'

    helpscout_bind_ids = fields.One2many(
        string='HelpScout Bindings',
        comodel_name='helpscout.thread',
        inverse_name='odoo_id',
    )


class HelpScoutThread(models.Model):

    _name = 'helpscout.thread'
    _inherit = 'helpscout.binding'
    _inherits = {'mail.message': 'odoo_id'}
    _description = 'HelpScout Conversation Threads'

    _rec_name = 'record_name'

    helpscout_action_type = fields.Selection(
        selection=[
            ('movedFromMailbox', 'Moved From Mailbox'),
            ('merged', 'Merged'),
            ('imported', 'Imported'),
            ('workflow', 'Workflow'),
            ('importedExternal', 'Imported External'),
            ('changedTicketCustomer', 'Changed Ticket Customer'),
            ('deletedTicket', 'Deleted Ticket'),
            ('restoredTicket', 'Restored Ticket'),
            ('originalCreator', 'Original Creator'),
        ],
    )
    helpscout_action_source = fields.Integer(
        help='ID associated with HelpScout Action Type.',
    )
    helpscout_from_mailbox = fields.Integer(
        help='If the conversation was moved, this represents the Mailbox from '
             'which it was moved.',
    )
    helpscout_date_opened = fields.Datetime(
        help='Date that thread was viewed by the customer.',
    )
    helpscout_type = fields.Selection(
        selection=[
            ('lineitem', 'Line Item'),
            ('note', 'Note'),
            ('message', 'Message'),
            ('chat', 'Chat'),
            ('customer', 'Customer'),
            ('forwardparent', 'Forward Parent'),
            ('forwardchild', 'Forward Child'),
            ('phone', 'Phone'),
        ],
    )
    helpscout_saved_reply_id = fields.Integer(
        help='ID of Saved reply that was used to create this Thread.',
    )
    helpscout_source_person_type = fields.Selection(
        selection=[
            ('customer', 'Customer'),
            ('user', 'User'),
        ],
        help='The person type by whom this thread was created.',
    )
    helpscout_source_type = fields.Selection(
        selection=[
            ('email', 'Email'),
            ('web', 'Web'),
            ('notification', 'Notification'),
            ('emailfwd', 'Email Forward'),
            ('api', 'API'),
            ('chat', 'Chat'),
        ],
        help='The method from which this thread was created.',
    )
    helpscout_state = fields.Selection(
        selection=[
            ('published', 'Published'),
            ('draft', 'Draft'),
            ('underreview', 'Under Review'),
            ('hidden', 'Hidden'),
        ],
    )
    helpscout_to = fields.Char(
        string='HelpScout Email To',
        help='Email addresses in the "to" field of the thread email.',
    )
    odoo_id = fields.Many2one(
        string='Message',
        comodel_name='mail.message',
        required=True,
        ondelete='cascade',
    )


class HelpScoutThreadAdapter(Component):
    """Utilize the API in context."""
    _name = 'helpscout.thread.adapter'
    _inherit = 'helpscout.adapter'
    _apply_on = 'helpscout.thread'
    _helpscout_endpoint = 'Conversations'

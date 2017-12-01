# -*- coding: utf-8 -*-
# Copyright 2017 LasLabs Inc.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import models, fields
from odoo.addons.component.core import Component


class ProjectTask(models.Model):

    _inherit = 'project.task'

    helpscout_bind_ids = fields.One2many(
        string='HelpScout Bindings',
        comodel_name='helpscout.conversation',
        inverse_name='odoo_id',
    )


class HelpScoutConversation(models.Model):

    _name = 'helpscout.conversation'
    _inherit = 'helpscout.binding'
    _inherits = {'project.task': 'odoo_id'}
    _description = 'HelpScout Conversations'

    _rec_name = 'name'

    helpscout_folder_id = fields.Many2one(
        string='HelpScout Mailbox Folder',
        comodel_name='helpscout.helpscout.folder',
        ondelete='set null',
    )
    helpscout_type = fields.Selection(
        selection=[
            ('email', 'Email'),
            ('chat', 'Chat'),
            ('phone', 'Phone'),
        ],
    )
    odoo_id = fields.Many2one(
        string='Task',
        comodel_name='project.task',
        required=True,
        ondelete='cascade',
    )


class HelpScoutConversationAdapter(Component):
    """Utilize the API in context."""
    _name = 'helpscout.conversation.adapter'
    _inherit = 'helpscout.adapter'
    _apply_on = 'helpscout.conversation'
    _helpscout_endpoint = 'Conversations'

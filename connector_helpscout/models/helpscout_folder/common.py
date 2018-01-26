# -*- coding: utf-8 -*-
# Copyright 2017 LasLabs Inc.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import models, fields
from odoo.addons.component.core import Component


class HelpScoutFolder(models.Model):
    _name = 'helpscout.folder'
    _description = 'HelpScout Mailbox Folders'

    helpscout_bind_ids = fields.One2many(
        string='HelpScout Bindings',
        comodel_name='helpscout.helpscout.folder',
        inverse_name='odoo_id',
    )
    helpscout_type = fields.Selection(
        selection=[
            ('assigned', 'Assigned'),
            ('closed', 'Closed'),
            ('drafts', 'Drafts'),
            ('mine', 'Mine'),
            ('needsattention', 'Needs Attention'),
            ('open', 'Open'),
            ('spam', 'Spam'),
            ('team', 'Team'),
        ],
    )
    name = fields.Char(
        string='HelpScout Folder Name',
        required=True,
    )


class HelpScoutHelpScoutFolder(models.Model):

    _name = 'helpscout.helpscout.folder'
    _inherit = 'helpscout.binding'
    _inherits = {'helpscout.folder': 'odoo_id'}
    _description = 'HelpScout HelpScoutFolders'

    _rec_name = 'name'

    helpscout_conversation_ids = fields.One2many(
        string='HelpScout Conversations',
        comodel_name='helpscout.conversation',
        inverse_name='helpscout_folder_id',
    )
    helpscout_mailbox_id = fields.Many2one(
        string='HelpScout Mailbox',
        comodel_name='helpscout.mailbox',
        ondelete='cascade',
    )
    odoo_id = fields.Many2one(
        string='HelpScout Folder',
        comodel_name='helpscout.folder',
        required=True,
        ondelete='cascade',
    )


class HelpScoutFolderAdapter(Component):
    """Utilize the API in context."""
    _name = 'helpscout.helpscout.folder.adapter'
    _inherit = 'helpscout.adapter'
    _apply_on = 'helpscout.helpscout.folder'
    _helpscout_endpoint = 'Mailboxes'

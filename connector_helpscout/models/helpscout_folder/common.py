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

    external_id = fields.Char(
        string='HelpScout Mailbox ID, Folder ID',
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

    def search_read(self, mailbox_id):
        """Gets and returns all folder objects associated with the provided
        mailbox_id"""
        return self.endpoint.get_folders(mailbox_id)

    def search(self, filters=None):
        """Returns IDs from list of objects returned by search_read"""
        mailbox_id = filters.get('mailbox_id')
        return [
            "%d,%d" % (mailbox_id, r.id)
            for r
            in self.search_read(mailbox_id)
        ]

    def read(self, _id):
        """Iterates over list of folder objects associated with mailbox_id,
        returns folder object matching provided folder id"""
        mailbox_id, folder_id = [int(n) for n in _id.split(',')]
        for r in self.search_read(mailbox_id):
            if r.id == folder_id:
                return r

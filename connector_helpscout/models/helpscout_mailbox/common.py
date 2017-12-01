# -*- coding: utf-8 -*-
# Copyright 2017 LasLabs Inc.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import models, fields
from odoo.addons.component.core import Component


class Project(models.Model):

    _inherit = 'project.project'

    helpscout_bind_ids = fields.One2many(
        string='HelpScout Bindings',
        comodel_name='helpscout.mailbox',
        inverse_name='odoo_id',
    )


class HelpScoutMailbox(models.Model):

    _name = 'helpscout.mailbox'
    _inherit = 'helpscout.binding'
    _inherits = {'project.project': 'odoo_id'}
    _description = 'HelpScout Mailboxes'

    _rec_name = 'name'

    helpscout_email = fields.Char(string="HelpScout mailbox email address")
    helpscout_folder_ids = fields.One2many(
        string='HelpScout Folders',
        comodel_name='helpscout.helpscout.folder',
        inverse_name='helpscout_mailbox_id',
    )
    odoo_id = fields.Many2one(
        string='Project',
        comodel_name='project.project',
        required=True,
        ondelete='cascade',
    )


class HelpScoutMailboxAdapter(Component):
    """Utilize the API in context."""
    _name = 'helpscout.mailbox.adapter'
    _inherit = 'helpscout.adapter'
    _apply_on = 'helpscout.mailbox'
    _helpscout_endpoint = 'Mailboxes'

    def search(self, filters=None):
        """Return entire mailbox list"""
        return [r.id for r in self.endpoint.list()]

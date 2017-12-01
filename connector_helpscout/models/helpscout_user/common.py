# -*- coding: utf-8 -*-
# Copyright 2017 LasLabs Inc.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import models, fields
from odoo.addons.component.core import Component


class ResUsers(models.Model):

    _inherit = 'res.users'

    helpscout_bind_ids = fields.One2many(
        string='HelpScout Bindings',
        comodel_name='helpscout.user',
        inverse_name='odoo_id',
    )


class HelpScoutUser(models.Model):

    _name = 'helpscout.user'
    _inherit = 'helpscout.binding'
    _inherits = {'res.users': 'odoo_id'}
    _description = 'HelpScout Users'

    _rec_name = 'name'

    helpscout_type = fields.Selection(
        selection=[
            ('user', 'User'),
            ('team', 'Team'),
        ],
    )
    odoo_id = fields.Many2one(
        string='User',
        comodel_name='res.users',
        required=True,
        ondelete='cascade',
    )


class HelpScoutUserAdapter(Component):
    """Utilize the API in context."""
    _name = 'helpscout.user.adapter'
    _inherit = 'helpscout.adapter'
    _apply_on = 'helpscout.user'
    _helpscout_endpoint = 'Users'

    def search(self, filters=None):
        """Return entire user list (there is no search endpoint for Users)"""
        return [r.id for r in self.endpoint.list()]

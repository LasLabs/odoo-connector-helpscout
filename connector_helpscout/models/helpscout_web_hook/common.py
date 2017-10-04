# -*- coding: utf-8 -*-
# Copyright 2017 LasLabs Inc.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

import logging

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


_logger = logging.getLogger(__name__)


class HelpScoutWebHook(models.Model):

    _name = 'helpscout.web.hook'
    _description = 'HelpScout Web Hook'
    _inherit = 'connector.backend'

    backend_id = fields.Many2one(
        string='Backend',
        comodel_name='helpscout.backend',
        required=True,
    )
    website_ids = fields.Many2many(
        string='Websites',
        required=True,
        default=lambda s: [
            (6, 0, s.env['website'].get_current_website().ids),
        ],
        help='The websites that should accept hooks for this hook. Note '
             'that a website can only be assigned to one hook at a '
             'time.',
    )
    secret_key = fields.Char(
        required=True,
        help='This is the secret key that is configured in your HelpScout '
             'account while setting up the web hook.',
    )

    @api.multi
    @api.constrains('website_ids')
    def _check_website_ids(self):
        """Do not allow two backends for the same website."""
        for record in self:
            results = self.search([
                ('website_ids', 'in', record.website_ids.ids),
            ])
            if len(results) > 1:
                raise ValidationError(_(
                    'You cannot assign two websites to the same web hook.',
                ))

    @api.model
    def receive(self, event):
        pass

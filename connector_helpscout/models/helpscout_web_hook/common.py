# -*- coding: utf-8 -*-
# Copyright 2017 LasLabs Inc.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

import logging

from odoo import models, fields, api, _

_logger = logging.getLogger(__name__)

try:
    from helpscout import HelpScoutWebHook
    from helpscout.web_hook.web_hook_event import WebHookEvent
except ImportError:
    _logger.info('`helpscout` Python library is not installed.')


class HelpScoutWebHook(models.Model):

    _name = 'helpscout.web.hook'
    _description = 'HelpScout Web Hook'
    _inherit = 'web.hook.adapter'

    # Use this to map Helpscout.model objects to Odoo binding models
    HOOK_MAPS = {
        'Customer': 'helpscout.customer',
    }

    backend_id = fields.Many2one(
        string='Backend',
        comodel_name='helpscout.backend',
        required=True,
    )

    @property
    @api.multi
    def hook_object(self):
        return HelpScoutWebHook(secret_key=self.secret)

    @api.multi
    def receive(self, data, headers):
        """Receive and process the web hook.

        Args:
            data (dict): Data that was received with the hook.
            headers (dict): Headers that were received with the request.

        Returns:
            mixed: A JSON serializable return, or ``None``.
        """
        self.ensure_one()
        hook = WebHookEvent(
            event_type=headers.get('X-HelpScout-Event'),
            record=data,
        )
        model_name = self.HOOK_MAPS[self.hook.record.__class__.__name__]
        odoo_model = self.env[model_name]
        return odoo_model.import_direct(
            backend=self.backend_id, external_record=hook.record,
        )

    @api.multi
    def extract_token(self, data, headers):
        return headers.get('X-HelpScout-Signature', '')


class HelpScoutWebHookToken(models.Model):

    _name = 'helpscout.web.hook.token'
    _description = 'Web Hook Token - HelpScout'
    _inherit = 'web.hook.token.adapter'

    @api.multi
    def validate(self, secret, data, data_string, headers):
        return self.hook_id.hook_object.validate_signature(
            secret, data_string,
        )

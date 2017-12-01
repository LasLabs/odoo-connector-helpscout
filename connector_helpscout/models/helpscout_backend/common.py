# -*- coding: utf-8 -*-
# Copyright 2017 LasLabs Inc.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

import logging

from contextlib import contextmanager

from datetime import datetime
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

from odoo.addons.connector.checkpoint import checkpoint
from ...components.backend_adapter import HelpScoutApi, HelpScoutHook


_logger = logging.getLogger(__name__)


class HelpscoutBackend(models.Model):

    _name = 'helpscout.backend'
    _description = 'HelpScout Backend'
    _inherit = 'connector.backend'

    EVENT_TO_MODEL = {
        'customer': 'helpscout.customer',
        'satisfaction': 'helpscout.rating',
        'convo': 'helpscout.conversation',
    }

    version = fields.Selection(
        selection='_get_versions',
        default='v1',
        required=True,
    )
    api_key = fields.Char(
        required=True,
    )
    company_id = fields.Many2one(
        string='Company',
        comodel_name='res.company',
        required=True,
        default=lambda s: s.env.user.company_id.id,
    )
    web_hook_id = fields.Many2one(
        string='Web Hook',
        comodel_name='helpscout.web.hook',
        readonly=True,
        help='The web hook that is associated with this backend.',
    )
    is_default_export = fields.Boolean(
        string='Default Exporter?',
        help='Check to indicate this is the default HelpScout connector '
             'that should be used for exporting records created in Odoo for '
             'this company, that are not otherwise assigned to a HelpScout '
             'backend.',
    )
    user_match_field = fields.Selection(
        selection=[
            ('email', 'Email'),
            ('login', 'Login'),
        ],
        required=True,
        default='email',
        string='User Match Field',
        help='Select which Odoo user field to use when matching imported '
             'Helpscout users to existing Odoo users. This field will be '
             'matched against the Helpscout user\'s email address.'
    )

    @property
    @api.model
    def default_exporter(self):
        """Return the default exporter for the current company."""
        return self.search([
            ('company_id', '=', self.env.user.company_id.id),
            ('is_default_export', '=', True),
        ])

    @api.model
    def _get_versions(self):
        """Available versions for this backend."""
        return [('v1', 'v1')]

    @api.multi
    @api.constrains('company_id', 'is_default_export')
    def _check_company_id_is_default_export(self):
        """Only allow one default exporter per company."""
        for record in self.filtered(lambda r: r.is_default_export):
            domain = [
                ('company_id', '=', record.company_id.id),
                ('is_default_export', '=', True),
            ]
            if len(self.search(domain)) > 1:
                raise ValidationError(_(
                    'You cannot have two default HelpScout exporters for the '
                    'same company.',
                ))

    @api.multi
    @contextmanager
    def work_on(self, model_name, **kwargs):
        """Context manager providing a usable API for external access.

        Yields:
            odoo.addons.component.core.WorkContext: The worker context for
                this backend record. The ``HelpScout`` object is exposed on
                the ``helpscout_api`` attribute of this context.
        """
        self.ensure_one()
        helpscout_api = HelpScoutApi(self.api_key)
        # From the components, we can do ``self.work.helpscout_api``
        with super(HelpscoutBackend, self).work_on(
            model_name, helpscout_api=helpscout_api, **kwargs
        ) as work:
            yield work

    @api.multi
    def add_checkpoint(self, record):
        self.ensure_one()
        record.ensure_one()
        return checkpoint.add_checkpoint(
            self.env, record._name, record.id, self._name, self.id,
        )

    @api.multi
    def action_initial_import(self):
        """
        Import external conversation records. Records for other models are
        imported as dependencies of conversations.
        """
        from_date = datetime(2011, 4, 17)  # HelpScout founding date
        for backend in self:
            self.env['helpscout.conversation'].with_delay().import_batch(
                backend,
                filters=[
                    ('modified_at', from_date, datetime.now()),
                ],
            )

    @api.multi
    def action_create_web_hook(self):
        """Create the web hook necessary for inbound sync & unlink existing."""
        for record in self:
            values = record._get_hook_values()
            if record.web_hook_id:
                record.web_hook_id.write(values)
            else:
                hook = self.env['helpscout.web.hook'].create(values)
                record.web_hook_id = hook.id

    @api.multi
    def _get_hook_values(self):
        """Return the values for creating/updating a hook."""
        self.ensure_one()
        secret = self.env['web.hook']._default_secret(40)
        name = '%s [%s]' % (self.name, self.company_id.name)
        values = {
            'interface_type': 'helpscout.web.hook',
            'token_type': 'helpscout.web.hook.token',
            'token_secret': secret,
            'backend_id': self.id,
            'name': name,
        }
        return values

    @api.multi
    def action_receive_hook(self, event_type, signature, data_str):
        """Process an inbound hook and queue an import of the provided record.

        Args:
            event_type (str): Name of the event that was received (from the
                request ``X-HelpScout-Event`` header).
            signature (str): The signature that was received, which serves as
                authentication (from the request ``X-HelpScout-Signature``
                header).
            data_str (str): The raw data that was posted by HelpScout
                to the web hook. This must be the raw string, because if it
                is parsed with JSON it will lose its ordering and not pass
                signature validation.

        Raises:
            helpscout.exceptions.HelpScoutSecurityException: If an invalid
                signature is provided, and ``raise_if_invalid`` is ``True``.
        """
        self.ensure_one()
        hook = HelpScoutHook(self.web_hook_id.secret_key)
        hook_event = hook.receive(event_type, signature, data_str)
        event_model, _ = event_type.split('.', 1)
        helpscout_model = self.EVENT_TO_MODEL[event_model]
        return self.env[helpscout_model].with_delay().import_direct(
            self, hook_event.record,
        )

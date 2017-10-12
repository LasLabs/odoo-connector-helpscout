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
        comodel_name='web.hook',
        help='Set this to enable web hooks for this backend.',
    )
    is_default_export = fields.Boolean(
        string='Default Exporter?',
        help='Check to indicate this is the default HelpScout connector '
             'that should be used for exporting records created in Odoo for '
             'this company, that are not otherwise assigned to a HelpScout '
             'backend.',
    )

    # These dates are used by the import crons to start where left off.
    import_customers_from_date = fields.Datetime()
    import_mailboxes_from_date = fields.Datetime()

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
    def import_from_date(self, model_name, from_date_field):
        """Import external records for a model from a date.

        Args:
            model_name (str): Name of model to import for.
            from_date_field (str): Name of the field on the backend that
                contains the last time this model was synced (e.g.
                ``import_customers_from_date`` for Customers).
        """

        import_start_time = datetime.now()

        for backend in self:

            from_date = backend[from_date_field]
            if from_date:
                from_date = fields.Datetime.from_string(from_date)
            else:
                # Hard-code to HelpScout founding date
                from_date = datetime(2011, 4, 17)

            self.env[model_name].with_delay().import_batch(
                backend,
                filters=[
                    ('modified_at', from_date, import_start_time),
                ],
            )

        self.write({
            from_date_field: fields.Datetime.to_string(import_start_time),
        })

    @api.model
    def get_for_website(self, website):
        """Return the backend that implements hooks for this website."""
        return self.search([('web_hook_id.website_ids', '=', website.id)])

    # Import actions
    @api.multi
    def action_import_mailboxes(self):
        """Trigger an import for mailboxes on the appropriate from field."""
        self.import_from_date('helpscout.mailbox',
                              'import_mailboxes_from_date')

    @api.multi
    def action_import_customers(self):
        """Trigger an import for customers on the appropriate from field."""
        self.import_from_date('helpscout.customer',
                              'import_customers_from_date')

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

# -*- coding: utf-8 -*-
# Copyright 2017 LasLabs Inc.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

import logging

from odoo.addons.component.core import Component
from odoo.addons.connector.components.mapper import mapping, none

_logger = logging.getLogger(__name__)

try:
    from helpscout.models.web_hook_event import EVENT_CHOICES
except ImportError:
    _logger.info('`helpscout` Python library is not installed.')


class HelpScoutWebHookExportMapper(Component):

    _name = 'helpscout.export.mapper.web.hook'
    _inherit = 'helpscout.export.mapper'
    _apply_on = 'helpscout.web.hook'

    direct = [(none('uri_json'), 'url'),
              (none('token_secret'), 'secret_key'),
              ]

    @mapping
    def events(self, _):
        """Subscribe to all events."""
        return {'events': EVENT_CHOICES.keys()}


class HelpScoutWebHookExporter(Component):
    """Export one HelpScout record."""
    _name = 'helpscout.web.hook.record.exporter'
    _inherit = 'helpscout.exporter'
    _apply_on = 'helpscout.web.hook'

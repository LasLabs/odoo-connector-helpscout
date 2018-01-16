# -*- coding: utf-8 -*-
# Copyright 2017 LasLabs Inc.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

import logging
import urllib2

from odoo.addons.component.core import Component
from odoo.addons.connector.components.mapper import mapping, none, only_create

_logger = logging.getLogger(__name__)


class HelpScoutUserImportMapper(Component):
    _name = 'helpscout.import.mapper.user'
    _inherit = 'helpscout.import.mapper'
    _apply_on = 'helpscout.user'

    direct = [(none('first_name'), 'firstname'),
              (none('last_name'), 'lastname'),
              ('email', 'login'),
              ('email', 'email'),
              (none('timezone'), 'tz'),
              (none('type'), 'helpscout_type'),
              ]

    @mapping
    @only_create
    def odoo_id(self, record):
        # Searches res.users records for matching email address,
        # excluding non-internal-users (e.g. customer users)
        user = self.env['res.users'].search([
            (self.backend_record.user_match_field, '=', record.email),
            ('share', '=', False),
        ])
        if user:
            return {'odoo_id': user.id}

    @mapping
    def photo_url(self, record):
        try:
            image = urllib2.urlopen(record.photo_url).read().encode('base64')
            return {'image': image}
        except Exception:
            _logger.debug('HelpScout photo not imported')
            return

    @mapping
    def role(self, record):
        group_xml_id = "connector_helpscout.group_helpscout_%s" % record.role
        helpscout_group = self.env.ref(group_xml_id)
        return {'groups_id': [(6, 0, [helpscout_group.id])]}


class HelpScoutUserImporter(Component):
    """Import one HelpScout record."""
    _name = 'helpscout.record.importer.user'
    _inherit = 'helpscout.importer'
    _apply_on = 'helpscout.user'

    def _must_skip(self):
        """Skip records incompatible with Odoo user model."""
        if self.helpscout_record.type == 'team':
            return "Skipping import of Helpscout Team record."
        if not self.helpscout_record.email:
            return "Skipping import of Helpscout User without email address."

        return


class HelpScoutUserBatchImporter(Component):
    """Import a batch of HelpScout records."""
    _name = 'helpscout.batch.importer.user'
    _inherit = 'helpscout.direct.batch.importer'
    _apply_on = 'helpscout.user'

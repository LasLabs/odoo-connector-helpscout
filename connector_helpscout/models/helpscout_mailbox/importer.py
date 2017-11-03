# -*- coding: utf-8 -*-
# Copyright 2017 LasLabs Inc.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.addons.component.core import Component
from odoo.addons.connector.components.mapper import mapping, none, only_create


class HelpScoutMailboxImportMapper(Component):
    _name = 'helpscout.import.mapper.mailbox'
    _inherit = 'helpscout.import.mapper'
    _apply_on = 'helpscout.mailbox'

    direct = [('name', 'name'),
              (none('email'), 'helpscout_email'),
              ('created_at', 'backend_date_created'),
              ('modified_at', 'backend_date_modified'),
              ]

    @mapping
    @only_create
    def odoo_id(self, record):
        # Searches project.project records for matching name
        project = self.env['project.project'].search([
            ('name', '=', record.name),
        ])
        if project:
            return {'odoo_id': project.id}


class HelpScoutMailboxImporter(Component):
    """Import one HelpScout record."""
    _name = 'helpscout.record.importer.mailbox'
    _inherit = 'helpscout.importer'
    _apply_on = 'helpscout.mailbox'


class HelpScoutMailboxBatchImporter(Component):
    """Import a batch of HelpScout records."""
    _name = 'helpscout.batch.importer.mailbox'
    _inherit = 'helpscout.direct.batch.importer'
    _apply_on = 'helpscout.mailbox'

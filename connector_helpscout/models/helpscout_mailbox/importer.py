# -*- coding: utf-8 -*-
# Copyright 2017 LasLabs Inc.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.addons.component.core import Component
from odoo.addons.connector.components.mapper import mapping, none, only_create


class HelpScoutMailboxImportMapper(Component):
    _name = 'helpscout.import.mapper.mailbox'
    _inherit = 'helpscout.import.mapper'
    _apply_on = 'helpscout.mailbox'

    HELPSCOUT_STATUSES = [
        'active',
        'pending',
        'closed',
        'spam',
    ]

    direct = [('name', 'name'),
              (none('email'), 'helpscout_email'),
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

    def _after_import(self, binding):
        self._add_project_stages(binding)
        self._import_folders(binding)

    def _add_project_stages(self, binding):
        stages = self.env['project.task.type']
        for status in self.HELPSCOUT_STATUSES:
            stages += self.env.ref('connector_helpscout.status_%s' % status)
        binding.type_ids = [(6, 0, stages.ids)]

    def _import_folders(self, binding):
        binding_model = self.env['helpscout.helpscout.folder']
        folders = binding_model
        for folder in self.helpscout_record['folders']:
            folders += binding_model.import_direct(self.backend_record, folder)
        binding.helpscout_folder_ids = [(6, 0, folders.ids)]


class HelpScoutMailboxBatchImporter(Component):
    """Import a batch of HelpScout records."""
    _name = 'helpscout.batch.importer.mailbox'
    _inherit = 'helpscout.direct.batch.importer'
    _apply_on = 'helpscout.mailbox'

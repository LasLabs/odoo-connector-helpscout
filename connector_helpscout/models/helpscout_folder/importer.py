# -*- coding: utf-8 -*-
# Copyright 2017 LasLabs Inc.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.addons.component.core import Component
from odoo.addons.connector.components.mapper import (mapping,
                                                     only_create,
                                                     )


class HelpScoutFolderImportMapper(Component):
    _name = 'helpscout.import.mapper.folder'
    _inherit = 'helpscout.import.mapper'
    _apply_on = 'helpscout.helpscout.folder'

    direct = [('type', 'helpscout_type')]

    def _get_user_name(self, user_id):
        user = self.env['helpscout.user'].search([
            ('external_id', '=', user_id),
        ]).odoo_id
        return user.name

    def _internal_name(self, record):
        if record.type == 'mine':
            user_name = self._get_user_name(record.user_id)
            return '%s (%s)' % (record.name, user_name)
        return record.name

    @mapping
    @only_create
    def odoo_id(self, record):
        """Searches helpscout.folder records for matching name"""
        folder = self.env['helpscout.folder'].search([
            ('name', '=', self._internal_name(record)),
        ])
        if folder:
            return {'odoo_id': folder.id}

    @mapping
    def name(self, record):
        return {'name': self._internal_name(record)}


class HelpScoutFolderImporter(Component):
    """Import one HelpScout record."""
    _name = 'helpscout.record.importer.folder'
    _inherit = 'helpscout.importer'
    _apply_on = 'helpscout.helpscout.folder'

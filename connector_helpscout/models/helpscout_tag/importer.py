# -*- coding: utf-8 -*-
# Copyright 2017 LasLabs Inc.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.addons.component.core import Component
from odoo.addons.connector.components.mapper import mapping, only_create


tag_color_map = {
    (211, 211, 211): 0,  # lightgrey
    (0, 128, 0): 1,  # green
    (255, 255, 0): 2,  # yellow
    (255, 0, 0): 4,  # red
    (128, 0, 128): 5,  # purple
    (0, 0, 255): 6,  # blue
}


class HelpScoutTagImportMapper(Component):
    _name = 'helpscout.import.mapper.tag'
    _inherit = 'helpscout.import.mapper'
    _apply_on = 'helpscout.tag'

    direct = [('tag', 'name'),
              ('slug', 'helpscout_slug'),
              ]

    @mapping
    @only_create
    def odoo_id(self, record):
        # Searches project.tags records for matching name
        tag = self.env['project.tags'].search([
            ('name', '=', record.tag)
        ], limit=1)
        if tag:
            return {'odoo_id': tag.id}

    @mapping
    def color(self, record):
        """Maps RGB tuple to Odoo Color Index"""
        try:
            color_index = tag_color_map[record.color]
            return {'color': color_index}
        except KeyError:
            return


class HelpScoutTagImporter(Component):
    """Import one HelpScout record."""
    _name = 'helpscout.record.importer.tag'
    _inherit = 'helpscout.importer'
    _apply_on = 'helpscout.tag'


class HelpScoutTagBatchImporter(Component):
    """Import a batch of HelpScout records."""
    _name = 'helpscout.batch.importer.tag'
    _inherit = 'helpscout.direct.batch.importer'
    _apply_on = 'helpscout.tag'

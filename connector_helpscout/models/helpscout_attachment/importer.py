# -*- coding: utf-8 -*-
# Copyright 2017 LasLabs Inc.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.addons.component.core import Component
from odoo.addons.connector.components.mapper import (mapping,
                                                     only_create,
                                                     )


class HelpScoutAttachmentImportMapper(Component):
    _name = 'helpscout.import.mapper.attachment'
    _inherit = 'helpscout.import.mapper'
    _apply_on = 'helpscout.attachment'

    direct = [('file_name', 'datas_fname'),
              ('file_name', 'name'),
              ('mime_type', 'mimetype'),
              ('url', 'url'),
              ('hash', 'helpscout_hash'),
              ('height', 'helpscout_height'),
              ('size', 'helpscout_file_size'),
              ('width', 'helpscout_width'),
              ]

    @mapping
    @only_create
    def odoo_id(self, record):
        attachment = self.env['ir.attachment'].search([
            ('url', '=', record.url),
            ('res_id', '=', record.res_id),
            ('res_model', '=', record.res_model),
        ])

        if attachment:
            return {'odoo_id': attachment.id}

    @mapping
    def res_id(self, record):
        return {'res_id': record.res_id}

    @mapping
    def res_model(self, record):
        return {'res_model': record.res_model}

    @mapping
    def type(self, record):
        return {'type': 'url'}


class HelpScoutAttachmentImporter(Component):
    """Import one HelpScout record."""
    _name = 'helpscout.record.importer.attachment'
    _inherit = 'helpscout.importer'
    _apply_on = 'helpscout.attachment'

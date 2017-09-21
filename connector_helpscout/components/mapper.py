# -*- coding: utf-8 -*-
# Copyright 2017 LasLabs Inc.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.addons.component.core import AbstractComponent
from odoo.addons.connector.components.mapper import mapping, only_create


class HelpScoutImportMapper(AbstractComponent):
    _name = 'helpscout.import.mapper'
    _inherit = ['base.helpscout.connector', 'base.import.mapper']
    _usage = 'import.mapper'

    @mapping
    @only_create
    def external_id(self, record):
        return {'external_id': record.id}

    @mapping
    @only_create
    def backend_date_created(self, record):
        return {'backend_date_created': record.get('created_at')}

    @mapping
    def backend_date_modified(self, record):
        return {'backend_date_modified': record.get('modified_at')}

    @mapping
    @only_create
    def backend_id(self, _):
        return {'backend_id': self.backend_record.id}


class HelpScoutExportMapper(AbstractComponent):
    _name = 'helpscout.export.mapper'
    _inherit = ['base.helpscout.connector', 'base.export.mapper']
    _usage = 'export.mapper'

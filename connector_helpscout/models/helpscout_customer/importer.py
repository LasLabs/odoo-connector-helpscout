# -*- coding: utf-8 -*-
# Copyright 2017 LasLabs Inc.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.addons.component.core import Component
from odoo.addons.connector.components.mapper import mapping, none


class HelpScoutCustomerImportMapper(Component):
    _name = 'helpscout.import.mapper.customer'
    _inherit = 'helpscout.import.mapper'
    _apply_on = 'helpscout.customer'

    direct = [(none('first_name'), 'firstname'),
              (none('last_name'), 'lastname'),
              (none('background'), 'comment'),
              (none('job_title'), 'title'),
              ('created_at', 'backend_date_created'),
              ('modified_at', 'backend_date_modified'),
              ]

    @mapping
    def email(self, record):
        try:
            return {'email': record.emails[0].value}
        except IndexError:
            return

    @mapping
    def phones(self, record):
        phones = {}
        for phone in record.phones:
            if phone.location in ['fax', 'mobile']:
                phones[phone.location] = phone.value
            else:
                phones['phone'] = phone.value
        return phones

    @mapping
    def website(self, record):
        try:
            return {'website': record.websites[0].value}
        except IndexError:
            return


class HelpScoutCustomerImporter(Component):
    """Import one HelpScout record."""
    _name = 'helpscout.record.importer.customer'
    _inherit = 'helpscout.importer'
    _apply_on = 'helpscout.customer'


class HelpScoutCustomerBatchImporter(Component):
    """Import a batch of HelpScout records."""
    _name = 'helpscout.batch.importer.customer'
    _inherit = 'helpscout.direct.batch.importer'
    _apply_on = 'helpscout.customer'

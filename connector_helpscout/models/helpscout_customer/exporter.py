# -*- coding: utf-8 -*-
# Copyright 2017 LasLabs Inc.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.addons.component.core import Component
from odoo.addons.connector.components.mapper import mapping, none


class HelpScoutCustomerExportMapper(Component):

    _name = 'helpscout.export.mapper.customer'
    _inherit = 'helpscout.export.mapper'
    _apply_on = 'helpscout.customer'

    direct = [(none('firstname'), 'first_name'),
              (none('lastname'), 'last_name'),
              (none('comment'), 'background'),
              (none('function'), 'job_title'),
              ]

    @mapping
    def emails(self, record):
        if record.email:
            return {'emails': [{'value': record.email}]}

    @mapping
    def phones(self, record):
        phone_map = {
            'phone': 'home',
            'mobile': 'mobile',
            'fax': 'fax',
        }
        phones = []
        for odoo_type, helpscout_type in phone_map.items():
            if record[odoo_type]:
                phones.append({
                    'value': record[odoo_type],
                    'location': helpscout_type,
                })
        if phones:
            return {'phones': phones}

    @mapping
    def websites(self, record):
        if record.website:
            return {'websites': [{'value': record.website}]}


class HelpScoutCustomerExporter(Component):
    """Export one HelpScout record."""
    _name = 'helpscout.customer.record.exporter'
    _inherit = 'helpscout.exporter'
    _apply_on = 'helpscout.customer'

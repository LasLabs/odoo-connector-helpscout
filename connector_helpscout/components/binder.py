# -*- coding: utf-8 -*-
# Copyright 2017 LasLabs Inc.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.addons.component.core import Component


class HelpScoutModelBinder(Component):
    """Bind records and give odoo/helpscout ID relations."""

    _name = 'helpscout.binder'
    _inherit = ['base.binder', 'base.helpscout.connector']
    _apply_on = [
        'helpscout.customer',
        'helpscout.user',
    ]

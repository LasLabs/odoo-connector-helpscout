# -*- coding: utf-8 -*-
# Copyright 2017 LasLabs Inc.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.addons.component.core import AbstractComponent


class BaseHelpScoutConnectorComponent(AbstractComponent):

    _name = 'base.helpscout.connector'
    _inherit = 'base.connector'
    _collection = 'helpscout.backend'

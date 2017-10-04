# -*- coding: utf-8 -*-
# Copyright 2017 LasLabs Inc.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import models, fields
from odoo.addons.component.core import Component


class ResPartner(models.Model):

    _inherit = 'res.partner'

    helpscout_bind_ids = fields.One2many(
        string='HelpScout Bindings',
        comodel_name='helpscout.customer',
        inverse_name='odoo_id',
    )


class HelpScoutCustomer(models.Model):

    _name = 'helpscout.customer'
    _inherit = 'helpscout.binding'
    _inherits = {'res.partner': 'odoo_id'}
    _description = 'HelpScout Customers'

    _rec_name = 'name'

    odoo_id = fields.Many2one(
        string='Partner',
        comodel_name='res.partner',
        required=True,
        ondelete='cascade',
    )


class HelpScoutCustomerAdapter(Component):
    """Utilize the API in context."""
    _name = 'helpscout.customer.adapter'
    _inherit = 'helpscout.adapter'
    _apply_on = 'helpscout.customer'
    _helpscout_endpoint = 'Customers'

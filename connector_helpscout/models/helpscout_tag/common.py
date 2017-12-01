# -*- coding: utf-8 -*-
# Copyright 2017 LasLabs Inc.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import models, fields
from odoo.addons.component.core import Component


class ProjectTags(models.Model):

    _inherit = 'project.tags'

    helpscout_bind_ids = fields.One2many(
        string='HelpScout Bindings',
        comodel_name='helpscout.tag',
        inverse_name='odoo_id',
    )


class HelpScoutTag(models.Model):

    _name = 'helpscout.tag'
    _inherit = 'helpscout.binding'
    _inherits = {'project.tags': 'odoo_id'}
    _description = 'HelpScout Tags'

    _rec_name = 'name'

    helpscout_slug = fields.Char()
    odoo_id = fields.Many2one(
        string='Tag',
        comodel_name='project.tags',
        required=True,
        ondelete='cascade',
    )


class HelpScoutTagAdapter(Component):
    """Utilize the API in context."""
    _name = 'helpscout.tag.adapter'
    _inherit = 'helpscout.adapter'
    _apply_on = 'helpscout.tag'
    _helpscout_endpoint = 'Tags'

    def search_read(self):
        return self.endpoint.list()

    def search(self, filters=None):
        return [r.id for r in self.search_read()]

    def read(self, external_id):
        for r in self.search_read():
            if r.id == external_id:
                return r

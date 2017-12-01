# -*- coding: utf-8 -*-
# Copyright 2017 LasLabs Inc.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import models, fields
from odoo.addons.component.core import Component


class Attachment(models.Model):

    _inherit = 'ir.attachment'

    helpscout_bind_ids = fields.One2many(
        string='HelpScout Bindings',
        comodel_name='helpscout.attachment',
        inverse_name='odoo_id',
    )


class HelpScoutAttachment(models.Model):

    _name = 'helpscout.attachment'
    _inherit = 'helpscout.binding'
    _inherits = {'ir.attachment': 'odoo_id'}
    _description = 'HelpScout Thread Attachments'

    _rec_name = 'name'

    helpscout_file_size = fields.Integer(
        string='Attachment Size',
    )
    helpscout_hash = fields.Char(
        string='Attachment Hash',
    )
    helpscout_height = fields.Integer(
        string='Attachment Height',
    )
    helpscout_width = fields.Integer(
        string='Attachment Width',
    )
    odoo_id = fields.Many2one(
        string='Attachment',
        comodel_name='ir.attachment',
        required=True,
        ondelete='cascade',
    )


class HelpScoutAttachmentAdapter(Component):
    """Utilize the API in context."""
    _name = 'helpscout.attachment.adapter'
    _inherit = 'helpscout.adapter'
    _apply_on = 'helpscout.attachment'
    _helpscout_endpoint = 'Attachments'

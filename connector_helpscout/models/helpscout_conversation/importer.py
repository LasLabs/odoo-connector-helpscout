# -*- coding: utf-8 -*-
# Copyright 2017 LasLabs Inc.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.addons.component.core import Component
from odoo.addons.connector.components.mapper import (convert,
                                                     mapping,
                                                     none,
                                                     only_create
                                                     )


class HelpScoutConversationImportMapper(Component):
    _name = 'helpscout.import.mapper.conversation'
    _inherit = 'helpscout.import.mapper'
    _apply_on = 'helpscout.conversation'

    direct = [(none('type'), 'helpscout_type'),
              (convert('number', str), 'code'),
              (none('subject'), 'name'),
              ]

    @mapping
    @only_create
    def odoo_id(self, record):
        conversation = self.env['project.task'].search([
            ('code', '=', str(record.number)),
        ])
        if conversation:
            return {'odoo_id': conversation.id}

    @mapping
    def helpscout_folder_id(self, record):
        folder = self.env['helpscout.helpscout.folder'].search([
            ('external_id', '=', record.folder_id),
        ])
        if folder:
            return {'helpscout_folder_id': folder.id}

    @mapping
    def partner_id(self, record):
        customer = self.env['helpscout.customer'].search([
            ('external_id', '=', record.customer.id),
        ])
        partner = customer.odoo_id
        return {'partner_id': partner.id}

    @mapping
    def project_id(self, record):
        mailbox = self.env['helpscout.mailbox'].search([
            ('external_id', '=', record.mailbox.id),
        ])
        project = mailbox.odoo_id
        if project:
            return {'project_id': project.id}

    @mapping
    def stage_id(self, record):
        stage = self.env.ref('connector_helpscout.status_%s' % record.status)
        if stage:
            return {'stage_id': stage.id}

    @mapping
    def tag_ids(self, record):
        tag_bindings = self.env['helpscout.tag'].search([
            ('name', 'in', record.tags),
            ('backend_id', '=', self.backend_record.id),
        ])
        if len(tag_bindings) != len(record.tags):
            self.env['helpscout.tag'].import_batch(self.backend_record)
            return self.tag_ids(record)
        tags = tag_bindings.mapped('odoo_id')
        if tags:
            return {'tag_ids': [(6, 0, tags.ids)]}

    @mapping
    def user_id(self, record):
        try:
            owner = self.env['helpscout.user'].search([
                ('external_id', '=', record.owner.id),
            ])
        except AttributeError:
            # in case a user/owner has not been assigned to the ticket
            return {'user_id': False}
        user = owner.odoo_id
        return {'user_id': user.id}


class HelpScoutConversationImporter(Component):
    """Import one HelpScout record."""
    _name = 'helpscout.record.importer.conversation'
    _inherit = 'helpscout.importer'
    _apply_on = 'helpscout.conversation'

    def _after_import(self, binding):
        binding_model = self.env['helpscout.thread'].with_context(
            tracking_disable=True,
        )
        threads = binding_model
        for thread in self.helpscout_record['threads']:
            threads += binding_model.import_direct(self.backend_record, thread)
        threads.write({
            'model': 'project.task',
            'res_id': binding.odoo_id.id,
        })


class HelpScoutConversationBatchImporter(Component):
    """Import a batch of HelpScout records."""
    _name = 'helpscout.batch.importer.conversation'
    _inherit = 'helpscout.direct.batch.importer'
    _apply_on = 'helpscout.conversation'

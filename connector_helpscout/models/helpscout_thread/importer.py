# -*- coding: utf-8 -*-
# Copyright 2017 LasLabs Inc.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.addons.component.core import Component
from odoo.addons.connector.components.mapper import (mapping,
                                                     only_create,
                                                     )


ACTION_DESCRIPTIONS = {
    'movedFromMailbox': 'The conversation was moved from',
    'merged': 'Another conversation was merged with this conversation.',
    'imported': 'The conversation was imported (no email notifications were '
                'sent).',
    'workflow': 'A workflow was run on this conversation (either automatic or '
                'manual).',
    'importedExternal': 'The ticket was imported from an external Service.',
    'changedTicketCustomer': 'The customer associated with the ticket was '
                             'changed.',
    'deletedTicket': 'The ticket was deleted.',
    'restoreTicket': 'The ticket was restored.',
}


class HelpScoutThreadImportMapper(Component):
    _name = 'helpscout.import.mapper.thread'
    _inherit = 'helpscout.import.mapper'
    _apply_on = 'helpscout.thread'

    direct = [('type', 'helpscout_type'),
              ('action_type', 'helpscout_action_type'),
              ('action_source_id', 'helpscout_action_source'),
              ('from_mailbox', 'helpscout_from_mailbox'),
              ('saved_reply_id', 'helpscout_saved_reply_id'),
              ('state', 'helpscout_state'),
              ('created_at', 'date'),
              ('opened_at', 'helpscout_date_opened'),
              ]

    def _author(self, record):
        person_type = record.created_by.type
        author = self.env['helpscout.%s' % person_type].search([
            ('external_id', '=', record.created_by.id),
        ]).odoo_id
        if person_type == 'user':
            author = author.partner_id
        return author

    def _message_type(self, record):
        source = self.helpscout_source_type(record)['helpscout_source_type']
        if source in ['email', 'emailfwd']:
            return 'email'
        elif record.type == 'lineitem':
            return 'notification'
        return 'comment'

    def _message_subtype(self, record):
        if record.type == 'note':
            return self.env.ref('mail.mt_note')
        return self.env.ref('connector_helpscout.thread_%s' % record.type)

    def _line_item_body(self, record):
        """
        Determines message contents when the message is a 'lineitem' type,
        which is generally an internal note describing a non-message action.
        """
        message = ACTION_DESCRIPTIONS.get(record.action_type, '')
        if record.action_type is None:
            # action_type not provided, must infer from other attributes
            return self._null_action_type_body(record)
        if record.action_type == 'movedFromMailbox':
            # append originating mailbox name to message if moved
            return '%s %s.' % (message, record.from_mailbox.name)
        if not message:
            # generic message if an unlisted lineitem action is performed
            return ('Conversation updated (view on HelpScout web portal for '
                    'details).')
        return message

    def _null_action_type_body(self, record):
        """
        Handles cases where a non-message action is implied, but an explicit
        action_type is not provided.

        There are two cases known at this point: conversation status changes,
        and conversation assignment/unassignment.
        """
        if record.status != 'nochange':
            return 'Conversation marked as %s.' % (record.status)

        try:
            assignment = '%s %s' % (
                record.assigned_to.first_name,
                record.assigned_to.last_name,
            )
        except AttributeError:
            assignment = 'Anyone'
        return 'Conversation assigned to %s.' % (assignment)

    @mapping
    @only_create
    def odoo_id(self, record):
        thread = self.env['mail.message'].search([
            ('model', '=', 'project.task'),
            ('date', '=', str(record.created_at)),
            ('body', '=', self.body(record)),
        ])

        if thread:
            return {'odoo_id': thread.id}

    @mapping
    def author_id(self, record):
        """Map author_id to internal partner_id"""
        try:
            return {'author_id': self._author(record).id}
        except AttributeError:
            return

    @mapping
    def body(self, record):
        if record.body:
            return {'body': record.body}

        if record.type == 'lineitem':
            return {'body': self._line_item_body(record)}

        return

    @mapping
    def helpscout_from_mailbox(self, record):
        try:
            return {'helpscout_from_mailbox': record.from_mailbox.id}
        except AttributeError:
            # in case there is no from_mailbox provided
            return

    @mapping
    def helpscout_source_person_type(self, record):
        return {'helpscout_source_person_type': record.source.via}

    @mapping
    def helpscout_source_type(self, record):
        return {'helpscout_source_type': record.source.type}

    @mapping
    def helpscout_to(self, record):
        return {'helpscout_to': ', '.join(record.to)}

    @mapping
    def message_type(self, record):
        """
        Represent HelpScout message types with Odoo message_types and subtypes.

        The HelpScout 'note' type is not visible to customers, similar to the
        purpose of the Odoo comment/note.
        """
        return {
            'message_type': self._message_type(record),
            'subtype_id': self._message_subtype(record).id,
        }


class HelpScoutThreadImporter(Component):
    """Import one HelpScout record."""
    _name = 'helpscout.record.importer.thread'
    _inherit = 'helpscout.importer'
    _apply_on = 'helpscout.thread'

    def _after_import(self, binding):
        binding_model = self.env['helpscout.attachment']
        attachments = []
        for attachment in self.helpscout_record['attachments']:
            attachment.res_id = binding.odoo_id.id
            attachment.res_model = 'mail.message'
            attachments.append(
                binding_model.import_direct(self.backend_record, attachment)
            )
        attachment_ids = [attachment.odoo_id.id for attachment in attachments]
        binding.odoo_id.write({'attachment_ids': [(6, 0, attachment_ids)]})

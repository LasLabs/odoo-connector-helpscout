# -*- coding: utf-8 -*-
# Copyright 2017 LasLabs Inc.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.addons.component.core import Component
from odoo.addons.component_event import skip_if


class HelpScoutListener(Component):
    """Generic event listener for HelpScout."""
    _name = 'helpscout.listener'
    _inherit = 'base.event.listener'

    def no_connector_export(self, record):
        return self.env.context.get('connector_no_export')

    def export_record(self, record, fields=None):
        record.with_delay().export_record(fields=fields)

    def delete_record(self, record):
        record.with_delay().export_delete_record()


class HelpScoutListenerBindingCreateUpdate(Component):
    """Generic event listener for HelpScout bindings for create/update.
    """
    _name = 'helpscout.listener.binding.create.update'
    _inherit = 'helpscout.listener'
    _apply_on = [
        'helpscout.customer',
        'helpscout.web.hook',
    ]

    @skip_if(lambda self, record, **kwargs: self.no_connector_export(record))
    def on_record_create(self, record, fields=None):
        self.export_record(record, fields)

    @skip_if(lambda self, record, **kwargs: self.no_connector_export(record))
    def on_record_write(self, record, fields=None):
        self.export_record(record, fields)


class HelpScoutListenerBindingAll(Component):
    """Generic event listener for HelpScout bindings, all CRUD."""
    _name = 'helpscout.listener.binding.all'
    _inherit = 'helpscout.listener.binding.create.update'
    _apply_on = []

    @skip_if(lambda self, record, **kwargs: self.no_connector_export(record))
    def on_record_unlink(self, record):
        self.delete_record(record)


class HelpScoutListenerOdooCreateUpdate(Component):
    """Generic event listener for Odoo models create/update."""
    _name = 'helpscout.listener.odoo.create.update'
    _inherit = 'helpscout.listener'
    _apply_on = [
        'res.partner',
    ]

    def new_binding(self, record):
        exporter = self.env['helpscout.backend'].default_exporter
        if exporter:
            return self.env[self._binding_model].create({
                'odoo_id': record.id,
                'backend_id': exporter.id,
            })

    @skip_if(lambda self, record, **kwargs: self.no_connector_export(record))
    def on_record_create(self, record, fields=None):
        self.export_record(record.helpscout_bind_ids, fields)

    @skip_if(lambda self, record, **kwargs: self.no_connector_export(record))
    def on_record_write(self, record, fields=None):
        if not record.helpscout_bind_ids:
            return
        self.export_record(record.helpscout_bind_ids, fields)


class HelpScoutListenerOdooAll(Component):
    """Generic event listener for Odoo models, all CRUD."""
    _name = 'helpscout.listener.odoo.all'
    _inherit = 'helpscout.listener.odoo.create.update'
    _apply_on = []

    @skip_if(lambda self, record, **kwargs: self.no_connector_export(record))
    def on_record_unlink(self, record):
        if not record.helpscout_bind_ids:
            return
        self.delete_record(record.helpscout_bind_ids)

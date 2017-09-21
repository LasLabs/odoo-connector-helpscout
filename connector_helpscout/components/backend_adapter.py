# -*- coding: utf-8 -*-
# Copyright 2017 LasLabs Inc.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

import logging

from odoo import _

from odoo.addons.component.core import AbstractComponent

_logger = logging.getLogger(__name__)

try:
    from helpscout import HelpScout, HelpScoutWebHook
except ImportError:
    _logger.debug("`helpscout` Python library not installed.")


class HelpScoutApi(object):
    def __new__(cls, api_key, *args, **kwargs):
        return HelpScout(api_key)


class HelpScoutHook(object):
    def __new__(cls, secret_key, *args, **kwargs):
        return HelpScoutWebHook(secret_key)


class HelpScoutCRUDAdapter(AbstractComponent):

    _name = 'helpscout.crud.adapter'
    _inherit = ['base.backend.adapter', 'base.helpscout.connector']
    _usage = 'backend.adapter'

    def search(self, filters=None):
        raise NotImplementedError

    def read(self, id):
        raise NotImplementedError

    def search_read(self, filters=None):
        raise NotImplementedError

    def create(self, data):
        raise NotImplementedError

    def write(self, id, data):
        raise NotImplementedError

    def delete(self, id):
        raise NotImplementedError


class HelpScoutAdapter(AbstractComponent):

    _name = 'helpscout.adapter'
    _inherit = 'helpscout.crud.adapter'

    _helpscout_endpoint = None

    @property
    def helpscout(self):
        """Return the HelpScout API for use."""
        try:
            return getattr(self.work, 'helpscout_api')
        except AttributeError:
            raise AttributeError(_(
                'You must provide a `helpscout_api` attribute to be able '
                'to use this Backend Adapter.',
            ))

    @property
    def endpoint(self):
        """Return a usable endpoint for the API."""
        return getattr(self.helpscout, self._helpscout_endpoint)

    def search(self, filters=None):
        """Search records according to filters and return the result IDs.

        Args:
            filters (Domain | iter): The queries for the domain. If a Domain
                object is provided, it will simply be returned. Otherwise, a
                Domain object will be generated from the complex queries. In
                this case, the queries should conform to the interface in
                `helpscout.domain.Domain.from_tuple()
                <https://laslabs.github.io/python-helpscout/helpscout.domain.
                html#helpscout.domain.Domain.from_tuple>`_
        """
        return [r.id for r in self.endpoint.search(filters)]

    def read(self, _id):
        """Get records according to its ID."""
        return self.endpoint.get(_id)

    def create(self, data):
        """Create a record on the remote."""
        return self.endpoint.create(self.new_record(data))

    def write(self, _id, data):
        """Write the record on the remote."""
        data['id'] = _id
        return self.endpoint.update(self.new_record(data))

    def delete(self, _id):
        """Delete the record from the remote."""
        record = self.new_record({'id': _id})
        return self.endpoint.delete(record)

    def new_record(self, data):
        """Return a memory record for the data."""
        return self.endpoint.proxy_class.new_object(data)

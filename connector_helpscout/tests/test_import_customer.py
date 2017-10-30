# -*- coding: utf-8 -*-
# Copyright 2017 LasLabs Inc.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

from .common import HelpScoutSyncTestCase, recorder


class TestImportCustomer(HelpScoutSyncTestCase):

    def setUp(self):
        super(TestImportCustomer, self).setUp()
        self.model = self.env['helpscout.customer']
        self.expect = {
            'firstname': 'Test',
            'lastname': 'User',
            'comment': 'This is a basic test user',
            'function': 'CEO',
            'backend_date_created': '2017-09-23 20:12:43',
            'backend_date_modified': '2017-10-28 17:21:12',
        }

    @recorder.use_cassette
    def _import_customer(self):
        self.model.import_record(self.backend, 144228647)
        partner = self.model.search([('external_id', '=', 144228647),
                                     ('backend_id', '=', self.backend.id)])
        return partner

    def test_import_customer(self):
        """It should import and bind the customer."""
        self.assertTrue(self._import_customer())

    def test_import_customer_direct(self):
        """It should import the direct mappings."""
        partner = self._import_customer()
        for key, value in self.expect.items():
            self.assertEqual(partner[key], value)

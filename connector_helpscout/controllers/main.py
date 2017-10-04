# -*- coding: utf-8 -*-
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import http


class HelpScout(http.Controller):
    """HelpScout Web Hook Controller."""

    CONTROLLER_VERSON = 'v1'

    @http.route('/helpscout/%s' % CONTROLLER_VERSON)
    def helpscout(self):
        """HelpScout central WebHook endpoint.

        It uses the ``X-HelpScout-Signature`` header to authenticate the
        request, then passes to the proper method using the parsed
        ``X-HelpScout-Event`` header.
        """

        env = http.request.env
        backend = env['helpscout.backend'].get_for_website(
            env['website'].get_current_website(),
        )
        if not backend:
            return

        headers = http.request.httprequest.headers
        signature = headers.get('X-HelpScout-Signature')
        event = headers.get('X-HelpScout-Event')

        backend.action_receive_hook(
            event,
            signature,
            http.request.httprequest.get_data(),
        )

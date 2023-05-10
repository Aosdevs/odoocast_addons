# Copyright (C) 2020 - Hendrix Costa
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from odoo import api, fields, models, modules


class ImLivechatChannel(models.Model):
    """ Livechat Channel
        Define a communication channel, which can be accessed with 'script_external' (script tag to put on
        external website), 'script_internal' (code to be integrated with odoo website) or via 'web_page' link.
        It provides rating tools, and access rules for anonymous people.
    """
    _inherit = 'im_livechat.channel'

    def _get_available_users(self):
        """ get available user of a given channel
            :retuns : return the res.users having their im_status online
        """
        users_ids = super(ImLivechatChannel, self)._get_available_users()

        has_chatbot_ai = \
            self.env['ir.config_parameter'].\
                sudo().get_param('has_chatbot_ai') or False

        if has_chatbot_ai:
            id_user = self.env['ir.config_parameter'].\
                sudo().get_param('chatbot_user_id')
            if id_user:
                return self.user_ids.browse(int(id_user))

        return users_ids

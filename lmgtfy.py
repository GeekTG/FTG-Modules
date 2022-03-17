# -*- coding: utf-8 -*-

import logging
import urllib

from .. import loader, utils

logger = logging.getLogger(__name__)


@loader.tds
class LMGTFYMod(loader.Module):
    """Let me Google that for you, coz you too lazy to do that yourself."""

    strings = {
        "name": "LetMeGoogleThatForYou",
        "result": "<b>Here you go, help yourself.</b>\n<a href='{}'>{}</a>",
        "default": "How to use Google?",
    }

    @loader.unrestricted
    async def lmgtfycmd(self, message):
        """Use in reply to another message or as .lmgtfy <text>"""
        text = utils.get_args_raw(message)
        if not text:
            if message.is_reply:
                text = (await message.get_reply_message()).message
            else:
                text = self.strings("default", message)
        query_encoded = urllib.parse.quote_plus(text)
        lmgtfy_url = "http://lmgtfy.com/?s=g&iie=1&q={}".format(query_encoded)
        await utils.answer(
            message,
            self.strings("result", message).format(
                utils.escape_html(lmgtfy_url), utils.escape_html(text)
            ),
        )

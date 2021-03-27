# -*- coding: utf-8 -*-

# requires: search-engine-parser>=0.6.2

import logging

from search_engine_parser import GoogleSearch

from .. import loader, utils

logger = logging.getLogger(__name__)


@loader.tds
class GoogleSearchMod(loader.Module):
    """Make a Google search, right in your chat!"""
    strings = {"name": "Google Search",
               "no_term": "<b>I can't Google nothing</b>",
               "no_results": "<b>Could not find anything about</b> <code>{}</code> <b>on Google</b>",
               "results": "<b>These came back from a Google search for</b> <code>{}</code>:\n\n",
               "result": "<a href='{}'>{}</a>\n\n<code>{}</code>\n"}

    @loader.unrestricted
    @loader.ratelimit
    async def googlecmd(self, message):
        """Shows Google search results."""
        text = utils.get_args_raw(message.message)
        if not text:
            text = (await message.get_reply_message()).message
        if not text:
            await utils.answer(message, self.strings("no_term", message))
            return
        # TODO: add ability to specify page number.
        gsearch = GoogleSearch()
        gresults = await gsearch.async_search(text, 1)
        if not gresults:
            await utils.answer(message, self.strings("no_results", message).format(text))
            return
        msg = ""
        results = zip(gresults["titles"], gresults["links"], gresults["descriptions"])
        for result in results:
            msg += self.strings("result", message).format(utils.escape_html(result[0]), utils.escape_html(result[1]),
                                                          utils.escape_html(result[2]))
        await utils.answer(message, self.strings("results", message).format(utils.escape_html(text)) + msg)

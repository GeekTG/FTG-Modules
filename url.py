# -*- coding: utf-8 -*-

# Module author: @GovnoCodules, @ftgmodulesbyfl1yd

import urllib
from telethon.errors.rpcerrorlist import YouBlockedUserError
from telethon import events
from .. import loader, utils
import logging
from requests import get, post
import os
from telethon import functions

logger = logging.getLogger(__name__)


@loader.tds
class URlMod(loader.Module):
    """URL Module"""
    strings = {
        "name": "URL",
        "some_rong": "<b>Ты делаешь что-то не так!\nНапиши</b> <code>.help "
                     "gg.gg</code> <b>для информации.</b>",
        "result": "<b>Here you go, help yourself.</b>\n<a href='{}'>{}</a>",
        "default": "How to use Google?"
    }

    async def client_ready(self, client, db):
        self.client = client

    async def ggcmd(self, message):
        """.gg <длинная ссылка или реплай на ссылку> """
        m_text = utils.get_args_raw(message)
        if not m_text:
            reply = await message.get_reply_message()
            if not reply:
                await utils.answer(message, self.strings("some_rong", message))
                return
            long_url = reply.raw_text
        else:
            long_url = m_text

        if 'http://' not in long_url and 'https://' not in long_url:
            long_url = 'http://' + long_url
        t_check = f"URL: {long_url}\nCheck..."
        await utils.answer(message, t_check)
        check = post('http://gg.gg/check',
                     data={'custom_path': None, 'use_norefs': '0',
                           'long_url': long_url, 'app': 'site',
                           'version': '0.1'}).text
        if check != "ok":
            await utils.answer(message, check)
            return
        await utils.answer(message, "Create...")
        short = post('http://gg.gg/create',
                     data={'custom_path': None, 'use_norefs': '0',
                           'long_url': long_url, 'app': 'site',
                           'version': '0.1'}).text
        await utils.answer(message, short)

    async def lgtcmd(self, message):
        """Сократить ссылку с помощью сервиса verylegit.link"""
        args = utils.get_args_raw(message)
        if not args: return await message.edit("Нет аргументов.")
        link = os.popen(
            f"curl verylegit.link/sketchify -d long_url={args}").read()
        await message.edit(f"Ссылка:\n> {link}")

    async def clckcmd(self, message):
        """Сократить ссылку с помощью сервиса clck.ru"""
        m_text = utils.get_args_raw(message)
        if not m_text:
            reply = await message.get_reply_message()
            if not reply:
                await utils.answer(message, self.strings("some_rong", message))
                return
            long_url = reply.raw_text
        else:
            long_url = m_text
        await utils.answer(message, "Creating...")
        fetcher = post(
            'https://clck.ru/--?url=' +
            long_url).text
        await utils.answer(message, fetcher)

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
        await utils.answer(message,
                           self.strings("result", message).format(
                               utils.escape_html(lmgtfy_url),
                               utils.escape_html(text)))

    async def nullcmd(self, message):
        """Сократить ссылку с помощью сервиса nullify"""
        chat = '@nullifybot'
        reply = await message.get_reply_message()
        async with message.client.conversation(chat) as conv:
            if not reply:
                text = utils.get_args_raw(message)
            else:
                text = await message.get_reply_message()
            try:
                response = conv.wait_event(
                    events.NewMessage(incoming=True, from_users=1481485420))
                mm = await message.client.send_message(chat, text)
                response = await response
                await mm.delete()
            except YouBlockedUserError:
                await message.edit('<code>Разблокируй @nullifybot</code>')
                return
            await message.edit(response.text.replace("🔗 Твоя ссылка: ", ""))
            await message.client(functions.messages.DeleteHistoryRequest(
                peer='nullifybot',
                max_id=0,
                just_clear=False,
                revoke=True
            ))
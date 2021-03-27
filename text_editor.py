# -*- coding: utf-8 -*-

# Module author: Official Repo, @GovnoCodules

import logging
from .. import loader, utils
import telethon
import io
from telethon.errors.rpcerrorlist import MessageNotModifiedError
import asyncio

logger = logging.getLogger(__name__)


@loader.tds
class TextEditorMod(loader.Module):
    """Text Editor Module"""
    strings = {
        "name": "TextEditor",
        "no_message": "<b>You can't type nothing!</b>",
        "type_char_cfg_doc": "Character for typewriter",
        "delay_typer_cfg_doc": "How long to delay showing the typewriter "
                               "character",
        "delay_text_cfg_doc": "How long to delay showing the text"
    }

    def __init__(self):
        self.config = loader.ModuleConfig("TYPE_CHAR", "▒",
                                          lambda m: self.strings("type_char_cfg_doc"),
                                          "DELAY_TYPER", 0.04,
                                          lambda m: self.strings("delay_typer_cfg_doc"),
                                          "DELAY_TEXT", 0.02,
                                          lambda m: self.strings("delay_text_cfg_doc"))

    async def switchcmd(self, message):
        """Если ты допустил ошибку и набрал текст не сменив раскладку
        клавиатуры то вернись в его начало и допиши `.switch` и твой текст
        станет читабельным. Если ты всё же отправил сообщение не в той
        расскладке, то просто ответь на него этой командой и он измениться.
        если же твой собеседник допустил ошибку, то просто ответь на его
        сообщение и сообщение с командой измениться. """
        RuKeys = """ёйцукенгшщзхъфывапролджэячсмитьбю.Ё"№;%:?ЙЦУКЕНГ
        ШЩЗХЪФЫВАПРОЛДЖЭ/ЯЧСМИТЬБЮ, """
        EnKeys = """`qwertyuiop[]asdfghjkl;'zxcvbnm,./~@#$%^&QWERTYUIOP{
        }ASDFGHJKL:"|ZXCVBNM<>? """

        if message.is_reply:
            reply = await message.get_reply_message()
            text = reply.raw_text
            if not text:
                await message.edit('Тут текста нету...')
                return
            change = str.maketrans(RuKeys + EnKeys, EnKeys + RuKeys)
            text = str.translate(text, change)

            if message.sender_id != reply.sender_id:
                await message.edit(text)
            else:
                await message.delete()
                await reply.edit(text)

        else:
            text = utils.get_args_raw(message)
            if not text:
                await message.edit('Тут текста нету...')
                return
            change = str.maketrans(RuKeys + EnKeys, EnKeys + RuKeys)
            text = str.translate(text, change)
            await message.edit(text)

    @loader.ratelimit
    async def codecmd(self, message):
        """.code <text or reply>"""
        if message.is_reply:
            reply = await message.get_reply_message()
            code = reply.raw_text
            code = code.replace("<", "&lt;").replace(">", "&gt;")
            await message.edit(f"<code>{code}</code>")
        else:
            code = message.raw_text[5:]
            code = code.replace("<", "&lt;").replace(">", "&gt;")
            try:
                await message.edit(f"<code>{code}</code>")
            except:
                await message.edit(self.strings("msg_is_emp", message))

    async def mtfcmd(self, message):
        """.mtf <reply to text>"""
        reply = await message.get_reply_message()
        if not reply or not reply.message:
            await message.edit("<b>Reply to text!</b>")
            return
        text = bytes(reply.raw_text, "utf8")
        fname = utils.get_args_raw(message) or str(
            message.id + reply.id) + ".txt"
        file = io.BytesIO(text)
        file.name = fname
        file.seek(0)
        await reply.reply(file=file)
        await message.delete()

    async def ftmcmd(self, message):
        """.ftm <reply to file>"""
        reply = await message.get_reply_message()
        if not reply or not reply.file:
            await message.edit("<b>Reply to file!</b>")
            return
        text = await reply.download_media(bytes)
        text = str(text, "utf8")
        if utils.get_args(message):
            text = f"<code>{text}</code>"
        await utils.answer(message, utils.escape_html(text))

    @loader.ratelimit
    async def typercmd(self, message):
        """.type <message>"""
        a = utils.get_args_raw(message)
        if not a:
            await utils.answer(message, self.strings("no_message", message))
            return
        m = ""
        entities = message.entities or []
        for c in a:
            m += self.config["TYPE_CHAR"]
            message = await update_message(message, m, entities)
            await asyncio.sleep(0.04)
            m = m[:-1] + c
            message = await update_message(message, m, entities)
            await asyncio.sleep(0.02)

    async def revcmd(self, message):
        """Используй .rev <текст или реплай>."""
        if message.text:
            text = utils.get_args_raw(message)
            reply = await message.get_reply_message()

            if not text and not reply:
                return await message.edit("Нет текста или реплая.")

            return await message.edit((text or reply.raw_text)[::-1])
        else:
            return await message.edit("Это не текст.")


async def update_message(message, m, entities):
    try:
        return await utils.answer(message, m,
                                  parse_mode=lambda t: (t, entities))
    except MessageNotModifiedError:
        return message  # space doesnt count
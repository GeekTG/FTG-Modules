# -*- coding: utf-8 -*-

# Module author: @GovnoCodules

from .. import loader, utils
import logging
from requests import post
import requests
from telethon.tl.types import DocumentAttributeFilename
from telethon.errors.rpcerrorlist import YouBlockedUserError
from telethon import events
import io
from io import BytesIO
from PIL import Image


logger = logging.getLogger(__name__)


@loader.tds
class FileUploaderMod(loader.Module):
    """Uploader"""
    strings = {
        "name": "File Uploader"
    }

    async def client_ready(self, client, db):
        self.client = client

    @loader.sudo
    async def x0cmd(self, message):
        """Upload to x0"""
        await message.edit("<b>Uploading...</b>")
        reply = await message.get_reply_message()
        if not reply:
            await message.edit("<b>Reply to message!</b>")
            return
        media = reply.media
        if not media:
            file = io.BytesIO(bytes(reply.raw_text, "utf-8"))
            file.name = "txt.txt"
        else:
            file = io.BytesIO(await self.client.download_file(media))
            file.name = reply.file.name if reply.file.name else reply.file.id + reply.file.ext
        try:
            x0at = post('https://x0.at', files={'file': file})
        except ConnectionError as e:
            await message.edit("<b>Error</b>")
            return
        url = x0at.text
        output = f'<a href="{url}">URL: </a><code>{url}</code>'
        await message.edit(output)

    async def telegraphcmd(self, message):
        """.ph <reply photo or video>"""
        if message.is_reply:
            reply_message = await message.get_reply_message()
            data = await check_media(reply_message)
            if isinstance(data, bool):
                await message.edit("<b>Reply to photo or video/gif</b>")
                return
        else:
            await message.edit("<b>Reply to photo or video/gif</b>")
            return

        file = await message.client.download_media(data, bytes)
        path = requests.post('https://te.legra.ph/upload', files={'file': ('file', file, None)}).json()
        try:
            link = 'https://te.legra.ph' + path[0]['src']
        except KeyError:
            link = path["error"]
        await message.edit("<b>" + link + "</b>")

    async def imgurcmd(self, message):
        """Upload to imgur"""
        chat = '@ImgUploadBot'
        reply = await message.get_reply_message()
        async with message.client.conversation(chat) as conv:

            if not reply:
                await message.edit("<b>Reply to photo</b>")
                return
            else:
                pic = await check_mediaa(message, reply)
                if not pic:
                    await utils.answer(message, '<b>Reply to photo</b>')
                    return
            await message.edit("<b>Uploading...</b>")
            try:
                what = lol(pic)
                response = conv.wait_event(events.NewMessage(incoming=True, from_users=985223903))
                await message.client.send_file(chat, what)
                response = await response
            except YouBlockedUserError:
                await message.edit('<code>Разблокируй @imgurbot_bot</code>')
                return
            await message.edit("<b>Imgur link - </b>" + response.text)


async def check_media(reply_message):
    if reply_message and reply_message.media:
        if reply_message.photo:
            data = reply_message.photo
        elif reply_message.document:
            if DocumentAttributeFilename(file_name='AnimatedSticker.tgs') in reply_message.media.document.attributes:
                return False
            if reply_message.audio or reply_message.voice:
                return False
            data = reply_message.media.document
        else:
            return False
    else:
        return False
    if not data or data is None:
        return False
    else:
        return data


def lol(reply):
    scrrrra = Image.open(BytesIO(reply))
    out = io.BytesIO()
    out.name = "outsider.png"
    scrrrra.save(out)
    return out.getvalue()


async def check_mediaa(message, reply):
    if reply and reply.media:
        if reply.photo:
            data = reply.photo
        elif reply.document:
            if reply.gif or reply.video or reply.audio or reply.voice:
                return None
            data = reply.media.document
        else:
            return None
    else:
        return None
    if not data or data is None:
        return None
    else:
        data = await message.client.download_file(data, bytes)
        try:
            Image.open(io.BytesIO(data))
            return data
        except:
            return None
# -*- coding: utf-8 -*-

# Module author: @GovnoCodules, @ftgmodulesbyfl1yd

import io
import os
from asyncio import sleep

from requests import get
from telethon import events, functions
from telethon.errors.rpcerrorlist import YouBlockedUserError
from telethon.tl.types import MessageEntityTextUrl, MessageEntityUrl

from .. import loader, utils


@loader.tds
class DownloaderMod(loader.Module):
    """Downloader module"""

    strings = {"name": "Downloader"}

    async def dlrcmd(self, message):
        """.dlr <path/file_name> - download file to server"""
        name = utils.get_args_raw(message)
        reply = await message.get_reply_message()
        if reply:
            await message.edit("Downloading...")
            if reply.text:
                text = reply.text
                fname = f"{name or message.id + reply.id}.txt"
                with open(fname, "w") as file:
                    file.write(text)
            else:
                ext = reply.file.ext
                fname = f"{name or message.id + reply.id}{ext}"
                await message.client.download_media(reply, fname)
            await message.edit(
                f"FIle saved as: <code>{fname}</code>.\n\nYou "
                f"can send it with command: "
                f"<code>.ulf {fname}</code>."
            )
        else:
            return await message.edit("There is no reply")

    async def ulfcmd(self, message):
        """.ulf <file_name/path> send file from server
        <d> - Delete file after sending"""
        name = utils.get_args_raw(message)
        d = False
        if "d " in name:
            d = True
        if not name:
            return await message.edit("No args")
        try:
            name = name.replace("d ", "")
            await message.edit(f"Sending <code>{name}</code>...")
            if d:
                await message.client.send_file(message.to_id, f"{name}")
                await message.edit(
                    f"Sending <code>{name}</code>... Success!\Deleting "
                    f"<code>{name}</code>..."
                )
                os.remove(name)
                await message.edit(
                    f"Sending <code>{name}</code>... Deleting!\nУдаляем "
                    f"<code>{name}</code>... Success!"
                )
                await sleep(0.5)
            else:
                await message.client.send_file(message.to_id, name)
        except:
            return await message.edit("File does not exist")
        await message.delete()

    async def dltiktokcmd(self, message):
        """TikTok video downloader"""
        chat = "@ttsavebot"
        reply = await message.get_reply_message()
        async with message.client.conversation(chat) as conv:
            text = utils.get_args_raw(message)
            if reply:
                text = await message.get_reply_message()
            await message.edit("<b>Downloading...</b>")
            try:
                response = conv.wait_event(
                    events.NewMessage(incoming=True, from_users=1087584961)
                )
                response2 = conv.wait_event(
                    events.NewMessage(incoming=True, from_users=1087584961)
                )
                response3 = conv.wait_event(
                    events.NewMessage(incoming=True, from_users=1087584961)
                )
                mm = await message.client.send_message(chat, text)
                response = await response
                response2 = await response2
                response3 = await response3
                await mm.delete()
            except YouBlockedUserError:
                await message.edit("<code>Разблокируй @ttsavebot</code>")
                return
            await message.client.send_file(
                message.to_id, response3.media, reply_to=reply
            )
            await message.delete()
            await message.client(
                functions.messages.DeleteHistoryRequest(
                    peer="ttsavebot", max_id=0, just_clear=False, revoke=True
                )
            )

    async def dlfilecmd(self, message):
        """File downloader (small files)"""
        await downloading(message)

    async def dlbigfilecmd(self, message):
        """File downloader (big files)"""
        await downloading(message, True)


async def downloading(message, big=False):
    args = utils.get_args_raw(message)
    reply = await message.get_reply_message()
    if not args:
        if not reply:
            await message.edit("<b>There is no link!</b>")
            return
        message = reply
    else:
        message = message

    if not message.entities:
        await message.edit("<b>There is no link!</b>")
        return

    urls = []
    for ent in message.entities:
        if type(ent) in [MessageEntityUrl, MessageEntityTextUrl]:
            if type(ent) == MessageEntityUrl:
                offset = ent.offset
                length = ent.length
                url = message.raw_text[offset : offset + length]
            else:
                url = ent.url
            if not url.startswith("http"):
                url = "http://" + url
            urls.append(url)

    if not urls:
        await message.edit("<b>There is no link!</b>")
        return
    for url in urls:
        try:
            await message.edit("<b>Downloading...</b>\n" + url)
            fname = url.split("/")[-1]
            text = get(url, stream=big)
            if big:
                f = open(fname, "wb")
                for chunk in text.iter_content(1024):
                    f.write(chunk)
                f.close()
                await message.edit("<b>Sending...</b>\n" + url)
                await message.client.send_file(
                    message.to_id, open(fname, "rb"), reply_to=reply
                )
                os.remove(fname)
            else:
                file = io.BytesIO(text.content)
                file.name = fname
                file.seek(0)
                await message.edit("<b>Sending...</b>\n" + url)
                await message.client.send_file(message.to_id, file, reply_to=reply)

        except Exception as e:
            await message.reply(
                "<b>Error while downloading!</b>\n"
                + url
                + "\n<code>"
                + str(e)
                + "</code>"
            )

    await message.delete()

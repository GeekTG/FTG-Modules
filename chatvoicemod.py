# .------.------.------.------.------.------.------.------.------.------.
# |D.--. |4.--. |N.--. |1.--. |3.--. |L.--. |3.--. |K.--. |0.--. |0.--. |
# | :/\: | :/\: | :(): | :/\: | :(): | :/\: | :(): | :/\: | :/\: | :/\: |
# | (__) | :\/: | ()() | (__) | ()() | (__) | ()() | :\/: | :\/: | :\/: |
# | '--'D| '--'4| '--'N| '--'1| '--'3| '--'L| '--'3| '--'K| '--'0| '--'0|
# `------`------`------`------`------`------`------`------`------`------'
#
#                     Copyright 2022 t.me/D4n13l3k00
#           Licensed under the Creative Commons CC BY-NC-ND 4.0
#
#                    Full license text can be found at:
#       https://creativecommons.org/licenses/by-nc-nd/4.0/legalcode
#
#                           Human-friendly one:
#            https://creativecommons.org/licenses/by-nc-nd/4.0

import contextlib
import os
import re
from typing import *

import pytgcalls
import youtube_dl
from pytgcalls import PyTgCalls, StreamType
from pytgcalls.types.input_stream import AudioPiped, AudioVideoPiped
from pytgcalls.types.input_stream.quality import HighQualityAudio, HighQualityVideo
from telethon import types

from .. import loader, utils

# meta developer: @D4n13l3k00
# requires: py-tgcalls youtube-dl


@loader.tds
class ChatVoiceMod(loader.Module):
    """Module for working with voicechat"""

    strings = {
        "name": "ChatVoiceMod",
        "downloading": "<b>[ChatVoiceMod]</b> Downloading...",
        "playing": "<b>[ChatVoiceMod]</b> Playing...",
        "notjoined": "<b>[ChatVoiceMod]</b> You are not joined",
        "stop": "<b>[ChatVoiceMod]</b> Playing stopped!",
        "leave": "<b>[ChatVoiceMod]</b> Leaved!",
        "pause": "<b>[ChatVoiceMod]</b> Paused!",
        "resume": "<b>[ChatVoiceMod]</b> Resumed!",
        "mute": "<b>[ChatVoiceMod]</b> Muted!",
        "unmute": "<b>[ChatVoiceMod]</b> Unmuted!",
        "error": "<b>[ChatVoiceMod]</b> Error: <code>{}</code>",
        "noargs": "<b>[ChatVoiceMod]</b> No args",
        "noreply": "<b>[ChatVoiceMod]</b> No reply",
        "nofile": "<b>[ChatVoiceMod]</b> No file",
        "nofiles": "<b>[ChatVoiceMod]</b> No files",
        "deleted": "<b>[ChatVoiceMod]</b> <code>{}</code> successfully deleted",
        "downloaded": "<b>[ChatVoiceMod]</b> Downloaded to <code>dl/{0}</code>. For playing use:\n<code>.cplaya dl/{0}</code>\n<code>.cplayv dl/{0}</code>",
    }

    async def client_ready(self, client, _):
        self.client = client
        self.call = PyTgCalls(client)

        @self.call.on_stream_end()
        async def _(_, update):
            with contextlib.suppress(Exception):
                await self.call.leave_group_call(update.chat_id)

        await self.call.start()

    async def parse_args(self, args):
        if not args or not re.match(
            r"http(?:s?):\/\/(?:www\.)?youtu(?:be\.com\/watch\?v=|\.be\/)([\w\-\_]*)(&(amp;)?‌​[\w\?‌​=]*)?",
            args,
        ):
            return args
        with youtube_dl.YoutubeDL({"format": "best"}) as ydl:
            info = ydl.extract_info(args, download=False)
            return info["formats"][0]["url"]

    async def cdlcmd(self, m: types.Message):
        "<reply_to_media> <name: optional> - Download media to server in `dl` folder"
        args = utils.get_args_raw(m)
        reply = await m.get_reply_message()
        if not reply:
            return await utils.answer(m, self.strings("noreply"))
        name = args or reply.file.name
        try:
            m = await utils.answer(m, self.strings("downloading"))
            await reply.download_media(f"dl/{name}")
            await utils.answer(m, self.strings("downloaded").format(name))
        except Exception as e:
            await utils.answer(m, self.strings("error").format(str(e)))

    async def clscmd(self, m: types.Message):
        "List all files in `dl` folder"
        if not os.path.isdir("dl") or not os.listdir("dl"):
            return await utils.answer(m, self.strings("nofiles"))
        files = [f"<code>dl/{f}</code>" for f in os.listdir("dl")]
        await utils.answer(m, "\n".join(files))

    # command for deleting file from dl folder
    async def cdelcmd(self, m: types.Message):
        "<name> - Delete file from `dl` folder"
        args = utils.get_args_raw(m)
        if not args:
            return await utils.answer(m, self.strings("noargs"))
        if not args.startswith("dl/"):
            args = f"dl/{args}"
        if not os.path.isfile(f"{args}"):
            return await utils.answer(m, self.strings("nofile"))
        try:
            os.remove(f"{args}")
            await utils.answer(m, self.strings("deleted").format(args))
        except Exception as e:
            await utils.answer(m, self.strings("error").format(str(e)))

    async def cplayvcmd(self, m: types.Message):
        "<link/path/reply_to_video> - Play video in voice chat"
        try:
            reply = await m.get_reply_message()
            path = await self.parse_args(utils.get_args_raw(m))
            chat = m.chat.id
            if not path:
                if not reply:
                    return await utils.answer(m, self.strings("noargs"))
                m = await utils.answer(m, self.strings("downloading"))
                path = await reply.download_media()
            with contextlib.suppress(pytgcalls.exceptions.GroupCallNotFound):
                self.call.get_active_call(chat)
                await self.call.leave_group_call(chat)
            await self.call.join_group_call(
                chat,
                AudioVideoPiped(
                    path,
                    HighQualityAudio(),
                    HighQualityVideo(),
                ),
                stream_type=StreamType().pulse_stream,
            )
            await utils.answer(m, self.strings("playing"))
        except Exception as e:
            await utils.answer(m, self.strings("error").format(str(e)))

    async def cplayacmd(self, m: types.Message):
        "<link/path/reply_to_audio> - Play audio in voice chat"
        try:
            reply = await m.get_reply_message()
            path = await self.parse_args(utils.get_args_raw(m))
            chat = m.chat.id
            if not path:
                if not reply:
                    return await utils.answer(m, self.strings("noargs"))
                m = await utils.answer(m, self.strings("downloading"))
                path = await reply.download_media()
            with contextlib.suppress(pytgcalls.exceptions.GroupCallNotFound):
                self.call.get_active_call(chat)
                await self.call.leave_group_call(chat)
            await self.call.join_group_call(
                chat,
                AudioPiped(
                    path,
                    HighQualityAudio(),
                ),
                stream_type=StreamType().pulse_stream,
            )
            await utils.answer(m, self.strings("playing"))
        except Exception as e:
            await utils.answer(m, self.strings("error").format(str(e)))

    async def cleavecmd(self, m: types.Message):
        "Leave"
        try:
            self.call.get_active_call(m.chat.id)
            await self.call.leave_group_call(m.chat.id)
            await utils.answer(m, self.strings("leave"))
        except pytgcalls.exceptions.GroupCallNotFound:
            await utils.answer(m, self.strings("notjoined"))
        except Exception as e:
            await utils.answer(m, self.strings("error").format(str(e)))

    async def cmutecmd(self, m: types.Message):
        "Mute"
        try:
            self.call.get_active_call(m.chat.id)
            await self.call.mute_stream(m.chat.id)
            await utils.answer(m, self.strings("mute"))
        except pytgcalls.exceptions.GroupCallNotFound:
            await utils.answer(m, self.strings("notjoined"))
        except Exception as e:
            await utils.answer(m, self.strings("error").format(str(e)))

    async def cunmutecmd(self, m: types.Message):
        "Unmute"
        try:
            self.call.get_active_call(m.chat.id)
            await self.call.unmute_stream(m.chat.id)
            await utils.answer(m, self.strings("unmute"))
        except pytgcalls.exceptions.GroupCallNotFound:
            await utils.answer(m, self.strings("notjoined"))
        except Exception as e:
            await utils.answer(m, self.strings("error").format(str(e)))

    async def cpausecmd(self, m: types.Message):
        "Pause"
        try:
            self.call.get_active_call(m.chat.id)
            await self.call.pause_stream(m.chat.id)
            await utils.answer(m, self.strings("pause"))
        except pytgcalls.exceptions.GroupCallNotFound:
            await utils.answer(m, self.strings("notjoined"))
        except Exception as e:
            await utils.answer(m, self.strings("error").format(str(e)))

    async def cresumecmd(self, m: types.Message):
        "Resume"
        try:
            self.call.get_active_call(m.chat.id)
            await self.call.resume_stream(m.chat.id)
            await utils.answer(m, self.strings("resume"))
        except pytgcalls.exceptions.GroupCallNotFound:
            await utils.answer(m, self.strings("notjoined"))
        except Exception as e:
            await utils.answer(m, self.strings("error").format(str(e)))

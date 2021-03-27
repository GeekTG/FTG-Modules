# -*- coding: utf-8 -*-

# Module author: @dekftgmodules

from .. import loader
from telethon import functions
from asyncio import sleep


@loader.tds
class VGCallControllerMod(loader.Module):
    "Control group voice calls"
    strings = {"name": "VGCallController"}

    @loader.owner
    async def callstartcmd(self, m):
        "Start call in chat"
        if not m.chat: return await m.edit("<b>[VGCallController]</b> It is not a chat!")
        call = (await m.client(functions.channels.GetFullChannelRequest(m.chat.id))).full_chat.call
        if not call:
            try:
                await m.client(functions.phone.CreateGroupCallRequest(peer=m.chat))
                await m.edit("<b>[VGCallController]</b> Call started!")
                await sleep(5)
            except:
                await m.edit("<b>[VGCallController]</b> Err...")
        else:
            await m.edit("<b>[VGCallController]</b> There is call now!")

    async def callstopcmd(self, m):
        "Stop call in chat"
        if not m.chat: return await m.edit("<b>[VGCallController]</b> It is not a chat!")
        call = (await m.client(functions.channels.GetFullChannelRequest(m.chat.id))).full_chat.call
        if call:
            try:
                await m.client(functions.phone.DiscardGroupCallRequest(call))
                await m.edit("<b>[VGCallController]</b> Call stopped!")
                await sleep(5)
            except:
                await m.edit("<b>[VGCallController]</b> Err...")
        else:
            await m.edit("<b>[VGCallController]</b> There is no call now!")

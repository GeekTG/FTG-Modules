# -*- coding: utf-8 -*-

# Module author: @dekftgmodules

from asyncio import sleep

from telethon import functions

from .. import loader, utils


@loader.tds
class VGCallControllerMod(loader.Module):
    """Control group voice calls"""

    strings = {"name": "VGCallController"}

    @loader.owner
    async def callstartcmd(self, m):
        """Start call in chat"""
        if not m.chat:
            return await utils.answer(m, "<b>[VGCallController]</b> It is not a chat!")
        call = (
            await m.client(functions.channels.GetFullChannelRequest(m.chat.id))
        ).full_chat.call
        if not call:
            try:
                await m.client(functions.phone.CreateGroupCallRequest(peer=m.chat))
                await utils.answer(m, "<b>[VGCallController]</b> Call started!")
            except:
                await utils.answer(m, "<b>[VGCallController]</b> Err...")
        else:
            await utils.answer(m, "<b>[VGCallController]</b> There is call now!")

    async def callstopcmd(self, m):
        """Stop call in chat"""
        if not m.chat:
            return await utils.answer(m, "<b>[VGCallController]</b> It is not a chat!")
        call = (
            await m.client(functions.channels.GetFullChannelRequest(m.chat.id))
        ).full_chat.call
        if call:
            try:
                await m.client(functions.phone.DiscardGroupCallRequest(call))
                await utils.answer(m, "<b>[VGCallController]</b> Call stopped!")
                await sleep(5)
            except:
                await utils.answer(m, "<b>[VGCallController]</b> Err...")
        else:
            await utils.answer(m, "<b>[VGCallController]</b> There is no call now!")

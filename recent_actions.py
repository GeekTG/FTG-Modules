# -*- coding: utf-8 -*-

import telethon

from .. import loader, utils


@loader.tds
class RecentActionsMod(loader.Module):
    """Reads recent actions"""

    strings = {
        "name": "Recent Actions",
        "reply_start": "<b>Reply to a message to specify where to start</b>",
        "invalid_chat": "<b>This isn't a supergroup or channel</b>",
        "needs_admin": "<b>Admin rights are required to read deleted messages</b>",
        "recovered": "Deleted message {} recovered. Originally sent at {} by {}, deleted at {} by {}",
    }

    @loader.group_admin
    @loader.ratelimit
    async def recoverdeletedcmd(self, message):
        """Restores deleted messages sent after replied message (optionally specify how many to recover)"""
        msgs = message.client.iter_admin_log(message.to_id, delete=True)
        if not message.is_reply:
            await utils.answer(message, self.strings("reply_start", message))
            return
        if not isinstance(message.to_id, telethon.tl.types.PeerChannel):
            await utils.answer(message, self.strings("invalid_chat", message))
            return
        target = (await message.get_reply_message()).date
        ret = []
        try:
            async for msg in msgs:
                if msg.original.date < target:
                    break
                if msg.original.action.message.date < target:
                    continue
                ret += [msg]
        except telethon.errors.rpcerrorlist.ChatAdminRequiredError:
            await utils.answer(message, self.strings("needs_admin", message))
        args = utils.get_args(message)
        if len(args) > 0:
            try:
                count = int(args[0])
                ret = ret[-count:]
            except ValueError:
                pass
        for msg in reversed(ret):
            orig = msg.original.action.message
            deldate = msg.original.date.isoformat()
            origdate = orig.date.isoformat()
            await message.respond(
                self.strings("recovered", message).format(
                    msg.id, origdate, orig.sender_id, deldate, msg.user_id
                )
            )
            if isinstance(orig, telethon.tl.types.MessageService):
                await message.respond(
                    "<b>" + utils.escape_html(orig.stringify()) + "</b>"
                )
            else:
                await message.respond(orig)

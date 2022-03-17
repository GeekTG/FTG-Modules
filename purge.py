# -*- coding: utf-8 -*-

import logging

import telethon

from .. import loader, utils

logger = logging.getLogger(__name__)


@loader.tds
class PurgeMod(loader.Module):
    """Deletes your messages"""

    strings = {
        "name": "Purge",
        "from_where": "<b>Which messages should be purged?</b>",
        "not_supergroup_bot": "<b>Purges can only take place in supergroups</b>",
        "delete_what": "<b>What message should be deleted?</b>",
    }

    @loader.group_admin_delete_messages
    @loader.ratelimit
    async def purgecmd(self, message):
        """Purge from the replied message"""
        if not message.is_reply:
            await utils.answer(message, self.strings("from_where", message))
            return
        from_users = set()
        args = utils.get_args(message)
        for arg in args:
            try:
                try:
                    arg = int(arg)
                except:
                    pass
                entity = await message.client.get_entity(arg)
                if isinstance(entity, telethon.tl.types.User):
                    from_users.add(entity.id)
            except ValueError:
                pass
        msgs = []
        from_ids = set()
        if await message.client.is_bot():
            if not message.is_channel:
                await utils.answer(message, self.strings("not_supergroup_bot", message))
                return
            for msg in range(message.reply_to_msg_id, message.id + 1):
                msgs.append(msg)
                if len(msgs) >= 99:
                    logger.debug(msgs)
                    await message.client.delete_messages(message.to_id, msgs)
                    msgs.clear()
        else:
            async for msg in message.client.iter_messages(
                entity=message.to_id, min_id=message.reply_to_msg_id - 1, reverse=True
            ):
                if from_users and msg.sender_id not in from_users:
                    continue
                msgs.append(msg.id)
                from_ids.add(msg.sender_id)
                if len(msgs) >= 99:
                    logger.debug(msgs)
                    await message.client.delete_messages(message.to_id, msgs)
                    msgs.clear()
        if msgs:
            logger.debug(msgs)
            await message.client.delete_messages(message.to_id, msgs)
        await self.allmodules.log("purge", group=message.to_id, affected_uids=from_ids)

    @loader.group_admin_delete_messages
    @loader.ratelimit
    async def delcmd(self, message):
        """Delete the replied message"""
        msgs = [message.id]
        if not message.is_reply:
            if await message.client.is_bot():
                await utils.answer(message, self.strings("delete_what", message))
                return
            msg = await message.client.iter_messages(
                message.to_id, 1, max_id=message.id
            ).__anext__()
        else:
            msg = await message.get_reply_message()
        msgs.append(msg.id)
        logger.debug(msgs)
        await message.client.delete_messages(message.to_id, msgs)
        await self.allmodules.log(
            "delete", group=message.to_id, affected_uids=[msg.sender_id]
        )

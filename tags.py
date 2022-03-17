# -*- coding: utf-8 -*-

# Module author: @ftgmodulesbyfl1yd

import random

from .. import loader, utils


@loader.tds
class TagMod(loader.Module):
    """Secretly tag a user"""

    strings = {"name": "Tags"}

    async def tagcmd(self, message):
        """.tag <@> <text>."""
        args = utils.get_args_raw(message).split(" ")
        reply = await message.get_reply_message()
        user, tag = None, None
        try:
            if len(args) == 1:
                args = utils.get_args_raw(message)
                user = await message.client.get_entity(
                    args if not args.isnumeric() else int(args)
                )
                tag = "Hey"
            elif len(args) >= 2:
                user = await message.client.get_entity(
                    args[0] if not args[0].isnumeric() else int(args[0])
                )
                tag = utils.get_args_raw(message).split(" ", 1)[1]
        except:
            return await message.edit("Failed to find a user.")
        await message.delete()
        await message.client.send_message(
            message.to_id,
            f'{tag} <a href="tg://user?id={user.id}">\u2060</a>',
            reply_to=reply.id if reply else None,
        )

    async def tagallcmd(self, message):
        """.tagall <text> - tag all users in chat"""
        args = utils.get_args_raw(message)
        tag = args or "Hey"
        await message.delete()
        tags = []
        async for user in message.client.iter_participants(message.to_id):
            tags.append(f"<a href='tg://user?id={user.id}'>\u2060</a>")
        chunkss = list(chunks(tags, 5))
        random.shuffle(chunkss)
        for chunk in chunkss:
            await message.client.send_message(message.to_id, tag + "\u2060".join(chunk))


def chunks(lst, n):
    for i in range(0, len(lst), n):
        yield lst[i : i + n]

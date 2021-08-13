import logging

from .. import loader, utils

logger = logging.getLogger(__name__)

big_rat_url = "https://bigrat.monster/media/bigrat.png"


@loader.tds
class BigRatMod(loader.Module):
    """Big rat"""
    strings = {"name": "Big rat"}

    async def ratcmd(self, message):
        """Usage: .rat (user)"""
        target = await self.get_target(message)
        if not target:
            return await message.edit("<b>Please specify who to rat.</b>")

        msg = await utils.answer(message, "<b>Sending big rat...</b>")
        await message.client.send_file(target, big_rat_url)
        await utils.answer(msg, "<b>Sent big rat successfully!</b>")

    @staticmethod
    async def get_target(message):
        args = utils.get_args_raw(message)
        if args:
            args = args.split()[0]
        reply = await message.get_reply_message()

        if not args and not reply:
            return None
        if reply and reply.from_id:
            return reply.from_id

        user = args if not args.isnumeric() else int(args)
        return await message.client.get_entity(user)

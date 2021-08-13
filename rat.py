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
        args = utils.get_args_raw(message)

        if not args:
            return await message.edit("<b>Please specify who to rat.</b>")
        user = await message.client.get_entity(args if not args.isnumeric() else int(args))

        msg = await utils.answer(message, "<b>Sending big rat...</b>")
        await message.client.send_file(user, big_rat_url)
        await utils.answer(msg, f"<b>Sent big rat to {args} successfully!</b>")
